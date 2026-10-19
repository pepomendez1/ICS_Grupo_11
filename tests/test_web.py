"""Tests de integración de la app web: recorren el flujo completo por HTTP."""
import os
import re
from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest

from parque.compra import PRECIOS
from web import create_app
from web.repositorio import RepositorioMemoria, RepositorioPostgres
from web.servicios import EstadoPago, PagoNoDisponibleError
from tests.conftest import EMAIL_VISITANTE

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

HOY = date(2026, 10, 6)  # martes
JUEVES = (HOY + timedelta(days=2)).isoformat()
LUNES = date(2026, 10, 12).isoformat()


@pytest.fixture(params=["memoria", "postgres"])
def repo(request):
    """Corre cada test web con memoria y, si hay TEST_DATABASE_URL, también con Postgres."""
    if request.param == "memoria":
        return RepositorioMemoria()
    if not TEST_DATABASE_URL:
        pytest.skip("Definí TEST_DATABASE_URL para probar contra Postgres")
    repo = RepositorioPostgres(TEST_DATABASE_URL)
    repo.crear_tablas()
    repo._conexion().execute("truncate entradas, mails, compras, pagos, usuarios")
    return repo


@pytest.fixture
def app(repo):
    return create_app(hoy=lambda: HOY, testing=True, repo=repo)


@pytest.fixture
def cliente(app):
    return app.test_client()


@pytest.fixture
def cliente_logueado(cliente, registrar):
    registrar(cliente)
    return cliente


def datos_compra(**cambios):
    datos = {
        "fecha_visita": JUEVES,
        "cantidad": "2",
        "edades": ["30", "8"],
        "tipo_pase": "REGULAR",
        "forma_pago": "EFECTIVO",
    }
    datos.update(cambios)
    return datos


class TestWeb:
    def test_web_comprar_sin_estar_logueado_redirige_a_login(self, cliente):
        respuesta = cliente.get("/comprar")
        assert respuesta.status_code == 302
        assert "/login" in respuesta.headers["Location"]

    def test_web_compra_en_efectivo_muestra_cantidad_y_fecha(self, cliente_logueado):
        respuesta = cliente_logueado.post("/comprar", data=datos_compra(), follow_redirects=True)
        html = respuesta.get_data(as_text=True)
        assert respuesta.status_code == 200
        assert "Compraste 2 entrada(s) para el 08/10/2026" in html

    def test_web_compra_con_tarjeta_redirige_a_mercado_pago(self, cliente_logueado):
        respuesta = cliente_logueado.post("/comprar", data=datos_compra(forma_pago="TARJETA"))
        assert respuesta.status_code == 302
        assert "/mercadopago/checkout/" in respuesta.headers["Location"]

    def test_web_pago_aprobado_en_mercado_pago_vuelve_a_confirmacion(self, cliente_logueado):
        redireccion = cliente_logueado.post("/comprar", data=datos_compra(forma_pago="TARJETA"))
        respuesta = cliente_logueado.post(redireccion.headers["Location"], follow_redirects=True)
        assert "(aprobado)" in respuesta.get_data(as_text=True)

    def test_web_compra_exitosa_llega_mail_a_la_bandeja(self, cliente_logueado, app):
        cliente_logueado.post("/comprar", data=datos_compra())
        mails = app.extensions["ecoharmony"]["repo"].todos_los_mails()
        assert len(mails) == 1
        assert mails[0]["para"] == EMAIL_VISITANTE

    def test_web_compra_parque_cerrado_muestra_error(self, cliente_logueado):
        respuesta = cliente_logueado.post("/comprar", data=datos_compra(fecha_visita=LUNES))
        assert respuesta.status_code == 400
        assert "cerrado" in respuesta.get_data(as_text=True)

    def test_web_compra_once_entradas_muestra_error(self, cliente_logueado):
        respuesta = cliente_logueado.post(
            "/comprar", data=datos_compra(cantidad="11", edades=["30"] * 11)
        )
        assert respuesta.status_code == 400
        assert "entre 1 y 10" in respuesta.get_data(as_text=True)

    def test_web_backend_rechaza_edad_151_aunque_se_saltee_el_html(self, cliente_logueado):
        # Un POST directo no pasa por los min/max del formulario.
        respuesta = cliente_logueado.post("/comprar", data=datos_compra(edades=["30", "151"]))
        assert respuesta.status_code == 400
        assert "entre 0 y 150" in respuesta.get_data(as_text=True)

    def test_web_inputs_de_edad_limitan_entre_0_y_150(self, cliente_logueado):
        html = cliente_logueado.post("/comprar", data=datos_compra(edades=["30", "151"])).get_data(as_text=True)
        assert html.count('min="0" max="150" step="1"') == 2  # los 2 inputs re-renderizados
        assert 'input.max = "150"' in html  # los que crea el JavaScript

    def test_web_registro_permite_comprar(self, cliente):
        cliente.post("/registro", data={"nombre": "Ana", "email": "ana@mail.com", "password": "secreta1"})
        respuesta = cliente.post("/comprar", data=datos_compra(), follow_redirects=True)
        assert "Compraste 2 entrada(s)" in respuesta.get_data(as_text=True)


MONTO_DOS_REGULARES = 2 * PRECIOS["REGULAR"]
URL_MP = "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=pref-1"


@pytest.fixture
def pasarela_mp():
    """Pasarela real de Mercado Pago reemplazada por un Mock."""
    pasarela = Mock()
    pasarela.crear_pago.return_value = URL_MP
    return pasarela


@pytest.fixture
def cliente_mp(repo, pasarela_mp, registrar):
    cliente = create_app(hoy=lambda: HOY, testing=True, repo=repo, pasarela=pasarela_mp).test_client()
    registrar(cliente)
    return cliente


def comprar_con_tarjeta(cliente, pasarela):
    """Compra 2 entradas regulares con tarjeta y devuelve el id de la compra."""
    cliente.post("/comprar", data=datos_compra(forma_pago="TARJETA"))
    return pasarela.crear_pago.call_args.kwargs["referencia"]


def notificar_pago(cliente, pago_id="555"):
    return cliente.post("/mercadopago/webhook", json={"type": "payment", "data": {"id": pago_id}})


class TestMercadoPago:
    """Con tarjeta se paga en Mercado Pago; la compra queda pagada solo si MP lo confirma."""

    def test_web_compra_con_tarjeta_redirige_al_checkout_de_mercado_pago(self, cliente_mp):
        respuesta = cliente_mp.post("/comprar", data=datos_compra(forma_pago="TARJETA"))
        assert respuesta.status_code == 302
        assert respuesta.headers["Location"] == URL_MP

    def test_web_webhook_pago_aprobado_marca_la_compra_pagada(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        pasarela_mp.consultar_pago.return_value = EstadoPago("approved", compra_id, MONTO_DOS_REGULARES)
        assert notificar_pago(cliente_mp).status_code == 200
        pasarela_mp.consultar_pago.assert_called_once_with("555")
        assert repo.obtener_compra(compra_id)["pagada"] is True

    def test_web_webhook_formato_ipn_marca_la_compra_pagada(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        pasarela_mp.consultar_pago.return_value = EstadoPago("approved", compra_id, MONTO_DOS_REGULARES)
        cliente_mp.post("/mercadopago/webhook?topic=payment&id=555")
        pasarela_mp.consultar_pago.assert_called_once_with("555")
        assert repo.obtener_compra(compra_id)["pagada"] is True

    @pytest.mark.parametrize("estado", ["pending", "in_process", "rejected"])
    def test_web_webhook_pago_no_aprobado_no_marca_la_compra(self, cliente_mp, pasarela_mp, repo, estado):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        pasarela_mp.consultar_pago.return_value = EstadoPago(estado, compra_id, MONTO_DOS_REGULARES)
        assert notificar_pago(cliente_mp).status_code == 200
        assert repo.obtener_compra(compra_id)["pagada"] is False

    def test_web_webhook_monto_distinto_no_marca_la_compra(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        pasarela_mp.consultar_pago.return_value = EstadoPago("approved", compra_id, 100)
        notificar_pago(cliente_mp)
        assert repo.obtener_compra(compra_id)["pagada"] is False

    def test_web_webhook_ignora_notificaciones_que_no_son_pagos(self, cliente_mp, pasarela_mp):
        respuesta = cliente_mp.post(
            "/mercadopago/webhook", json={"type": "merchant_order", "data": {"id": "9"}}
        )
        assert respuesta.status_code == 200
        pasarela_mp.consultar_pago.assert_not_called()

    def test_web_webhook_si_mp_no_responde_pide_reintento(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        pasarela_mp.consultar_pago.side_effect = PagoNoDisponibleError("timeout")
        assert notificar_pago(cliente_mp).status_code == 502
        assert repo.obtener_compra(compra_id)["pagada"] is False

    def test_web_vuelta_de_mp_no_confia_en_los_query_params(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        respuesta = cliente_mp.get(
            f"/compras/{compra_id}?mp=success&status=approved"
            "&collection_status=approved&payment_id=555"
        )
        assert respuesta.status_code == 200
        assert "(pendiente)" in respuesta.get_data(as_text=True)
        assert repo.obtener_compra(compra_id)["pagada"] is False
        pasarela_mp.consultar_pago.assert_not_called()

    def test_web_vuelta_de_mp_con_pago_fallido_avisa(self, cliente_mp, pasarela_mp):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        respuesta = cliente_mp.get(f"/compras/{compra_id}?mp=failure")
        assert "No se pudo completar el pago" in respuesta.get_data(as_text=True)


class TestSinUsuarioDemo:
    """No hay un usuario con contraseña pública: cada visitante se registra."""

    def test_web_no_existe_el_usuario_demo(self, cliente, repo):
        respuesta = cliente.post("/login", data={"email": "demo@ecoharmony.com", "password": "demo123"})
        assert respuesta.status_code == 401
        assert repo.obtener_usuario("demo@ecoharmony.com") is None

    def test_web_login_no_muestra_credenciales_de_prueba(self, cliente):
        html = cliente.get("/login").get_data(as_text=True)
        assert "demo@ecoharmony.com" not in html
        assert "demo123" not in html


SECTORES = ["Terrestre", "Acuático", "Aéreo"]
ACTIVIDADES = ["Tirolesa", "Safari", "Palestra", "Jardinería"]
TERMINOS_DE_PARQUE_DE_DIVERSIONES = [
    "calesita", "montaña rusa", "rueda de la fortuna", "casa del terror", "autitos",
    "chocadores", "hamacas", "diversiones", "fila rápida", "vueltas ilimitadas",
    "atracciones", "atracción", "adrenalina", "juegos mecánicos",
]


def sin_terminos_de_parque_de_diversiones(html, donde):
    html = html.lower()
    for termino in TERMINOS_DE_PARQUE_DE_DIVERSIONES:
        assert termino not in html, f"'{termino}' aparece en {donde}"


class TestBioparque:
    """EcoHarmony Park es un bioparque, no un parque de diversiones."""

    def test_web_inicio_presenta_el_bioparque_y_sus_tres_sectores(self, cliente):
        html = cliente.get("/").get_data(as_text=True)
        assert "bioparque" in html.lower()
        for sector in SECTORES:
            assert f"Sector {sector}" in html
        assert "Horarios de alimentación" in html

    def test_web_inicio_menciona_actividades_con_inscripcion_aparte(self, cliente):
        html = cliente.get("/").get_data(as_text=True)
        for actividad in ACTIVIDADES:
            assert actividad in html
        assert "La inscripción es aparte" in html
        assert "no están incluidas en el pase" in html

    def test_web_las_actividades_no_se_venden_en_la_compra(self, cliente_logueado):
        html = cliente_logueado.get("/comprar").get_data(as_text=True)
        for actividad in ACTIVIDADES:
            assert actividad not in html

    def test_web_inicio_describe_los_pases(self, cliente):
        html = cliente.get("/").get_data(as_text=True)
        assert "Acceso al parque, senderos y exhibiciones." in html
        assert "fila preferencial" in html

    @pytest.mark.parametrize("ruta", ["/", "/comprar", "/login", "/registro", "/mails"])
    def test_web_paginas_sin_terminos_de_parque_de_diversiones(self, cliente_logueado, ruta):
        cliente_logueado.post("/comprar", data=datos_compra())  # para que haya un mail en /mails
        sin_terminos_de_parque_de_diversiones(cliente_logueado.get(ruta).get_data(as_text=True), ruta)

    def test_web_confirmacion_sin_terminos_de_parque_de_diversiones(self, cliente_logueado):
        respuesta = cliente_logueado.post("/comprar", data=datos_compra(), follow_redirects=True)
        sin_terminos_de_parque_de_diversiones(respuesta.get_data(as_text=True), "la confirmación")


BASE_URL_APP = "https://ecoharmony.test"
QR = 'class="qr"'  # el <svg> que genera web.entradas.qr_svg


def comprar_en_efectivo(cliente, **cambios):
    """Compra (por defecto 2 entradas: 30 y 8 años) en efectivo y devuelve el id de la compra."""
    respuesta = cliente.post("/comprar", data=datos_compra(**cambios))
    return respuesta.headers["Location"].rsplit("/", 1)[-1]


def entradas_de(repo, compra_id):
    return repo.obtener_compra(compra_id)["resultado"].entradas


class TestEntradasConQR:
    """Cada entrada tiene su página /entradas/<codigo>, con QR si es válida."""

    def test_web_compra_guarda_una_entrada_por_visitante(self, cliente_logueado, repo):
        compra_id = comprar_en_efectivo(cliente_logueado)
        entradas = entradas_de(repo, compra_id)
        assert [(e.numero, e.edad) for e in entradas] == [(1, 30), (2, 8)]
        assert repo.obtener_entrada(entradas[1].codigo)["compra"]["id"] == compra_id

    def test_web_pagina_de_entrada_muestra_sus_datos_sin_iniciar_sesion(self, cliente_logueado, repo, app):
        compra_id = comprar_en_efectivo(cliente_logueado)
        segunda = entradas_de(repo, compra_id)[1]
        html = app.test_client().get(f"/entradas/{segunda.codigo}").get_data(as_text=True)
        for dato in ["EcoHarmony Park", "08/10/2026", "Regular", "8 años", "Entrada 2 de 2"]:
            assert dato in html

    def test_web_entrada_en_efectivo_tiene_qr_valido_y_se_paga_en_boleteria(self, cliente_logueado, repo, monkeypatch):
        from web.entradas import qr_svg
        monkeypatch.setenv("APP_BASE_URL", BASE_URL_APP)
        entrada = entradas_de(repo, comprar_en_efectivo(cliente_logueado))[0]
        html = cliente_logueado.get(f"/entradas/{entrada.codigo}").get_data(as_text=True)
        assert qr_svg(f"{BASE_URL_APP}/entradas/{entrada.codigo}") in html
        assert "Pagar en boletería" in html

    def test_web_entrada_con_tarjeta_pendiente_no_tiene_qr(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        entrada = entradas_de(repo, compra_id)[0]
        html = cliente_mp.get(f"/entradas/{entrada.codigo}").get_data(as_text=True)
        assert "Esperando confirmación del pago" in html
        assert QR not in html

    def test_web_entrada_con_tarjeta_aprobada_por_el_webhook_tiene_qr(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        pasarela_mp.consultar_pago.return_value = EstadoPago("approved", compra_id, MONTO_DOS_REGULARES)
        notificar_pago(cliente_mp)
        entrada = entradas_de(repo, compra_id)[0]
        html = cliente_mp.get(f"/entradas/{entrada.codigo}").get_data(as_text=True)
        assert QR in html
        assert "Esperando confirmación del pago" not in html

    def test_web_entrada_inexistente_da_404(self, cliente):
        assert cliente.get("/entradas/no-existe").status_code == 404

    def test_web_pagina_de_entrada_sin_terminos_de_parque_de_diversiones(self, cliente_logueado, repo):
        entrada = entradas_de(repo, comprar_en_efectivo(cliente_logueado))[0]
        html = cliente_logueado.get(f"/entradas/{entrada.codigo}").get_data(as_text=True)
        sin_terminos_de_parque_de_diversiones(html, "la página de la entrada")

    def test_web_confirmacion_en_efectivo_muestra_cada_entrada_con_su_qr(self, cliente_logueado):
        compra_id = comprar_en_efectivo(cliente_logueado)
        html = cliente_logueado.get(f"/compras/{compra_id}").get_data(as_text=True)
        assert html.count(QR) == 2
        assert "Entrada 1 de 2" in html and "Entrada 2 de 2" in html
        assert "Pagar en boletería" in html

    def test_web_confirmacion_con_tarjeta_pendiente_muestra_las_entradas_sin_qr(self, cliente_mp, pasarela_mp):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        html = cliente_mp.get(f"/compras/{compra_id}?mp=pending").get_data(as_text=True)
        assert QR not in html
        assert "Entrada 2 de 2" in html
        assert "Esperando confirmación del pago" in html

    def test_web_confirmacion_se_puede_imprimir(self, cliente_logueado):
        compra_id = comprar_en_efectivo(cliente_logueado)
        html = cliente_logueado.get(f"/compras/{compra_id}").get_data(as_text=True)
        assert "@media print" in html
        assert "window.print()" in html


ASUNTO_TUS_ENTRADAS = "EcoHarmony Park — Tus entradas"


def mails_tus_entradas(repo):
    return [m for m in repo.todos_los_mails() if m["asunto"] == ASUNTO_TUS_ENTRADAS]


class TestMailTusEntradas:
    """Con tarjeta, los QR llegan en un segundo mail cuando se aprueba el pago."""

    def test_web_webhook_aprobado_manda_tus_entradas(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        pasarela_mp.consultar_pago.return_value = EstadoPago("approved", compra_id, MONTO_DOS_REGULARES)
        notificar_pago(cliente_mp)
        mails = mails_tus_entradas(repo)
        assert len(mails) == 1
        assert mails[0]["para"] == EMAIL_VISITANTE

    def test_web_webhook_repetido_no_manda_tus_entradas_dos_veces(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        pasarela_mp.consultar_pago.return_value = EstadoPago("approved", compra_id, MONTO_DOS_REGULARES)
        notificar_pago(cliente_mp)
        notificar_pago(cliente_mp)  # MP reintenta las notificaciones
        assert len(mails_tus_entradas(repo)) == 1

    def test_web_webhook_pendiente_no_manda_tus_entradas(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        pasarela_mp.consultar_pago.return_value = EstadoPago("pending", compra_id, MONTO_DOS_REGULARES)
        notificar_pago(cliente_mp)
        assert mails_tus_entradas(repo) == []

    def test_web_checkout_simulado_aprobado_manda_tus_entradas(self, cliente_logueado, repo):
        redireccion = cliente_logueado.post("/comprar", data=datos_compra(forma_pago="TARJETA"))
        cliente_logueado.post(redireccion.headers["Location"])
        assert len(mails_tus_entradas(repo)) == 1

    def test_web_compra_en_efectivo_no_manda_tus_entradas(self, cliente_logueado, repo):
        comprar_en_efectivo(cliente_logueado)  # los QR ya van en el mail de confirmación
        assert mails_tus_entradas(repo) == []


BOTON_COMPRAR_MAS = '<a class="boton" href="/comprar">Comprar más entradas</a>'


@pytest.fixture
def con_gmail(monkeypatch):
    """Gmail real configurado (con smtplib mockeado: no sale ningún mail)."""
    monkeypatch.setenv("GMAIL_USER", "ecoharmony.park@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "abcd efgh ijkl mnop")
    with patch("web.servicios.smtplib.SMTP"):
        yield


@pytest.fixture
def cliente_gmail(con_gmail, repo, pasarela_mp, registrar):
    cliente = create_app(hoy=lambda: HOY, testing=True, repo=repo, pasarela=pasarela_mp).test_client()
    registrar(cliente)
    return cliente


class TestBandejaSimulada:
    """"Mis mails" existe solo mientras no hay Gmail real configurado."""

    def test_web_con_gmail_la_confirmacion_no_tiene_boton_ni_link_a_mis_mails(self, cliente_gmail):
        compra_id = comprar_en_efectivo(cliente_gmail)
        html = cliente_gmail.get(f"/compras/{compra_id}").get_data(as_text=True)
        assert "Ver mail de confirmación" not in html
        assert 'href="/mails"' not in html
        assert "Mis mails" not in html

    def test_web_con_gmail_mis_mails_da_404(self, cliente_gmail):
        assert cliente_gmail.get("/mails").status_code == 404

    def test_web_con_gmail_en_efectivo_avisa_que_mandamos_las_entradas(self, cliente_gmail):
        compra_id = comprar_en_efectivo(cliente_gmail)
        html = cliente_gmail.get(f"/compras/{compra_id}").get_data(as_text=True)
        assert f"Te mandamos un mail con tus entradas a <strong>{EMAIL_VISITANTE}</strong>" in html

    def test_web_con_gmail_con_tarjeta_pendiente_avisa_que_las_mandamos_al_aprobarse(self, cliente_gmail, pasarela_mp):
        compra_id = comprar_con_tarjeta(cliente_gmail, pasarela_mp)
        html = cliente_gmail.get(f"/compras/{compra_id}?mp=pending").get_data(as_text=True)
        assert f"Cuando se apruebe te mandamos las entradas a <strong>{EMAIL_VISITANTE}</strong>" in html

    def test_web_con_gmail_comprar_mas_entradas_es_el_boton_principal(self, cliente_gmail):
        compra_id = comprar_en_efectivo(cliente_gmail)
        assert BOTON_COMPRAR_MAS in cliente_gmail.get(f"/compras/{compra_id}").get_data(as_text=True)

    def test_web_sin_gmail_sigue_la_bandeja_y_comprar_mas_es_el_boton_principal(self, cliente_logueado):
        compra_id = comprar_en_efectivo(cliente_logueado)
        html = cliente_logueado.get(f"/compras/{compra_id}").get_data(as_text=True)
        assert "Ver mail de confirmación" in html
        assert 'href="/mails"' in html
        assert BOTON_COMPRAR_MAS in html
        assert cliente_logueado.get("/mails").status_code == 200


def volver_de_mp(cliente, compra_id, resultado=None):
    """La back_url de Mercado Pago: /compras/<id>?mp=success|pending|failure."""
    ruta = f"/compras/{compra_id}" + (f"?mp={resultado}" if resultado else "")
    return cliente.get(ruta).get_data(as_text=True)


def aprobar_por_webhook(cliente, pasarela, compra_id):
    pasarela.consultar_pago.return_value = EstadoPago("approved", compra_id, MONTO_DOS_REGULARES)
    notificar_pago(cliente)


class TestVueltaDeMercadoPago:
    """La vuelta de MP distingue aprobado / pendiente / rechazado. Pagada solo la marca el webhook."""

    def test_web_rechazado_no_promete_mails_ni_muestra_qr(self, cliente_mp, pasarela_mp):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        html = volver_de_mp(cliente_mp, compra_id, "failure")
        assert "No se pudo completar el pago" in html
        assert "mail de confirmación" not in html.lower()
        assert "te mandamos las entradas" not in html.lower()
        assert QR not in html
        assert "Volver e intentar de nuevo" in html
        assert "Comprar más entradas" not in html

    def test_web_rechazado_queda_registrado_en_la_base(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        volver_de_mp(cliente_mp, compra_id, "failure")
        assert repo.obtener_compra(compra_id)["estado"] == "rechazada"
        # Sigue rechazada aunque después se abra sin el query param.
        assert "No se pudo completar el pago" in volver_de_mp(cliente_mp, compra_id)

    def test_web_entrada_de_compra_rechazada_no_es_valida(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        volver_de_mp(cliente_mp, compra_id, "failure")
        entrada = entradas_de(repo, compra_id)[0]
        html = cliente_mp.get(f"/entradas/{entrada.codigo}").get_data(as_text=True)
        assert "Compra cancelada · Entrada no válida" in html
        assert QR not in html

    def test_web_pendiente_sin_aviso_de_error_ni_qr(self, cliente_mp, pasarela_mp):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        html = volver_de_mp(cliente_mp, compra_id, "pending")
        assert "Tu pago está pendiente" in html
        assert f"Cuando se apruebe te mandamos las entradas a <strong>{EMAIL_VISITANTE}</strong>" in html
        assert 'class="aviso error"' not in html
        assert QR not in html

    def test_web_webhook_aprobado_y_vuelta_con_failure_se_muestra_aprobada(self, cliente_mp, pasarela_mp, repo):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        aprobar_por_webhook(cliente_mp, pasarela_mp, compra_id)
        html = volver_de_mp(cliente_mp, compra_id, "failure")
        assert "¡Listo, te esperamos!" in html
        assert QR in html
        assert "No se pudo completar el pago" not in html
        assert repo.obtener_compra(compra_id)["estado"] != "rechazada"

    def test_web_rechazada_y_despues_aprobada_por_el_webhook_queda_aprobada(self, cliente_mp, pasarela_mp, repo):
        # Si MP termina cobrando (por ejemplo, un medio que se acredita tarde), la compra vale.
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        volver_de_mp(cliente_mp, compra_id, "failure")
        aprobar_por_webhook(cliente_mp, pasarela_mp, compra_id)
        assert QR in volver_de_mp(cliente_mp, compra_id)
        entrada = entradas_de(repo, compra_id)[0]
        assert QR in cliente_mp.get(f"/entradas/{entrada.codigo}").get_data(as_text=True)


def compra_rechazada(cliente, pasarela, **datos):
    """Compra con tarjeta que vuelve de MP con failure. Devuelve su id."""
    cliente.post("/comprar", data=datos_compra(forma_pago="TARJETA", **datos))
    compra_id = pasarela.crear_pago.call_args.kwargs["referencia"]
    volver_de_mp(cliente, compra_id, "failure")
    return compra_id


class TestReintentoDeCompraRechazada:
    """"Volver e intentar de nuevo" precarga la compra rechazada en el formulario."""

    def test_web_reintento_precarga_todos_los_campos_incluidas_las_edades(self, cliente_mp, pasarela_mp):
        compra_id = compra_rechazada(
            cliente_mp, pasarela_mp, fecha_visita="2026-10-09", cantidad="3",
            edades=["41", "12", "0"], tipo_pase="VIP",
        )
        html = cliente_mp.get(f"/comprar?reintentar={compra_id}").get_data(as_text=True)
        assert re.search(r'name="fecha_visita"[^>]*value="2026-10-09"', html)
        assert re.search(r'name="cantidad"[^>]*value="3"', html)
        assert re.findall(r'<input name="edades"[^>]*value="(\d+)"', html) == ["41", "12", "0"]
        assert 'name="tipo_pase" value="VIP" checked' in html
        assert 'name="forma_pago" value="TARJETA" checked' in html

    def test_web_reintento_crea_una_compra_nueva_y_la_rechazada_no_se_reutiliza(self, cliente_mp, pasarela_mp, repo):
        rechazada = compra_rechazada(cliente_mp, pasarela_mp)
        respuesta = cliente_mp.post("/comprar", data=datos_compra(forma_pago="EFECTIVO"))
        nueva = respuesta.headers["Location"].rsplit("/", 1)[-1]
        assert nueva != rechazada
        assert repo.obtener_compra(rechazada)["estado"] == "rechazada"
        assert repo.obtener_compra(nueva)["estado"] == "activa"

    def test_web_no_se_puede_reintentar_la_compra_de_otro_visitante(self, cliente_mp, pasarela_mp, app, registrar):
        compra_id = compra_rechazada(cliente_mp, pasarela_mp)
        otro = app.test_client()
        registrar(otro, "otra.persona@mail.com")
        assert otro.get(f"/comprar?reintentar={compra_id}").status_code == 404


class TestConfirmandoPago:
    """Volvió aprobado pero el webhook todavía no llegó: la página consulta el estado."""

    def test_web_estado_de_la_compra_devuelve_json_con_el_estado(self, cliente_mp, pasarela_mp):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        respuesta = cliente_mp.get(f"/compras/{compra_id}/estado")
        assert respuesta.status_code == 200
        assert respuesta.get_json() == {"pagada": False, "estado": "activa"}
        assert respuesta.headers["Cache-Control"] == "no-store"
        aprobar_por_webhook(cliente_mp, pasarela_mp, compra_id)
        assert cliente_mp.get(f"/compras/{compra_id}/estado").get_json() == {"pagada": True, "estado": "activa"}

    def test_web_estado_de_una_compra_rechazada(self, cliente_mp, pasarela_mp):
        compra_id = compra_rechazada(cliente_mp, pasarela_mp)
        assert cliente_mp.get(f"/compras/{compra_id}/estado").get_json() == {"pagada": False, "estado": "rechazada"}

    def test_web_estado_de_la_compra_de_otro_visitante_da_404(self, cliente_mp, pasarela_mp, app, registrar):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        otro = app.test_client()
        registrar(otro, "otra.persona@mail.com")
        assert otro.get(f"/compras/{compra_id}/estado").status_code == 404

    def test_web_estado_sin_sesion_da_401(self, cliente_mp, pasarela_mp, app):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        assert app.test_client().get(f"/compras/{compra_id}/estado").status_code == 401

    @pytest.mark.parametrize("vuelta", ["approved", "success"])
    def test_web_aprobado_sin_webhook_muestra_confirmando_sin_qr(self, cliente_mp, pasarela_mp, vuelta):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        html = volver_de_mp(cliente_mp, compra_id, vuelta)
        assert "Estamos confirmando tu pago…" in html
        assert 'class="cargando"' in html
        assert QR not in html
        assert "Entrada 1 de 2" not in html  # nada de entradas vacías
        assert f'data-estado-url="/compras/{compra_id}/estado"' in html
        assert 'data-intervalo-ms="3000"' in html
        assert 'data-limite-ms="60000"' in html
        assert ("Tu pago se está procesando. Cuando se confirme te mandamos las entradas a "
                f"<strong>{EMAIL_VISITANTE}</strong>.") in html

    def test_web_aprobado_con_webhook_ya_recibido_muestra_los_qr(self, cliente_mp, pasarela_mp):
        compra_id = comprar_con_tarjeta(cliente_mp, pasarela_mp)
        aprobar_por_webhook(cliente_mp, pasarela_mp, compra_id)
        html = volver_de_mp(cliente_mp, compra_id, "approved")
        assert "Estamos confirmando tu pago…" not in html
        assert QR in html


class TestHorario:
    """FAQ 11: el parque abre de 8:30 a 19:00."""

    @pytest.mark.parametrize("ruta", ["/", "/comprar"])
    def test_web_muestra_el_horario(self, cliente_logueado, ruta):
        html = cliente_logueado.get(ruta).get_data(as_text=True)
        assert "de 8:30 a 19:00" in html
