"""Tests de integración de la app web: recorren el flujo completo por HTTP."""
import os
from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from parque.compra import PRECIOS
from web import create_app
from web.repositorio import RepositorioMemoria, RepositorioPostgres
from web.servicios import EstadoPago, PagoNoDisponibleError

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
    repo._conexion().execute("truncate mails, compras, pagos, usuarios")
    return repo


@pytest.fixture
def app(repo):
    return create_app(hoy=lambda: HOY, testing=True, repo=repo)


@pytest.fixture
def cliente(app):
    return app.test_client()


@pytest.fixture
def cliente_logueado(cliente):
    cliente.post("/login", data={"email": "demo@ecoharmony.com", "password": "demo123"})
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
        assert mails[0]["para"] == "demo@ecoharmony.com"

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
def cliente_mp(repo, pasarela_mp):
    cliente = create_app(hoy=lambda: HOY, testing=True, repo=repo, pasarela=pasarela_mp).test_client()
    cliente.post("/login", data={"email": "demo@ecoharmony.com", "password": "demo123"})
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
        assert "El pago no se completó" in respuesta.get_data(as_text=True)
