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
from email.utils import make_msgid
from html import escape
from typing import Optional
from urllib.parse import urlsplit

import mercadopago

import parque.compra
from parque.compra import CompraError, ResultadoCompra
from web.contenido import FORMAS_DE_PAGO, PASES, horario, pesos
from web.entradas import qr_png, url_entrada

log = logging.getLogger(__name__)

ASUNTO_CONFIRMACION = "EcoHarmony Park — Confirmación de compra"
ASUNTO_ENTRADAS = "EcoHarmony Park — Tus entradas"
BASE_URL_LOCAL = "http://localhost:5001"  # si no hay APP_BASE_URL


class CalendarioEcoHarmony:
    """EcoHarmony Park cierra el día de la semana configurado en
    parque.compra.DIA_CIERRE (los lunes) y en los feriados cargados acá."""

    FERIADOS_CERRADO = {
        date(2026, 12, 25),
        date(2027, 1, 1),
    }

    def esta_abierto(self, fecha: date) -> bool:
        return fecha.weekday() != parque.compra.DIA_CIERRE and fecha not in self.FERIADOS_CERRADO


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
    """Sin credenciales de Gmail: guarda el mail en la base (se ve en "Mis mails")
    y lo imprime por consola."""

    ASUNTO = ASUNTO_CONFIRMACION

    def __init__(self, repo, base_url: str = BASE_URL_LOCAL):
        self._repo = repo
        self._base_url = base_url

    def enviar_confirmacion(self, email: str, mensaje: str, resultado=None) -> None:
        self._repo.guardar_mail(email, self.ASUNTO, mensaje)
        print(f"[MAIL] Para: {email} | {mensaje}")

    def enviar_entradas(self, email: str, resultado: ResultadoCompra) -> None:
        texto, _, _ = armar_mail_entradas(resultado, self._base_url)
        self._repo.guardar_mail(email, ASUNTO_ENTRADAS, texto)
        print(f"[MAIL] Para: {email} | {ASUNTO_ENTRADAS}")


# ---------- Contenido de los mails ----------

def _filas_detalle(resultado: ResultadoCompra) -> list[tuple[str, str]]:
    return [
        ("Entradas", str(resultado.cantidad)),
        ("Fecha de visita", resultado.fecha_visita.strftime("%d/%m/%Y")),
        ("Tipo de pase", PASES[resultado.tipo_pase.value]["nombre"]),
        ("Total", pesos(resultado.monto)),
        ("Forma de pago", FORMAS_DE_PAGO[resultado.forma_pago.value]),
    ]


def _bloque_entradas(resultado: ResultadoCompra, base_url: str, leyenda: str):
    """Texto, HTML e imágenes (cid, png) con el QR de cada entrada."""
    lineas, filas_html, imagenes = [], [], []
    for e in resultado.entradas:
        url = url_entrada(base_url, e.codigo)
        cid = make_msgid(idstring=f"entrada{e.numero}", domain="ecoharmony.park")[1:-1]
        imagenes.append((cid, qr_png(url)))
        titulo = f"Entrada {e.numero} de {resultado.cantidad} · {e.edad} años"
        lineas.append(f"{titulo}: {url}")
        filas_html.append(
            '<tr><td style="padding:12px 0;border-top:1px dashed #dcd4c0;vertical-align:middle">'
            f'<img src="cid:{cid}" width="150" height="150" alt="QR de la entrada {e.numero}" '
            'style="display:block;border:0"></td>'
            '<td style="padding:12px 0 12px 18px;border-top:1px dashed #dcd4c0;vertical-align:middle">'
            f'<strong style="color:#1e3a2b">{escape(titulo)}</strong><br>'
            f'<span style="color:#5c6657;font-size:14px">{escape(leyenda)}</span><br>'
            f'<a href="{escape(url)}" style="color:#3d6b4f;font-size:13px">Ver entrada</a></td></tr>'
        )
    html = (
        '<h2 style="margin:28px 0 4px;font-size:18px;color:#1e3a2b">Tus entradas</h2>'
        '<p style="margin:0 0 8px;color:#5c6657">Cada visitante ingresa con su QR.</p>'
        f'<table role="presentation" cellpadding="0" cellspacing="0" width="100%">{"".join(filas_html)}</table>'
    )
    return lineas, html, imagenes


def _html_mail(titulo: str, cuerpo_html: str) -> str:
    return f"""\
<!doctype html>
<html lang="es"><body style="margin:0;background:#f6f2e8;font-family:Arial,Helvetica,sans-serif;color:#1f261f">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#fffdf8;border:1px solid #dcd4c0">
    <tr><td style="background:#1e3a2b;color:#f6f2e8;padding:20px 28px;font-size:20px;font-weight:bold">EcoHarmony Park <span style="font-size:11px;letter-spacing:2px;font-weight:normal;opacity:.8">BIOPARQUE</span></td></tr>
    <tr><td style="height:4px;background:#8fb573"></td></tr>
    <tr><td style="padding:28px">
      <h1 style="margin:0 0 8px;font-size:22px;color:#1e3a2b">{escape(titulo)}</h1>
      {cuerpo_html}
      <p style="margin:24px 0 0;color:#5c6657">Te esperamos en EcoHarmony Park. {escape(horario())}.</p>
    </td></tr>
  </table>
</body></html>
"""


def armar_mail_confirmacion(mensaje: str, resultado: Optional[ResultadoCompra],
                            base_url: str = BASE_URL_LOCAL) -> tuple[str, str, list]:
    """(texto plano, HTML, imágenes inline) del mail de confirmación.

    En efectivo las entradas ya son válidas y van con su QR. Con tarjeta el
    pago todavía no está confirmado: los QR llegan después en "Tus entradas".
    """
    if resultado is None:
        return mensaje, f"<p>{escape(mensaje)}</p>", []

    filas = _filas_detalle(resultado)
    texto = ["¡Gracias por tu compra en EcoHarmony Park!", "", mensaje + ".", "",
             *(f"{nombre}: {valor}" for nombre, valor in filas), ""]
    cuerpo = (
        f'<p style="margin:0 0 20px">{escape(mensaje)}.</p>'
        '<table role="presentation" cellpadding="0" cellspacing="0">'
        + "".join(
            f'<tr><td style="padding:6px 16px 6px 0;color:#5c6657">{escape(n)}</td>'
            f'<td style="padding:6px 0;font-weight:600">{escape(v)}</td></tr>'
            for n, v in filas
        )
        + "</table>"
    )
    imagenes = []
    if resultado.forma_pago.value == "EFECTIVO":
        lineas, bloque, imagenes = _bloque_entradas(resultado, base_url, "Válida · Pagar en boletería")
        texto += ["Tus entradas · Pagar en boletería:", *lineas, ""]
        cuerpo += bloque
    else:
        aviso = ("Pago pendiente de confirmación. Cuando Mercado Pago apruebe el pago "
                 "te mandamos otro mail con tus entradas.")
        texto += [aviso, ""]
        cuerpo += (f'<p style="margin:20px 0 0;padding:12px 14px;background:#fbf0d9;'
                   f'color:#85600f;border-radius:8px">{escape(aviso)}</p>')
    texto.append(f"Te esperamos en EcoHarmony Park. {horario()}.")
    return "\n".join(texto), _html_mail("¡Gracias por tu compra!", cuerpo), imagenes


def armar_mail_entradas(resultado: ResultadoCompra, base_url: str) -> tuple[str, str, list]:
    """(texto plano, HTML, imágenes inline) del mail "Tus entradas"."""
    lineas, bloque, imagenes = _bloque_entradas(resultado, base_url, "Válida · Pagada con Mercado Pago")
    intro = (f"Se confirmó el pago de tu compra para el "
             f"{resultado.fecha_visita.strftime('%d/%m/%Y')}. Estas son tus entradas.")
    texto = "\n".join([intro, "", *lineas, "", f"Te esperamos en EcoHarmony Park. {horario()}."])
    html = _html_mail("Tus entradas", f'<p style="margin:0 0 8px">{escape(intro)}</p>{bloque}')
    return texto, html, imagenes


class NotificadorGmail:
    """Manda los mails por Gmail (SMTP con STARTTLS).

    Necesita una contraseña de aplicación de Google, no la contraseña de la
    cuenta. Si el envío falla se loguea y la compra sigue: el mail no es
    motivo para perder una venta.
    """

    SERVIDOR = "smtp.gmail.com"
    PUERTO = 587

    def __init__(self, usuario: str, app_password: str, repo, base_url: str = BASE_URL_LOCAL):
        self._usuario = usuario
        self._app_password = app_password
        self._repo = repo
        self._base_url = base_url

    def _enviar(self, que: str, para: str, asunto: str, texto: str, html: str, imagenes: list) -> bool:
        mail = EmailMessage()
        mail["Subject"] = asunto
        mail["From"] = f"EcoHarmony Park <{self._usuario}>"
        mail["To"] = para
        mail.set_content(texto)
        mail.add_alternative(html, subtype="html")
        if imagenes:
            # QR como imágenes inline referenciadas desde el HTML por Content-ID
            # (los clientes de mail suelen bloquear las data: URI).
            parte_html = mail.get_body(preferencelist=("html",))
            for numero, (cid, png) in enumerate(imagenes, start=1):
                parte_html.add_related(
                    png, maintype="image", subtype="png", cid=f"<{cid}>",
                    disposition="inline", filename=f"entrada-{numero}.png",
                )
        try:
            with smtplib.SMTP(self.SERVIDOR, self.PUERTO, timeout=10) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                smtp.login(self._usuario, self._app_password)
                smtp.send_message(mail)
        except OSError:  # incluye todos los smtplib.SMTPException
            log.exception("No se pudo enviar %s a %s", que, para)
            return False
        return True

    def enviar_confirmacion(self, email: str, mensaje: str, resultado=None) -> None:
        texto, html, imagenes = armar_mail_confirmacion(mensaje, resultado, self._base_url)
        if not self._enviar("el mail de confirmación", email, ASUNTO_CONFIRMACION, texto, html, imagenes):
            return
        # Copia en "Mis mails" para que se vea también desde la app.
        self._repo.guardar_mail(email, ASUNTO_CONFIRMACION, mensaje)

    def enviar_entradas(self, email: str, resultado: ResultadoCompra) -> None:
        texto, html, imagenes = armar_mail_entradas(resultado, self._base_url)
        if not self._enviar("el mail de entradas", email, ASUNTO_ENTRADAS, texto, html, imagenes):
            return
        self._repo.guardar_mail(email, ASUNTO_ENTRADAS, texto)


def crear_notificador(repo, entorno):
    """Gmail si están GMAIL_USER y GMAIL_APP_PASSWORD; si no, la bandeja simulada.
    APP_BASE_URL es la URL que va en los QR de los mails."""
    base_url = entorno.get("APP_BASE_URL") or BASE_URL_LOCAL
    usuario = entorno.get("GMAIL_USER")
    app_password = entorno.get("GMAIL_APP_PASSWORD")
    if usuario and app_password:
        return NotificadorGmail(usuario, app_password, repo, base_url)
    return NotificadorMailSimulado(repo, base_url)
