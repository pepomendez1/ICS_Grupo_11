"""El día de cierre se configura en un solo lugar (parque.compra.DIA_CIERRE)."""
import calendar
from datetime import date

import parque.compra
from web.servicios import CalendarioEcoHarmony

LUNES = date(2026, 10, 12)
MARTES = date(2026, 10, 13)


def test_cierra_los_lunes():
    assert parque.compra.DIA_CIERRE == calendar.MONDAY
    assert CalendarioEcoHarmony().esta_abierto(LUNES) is False
    assert CalendarioEcoHarmony().esta_abierto(MARTES) is True


def test_cambiar_el_dia_de_cierre_en_la_configuracion_cambia_el_calendario(monkeypatch):
    monkeypatch.setattr(parque.compra, "DIA_CIERRE", calendar.TUESDAY)
    assert CalendarioEcoHarmony().esta_abierto(MARTES) is False
    assert CalendarioEcoHarmony().esta_abierto(LUNES) is True
