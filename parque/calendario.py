"""Calendario del parque (FAQ 1 y 11) y para qué fechas se venden entradas (FAQ 25 y 26)."""
import calendar as _calendar
from datetime import date, datetime
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
