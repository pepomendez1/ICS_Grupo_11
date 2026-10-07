"""Implementaciones concretas de las dependencias externas para la app web.

Mercado Pago y el mail tienen una versión real y una simulada con la misma
interfaz; cuál se usa depende de las variables de entorno. parque/compra.py
no se entera.
"""
import logging
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Optional
from urllib.parse import urlsplit

import mercadopago

from parque.compra import CompraError

log = logging.getLogger(__name__)


class CalendarioEcoHarmony:
    """EcoHarmony Park abre de martes a domingo (cierra los lunes)
    y además cierra en los feriados cargados acá."""

    FERIADOS_CERRADO = {
        date(2026, 12, 25),
        date(2027, 1, 1),
    }

    def esta_abierto(self, fecha: date) -> bool:
        return fecha.weekday() != 0 and fecha not in self.FERIADOS_CERRADO


class PasarelaMercadoPagoSimulada:
    """Simula la creación de una preferencia de pago en Mercado Pago."""

    def __init__(self, repo):
        self._repo = repo

    PREFIJO_URL = "/mercadopago/checkout/"

    def crear_pago(self, monto: int, email: str, referencia: Optional[str] = None) -> str:
        pago_id = uuid.uuid4().hex[:10]
        self._repo.guardar_pago(pago_id, monto, email)
        return f"{self.PREFIJO_URL}{pago_id}?compra={referencia}"

    @classmethod
    def id_de_pago(cls, url: Optional[str]) -> Optional[str]:
        """El id del pago simulado que está en la URL, o None si la URL no es suya."""
        ruta = urlsplit(url or "").path
        return ruta.removeprefix(cls.PREFIJO_URL) if ruta.startswith(cls.PREFIJO_URL) else None


class PagoNoDisponibleError(CompraError):
    """Mercado Pago no pudo iniciar el pago."""


@dataclass
class EstadoPago:
    estado: str       # "approved", "pending", "rejected", ...
    referencia: str   # external_reference = id de la compra
    monto: int


class PasarelaMercadoPago:
    """Checkout Pro de Mercado Pago con el SDK oficial.

    No mandamos el email del comprador en la preferencia: en el entorno de
    prueba, mezclar un email real con usuarios de prueba hace que MP rechace
    el pago.
    """

    TITULO = "EcoHarmony Park · Entradas"

    def __init__(self, access_token: str, base_url: str):
        self._sdk = mercadopago.SDK(access_token)
        self._base_url = base_url.rstrip("/")
        self._sandbox = access_token.startswith("TEST-")

    def crear_pago(self, monto: int, email: str, referencia: Optional[str] = None) -> str:
        vuelta = f"{self._base_url}/compras/{referencia}?mp="
        respuesta = self._sdk.preference().create({
            "items": [{
                "title": self.TITULO,
                "quantity": 1,
                "unit_price": monto,
                "currency_id": "ARS",
            }],
            "external_reference": referencia,
            "back_urls": {
                "success": vuelta + "success",
                "failure": vuelta + "failure",
                "pending": vuelta + "pending",
            },
            "auto_return": "approved",
            "notification_url": f"{self._base_url}/mercadopago/webhook",
        })
        if respuesta.get("status") not in (200, 201):
            log.error("Mercado Pago rechazó la preferencia: %s", respuesta)
            raise PagoNoDisponibleError(
                "No pudimos conectar con Mercado Pago. Probá de nuevo o elegí pagar en efectivo."
            )
        preferencia = respuesta["response"]
        return preferencia["sandbox_init_point" if self._sandbox else "init_point"]

    def consultar_pago(self, pago_id: str) -> EstadoPago:
        respuesta = self._sdk.payment().get(pago_id)
        if respuesta.get("status") != 200:
            log.error("No se pudo consultar el pago %s en Mercado Pago: %s", pago_id, respuesta)
            raise PagoNoDisponibleError(f"No se pudo consultar el pago {pago_id}")
        pago = respuesta["response"]
        return EstadoPago(
            estado=pago["status"],
            referencia=pago.get("external_reference"),
            monto=round(pago["transaction_amount"]),
        )


def crear_pasarela(repo, entorno):
    """Mercado Pago real si está MP_ACCESS_TOKEN; si no, el checkout simulado."""
    access_token = entorno.get("MP_ACCESS_TOKEN")
    if not access_token:
        return PasarelaMercadoPagoSimulada(repo)
    base_url = entorno.get("APP_BASE_URL")
    if not base_url:
        raise ValueError(
            "Falta APP_BASE_URL: Mercado Pago la necesita para volver a la app y avisar los pagos"
        )
    return PasarelaMercadoPago(access_token, base_url)


class NotificadorMailSimulado:
    """Guarda los mails en la base (bandeja simulada) y los imprime por consola."""

    ASUNTO = "EcoHarmony Park — Confirmación de compra"

    def __init__(self, repo):
        self._repo = repo

    def enviar_confirmacion(self, email: str, mensaje: str, resultado=None) -> None:
        self._repo.guardar_mail(email, self.ASUNTO, mensaje)
        print(f"[MAIL] Para: {email} | {mensaje}")
