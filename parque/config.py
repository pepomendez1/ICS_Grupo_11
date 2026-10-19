"""Definiciones de la PO para la US "Comprar entradas" (FAQ oficial de la cátedra).

Toda regla configurable del negocio vive acá, en un único lugar. El resto del
código (dominio, web, mails, PDF) las lee de este módulo.
"""
import calendar
from datetime import time
from zoneinfo import ZoneInfo

ZONA_HORARIA = ZoneInfo("America/Argentina/Cordoba")  # la hora del parque

# ---------- Calendario (FAQ 1 y 11) ----------

DIA_CIERRE = calendar.MONDAY            # FAQ 1: cierra todos los lunes
FERIADOS_CERRADO = {(12, 25), (1, 1)}   # FAQ 1: (mes, día), de cualquier año
HORA_APERTURA = time(8, 30)             # FAQ 11
HORA_CIERRE = time(19, 0)               # FAQ 11

# ---------- Venta de entradas (FAQ 25 y 26) ----------

HORIZONTE_MESES = 1                       # FAQ 25: hasta hoy + 1 mes calendario, inclusive
HORA_LIMITE_COMPRA_PARA_HOY = time(17, 30)  # FAQ 26: para el mismo día, hasta las 17:30 inclusive

# ---------- Compra ----------

CANTIDAD_MAXIMA_ENTRADAS = 10  # FAQ 27: por usuario y por fecha de visita, sumando sus compras

EDAD_MAXIMA = 150  # supuesto del equipo (sin confirmar por la PO); la edad 0 es válida

# ---------- Precios (FAQ 6, 7 y 21) ----------

PRECIOS = {  # por entrada, en pesos. FAQ 6: la única diferencia entre los pases es el precio
    "REGULAR": 10_000,
    "VIP": 20_000,
}

# FAQ 7 y 21: descuento por visitante según su edad. (desde, hasta, % off, nombre);
# hasta=None es "sin tope". Una edad que no entra en ninguna paga el precio completo.
DESCUENTOS_POR_EDAD = [
    (0, 3, 100, "Hasta 3 años"),
    (4, 15, 50, "De 4 a 15 años"),
    (60, None, 50, "60 años o más"),
]
TARIFA_GENERAL = "General"
