"""Calendario del parque (FAQ 1 y 11): qué días abre y en qué horario."""
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
    def hora(t):
        return f"{t.hour}:{t.minute:02d}"
    return f"de {hora(config.HORA_APERTURA)} a {hora(config.HORA_CIERRE)}"
