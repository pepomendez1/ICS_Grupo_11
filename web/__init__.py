"""Aplicación web de EcoHarmony Park, bioparque (Flask)."""
import os
import secrets
import uuid
from datetime import date, timezone
from functools import wraps

import logging

from flask import Flask, abort, flash, g, jsonify, redirect, render_template, request, session, url_for

from parque import config
from parque.calendario import ahora_en_el_parque
from parque.compra import (
    CANTIDAD_MAXIMA_ENTRADAS,
    EDAD_MAXIMA,
    PRECIOS,
    CompraError,
    FormaPago,
    ServicioCompraEntradas,
    SolicitudCompra,
    TipoPase,
    Usuario,
)
from web.contenido import (
    ACTIVIDADES,
    HORARIOS_ALIMENTACION,
    PASES,
    SECTORES,
    dia_de_cierre,
    horario,
    pesos,
)
from web.entradas import estado_de, qr_svg, url_entrada
from web.repositorio import crear_repositorio
from web.servicios import (
    CalendarioEcoHarmony,
    NotificadorMailSimulado,
    PagoNoDisponibleError,
    PasarelaMercadoPagoSimulada,
    crear_notificador,
    crear_pasarela,
)
from web.usuarios import RepositorioUsuarios


log = logging.getLogger(__name__)


def _parse_fecha(valor):
    try:
        return date.fromisoformat(valor) if valor else None
    except ValueError:
        return None


def _parse_int(valor):
    try:
        return int(valor) if valor not in (None, "") else None
    except ValueError:
        return None


def _parse_enum(enum_cls, valor):
    try:
        return enum_cls(valor)
    except ValueError:
        return None


ZONA_PARQUE = config.ZONA_HORARIA


def resultado_del_pago(compra, vuelta_mp):
    """Qué pantalla de confirmación mostrar. Lo guardado en la base manda sobre
    el query param: si el webhook ya aprobó el pago, es "aprobado" aunque MP
    haya vuelto con failure."""
    if compra["resultado"].forma_pago == FormaPago.EFECTIVO:
        return "efectivo"
    if compra["pagada"]:
        return "aprobado"
    if compra["estado"] == "rechazada":
        return "rechazado"
    if vuelta_mp in ("success", "approved"):
        return "confirmando"  # MP dice que aprobó, falta que llegue el webhook
    return "pendiente"


def create_app(reloj=ahora_en_el_parque, testing=False, repo=None, pasarela=None, notificador=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
    app.config["TESTING"] = testing

    repo = repo or crear_repositorio()
    usuarios = RepositorioUsuarios(repo)

    pasarela = pasarela or crear_pasarela(repo, os.environ)
    notificador = notificador or crear_notificador(repo, os.environ)
    servicio = ServicioCompraEntradas(
        calendario=CalendarioEcoHarmony(),
        pasarela_pago=pasarela,
        notificador=notificador,
        reloj=reloj,
    )
    app.extensions["ecoharmony"] = {"repo": repo}
    # "Mis mails" es la bandeja del notificador simulado: con Gmail real no existe.
    bandeja_simulada = isinstance(notificador, NotificadorMailSimulado)

    app.add_template_filter(pesos, "pesos")

    @app.template_filter("fecha_hora")
    def fecha_hora(momento):
        if momento.tzinfo is None:
            momento = momento.replace(tzinfo=timezone.utc)
        return momento.astimezone(ZONA_PARQUE).strftime("%d/%m/%Y %H:%M")

    def usuario_actual():
        # Se busca una sola vez por request y se guarda en g.
        if "usuario" not in g:
            email = session.get("email")
            g.usuario = usuarios.obtener(email) if email else None
        return g.usuario

    @app.context_processor
    def contexto_global():
        return {
            "usuario": usuario_actual(), "precios": PRECIOS, "pases": PASES,
            "dia_cierre": dia_de_cierre(), "horario": horario(),
            "bandeja_simulada": bandeja_simulada,
        }

    def base_url():
        """URL pública de la app: la que va en los QR."""
        return os.environ.get("APP_BASE_URL") or request.url_root

    def tickets(compra):
        """Las entradas de la compra listas para mostrar, con QR solo si son válidas."""
        valida = estado_de(compra).valida
        return [
            {"entrada": e, "qr": qr_svg(url_entrada(base_url(), e.codigo)) if valida else None}
            for e in compra["resultado"].entradas
        ]

    def login_requerido(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if not usuario_actual():
                flash("Tenés que iniciar sesión para comprar entradas.", "error")
                return redirect(url_for("login", next=request.path))
            return vista(*args, **kwargs)
        return envoltura

    # ---------- Páginas ----------

    @app.get("/")
    def inicio():
        return render_template(
            "inicio.html", sectores=SECTORES, horarios_alimentacion=HORARIOS_ALIMENTACION,
            actividades=ACTIVIDADES, maximo_entradas=CANTIDAD_MAXIMA_ENTRADAS,
        )

    @app.route("/registro", methods=["GET", "POST"])
    def registro():
        if request.method == "POST":
            try:
                usuarios.registrar(
                    request.form.get("nombre", ""),
                    request.form.get("email", ""),
                    request.form.get("password", ""),
                )
            except ValueError as e:
                flash(str(e), "error")
                return render_template("registro.html", form=request.form), 400
            session["email"] = request.form["email"].strip().lower()
            flash("¡Cuenta creada! Ya podés comprar tus entradas.", "ok")
            return redirect(url_for("comprar"))
        return render_template("registro.html", form={})

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            usuario = usuarios.autenticar(request.form.get("email", ""), request.form.get("password", ""))
            if not usuario:
                flash("Email o contraseña incorrectos.", "error")
                return render_template("login.html", form=request.form), 401
            session["email"] = usuario["email"]
            destino = request.args.get("next") or url_for("comprar")
            if not destino.startswith("/"):
                destino = url_for("comprar")
            return redirect(destino)
        return render_template("login.html", form={})

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("inicio"))

    @app.route("/comprar", methods=["GET", "POST"])
    @login_requerido
    def comprar():
        contexto = {
            "hoy": reloj().date().isoformat(),
            "maximo": CANTIDAD_MAXIMA_ENTRADAS,
            "edad_maxima": EDAD_MAXIMA,
            "form": {},
            "edades": [],
        }
        if request.method == "GET":
            reintentar = request.args.get("reintentar")
            if reintentar:
                # "Volver e intentar de nuevo": precarga la compra anterior. Al
                # confirmar se crea una compra nueva; la anterior no se reutiliza.
                anterior = repo.obtener_compra(reintentar)
                if not anterior or anterior["email"] != usuario_actual()["email"]:
                    abort(404)
                r = anterior["resultado"]
                contexto.update(
                    form={
                        "fecha_visita": r.fecha_visita.isoformat(),
                        "cantidad": str(r.cantidad),
                        "tipo_pase": r.tipo_pase.value,
                        "forma_pago": r.forma_pago.value,
                    },
                    edades=[str(e) for e in anterior["edades"]],
                    reintento=True,
                )
            return render_template("comprar.html", **contexto)

        compra_id = uuid.uuid4().hex[:10]
        edades = [_parse_int(e) for e in request.form.getlist("edades")]
        solicitud = SolicitudCompra(
            fecha_visita=_parse_fecha(request.form.get("fecha_visita")),
            cantidad=_parse_int(request.form.get("cantidad")),
            edades=edades,
            tipo_pase=_parse_enum(TipoPase, request.form.get("tipo_pase")),
            forma_pago=_parse_enum(FormaPago, request.form.get("forma_pago")),
            referencia=compra_id,
        )
        u = usuario_actual()
        try:
            resultado = servicio.comprar(Usuario(email=u["email"], registrado=True), solicitud)
        except CompraError as e:
            contexto.update(form=request.form, edades=request.form.getlist("edades"), error=str(e))
            return render_template("comprar.html", **contexto), 400


        pago_id = PasarelaMercadoPagoSimulada.id_de_pago(resultado.url_pago)
        repo.guardar_compra(compra_id, u["email"], resultado, solicitud.edades, pago_id)

        if resultado.url_pago:  # tarjeta → Mercado Pago
            return redirect(resultado.url_pago)
        return redirect(url_for("confirmacion", compra_id=compra_id))

    @app.get("/compras/<compra_id>")
    @login_requerido
    def confirmacion(compra_id):
        compra = repo.obtener_compra(compra_id)
        if not compra or compra["email"] != usuario_actual()["email"]:
            abort(404)
        # ?mp=... es la back_url de Mercado Pago. Sirve para MOSTRAR el resultado
        # y para cancelar la compra si volvió sin pagar, pero nunca para marcarla
        # pagada: eso lo decide solo el webhook.
        vuelta_mp = request.args.get("mp")
        con_tarjeta = compra["resultado"].forma_pago == FormaPago.TARJETA
        if con_tarjeta and vuelta_mp == "failure" and repo.marcar_compra_rechazada(compra_id):
            compra = repo.obtener_compra(compra_id)
        return render_template(
            "confirmacion.html", compra=compra, r=compra["resultado"],
            resultado_pago=resultado_del_pago(compra, vuelta_mp),
            tickets=tickets(compra), estado=estado_de(compra),
        )

    def acreditar_pago(compra_id):
        """Marca la compra pagada y manda "Tus entradas" con los QR. Si ya estaba
        pagada no hace nada: MP puede repetir la misma notificación."""
        if not repo.marcar_compra_pagada(compra_id):
            return
        compra = repo.obtener_compra(compra_id)
        notificador.enviar_entradas(compra["email"], compra["resultado"])

    @app.get("/entradas/<codigo>")
    def entrada(codigo):
        """Página pública de una entrada: es a donde apunta su QR. El código no se
        puede adivinar, así que no pide sesión (se escanea en el ingreso)."""
        encontrada = repo.obtener_entrada(codigo)
        if not encontrada:
            abort(404)
        compra = encontrada["compra"]
        t = next(t for t in tickets(compra) if t["entrada"].codigo == codigo)
        return render_template(
            "entrada.html", r=compra["resultado"], t=t, estado=estado_de(compra)
        )

    @app.get("/compras/<compra_id>/estado")
    def estado_compra(compra_id):
        """Estado liviano de la compra para el polling de "Estamos confirmando
        tu pago…". Solo para el dueño; JSON también en los errores."""
        usuario = usuario_actual()
        if not usuario:
            return jsonify(error="Tenés que iniciar sesión"), 401
        compra = repo.obtener_compra(compra_id)
        if not compra or compra["email"] != usuario["email"]:
            return jsonify(error="No existe la compra"), 404
        respuesta = jsonify(pagada=compra["pagada"], estado=compra["estado"])
        respuesta.headers["Cache-Control"] = "no-store"
        return respuesta

    # ---------- Mercado Pago ----------

    @app.post("/mercadopago/webhook")
    def mercadopago_webhook():
        """notification_url de la preferencia. MP avisa que cambió un pago y acá
        se lo consultamos a su API: el aviso en sí no se toma como prueba de nada."""
        if not hasattr(pasarela, "consultar_pago"):
            abort(404)  # pasarela simulada: no hay webhook
        datos = request.get_json(silent=True) or {}
        # Webhooks: {"type": "payment", "data": {"id": ...}}; IPN: ?topic=payment&id=...
        tipo = datos.get("type") or request.args.get("type") or request.args.get("topic")
        pago_id = (datos.get("data") or {}).get("id") or request.args.get("data.id") or request.args.get("id")
        if tipo != "payment" or not pago_id:
            return "", 200

        try:
            pago = pasarela.consultar_pago(str(pago_id))
        except PagoNoDisponibleError:
            return "", 502  # MP reintenta la notificación más tarde

        compra = repo.obtener_compra(pago.referencia) if pago.referencia else None
        if not compra:
            log.warning("Pago %s de MP sin compra asociada (%s)", pago_id, pago.referencia)
        elif pago.estado != "approved":
            log.info("Pago %s de la compra %s en estado %s", pago_id, pago.referencia, pago.estado)
        elif pago.monto != compra["resultado"].monto:
            log.warning("Pago %s por $%s no coincide con la compra %s", pago_id, pago.monto, pago.referencia)
        else:
            acreditar_pago(pago.referencia)
        return "", 200

    # ---------- Mercado Pago simulado ----------

    @app.route("/mercadopago/checkout/<pago_id>", methods=["GET", "POST"])
    def mercadopago_checkout(pago_id):
        pago = repo.obtener_pago(pago_id)
        compra_id = request.args.get("compra", "")
        compra = repo.obtener_compra(compra_id)
        if not pago or not compra or compra["pago_id"] != pago_id:
            abort(404)
        if request.method == "POST":
            repo.aprobar_pago(pago_id)
            acreditar_pago(compra_id)
            return redirect(url_for("confirmacion", compra_id=compra_id))
        return render_template("mp_checkout.html", pago=pago, pago_id=pago_id, compra_id=compra_id)

    # ---------- Bandeja de mails (simulada) ----------

    @app.get("/mails")
    @login_requerido
    def mails():
        if not bandeja_simulada:
            abort(404)
        return render_template("mails.html", mails=repo.mails_de(usuario_actual()["email"]))

    return app
