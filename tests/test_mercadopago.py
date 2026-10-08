"""Tests de la pasarela real de Mercado Pago. El SDK siempre está mockeado:
nunca se llama a la API de verdad."""
from unittest.mock import patch

import pytest

from parque.compra import PRECIOS, CompraError
from web import create_app
from web.repositorio import RepositorioMemoria
from web.servicios import (
    EstadoPago,
    PagoNoDisponibleError,
    PasarelaMercadoPago,
    PasarelaMercadoPagoSimulada,
    crear_pasarela,
)

BASE_URL = "https://ecoharmony.vercel.app"


@pytest.fixture
def sdk():
    with patch("web.servicios.mercadopago.SDK") as clase_sdk:
        sdk = clase_sdk.return_value
        sdk.preference.return_value.create.return_value = {
            "status": 201,
            "response": {
                "id": "pref-1",
                "init_point": "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=pref-1",
                "sandbox_init_point": "https://sandbox.mercadopago.com.ar/checkout/v1/redirect?pref_id=pref-1",
            },
        }
        yield sdk


def preferencia_enviada(sdk):
    return sdk.preference.return_value.create.call_args.args[0]


class TestCrearPago:
    def test_usa_el_access_token(self, sdk):
        with patch("web.servicios.mercadopago.SDK") as clase_sdk:
            PasarelaMercadoPago("APP_USR-token", BASE_URL)
        clase_sdk.assert_called_once_with("APP_USR-token")

    def test_preferencia_con_monto_y_referencia_de_la_compra(self, sdk):
        PasarelaMercadoPago("APP_USR-token", BASE_URL).crear_pago(24000, "ana@mail.com", referencia="c1")
        pref = preferencia_enviada(sdk)
        assert pref["external_reference"] == "c1"
        assert pref["items"] == [{
            "title": "EcoHarmony Park · Entradas",
            "quantity": 1,
            "unit_price": 24000,
            "currency_id": "ARS",
        }]

    def test_preferencia_vuelve_a_la_compra_y_notifica_al_webhook(self, sdk):
        PasarelaMercadoPago("APP_USR-token", BASE_URL + "/").crear_pago(24000, "ana@mail.com", referencia="c1")
        pref = preferencia_enviada(sdk)
        assert pref["back_urls"] == {
            "success": f"{BASE_URL}/compras/c1?mp=success",
            "failure": f"{BASE_URL}/compras/c1?mp=failure",
            "pending": f"{BASE_URL}/compras/c1?mp=pending",
        }
        assert pref["auto_return"] == "approved"
        assert pref["notification_url"] == f"{BASE_URL}/mercadopago/webhook"

    def test_devuelve_el_init_point(self, sdk):
        url = PasarelaMercadoPago("APP_USR-token", BASE_URL).crear_pago(24000, "ana@mail.com", referencia="c1")
        assert url == "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=pref-1"

    def test_con_credenciales_test_devuelve_el_sandbox_init_point(self, sdk):
        url = PasarelaMercadoPago("TEST-token", BASE_URL).crear_pago(24000, "ana@mail.com", referencia="c1")
        assert url == "https://sandbox.mercadopago.com.ar/checkout/v1/redirect?pref_id=pref-1"

    def test_si_mp_rechaza_la_preferencia_lanza_error_de_compra(self, sdk):
        sdk.preference.return_value.create.return_value = {
            "status": 400, "response": {"message": "invalid access token"},
        }
        with pytest.raises(PagoNoDisponibleError) as error:
            PasarelaMercadoPago("APP_USR-token", BASE_URL).crear_pago(24000, "ana@mail.com", referencia="c1")
        assert isinstance(error.value, CompraError)


class TestConsultarPago:
    def test_consulta_el_pago_a_la_api(self, sdk):
        sdk.payment.return_value.get.return_value = {"status": 200, "response": {
            "id": 555, "status": "approved", "external_reference": "c1", "transaction_amount": 24000.0,
        }}
        estado = PasarelaMercadoPago("APP_USR-token", BASE_URL).consultar_pago("555")
        sdk.payment.return_value.get.assert_called_once_with("555")
        assert estado == EstadoPago(estado="approved", referencia="c1", monto=24000)

    def test_si_la_api_falla_lanza_error(self, sdk):
        sdk.payment.return_value.get.return_value = {"status": 404, "response": {"message": "not found"}}
        with pytest.raises(PagoNoDisponibleError):
            PasarelaMercadoPago("APP_USR-token", BASE_URL).consultar_pago("555")


class TestElegirPasarela:
    """Con MP_ACCESS_TOKEN se usa Mercado Pago real; sin él, la simulada."""

    def test_sin_access_token_usa_la_simulada(self):
        assert isinstance(crear_pasarela(RepositorioMemoria(), {}), PasarelaMercadoPagoSimulada)

    def test_con_access_token_usa_mercado_pago(self, sdk):
        entorno = {"MP_ACCESS_TOKEN": "TEST-token", "APP_BASE_URL": BASE_URL}
        assert isinstance(crear_pasarela(RepositorioMemoria(), entorno), PasarelaMercadoPago)

    def test_con_access_token_sin_app_base_url_falla(self, sdk):
        with pytest.raises(ValueError, match="APP_BASE_URL"):
            crear_pasarela(RepositorioMemoria(), {"MP_ACCESS_TOKEN": "TEST-token"})

    def test_la_app_usa_mercado_pago_si_hay_access_token(self, sdk, monkeypatch, registrar):
        monkeypatch.setenv("MP_ACCESS_TOKEN", "TEST-token")
        monkeypatch.setenv("APP_BASE_URL", BASE_URL)
        cliente = create_app(testing=True, repo=RepositorioMemoria()).test_client()
        registrar(cliente)
        cliente.post("/comprar", data={
            "fecha_visita": "2099-01-01", "cantidad": "1", "edades": ["30"],  # jueves
            "tipo_pase": "VIP", "forma_pago": "TARJETA",
        })
        assert preferencia_enviada(sdk)["items"][0]["unit_price"] == PRECIOS["VIP"]
