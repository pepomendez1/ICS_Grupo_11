"""Calendario del parque (FAQ 1 y 11). Las reglas viven en parque/config.py."""
import calendar
from datetime import date

import parque.config
from parque.calendario import CalendarioEcoHarmony, fecha_maxima_de_compra, sumar_meses

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


# FAQ 25: "1 mes calendario" (definición del equipo para fin de mes: si el día
# no existe en el mes siguiente, se toma el último día de ese mes).

def test_un_mes_desde_el_19_10_es_el_19_11():
    assert sumar_meses(date(2026, 10, 19), 1) == date(2026, 11, 19)


def test_un_mes_desde_el_31_01_es_el_ultimo_dia_de_febrero():
    assert sumar_meses(date(2027, 1, 31), 1) == date(2027, 2, 28)
    assert sumar_meses(date(2028, 1, 31), 1) == date(2028, 2, 29)  # bisiesto


def test_un_mes_desde_el_31_03_es_el_30_04():
    assert sumar_meses(date(2027, 3, 31), 1) == date(2027, 4, 30)


def test_un_mes_desde_diciembre_pasa_al_anio_siguiente():
    assert sumar_meses(date(2026, 12, 15), 1) == date(2027, 1, 15)


def test_fecha_maxima_de_compra_es_hoy_mas_un_mes():
    assert fecha_maxima_de_compra(date(2026, 10, 19)) == date(2026, 11, 19)
