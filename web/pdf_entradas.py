"""PDF con las entradas (FAQ 5), generado con fpdf2 y la fuente Lato.

Primera página: resumen con el desglose, el total y la forma de pago.
Después, una página por entrada con su QR, fecha, pase, edad, tarifa y número.
"""
import io
import os

from fpdf import FPDF

from parque.calendario import texto_horario
from web.contenido import FORMAS_DE_PAGO, PASES, pesos
from web.entradas import qr_png, url_entrada

ESTATICOS = os.path.join(os.path.dirname(__file__), "static")
FUENTES = os.path.join(ESTATICOS, "fonts")

# Paleta de la PO (FAQ 3)
VERDE_OSCURO = (0x38, 0x66, 0x41)
VERDE = (0x6A, 0x99, 0x4E)
VERDE_CLARO = (0xA7, 0xC9, 0x57)
CREMA = (0xF2, 0xE8, 0xCF)
TEXTO = (0x24, 0x33, 0x27)
SUAVE = (0x55, 0x5F, 0x52)


def nombre_del_pdf(resultado) -> str:
    return f"entradas-ecoharmony-{resultado.fecha_visita.strftime('%Y-%m-%d')}.pdf"


def _forma_de_pago(resultado) -> str:
    if resultado.sin_cargo:
        return "Sin cargo (no hay nada que pagar)"
    return FORMAS_DE_PAGO[resultado.forma_pago.value]


def _estado(resultado) -> str:
    if resultado.forma_pago.value == "EFECTIVO":
        return "Válida · Pagar en boletería"
    if resultado.sin_cargo:
        return "Válida · Sin cargo"
    return "Válida · Pagada con Mercado Pago"


def _descuento(entrada) -> str:
    if entrada.descuento == 100:
        return "Sin cargo"
    return f"{entrada.descuento}% off" if entrada.descuento else "—"


class _PdfEntradas(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.add_font("Lato", "", os.path.join(FUENTES, "Lato-Regular.ttf"))
        self.add_font("LatoLight", "", os.path.join(FUENTES, "Lato-Light.ttf"))
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(18, 18, 18)

    def encabezado(self, subtitulo: str):
        self.set_fill_color(*VERDE_OSCURO)
        self.rect(0, 0, self.w, 30, style="F")
        self.set_fill_color(*VERDE_CLARO)
        self.rect(0, 30, self.w, 1.6, style="F")
        logo = os.path.join(ESTATICOS, "logo.svg")
        x_texto = 18
        if os.path.exists(logo):
            self.image(logo, x=18, y=5, h=20)
            x_texto = 42
        self.set_xy(x_texto, 8)
        self.set_text_color(*CREMA)
        self.set_font("Lato", size=20)
        self.cell(0, 9, "EcoHarmony Park")
        self.set_xy(x_texto, 17)
        self.set_font("LatoLight", size=10)
        self.cell(0, 6, f"BIOPARQUE · {subtitulo.upper()}")
        self.set_y(40)
        self.set_text_color(*TEXTO)

    def dato(self, etiqueta: str, valor: str, ancho_etiqueta=42):
        self.set_font("LatoLight", size=11)
        self.set_text_color(*SUAVE)
        self.cell(ancho_etiqueta, 7.5, etiqueta)
        self.set_font("Lato", size=11)
        self.set_text_color(*TEXTO)
        self.cell(0, 7.5, valor, new_x="LMARGIN", new_y="NEXT")


def generar_pdf_entradas(resultado, base_url: str) -> bytes:
    """El PDF de las entradas de una compra (resultado: ResultadoCompra)."""
    pdf = _PdfEntradas()
    pdf.set_title("Entradas · EcoHarmony Park")
    pdf.set_author("EcoHarmony Park")
    fecha = resultado.fecha_visita.strftime("%d/%m/%Y")
    pase = PASES[resultado.tipo_pase.value]["nombre"]

    # ---------- Resumen ----------
    pdf.add_page()
    pdf.encabezado("Resumen de la compra")
    pdf.set_font("Lato", size=18)
    pdf.set_text_color(*VERDE_OSCURO)
    pdf.cell(0, 10, "Tus entradas", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.dato("Fecha de visita", fecha)
    pdf.dato("Tipo de pase", pase)
    pdf.dato("Entradas", str(resultado.cantidad))
    pdf.dato("Forma de pago", _forma_de_pago(resultado))
    pdf.dato("Estado", _estado(resultado))
    pdf.ln(6)

    columnas = [("Entrada", 26), ("Edad", 22), ("Tarifa", 54), ("Descuento", 34), ("Subtotal", 38)]
    pdf.set_font("Lato", size=9)
    pdf.set_fill_color(*CREMA)
    pdf.set_text_color(*VERDE_OSCURO)
    for titulo, ancho in columnas:
        pdf.cell(ancho, 8, titulo.upper(), fill=True, align="R" if titulo == "Subtotal" else "L")
    pdf.ln()
    pdf.set_text_color(*TEXTO)
    pdf.set_draw_color(*CREMA)
    for e in resultado.entradas:
        pdf.set_font("Lato", size=11)
        valores = [f"{e.numero} de {resultado.cantidad}", f"{e.edad} años", e.tarifa, _descuento(e), pesos(e.precio)]
        for (titulo, ancho), valor in zip(columnas, valores):
            pdf.cell(ancho, 8.5, valor, border="B", align="R" if titulo == "Subtotal" else "L")
        pdf.ln()
    pdf.ln(2)
    pdf.set_font("Lato", size=14)
    pdf.set_text_color(*VERDE_OSCURO)
    pdf.cell(sum(a for _, a in columnas) - 38, 10, "Total")
    pdf.cell(38, 10, pesos(resultado.monto), align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("LatoLight", size=10)
    pdf.set_text_color(*SUAVE)
    pdf.multi_cell(0, 5.5, (
        f"Cada visitante ingresa con su QR (una entrada por página). Podés mostrarlo desde el "
        f"celular o impreso. El parque abre de martes a domingo, {texto_horario()}."
    ))

    # ---------- Una página por entrada ----------
    for e in resultado.entradas:
        url = url_entrada(base_url, e.codigo)
        pdf.add_page()
        pdf.encabezado(f"Entrada {e.numero} de {resultado.cantidad}")
        pdf.set_font("Lato", size=22)
        pdf.set_text_color(*VERDE_OSCURO)
        pdf.cell(0, 12, f"Entrada {e.numero} de {resultado.cantidad}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.dato("Fecha de visita", fecha)
        pdf.dato("Tipo de pase", pase)
        pdf.dato("Visitante", f"{e.edad} {'año' if e.edad == 1 else 'años'}")
        pdf.dato("Tarifa", f"{e.tarifa} · {_descuento(e)} · {pesos(e.precio)}")
        pdf.dato("Estado", _estado(resultado))

        lado = 80
        x = (pdf.w - lado) / 2
        y = pdf.get_y() + 8
        pdf.set_draw_color(*VERDE)
        pdf.set_line_width(0.6)
        pdf.rect(x - 6, y - 6, lado + 12, lado + 12, round_corners=True, corner_radius=4)
        pdf.image(io.BytesIO(qr_png(url)), x=x, y=y, w=lado, h=lado, link=url)
        pdf.set_y(y + lado + 10)
        pdf.set_font("LatoLight", size=10)
        pdf.set_text_color(*SUAVE)
        pdf.cell(0, 6, f"Código: {e.codigo}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Lato", size=11)
        pdf.set_text_color(*VERDE_OSCURO)
        pdf.cell(0, 8, "Ver la entrada online", align="C", link=url, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
