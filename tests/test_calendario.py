"""Calendario del parque (FAQ 1 y 11). Las reglas viven en parque/config.py."""
import calendar
from datetime import date

import parque.config
from parque.calendario import CalendarioEcoHarmony

LUNES = date(2026, 10, 12)
MARTES = date(2026, 10, 13)


def test_cierra_los_lunes():
    assert parque.config.DIA_CIERRE == calendar.MONDAY
    assert CalendarioEcoHarmony().esta_abierto(LUNES) is False
    assert CalendarioEcoHarmony().esta_abierto(MARTES) is True


def test_cambiar_el_dia_de_cierre_en_la_configuracion_cambia_el_calendario(monkeypatch):
    monkeypatch.setattr(parque.config, "DIA_CIERRE", calendar.TUESDAY)
    assert CalendarioEcoHarmony().esta_abierto(MARTES) is False
    assert CalendarioEcoHarmony().esta_abierto(LUNES) is True


def test_cierra_el_25_de_diciembre_de_cualquier_anio():
    for anio in (2026, 2027, 2031, 2040):
        assert CalendarioEcoHarmony().esta_abierto(date(anio, 12, 25)) is False


def test_cierra_el_1_de_enero_de_cualquier_anio():
    for anio in (2027, 2028, 2033, 2041):
        assert CalendarioEcoHarmony().esta_abierto(date(anio, 1, 1)) is False


def test_abre_un_martes_de_otro_anio():
    assert CalendarioEcoHarmony().esta_abierto(date(2031, 3, 4)) is True  # martes


def test_el_motivo_de_cierre_explica_por_que():
    assert "lunes" in CalendarioEcoHarmony().motivo_cierre(LUNES)
    assert "feriado" in CalendarioEcoHarmony().motivo_cierre(date(2030, 12, 25)).lower()
    assert CalendarioEcoHarmony().motivo_cierre(MARTES) is None


def test_horario_de_8_30_a_19():
    assert (parque.config.HORA_APERTURA.strftime("%H:%M"), parque.config.HORA_CIERRE.strftime("%H:%M")) == ("08:30", "19:00")
