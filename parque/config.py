"""Definiciones de la PO para la US "Comprar entradas" (FAQ oficial de la cátedra).

Toda regla configurable del negocio vive acá, en un único lugar. El resto del
código (dominio, web, mails, PDF) las lee de este módulo.
"""
import calendar
from datetime import time

# ---------- Calendario (FAQ 1 y 11) ----------

DIA_CIERRE = calendar.MONDAY            # FAQ 1: cierra todos los lunes
FERIADOS_CERRADO = {(12, 25), (1, 1)}   # FAQ 1: (mes, día), de cualquier año
HORA_APERTURA = time(8, 30)             # FAQ 11
HORA_CIERRE = time(19, 0)               # FAQ 11

# ---------- Compra ----------

CANTIDAD_MAXIMA_ENTRADAS = 10

EDAD_MAXIMA = 150  # supuesto del equipo (sin confirmar por la PO); la edad 0 es válida

PRECIOS = {  # por entrada, en pesos
    "REGULAR": 50_000,
    "VIP": 75_000,
}
