from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from parque.compra import (
    FormaPago,
    ServicioCompraEntradas,
    SolicitudCompra,
    TipoPase,
    Usuario,
)

HOY = date(2026, 10, 6)          # martes
DIA_CERRADO = date(2026, 10, 12)  # lunes: el parque cierra los lunes
URL_MP = "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=123"


class CalendarioFake:
    """El parque abre todos los días menos los lunes."""

    def esta_abierto(self, fecha: date) -> bool:
        return fecha.weekday() != 0


@pytest.fixture
def pasarela_mp():
    pasarela = Mock()
    pasarela.crear_pago.return_value = URL_MP
    return pasarela


@pytest.fixture
def notificador():
    return Mock()


@pytest.fixture
def servicio(pasarela_mp, notificador):
    return ServicioCompraEntradas(
        calendario=CalendarioFake(),
        pasarela_pago=pasarela_mp,
        notificador=notificador,
        hoy=lambda: HOY,
    )


@pytest.fixture
def usuario_registrado():
    return Usuario(email="visitante@mail.com", registrado=True)


@pytest.fixture
def solicitud_valida():
    """Compra válida de base: cada test cambia solo el dato que quiere romper."""
    return SolicitudCompra(
        fecha_visita=HOY + timedelta(days=2),  # jueves, abierto
        cantidad=3,
        edades=[35, 33, 8],
        tipo_pase=TipoPase.REGULAR,
        forma_pago=FormaPago.TARJETA,
    )
