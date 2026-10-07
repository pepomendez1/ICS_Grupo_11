"""Implementaciones concretas de las dependencias externas para la app web.

Mercado Pago y el envío de mail están simulados: no hay credenciales reales.
Para pasar a producción alcanza con reemplazar estas clases por otras que usen
el SDK de Mercado Pago y un servidor SMTP, sin tocar parque/compra.py.
"""
import uuid
from datetime import date
from typing import Optional
from urllib.parse import urlsplit


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


class NotificadorMailSimulado:
    """Guarda los mails en la base (bandeja simulada) y los imprime por consola."""

    ASUNTO = "EcoHarmony Park — Confirmación de compra"

    def __init__(self, repo):
        self._repo = repo

    def enviar_confirmacion(self, email: str, mensaje: str) -> None:
        self._repo.guardar_mail(email, self.ASUNTO, mensaje)
        print(f"[MAIL] Para: {email} | {mensaje}")
