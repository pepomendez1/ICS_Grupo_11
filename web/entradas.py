"""Entradas individuales: URL de cada una, su QR y su estado."""
import io
from dataclasses import dataclass

import segno

from parque.compra import EstadoCompra, estado_de_compra

COLOR_QR = "#1f261f"


def url_entrada(base_url: str, codigo: str) -> str:
    """Lo que codifica el QR: la página pública de la entrada."""
    return f"{base_url.rstrip('/')}/entradas/{codigo}"


def _qr(url: str):
    return segno.make(url, error="m")


def qr_svg(url: str) -> str:
    """QR como SVG inline para las páginas (escala con CSS: usa viewBox)."""
    return _qr(url).svg_inline(
        border=2, svgclass="qr", omitsize=True, dark=COLOR_QR, light="#ffffff",
    )


def qr_png(url: str) -> bytes:
    """QR como PNG para adjuntar inline en los mails (segno, sin Pillow)."""
    salida = io.BytesIO()
    _qr(url).save(salida, kind="png", scale=6, border=2, dark=COLOR_QR, light="#ffffff")
    return salida.getvalue()


@dataclass
class EstadoEntrada:
    clave: str   # "efectivo" | "sin_cargo" | "pagada" | "pendiente" | "vencida" | "rechazada" | "cancelada"
    texto: str
    valida: bool  # si tiene QR para entrar al parque


def estado_de(compra: dict, ahora) -> EstadoEntrada:
    """El estado de las entradas de una compra (todas comparten el de la compra).
    Las reglas son del dominio (parque.compra.estado_de_compra); acá solo el texto."""
    estado = estado_de_compra(compra["existente"], ahora)
    if estado == EstadoCompra.CONFIRMADA:
        if compra["resultado"].forma_pago.value == "EFECTIVO":
            return EstadoEntrada("efectivo", "Válida · Pagar en boletería", True)
        if compra["resultado"].sin_cargo:
            return EstadoEntrada("sin_cargo", "Válida · Sin cargo", True)
        return EstadoEntrada("pagada", "Válida · Pagada con Mercado Pago", True)
    if estado == EstadoCompra.VENCIDA:
        return EstadoEntrada("vencida", "Pago vencido · Entrada no válida", False)
    if estado in (EstadoCompra.RECHAZADA, EstadoCompra.CANCELADA):
        return EstadoEntrada(estado.value, "Compra cancelada · Entrada no válida", False)
    return EstadoEntrada("pendiente", "Esperando confirmación del pago", False)
