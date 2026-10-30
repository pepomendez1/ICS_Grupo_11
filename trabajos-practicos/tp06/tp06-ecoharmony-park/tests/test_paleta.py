"""FAQ 3: paleta obligatoria, contraste AA, fuente Lato y logo en un solo archivo."""
import os
import re
from unittest.mock import patch

import pytest

RAIZ = os.path.dirname(os.path.dirname(__file__))
PLANTILLAS = os.path.join(RAIZ, "web", "templates")
ESTATICOS = os.path.join(RAIZ, "web", "static")
PALETA = {"#386641", "#6A994E", "#A7C957", "#F2E8CF", "#BC4749"}
COLORES_VIEJOS = ["#1e3a2b", "#3d6b4f", "#8fb573", "#f6f2e8", "#8a5a3b", "#a63d2f", "#e7eedf"]


def leer(*partes):
    with open(os.path.join(*partes), encoding="utf-8") as f:
        return f.read()


def variables_css():
    raiz = re.search(r":root\s*\{(.*?)\}", leer(PLANTILLAS, "base.html"), re.S).group(1)
    return {k: v.upper() for k, v in re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", raiz)}


def contraste(a, b):
    def luminancia(color):
        r, g, b_ = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
        canal = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b_)]
        return 0.2126 * canal[0] + 0.7152 * canal[1] + 0.0722 * canal[2]
    claro, oscuro = sorted([luminancia(a), luminancia(b)], reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def test_el_css_declara_los_cinco_colores_de_la_paleta():
    assert PALETA <= set(variables_css().values())


def test_no_quedan_colores_de_la_paleta_anterior():
    for nombre in os.listdir(PLANTILLAS):
        html = leer(PLANTILLAS, nombre).lower()
        for color in COLORES_VIEJOS:
            assert color not in html, f"{color} en {nombre}"


@pytest.mark.parametrize("texto, fondo", [
    ("texto", "crema"), ("texto", "papel"),      # texto corrido
    ("suave", "crema"), ("suave", "papel"),      # textos secundarios
    ("bosque", "crema"), ("bosque", "papel"),    # títulos y links
    ("sobre-bosque", "bosque"),                  # texto de botones y header
    ("error", "papel"),                          # errores (siempre sobre fondo claro)
])
def test_contraste_aa_de_textos_y_botones(texto, fondo):
    v = variables_css()
    assert contraste(v[texto], v[fondo]) >= 4.5, f"{texto} sobre {fondo}"


def test_el_foco_se_ve_sobre_el_fondo():
    v = variables_css()
    assert contraste(v["foco"], v["crema"]) >= 3  # WCAG 1.4.11 (componentes)


def test_toda_la_app_usa_lato():
    base = leer(PLANTILLAS, "base.html")
    assert "family=Lato" in base
    assert re.search(r'body\s*\{[^}]*font-family:\s*"Lato"', base)
    for nombre in os.listdir(PLANTILLAS):
        html = leer(PLANTILLAS, nombre)
        assert "Fraunces" not in html and '"Inter"' not in html, nombre


class TestLogo:
    def test_el_logo_y_el_icono_solo_usan_los_verdes_de_la_paleta(self):
        for nombre in ("logo.svg", "logo-icono.svg"):
            svg = leer(ESTATICOS, nombre)
            colores = {c.upper() for c in re.findall(r'fill="(#[0-9a-fA-F]{6})"', svg)}
            assert colores and colores <= {"#386641", "#6A994E", "#A7C957"}, nombre
            assert "<rect" not in svg, f"{nombre} no debe tener fondo"

    def test_hay_favicon_ico_y_apple_touch_icon(self):
        with open(os.path.join(ESTATICOS, "favicon.ico"), "rb") as f:
            assert f.read(4) == b"\x00\x00\x01\x00"
        from PIL import Image
        assert Image.open(os.path.join(ESTATICOS, "apple-touch-icon.png")).size == (180, 180)

    def test_el_header_usa_logo_svg_y_el_favicon_el_icono(self, cliente):
        html = cliente.get("/").get_data(as_text=True)
        assert re.search(r'<img[^>]*src="/static/logo\.svg"', html)
        assert '<link rel="icon" href="/static/logo-icono.svg" type="image/svg+xml">' in html
        assert 'href="/static/favicon.ico"' in html
        assert 'href="/static/apple-touch-icon.png"' in html
        assert cliente.get("/static/logo.svg").status_code == 200

    def test_el_pdf_usa_lato_y_el_logo(self):
        from datetime import date
        from fpdf import FPDF
        from parque.compra import Entrada, FormaPago, ResultadoCompra, TipoPase
        from web.pdf_entradas import generar_pdf_entradas
        r = ResultadoCompra(cantidad=1, fecha_visita=date(2026, 10, 8), monto=10_000, tipo_pase=TipoPase.REGULAR,
                            forma_pago=FormaPago.EFECTIVO, entradas=[Entrada(1, 30, "cod", 10_000, 0, "General")])
        with patch.object(FPDF, "image", autospec=True, side_effect=FPDF.image) as imagen:
            pdf = generar_pdf_entradas(r, "https://x.test")
        assert b"Lato" in pdf
        rutas = [str(c.args[1]) for c in imagen.call_args_list]
        assert any(ruta.endswith(os.path.join("static", "logo.svg")) for ruta in rutas)


@pytest.fixture
def cliente():
    from web import create_app
    from web.repositorio import RepositorioMemoria
    return create_app(testing=True, repo=RepositorioMemoria()).test_client()
