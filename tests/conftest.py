from datetime import date, datetime, timedelta
from unittest.mock import Mock

import pytest

from parque.config import ZONA_HORARIA
from parque.compra import (
    DIA_CIERRE,
    FormaPago,
    ServicioCompraEntradas,
    SolicitudCompra,
    TipoPase,
    Usuario,
)

HOY = datetime(2026, 10, 6, 10, 0, tzinfo=ZONA_HORARIA)  # martes a las 10:00 (hora de Córdoba)
DIA_CERRADO = date(2026, 10, 12)  # lunes: el parque cierra los lunes
URL_MP = "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=123"
EMAIL_VISITANTE = "visitante.web@mail.com"


@pytest.fixture(autouse=True)
def sin_credenciales_reales(monkeypatch):
    """Aunque estén exportadas en la terminal, los tests nunca usan Mercado Pago
    ni Gmail de verdad: cada test que las necesita las define y mockea."""
    for variable in ("MP_ACCESS_TOKEN", "APP_BASE_URL", "GMAIL_USER", "GMAIL_APP_PASSWORD"):
        monkeypatch.delenv(variable, raising=False)


class CalendarioFake:
    """El parque abre todos los días menos el de cierre (los lunes)."""

    def esta_abierto(self, fecha: date) -> bool:
        return fecha.weekday() != DIA_CIERRE


class ComprasFake:
    """Fake del puerto ComprasDelVisitante: compras anteriores en memoria."""

    def __init__(self):
        self._compras = []  # (email, fecha, CompraExistente)

    def agregar(self, email, fecha, cantidad, forma_pago=FormaPago.EFECTIVO, pagada=False,
                estado="activa", monto=10_000, creado=None, compra_id=None):
        from parque.compra import CompraExistente
        compra = CompraExistente(
            id=compra_id or f"previa-{len(self._compras) + 1}", cantidad=cantidad,
            forma_pago=forma_pago, pagada=pagada, estado=estado, monto=monto,
            creado=creado or HOY,
        )
        self._compras.append((email, fecha, compra))
        return compra

    def compras_para(self, email, fecha):
        return [c for (e, f, c) in self._compras if e == email and f == fecha]


@pytest.fixture
def compras_previas():
    return ComprasFake()


@pytest.fixture
def pasarela_mp():
    pasarela = Mock()
    pasarela.crear_pago.return_value = URL_MP
    return pasarela


@pytest.fixture
def notificador():
    return Mock()


@pytest.fixture
def servicio(pasarela_mp, notificador, compras_previas):
    return ServicioCompraEntradas(
        calendario=CalendarioFake(),
        pasarela_pago=pasarela_mp,
        notificador=notificador,
        reloj=lambda: HOY,
        compras=compras_previas,
    )


@pytest.fixture
def servicio_con_reloj(pasarela_mp, notificador, compras_previas):
    """El mismo servicio, pero con el reloj en otro momento (FAQ 26 y vencimientos)."""
    def crear(ahora):
        return ServicioCompraEntradas(
            calendario=CalendarioFake(),
            pasarela_pago=pasarela_mp,
            notificador=notificador,
            reloj=lambda: ahora,
            compras=compras_previas,
        )
    return crear


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


@pytest.fixture
def registrar():
    """Registra (y deja logueado) un visitante propio del test en el cliente web."""
    def registrar(cliente, email=EMAIL_VISITANTE):
        respuesta = cliente.post(
            "/registro", data={"nombre": "Visitante", "email": email, "password": "secreta1"}
        )
        assert respuesta.status_code == 302, "no se pudo registrar el visitante de prueba"
        return email
    return registrar
