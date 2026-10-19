"""Calendario del parque (FAQ 1 y 11) y para qué fechas se venden entradas (FAQ 25 y 26)."""
import calendar as _calendar
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from parque import config

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def ahora_en_el_parque() -> datetime:
    """El reloj real: fecha y hora de Córdoba. Vercel corre en UTC, así que sin
    la zona horaria después de las 21 h "hoy" sería mañana."""
    return datetime.now(config.ZONA_HORARIA)


def nombre_del_dia(numero: int) -> str:
    return DIAS_SEMANA[numero]


class CalendarioEcoHarmony:
    """Cierra el día de la semana de config.DIA_CIERRE y los feriados de
    config.FERIADOS_CERRADO de cualquier año. Lee la configuración en cada
    llamada, así un cambio en config se refleja sin tocar esta clase."""

    def motivo_cierre(self, fecha: date) -> Optional[str]:
        if fecha.weekday() == config.DIA_CIERRE:
            return f"El parque cierra los {nombre_del_dia(config.DIA_CIERRE)}"
        if (fecha.month, fecha.day) in config.FERIADOS_CERRADO:
            return "Feriado: el parque está cerrado"
        return None

    def esta_abierto(self, fecha: date) -> bool:
        return self.motivo_cierre(fecha) is None


def texto_horario() -> str:
    """"de 8:30 a 19:00" (sin cero a la izquierda en la hora)."""
    return f"de {texto_hora(config.HORA_APERTURA)} a {texto_hora(config.HORA_CIERRE)}"


def sumar_meses(fecha: date, meses: int) -> date:
    """Suma meses calendario. Si el día no existe en el mes de destino (31/01 + 1
    mes), se toma el último día de ese mes (28/02 o 29/02)."""
    indice = fecha.month - 1 + meses
    anio, mes = fecha.year + indice // 12, indice % 12 + 1
    ultimo_dia = _calendar.monthrange(anio, mes)[1]
    return date(anio, mes, min(fecha.day, ultimo_dia))


def fecha_maxima_de_compra(hoy: date) -> date:
    """FAQ 25: la última fecha que se puede elegir (inclusive)."""
    return sumar_meses(hoy, config.HORIZONTE_MESES)


def se_vende_para_hoy(ahora: datetime) -> bool:
    """FAQ 26: para el mismo día se vende hasta las 17:30 inclusive (17:30:59)."""
    limite = config.HORA_LIMITE_COMPRA_PARA_HOY
    return (ahora.hour, ahora.minute) <= (limite.hour, limite.minute)


def texto_hora(t) -> str:
    return f"{t.hour}:{t.minute:02d}"


# ---------- ¿Se venden entradas para esta fecha? ----------

@dataclass
class MotivoSinVenta:
    tipo: str      # "pasado" | "horizonte" | "hora_limite" | "cerrado"
    mensaje: str   # para el error de la compra
    corto: str     # para el calendario ("no disponible: ...")


def motivo_sin_venta(fecha: date, ahora: datetime, calendario) -> Optional[MotivoSinVenta]:
    """La única fuente de verdad sobre qué días se venden: la usan la validación
    del servicio y el calendario de la web. None si se puede comprar.

    Si hay varios motivos se informa el principal: un día pasado, después que el
    parque está cerrado (FAQ 1), y recién ahí el horizonte (FAQ 25) y el
    horario de venta para hoy (FAQ 26).
    """
    hoy = ahora.date()
    if fecha < hoy:
        return MotivoSinVenta("pasado", "La fecha de visita debe ser hoy o una fecha futura", "ya pasó")
    if not calendario.esta_abierto(fecha):  # FAQ 1
        detalle = calendario.motivo_cierre(fecha) if hasattr(calendario, "motivo_cierre") else None
        corto = (detalle or "el parque está cerrado")
        return MotivoSinVenta("cerrado", "El parque está cerrado en la fecha elegida", corto[0].lower() + corto[1:])
    maxima = fecha_maxima_de_compra(hoy)
    if fecha > maxima:  # FAQ 25
        return MotivoSinVenta(
            "horizonte",
            f"Se pueden comprar entradas hasta el {maxima.strftime('%d/%m/%Y')} (un mes desde hoy)",
            f"se vende hasta el {maxima.strftime('%d/%m')}",
        )
    if fecha == hoy and not se_vende_para_hoy(ahora):  # FAQ 26
        limite = texto_hora(config.HORA_LIMITE_COMPRA_PARA_HOY)
        return MotivoSinVenta(
            "hora_limite",
            f"Para hoy se pueden comprar entradas hasta las {limite}. Elegí otra fecha.",
            f"para hoy se vende hasta las {limite}",
        )
    return None


@dataclass
class DiaDeVenta:
    fecha: date
    motivo: Optional[MotivoSinVenta]

    @property
    def disponible(self) -> bool:
        return self.motivo is None


def dias_de_venta(desde: date, hasta: date, ahora: datetime, calendario) -> list:
    """Cada día entre desde y hasta (inclusive) con su disponibilidad."""
    dias, fecha = [], desde
    while fecha <= hasta:
        dias.append(DiaDeVenta(fecha, motivo_sin_venta(fecha, ahora, calendario)))
        fecha += timedelta(days=1)
    return dias
