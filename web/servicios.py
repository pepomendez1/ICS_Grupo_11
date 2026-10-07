"""Implementaciones concretas de las dependencias externas para la app web.

Mercado Pago y el mail tienen una versión real y una simulada con la misma
interfaz; cuál se usa depende de las variables de entorno. parque/compra.py
no se entera.
"""
import logging
import smtplib
import ssl
import uuid
from dataclasses import dataclass
from datetime import date
from email.message import EmailMessage
from html import escape
from typing import Optional
from urllib.parse import urlsplit

import mercadopago

from parque.compra import CompraError, ResultadoCompra
from web.contenido import FORMAS_DE_PAGO, PASES, pesos

log = logging.getLogger(__name__)

ASUNTO_CONFIRMACION = "EcoHarmony Park — Confirmación de compra"


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

    ASUNTO = ASUNTO_CONFIRMACION

    def __init__(self, repo):
        self._repo = repo

    def enviar_confirmacion(self, email: str, mensaje: str, resultado=None) -> None:
        self._repo.guardar_mail(email, self.ASUNTO, mensaje)
        print(f"[MAIL] Para: {email} | {mensaje}")



def armar_mail_confirmacion(mensaje: str, resultado: Optional[ResultadoCompra]) -> tuple[str, str]:
    """Devuelve (texto plano, HTML) del mail de confirmación."""
    if resultado is None:
        return mensaje, f"<p>{escape(mensaje)}</p>"

    filas = [
        ("Entradas", str(resultado.cantidad)),
        ("Fecha de visita", resultado.fecha_visita.strftime("%d/%m/%Y")),
        ("Tipo de pase", PASES[resultado.tipo_pase.value]["nombre"]),
        ("Total", pesos(resultado.monto)),
        ("Forma de pago", FORMAS_DE_PAGO[resultado.forma_pago.value]),
    ]
    cierre = "Te esperamos en EcoHarmony Park. Abrimos de martes a domingo."

    texto = "\n".join([
        "¡Gracias por tu compra en EcoHarmony Park!",
        "",
        mensaje + ".",
        "",
        *(f"{nombre}: {valor}" for nombre, valor in filas),
        "",
        cierre,
    ])

    filas_html = "".join(
        f'<tr><td style="padding:6px 16px 6px 0;color:#5f6478">{escape(nombre)}</td>'
        f'<td style="padding:6px 0;font-weight:600">{escape(valor)}</td></tr>'
        for nombre, valor in filas
    )
    html = f"""\
<!doctype html>
<html lang="es"><body style="margin:0;background:#fbf6ee;font-family:Arial,Helvetica,sans-serif;color:#1d2233">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#fffdf9;border:1px solid #e6ddcd">
    <tr><td style="background:#1c2541;color:#fbf6ee;padding:20px 28px;font-size:20px;font-weight:bold">EcoHarmony Park</td></tr>
    <tr><td style="height:6px;background:#e4572e"></td></tr>
    <tr><td style="padding:28px">
      <h1 style="margin:0 0 8px;font-size:22px;color:#1c2541">¡Gracias por tu compra!</h1>
      <p style="margin:0 0 20px">{escape(mensaje)}.</p>
      <table role="presentation" cellpadding="0" cellspacing="0">{filas_html}</table>
      <p style="margin:24px 0 0;color:#5f6478">{escape(cierre)}</p>
    </td></tr>
  </table>
</body></html>
"""
    return texto, html


class NotificadorGmail:
    """Manda el mail de confirmación por Gmail (SMTP con STARTTLS).

    Necesita una contraseña de aplicación de Google, no la contraseña de la
    cuenta. Si el envío falla se loguea y la compra sigue: el mail no es
    motivo para perder una venta.
    """

    SERVIDOR = "smtp.gmail.com"
    PUERTO = 587

    def __init__(self, usuario: str, app_password: str, repo):
        self._usuario = usuario
        self._app_password = app_password
        self._repo = repo

    def enviar_confirmacion(self, email: str, mensaje: str, resultado=None) -> None:
        texto, html = armar_mail_confirmacion(mensaje, resultado)
        mail = EmailMessage()
        mail["Subject"] = ASUNTO_CONFIRMACION
        mail["From"] = f"EcoHarmony Park <{self._usuario}>"
        mail["To"] = email
        mail.set_content(texto)
        mail.add_alternative(html, subtype="html")

        try:
            with smtplib.SMTP(self.SERVIDOR, self.PUERTO, timeout=10) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                smtp.login(self._usuario, self._app_password)
                smtp.send_message(mail)
        except OSError:  # incluye todos los smtplib.SMTPException
            log.exception("No se pudo enviar el mail de confirmación a %s", email)
            return

        # Copia en "Mis mails" para que se vea también desde la app.
        self._repo.guardar_mail(email, ASUNTO_CONFIRMACION, mensaje)


def crear_notificador(repo, entorno):
    """Gmail si están GMAIL_USER y GMAIL_APP_PASSWORD; si no, la bandeja simulada."""
    usuario = entorno.get("GMAIL_USER")
    app_password = entorno.get("GMAIL_APP_PASSWORD")
    if usuario and app_password:
        return NotificadorGmail(usuario, app_password, repo)
    return NotificadorMailSimulado(repo)
