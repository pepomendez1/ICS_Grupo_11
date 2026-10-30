"""Arma la grilla del calendario de compra (presentación). Qué día se vende o no
lo decide el dominio (parque.calendario.motivo_sin_venta): acá no hay reglas."""
import calendar
from datetime import date, datetime

from parque.calendario import dias_de_venta, fecha_maxima_de_compra, nombre_del_dia

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_CORTOS = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]


def fecha_larga(fecha: date) -> str:
    """"jueves 8 de octubre de 2026"."""
    return f"{nombre_del_dia(fecha.weekday())} {fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def meses_de_compra(ahora: datetime, calendario_parque) -> list:
    """Los meses que van de hoy a la fecha máxima de compra, semana por semana.
    Cada celda es un DiaDeVenta (o None si el día es de otro mes)."""
    hoy = ahora.date()
    maxima = fecha_maxima_de_compra(hoy)
    desde = hoy.replace(day=1)
    hasta = maxima.replace(day=calendar.monthrange(maxima.year, maxima.month)[1])
    dias = {d.fecha: d for d in dias_de_venta(desde, hasta, ahora, calendario_parque)}

    meses, anio, mes = [], desde.year, desde.month
    grilla = calendar.Calendar(firstweekday=calendar.MONDAY)
    while (anio, mes) <= (hasta.year, hasta.month):
        semanas = [
            [dias.get(d) if d.month == mes else None for d in semana]
            for semana in grilla.monthdatescalendar(anio, mes)
        ]
        meses.append({"titulo": f"{MESES[mes - 1]} {anio}", "semanas": semanas})
        anio, mes = (anio + 1, 1) if mes == 12 else (anio, mes + 1)
    return meses
