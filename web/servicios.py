"""Implementaciones concretas de las dependencias externas para la app web.

Mercado Pago y el mail tienen una versión real y una simulada con la misma
interfaz; cuál se usa depende de las variables de entorno. parque/compra.py
no se entera.
"""
import logging
import os
import smtplib
import ssl
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from email.message import EmailMessage
from email.utils import make_msgid
from html import escape
from typing import Optional
from urllib.parse import urlsplit

import mercadopago

from parque import config
from parque.calendario import CalendarioEcoHarmony, ahora_en_el_parque  # noqa: F401  (el calendario vive en el dominio)
from parque.compra import CompraError, ResultadoCompra
from web.contenido import FORMAS_DE_PAGO, PASES, horario, pesos
from web.entradas import qr_png, url_entrada
from web.pdf_entradas import generar_pdf_entradas, nombre_del_pdf

log = logging.getLogger(__name__)

ASUNTO_CONFIRMACION = "EcoHarmony Park — Confirmación de compra"
ASUNTO_ENTRADAS = "EcoHarmony Park — Tus entradas"
BASE_URL_LOCAL = "http://localhost:5001"  # si no hay APP_BASE_URL


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

    def __init__(self, access_token: str, base_url: str, reloj=ahora_en_el_parque):
        self._sdk = mercadopago.SDK(access_token)
        self._base_url = base_url.rstrip("/")
        self._sandbox = access_token.startswith("TEST-")
        self._reloj = reloj

    def crear_pago(self, monto: int, email: str, referencia: Optional[str] = None) -> str:
        vuelta = f"{self._base_url}/compras/{referencia}?mp="
        # Vence junto con la compra pendiente (config.VENCIMIENTO_PAGO_MINUTOS):
        # pasado ese plazo la compra deja de contar para el límite de 10.
        desde = self._reloj()
        hasta = desde + timedelta(minutes=config.VENCIMIENTO_PAGO_MINUTOS)
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
            # Solo tarjetas: sin efectivo (Rapipago, Pago Fácil) ni cajero, que
            # se acreditan después de que la compra ya venció.
            "payment_methods": {"excluded_payment_types": [{"id": "ticket"}, {"id": "atm"}]},
            "expires": True,
            "expiration_date_from": desde.isoformat(timespec="milliseconds"),
            "expiration_date_to": hasta.isoformat(timespec="milliseconds"),
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


def crear_pasarela(repo, entorno, reloj=ahora_en_el_parque):
    """Mercado Pago real si está MP_ACCESS_TOKEN; si no, el checkout simulado."""
    access_token = entorno.get("MP_ACCESS_TOKEN")
    if not access_token:
        return PasarelaMercadoPagoSimulada(repo)
    base_url = entorno.get("APP_BASE_URL")
    if not base_url:
        raise ValueError(
            "Falta APP_BASE_URL: Mercado Pago la necesita para volver a la app y avisar los pagos"
        )
    return PasarelaMercadoPago(access_token, base_url, reloj)


class NotificadorMailSimulado:
    """Sin credenciales de Gmail: guarda el mail en la base (se ve en "Mis mails",
    con el PDF adjunto para descargar) y lo imprime por consola."""

    ASUNTO = ASUNTO_CONFIRMACION

    def __init__(self, repo, base_url: str = BASE_URL_LOCAL):
        self._repo = repo
        self._base_url = base_url

    def _guardar(self, email, asunto, texto, resultado, con_pdf):
        if con_pdf:
            self._repo.guardar_mail(email, asunto, texto, adjunto=generar_pdf_entradas(resultado, self._base_url),
                                    adjunto_nombre=nombre_del_pdf(resultado))
        else:
            self._repo.guardar_mail(email, asunto, texto)
        print(f"[MAIL] Para: {email} | {asunto}")

    def enviar_confirmacion(self, email: str, mensaje: str, resultado=None) -> None:
        texto, _, _ = armar_mail_confirmacion(mensaje, resultado, self._base_url)
        self._guardar(email, self.ASUNTO, texto, resultado, entradas_validas(resultado))

    def enviar_entradas(self, email: str, resultado: ResultadoCompra) -> None:
        texto, _, _ = armar_mail_entradas(resultado, self._base_url)
        self._guardar(email, ASUNTO_ENTRADAS, texto, resultado, True)


# ---------- Contenido de los mails ----------

# Colores del mail (paleta de la PO, FAQ 3). Los clientes de mail no leen CSS
# externo, así que van inline.
COLOR_FONDO = "#F2E8CF"
COLOR_PAPEL = "#FFFDF6"
COLOR_OSCURO = "#386641"
COLOR_ACENTO = "#A7C957"
COLOR_TEXTO = "#243327"
COLOR_SUAVE = "#555F52"
COLOR_LINEA = "#E2D7BA"
FUENTE = "Lato, 'Helvetica Neue', Arial, Helvetica, sans-serif"

# Logo del mail: PNG generado desde web/static/logo.svg (scripts/generar_iconos.py),
# porque Gmail y Outlook no muestran SVG. Va inline, referenciado por Content-ID.
LOGO_MAIL = os.path.join(os.path.dirname(__file__), "static", "logo-mail.png")
CID_LOGO = "logo@ecoharmony.park"


def entradas_validas(resultado: Optional[ResultadoCompra]) -> bool:
    """Las entradas ya sirven para entrar: efectivo (se paga en boletería) o total $0."""
    return resultado is not None and (resultado.forma_pago.value == "EFECTIVO" or resultado.sin_cargo)


def _forma_de_pago(resultado: ResultadoCompra) -> str:
    return "Sin cargo (no hay nada que pagar)" if resultado.sin_cargo else FORMAS_DE_PAGO[resultado.forma_pago.value]


def _filas_detalle(resultado: ResultadoCompra) -> list[tuple[str, str]]:
    return [
        ("Entradas", str(resultado.cantidad)),
        ("Fecha de visita", resultado.fecha_visita.strftime("%d/%m/%Y")),
        ("Tipo de pase", PASES[resultado.tipo_pase.value]["nombre"]),
        ("Total", pesos(resultado.monto)),
        ("Forma de pago", _forma_de_pago(resultado)),
    ]


def _descuento(e) -> str:
    if e.descuento == 100:
        return "sin cargo"
    return f"{e.descuento}% off" if e.descuento else "precio completo"


def _desglose(resultado: ResultadoCompra) -> tuple[list[str], str]:
    """El desglose por visitante y el total, en texto y en HTML."""
    lineas = ["Detalle del precio:"]
    filas = []
    for e in resultado.entradas:
        lineas.append(f"  Entrada {e.numero} · {e.edad} años · {e.tarifa} ({_descuento(e)}): {pesos(e.precio)}")
        filas.append(
            f'<tr><td style="padding:7px 8px 7px 0;border-bottom:1px solid {COLOR_LINEA}">Entrada {e.numero} · {e.edad} años</td>'
            f'<td style="padding:7px 8px;border-bottom:1px solid {COLOR_LINEA}">{escape(e.tarifa)}</td>'
            f'<td style="padding:7px 8px;border-bottom:1px solid {COLOR_LINEA};color:{COLOR_SUAVE}">{escape(_descuento(e))}</td>'
            f'<td style="padding:7px 0;border-bottom:1px solid {COLOR_LINEA};text-align:right">{pesos(e.precio)}</td></tr>'
        )
    lineas.append(f"  Total: {pesos(resultado.monto)}")
    html = (
        f'<h2 style="margin:24px 0 6px;font-size:17px;color:{COLOR_OSCURO}">Detalle del precio</h2>'
        f'<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="font-size:14px">{"".join(filas)}'
        f'<tr><td colspan="3" style="padding:10px 0 0;font-weight:bold">Total</td>'
        f'<td style="padding:10px 0 0;text-align:right;font-weight:bold;font-size:16px">{pesos(resultado.monto)}</td></tr></table>'
    )
    return lineas, html


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
            f'<tr><td style="padding:12px 0;border-top:1px dashed {COLOR_LINEA};vertical-align:middle">'
            f'<img src="cid:{cid}" width="150" height="150" alt="QR de la entrada {e.numero}" '
            'style="display:block;border:0"></td>'
            f'<td style="padding:12px 0 12px 18px;border-top:1px dashed {COLOR_LINEA};vertical-align:middle">'
            f'<strong style="color:{COLOR_OSCURO}">{escape(titulo)}</strong><br>'
            f'<span style="color:{COLOR_SUAVE};font-size:14px">{escape(leyenda)}</span><br>'
            f'<a href="{escape(url)}" style="color:{COLOR_OSCURO};font-size:13px">Ver entrada</a></td></tr>'
        )
    html = (
        f'<h2 style="margin:28px 0 4px;font-size:18px;color:{COLOR_OSCURO}">Tus entradas</h2>'
        f'<p style="margin:0 0 8px;color:{COLOR_SUAVE}">Cada visitante ingresa con su QR. '
        'También van en el PDF adjunto, una por página.</p>'
        f'<table role="presentation" cellpadding="0" cellspacing="0" width="100%">{"".join(filas_html)}</table>'
    )
    return lineas, html, imagenes


def _html_mail(titulo: str, cuerpo_html: str) -> str:
    return f"""\
<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">
</head><body style="margin:0;background:{COLOR_FONDO};font-family:{FUENTE};color:{COLOR_TEXTO}">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:{COLOR_PAPEL};border:1px solid {COLOR_LINEA};font-family:{FUENTE}">
    <tr><td style="padding:16px 28px;color:{COLOR_OSCURO}">
      <table role="presentation" cellpadding="0" cellspacing="0"><tr>
        <td style="padding-right:12px"><img src="cid:{CID_LOGO}" width="56" height="56" alt="" style="display:block;border:0"></td>
        <td style="font-family:{FUENTE};font-size:21px;font-weight:900;color:{COLOR_OSCURO}">EcoHarmony Park<br>
          <span style="font-size:11px;letter-spacing:2px;font-weight:bold;color:{COLOR_SUAVE}">BIOPARQUE</span></td>
      </tr></table>
    </td></tr>
    <tr><td style="height:4px;background:{COLOR_ACENTO}"></td></tr>
    <tr><td style="padding:28px">
      <h1 style="margin:0 0 8px;font-size:22px;color:{COLOR_OSCURO}">{escape(titulo)}</h1>
      {cuerpo_html}
      <p style="margin:24px 0 0;color:{COLOR_SUAVE}">Te esperamos en EcoHarmony Park. {escape(horario())}.</p>
    </td></tr>
  </table>
</body></html>
"""


def armar_mail_confirmacion(mensaje: str, resultado: Optional[ResultadoCompra],
                            base_url: str = BASE_URL_LOCAL) -> tuple[str, str, list]:
    """(texto plano, HTML, imágenes inline) del mail de confirmación.

    En efectivo o con total $0 las entradas ya son válidas y van con su QR. Con
    tarjeta el pago todavía no está confirmado: los QR llegan después en "Tus entradas".
    """
    if resultado is None:
        return mensaje, f"<p>{escape(mensaje)}</p>", []

    filas = _filas_detalle(resultado)
    lineas_desglose, html_desglose = _desglose(resultado)
    texto = ["¡Gracias por tu compra en EcoHarmony Park!", "", mensaje + ".", "",
             *(f"{nombre}: {valor}" for nombre, valor in filas), "", *lineas_desglose, ""]
    cuerpo = (
        f'<p style="margin:0 0 20px">{escape(mensaje)}.</p>'
        '<table role="presentation" cellpadding="0" cellspacing="0">'
        + "".join(
            f'<tr><td style="padding:6px 16px 6px 0;color:{COLOR_SUAVE}">{escape(n)}</td>'
            f'<td style="padding:6px 0;font-weight:bold">{escape(v)}</td></tr>'
            for n, v in filas
        )
        + "</table>" + html_desglose
    )
    imagenes = []
    if entradas_validas(resultado):
        leyenda = "Válida · Sin cargo" if resultado.sin_cargo else "Válida · Pagar en boletería"
        lineas, bloque, imagenes = _bloque_entradas(resultado, base_url, leyenda)
        texto += [f"Tus entradas · {leyenda} (también en el PDF adjunto):", *lineas, ""]
        cuerpo += bloque
    else:
        aviso = ("Pago pendiente de confirmación. Cuando Mercado Pago apruebe el pago "
                 "te mandamos otro mail con tus entradas.")
        texto += [aviso, ""]
        cuerpo += (f'<p style="margin:20px 0 0;padding:12px 14px;background:{COLOR_FONDO};'
                   f'color:{COLOR_TEXTO};border-left:4px solid {COLOR_ACENTO}">{escape(aviso)}</p>')
    texto.append(f"Te esperamos en EcoHarmony Park. {horario()}.")
    return "\n".join(texto), _html_mail("¡Gracias por tu compra!", cuerpo), imagenes


def armar_mail_entradas(resultado: ResultadoCompra, base_url: str) -> tuple[str, str, list]:
    """(texto plano, HTML, imágenes inline) del mail "Tus entradas"."""
    lineas, bloque, imagenes = _bloque_entradas(resultado, base_url, "Válida · Pagada con Mercado Pago")
    lineas_desglose, html_desglose = _desglose(resultado)
    intro = (f"Se confirmó el pago de tu compra para el "
             f"{resultado.fecha_visita.strftime('%d/%m/%Y')}. Estas son tus entradas "
             f"(también van en el PDF adjunto).")
    texto = "\n".join([intro, "", *lineas_desglose, "", *lineas, "",
                       f"Te esperamos en EcoHarmony Park. {horario()}."])
    html = _html_mail("Tus entradas", f'<p style="margin:0 0 8px">{escape(intro)}</p>{html_desglose}{bloque}')
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

    def _enviar(self, que: str, para: str, asunto: str, texto: str, html: str, imagenes: list,
                adjunto=None) -> bool:
        mail = EmailMessage()
        mail["Subject"] = asunto
        mail["From"] = f"EcoHarmony Park <{self._usuario}>"
        mail["To"] = para
        mail.set_content(texto)
        mail.add_alternative(html, subtype="html")
        # Logo y QR como imágenes inline referenciadas desde el HTML por Content-ID
        # (los clientes de mail suelen bloquear las data: URI).
        parte_html = mail.get_body(preferencelist=("html",))
        with open(LOGO_MAIL, "rb") as f:
            parte_html.add_related(f.read(), maintype="image", subtype="png", cid=f"<{CID_LOGO}>",
                                   disposition="inline", filename="logo.png")
        if imagenes:
            for numero, (cid, png) in enumerate(imagenes, start=1):
                parte_html.add_related(
                    png, maintype="image", subtype="png", cid=f"<{cid}>",
                    disposition="inline", filename=f"entrada-{numero}.png",
                )
        if adjunto:  # (nombre, bytes) del PDF con las entradas (FAQ 5)
            nombre, contenido = adjunto
            mail.add_attachment(contenido, maintype="application", subtype="pdf", filename=nombre)
        try:
            with smtplib.SMTP(self.SERVIDOR, self.PUERTO, timeout=10) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                smtp.login(self._usuario, self._app_password)
                smtp.send_message(mail)
        except OSError:  # incluye todos los smtplib.SMTPException
            log.exception("No se pudo enviar %s a %s", que, para)
            return False
        return True

    def _pdf(self, resultado):
        return nombre_del_pdf(resultado), generar_pdf_entradas(resultado, self._base_url)

    def enviar_confirmacion(self, email: str, mensaje: str, resultado=None) -> None:
        texto, html, imagenes = armar_mail_confirmacion(mensaje, resultado, self._base_url)
        adjunto = self._pdf(resultado) if entradas_validas(resultado) else None
        if not self._enviar("el mail de confirmación", email, ASUNTO_CONFIRMACION, texto, html, imagenes, adjunto):
            return
        # Copia en "Mis mails" para que se vea también desde la app.
        self._repo.guardar_mail(email, ASUNTO_CONFIRMACION, mensaje)

    def enviar_entradas(self, email: str, resultado: ResultadoCompra) -> None:
        texto, html, imagenes = armar_mail_entradas(resultado, self._base_url)
        if not self._enviar("el mail de entradas", email, ASUNTO_ENTRADAS, texto, html, imagenes,
                            self._pdf(resultado)):
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
