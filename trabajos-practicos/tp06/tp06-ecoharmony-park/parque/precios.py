"""Precio de cada entrada (FAQ 6, 7 y 21). Las reglas están en parque/config.py."""
from dataclasses import dataclass

from parque import config


@dataclass(frozen=True)
class Tarifa:
    nombre: str       # "General", "De 4 a 15 años", ...
    precio_base: int  # el del pase
    descuento: int    # porcentaje (0, 50, 100)
    precio: int       # lo que se cobra por esa entrada


def tarifa_para(tipo_pase: str, edad: int) -> Tarifa:
    """tipo_pase es "REGULAR" o "VIP" (o el TipoPase)."""
    clave = getattr(tipo_pase, "value", tipo_pase)
    base = config.PRECIOS[clave]
    for desde, hasta, descuento, nombre in config.DESCUENTOS_POR_EDAD:
        if edad >= desde and (hasta is None or edad <= hasta):
            return Tarifa(nombre, base, descuento, base * (100 - descuento) // 100)
    return Tarifa(config.TARIFA_GENERAL, base, 0, base)


def reglas_de_precio() -> dict:
    """Las reglas tal cual, para que la pantalla calcule el desglose sin
    duplicarlas en JavaScript. El backend siempre recalcula al comprar."""
    return {
        "precios": dict(config.PRECIOS),
        "descuentos": [
            {"desde": desde, "hasta": hasta, "porcentaje": descuento, "nombre": nombre}
            for desde, hasta, descuento, nombre in config.DESCUENTOS_POR_EDAD
        ],
        "tarifa_general": config.TARIFA_GENERAL,
    }
