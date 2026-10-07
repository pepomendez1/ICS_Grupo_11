"""Aplicación web de EcoHarmony Park, parque de diversiones (Flask)."""
import os
import secrets
import uuid
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from functools import wraps

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from parque.compra import (
    CANTIDAD_MAXIMA_ENTRADAS,
    PRECIOS,
    CompraError,
    FormaPago,
    ServicioCompraEntradas,
    SolicitudCompra,
    TipoPase,
    Usuario,
)
from web.contenido import ATRACCIONES, PASES
from web.repositorio import crear_repositorio
from web.servicios import CalendarioEcoHarmony, NotificadorMailSimulado, PasarelaMercadoPagoSimulada
from web.usuarios import RepositorioUsuarios


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


ZONA_PARQUE = ZoneInfo("America/Argentina/Cordoba")


def hoy_en_el_parque() -> date:
    # Vercel corre en UTC: sin esto, después de las 21 h "hoy" sería mañana.
    return datetime.now(ZONA_PARQUE).date()


def create_app(hoy=hoy_en_el_parque, testing=False, repo=None):
    app = Flask(__name__)
    # En Vercel SECRET_KEY tiene que ser fija: si cada instancia generara una
    # distinta, la sesión se perdería entre requests.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
    app.config["TESTING"] = testing

    repo = repo or crear_repositorio()
    usuarios = RepositorioUsuarios(repo)
    usuarios.asegurar_usuario_demo()

    pasarela = PasarelaMercadoPagoSimulada(repo)
    notificador = NotificadorMailSimulado(repo)
    servicio = ServicioCompraEntradas(
        calendario=CalendarioEcoHarmony(),
        pasarela_pago=pasarela,
        notificador=notificador,
        hoy=hoy,
    )
    app.extensions["ecoharmony"] = {"repo": repo}

    @app.template_filter("pesos")
    def pesos(monto):
        return "$" + f"{monto:,}".replace(",", ".")

    @app.template_filter("fecha_hora")
    def fecha_hora(momento):
        if momento.tzinfo is None:
            momento = momento.replace(tzinfo=timezone.utc)
        return momento.astimezone(ZONA_PARQUE).strftime("%d/%m/%Y %H:%M")

    def usuario_actual():
        email = session.get("email")
        return usuarios.obtener(email) if email else None

    @app.context_processor
    def contexto_global():
        return {"usuario": usuario_actual(), "precios": PRECIOS, "pases": PASES}

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
        return render_template("inicio.html", atracciones=ATRACCIONES)

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
            "hoy": hoy().isoformat(),
            "maximo": CANTIDAD_MAXIMA_ENTRADAS,
            "form": {},
            "edades": [],
        }
        if request.method == "GET":
            return render_template("comprar.html", **contexto)

        edades = [_parse_int(e) for e in request.form.getlist("edades")]
        solicitud = SolicitudCompra(
            fecha_visita=_parse_fecha(request.form.get("fecha_visita")),
            cantidad=_parse_int(request.form.get("cantidad")),
            edades=edades,
            tipo_pase=_parse_enum(TipoPase, request.form.get("tipo_pase")),
            forma_pago=_parse_enum(FormaPago, request.form.get("forma_pago")),
        )
        u = usuario_actual()
        try:
            resultado = servicio.comprar(Usuario(email=u["email"], registrado=True), solicitud)
        except CompraError as e:
            contexto.update(form=request.form, edades=request.form.getlist("edades"), error=str(e))
            return render_template("comprar.html", **contexto), 400

        compra_id = uuid.uuid4().hex[:10]
        pago_id = resultado.url_pago.rsplit("/", 1)[-1] if resultado.url_pago else None
        repo.guardar_compra(compra_id, u["email"], resultado, solicitud.edades, pago_id)

        if resultado.url_pago:  # tarjeta → Mercado Pago
            return redirect(resultado.url_pago + f"?compra={compra_id}")
        return redirect(url_for("confirmacion", compra_id=compra_id))

    @app.get("/compras/<compra_id>")
    @login_requerido
    def confirmacion(compra_id):
        compra = repo.obtener_compra(compra_id)
        if not compra or compra["email"] != usuario_actual()["email"]:
            abort(404)
        return render_template("confirmacion.html", compra=compra, r=compra["resultado"])

    # ---------- Mercado Pago (simulado) ----------

    @app.route("/mercadopago/checkout/<pago_id>", methods=["GET", "POST"])
    def mercadopago_checkout(pago_id):
        pago = repo.obtener_pago(pago_id)
        compra_id = request.args.get("compra", "")
        compra = repo.obtener_compra(compra_id)
        if not pago or not compra or compra["pago_id"] != pago_id:
            abort(404)
        if request.method == "POST":
            repo.aprobar_pago(pago_id)
            repo.marcar_compra_pagada(compra_id)
            return redirect(url_for("confirmacion", compra_id=compra_id))
        return render_template("mp_checkout.html", pago=pago, pago_id=pago_id, compra_id=compra_id)

    # ---------- Bandeja de mails (simulada) ----------

    @app.get("/mails")
    @login_requerido
    def mails():
        return render_template("mails.html", mails=repo.mails_de(usuario_actual()["email"]))

    return app
