"""Tests del envío de mail por Gmail. smtplib siempre está mockeado:
nunca se manda un mail de verdad."""
import os
import re
import smtplib
from datetime import date
from unittest.mock import Mock, patch

import pytest

from parque.compra import Entrada, FormaPago, ResultadoCompra, ServicioCompraEntradas, TipoPase, Usuario
from tests.conftest import HOY, CalendarioFake
from tests.test_web import sin_terminos_de_parque_de_diversiones
from web import create_app
from web.repositorio import RepositorioMemoria
from web.servicios import NotificadorGmail, NotificadorMailSimulado, crear_notificador

USUARIO_GMAIL = "ecoharmony.park@gmail.com"
APP_PASSWORD = "abcd efgh ijkl mnop"
BASE_URL = "https://ecoharmony.test"
ENTRADAS = [  # VIP: 38 y 36 años a precio completo, 7 años con 50% off (FAQ 6, 7 y 21)
    Entrada(1, 38, "cod-uno", precio=20_000, descuento=0, tarifa="General"),
    Entrada(2, 36, "cod-dos", precio=20_000, descuento=0, tarifa="General"),
    Entrada(3, 7, "cod-tres", precio=10_000, descuento=50, tarifa="De 4 a 15 años"),
]


@pytest.fixture
def smtp():
    with patch("web.servicios.smtplib.SMTP") as clase_smtp:
        clase_smtp.servidor = clase_smtp.return_value.__enter__.return_value
        yield clase_smtp


@pytest.fixture
def repo():
    return Mock()


@pytest.fixture
def notificador(repo):
    return NotificadorGmail(USUARIO_GMAIL, APP_PASSWORD, repo)


@pytest.fixture
def notificador_qr(repo):
    """Notificador que conoce la URL pública de la app (la que va en los QR)."""
    return NotificadorGmail(USUARIO_GMAIL, APP_PASSWORD, repo, base_url=BASE_URL)


def resultado(forma_pago=FormaPago.TARJETA):
    return ResultadoCompra(
        cantidad=3, fecha_visita=date(2026, 10, 8), monto=sum(e.precio for e in ENTRADAS),
        tipo_pase=TipoPase.VIP, forma_pago=forma_pago, entradas=list(ENTRADAS),
    )


def imagenes(mail):
    """Los QR del mail (el logo también va inline, pero no cuenta)."""
    return [p for p in mail.walk() if p.get_content_maintype() == "image" and p.get_filename() != "logo.png"]


def enviar(notificador, r=None):
    r = r or resultado()
    notificador.enviar_confirmacion("ana@mail.com", r.mensaje, resultado=r)


def mail_enviado(smtp):
    return smtp.servidor.send_message.call_args.args[0]


def texto_y_html(mail):
    return (
        mail.get_body(preferencelist=("plain",)).get_content(),
        mail.get_body(preferencelist=("html",)).get_content(),
    )


class TestEnvio:
    def test_se_conecta_a_gmail_con_starttls_y_app_password(self, smtp, notificador):
        enviar(notificador)
        smtp.assert_called_once_with("smtp.gmail.com", 587, timeout=10)
        llamadas = [nombre for nombre, *_ in smtp.servidor.mock_calls]
        assert llamadas == ["starttls", "login", "send_message"]
        smtp.servidor.login.assert_called_once_with(USUARIO_GMAIL, APP_PASSWORD)

    def test_mail_va_al_comprador_desde_la_cuenta_del_parque(self, smtp, notificador):
        enviar(notificador)
        mail = mail_enviado(smtp)
        assert mail["To"] == "ana@mail.com"
        assert USUARIO_GMAIL in mail["From"]
        assert "EcoHarmony Park" in mail["Subject"]

    def test_mail_tiene_version_html_y_texto_plano(self, smtp, notificador):
        enviar(notificador)
        mail = mail_enviado(smtp)
        assert mail.get_content_type() == "multipart/alternative"
        # el HTML va con sus imágenes inline (el logo) en un multipart/related
        assert [p.get_content_type() for p in mail.iter_parts()] == ["text/plain", "multipart/related"]
        assert mail.get_body(preferencelist=("html",)).get_content_type() == "text/html"

    @pytest.mark.parametrize("dato", [
        "EcoHarmony Park", "3", "08/10/2026", "VIP", "$50.000", "Tarjeta (Mercado Pago)",
    ])
    def test_ambas_versiones_tienen_el_detalle_de_la_compra(self, smtp, notificador, dato):
        enviar(notificador)
        texto, html = texto_y_html(mail_enviado(smtp))
        assert dato in texto
        assert dato in html

    def test_pago_en_efectivo_indica_boleteria(self, smtp, notificador):
        enviar(notificador, resultado(FormaPago.EFECTIVO))
        texto, html = texto_y_html(mail_enviado(smtp))
        assert "Efectivo en boletería" in texto
        assert "Efectivo en boletería" in html

    def test_guarda_una_copia_en_mis_mails(self, smtp, notificador, repo):
        enviar(notificador)
        repo.guardar_mail.assert_called_once()
        assert repo.guardar_mail.call_args.args[0] == "ana@mail.com"


class TestEntradasEnElMail:
    """Los QR van como imágenes inline (Content-ID), nunca como data: URI."""

    def test_remitente_es_ecoharmony_park_con_la_cuenta_de_gmail(self, smtp, notificador_qr):
        enviar(notificador_qr)
        assert mail_enviado(smtp)["From"] == f"EcoHarmony Park <{USUARIO_GMAIL}>"

    def test_en_efectivo_el_mail_de_confirmacion_incluye_un_qr_por_entrada(self, smtp, notificador_qr):
        enviar(notificador_qr, resultado(FormaPago.EFECTIVO))
        mail = mail_enviado(smtp)
        assert len(imagenes(mail)) == 3

    def test_los_qr_van_inline_con_content_id_y_no_como_data_uri(self, smtp, notificador_qr):
        enviar(notificador_qr, resultado(FormaPago.EFECTIVO))
        mail = mail_enviado(smtp)
        _, html = texto_y_html(mail)
        assert "data:" not in html
        for imagen in imagenes(mail):
            assert imagen.get_content_type() == "image/png"
            assert imagen["Content-Disposition"].startswith("inline")
            cid = imagen["Content-ID"].strip("<>")
            assert f'src="cid:{cid}"' in html

    def test_cada_qr_codifica_la_url_de_su_entrada(self, smtp, notificador_qr):
        from web.entradas import qr_png
        enviar(notificador_qr, resultado(FormaPago.EFECTIVO))
        pngs = [i.get_content() for i in imagenes(mail_enviado(smtp))]
        assert pngs == [qr_png(f"{BASE_URL}/entradas/{e.codigo}") for e in ENTRADAS]

    def test_en_efectivo_el_texto_plano_tiene_el_link_de_cada_entrada(self, smtp, notificador_qr):
        enviar(notificador_qr, resultado(FormaPago.EFECTIVO))
        texto, _ = texto_y_html(mail_enviado(smtp))
        for e in ENTRADAS:
            assert f"{BASE_URL}/entradas/{e.codigo}" in texto
        assert "Pagar en boletería" in texto

    def test_con_tarjeta_el_mail_dice_pago_pendiente_y_no_lleva_qr(self, smtp, notificador_qr):
        enviar(notificador_qr, resultado(FormaPago.TARJETA))
        mail = mail_enviado(smtp)
        texto, html = texto_y_html(mail)
        assert "pago pendiente de confirmación" in texto.lower()
        assert "pago pendiente de confirmación" in html.lower()
        assert imagenes(mail) == []

    def test_mail_tus_entradas_lleva_un_qr_por_entrada(self, smtp, notificador_qr, repo):
        notificador_qr.enviar_entradas("ana@mail.com", resultado(FormaPago.TARJETA))
        mail = mail_enviado(smtp)
        assert mail["Subject"] == "EcoHarmony Park — Tus entradas"
        assert mail["From"] == f"EcoHarmony Park <{USUARIO_GMAIL}>"
        assert mail["To"] == "ana@mail.com"
        assert len(imagenes(mail)) == 3
        repo.guardar_mail.assert_called_once()

    def test_si_falla_el_mail_tus_entradas_se_loguea_sin_lanzar(self, smtp, notificador_qr, caplog):
        smtp.side_effect = OSError("sin red")
        notificador_qr.enviar_entradas("ana@mail.com", resultado())
        assert "No se pudo enviar el mail de entradas a ana@mail.com" in caplog.text


class TestContenidoBioparque:
    @pytest.mark.parametrize("forma_pago", [FormaPago.TARJETA, FormaPago.EFECTIVO])
    def test_mail_sin_terminos_de_parque_de_diversiones(self, smtp, notificador, forma_pago):
        enviar(notificador, resultado(forma_pago))
        texto, html = texto_y_html(mail_enviado(smtp))
        sin_terminos_de_parque_de_diversiones(texto, "el mail (texto)")
        sin_terminos_de_parque_de_diversiones(html, "el mail (HTML)")


class TestFallas:
    @pytest.mark.parametrize("error", [
        smtplib.SMTPAuthenticationError(535, b"Username and Password not accepted"),
        smtplib.SMTPServerDisconnected("se cortó"),
        OSError("sin red"),
    ])
    def test_si_gmail_falla_no_lanza_y_loguea_el_error(self, smtp, notificador, repo, caplog, error):
        smtp.servidor.send_message.side_effect = error
        enviar(notificador)  # no lanza
        assert "No se pudo enviar el mail de confirmación a ana@mail.com" in caplog.text
        repo.guardar_mail.assert_not_called()

    def test_si_gmail_falla_la_compra_se_completa_igual(self, smtp, notificador, solicitud_valida):
        smtp.side_effect = OSError("sin red")
        servicio = ServicioCompraEntradas(
            calendario=CalendarioFake(), pasarela_pago=Mock(), notificador=notificador, reloj=lambda: HOY,
        )
        r = servicio.comprar(Usuario(email="ana@mail.com", registrado=True), solicitud_valida)
        assert r.cantidad == solicitud_valida.cantidad


class TestElegirNotificador:
    """Con GMAIL_USER y GMAIL_APP_PASSWORD se usa Gmail; si falta alguna, la bandeja simulada."""

    @pytest.mark.parametrize("entorno", [
        {},
        {"GMAIL_USER": USUARIO_GMAIL},
        {"GMAIL_APP_PASSWORD": APP_PASSWORD},
    ])
    def test_sin_las_dos_variables_usa_el_simulado(self, entorno):
        assert isinstance(crear_notificador(RepositorioMemoria(), entorno), NotificadorMailSimulado)

    def test_con_las_dos_variables_usa_gmail(self):
        entorno = {"GMAIL_USER": USUARIO_GMAIL, "GMAIL_APP_PASSWORD": APP_PASSWORD}
        assert isinstance(crear_notificador(RepositorioMemoria(), entorno), NotificadorGmail)

    def test_los_qr_del_mail_usan_app_base_url(self, smtp):
        entorno = {"GMAIL_USER": USUARIO_GMAIL, "GMAIL_APP_PASSWORD": APP_PASSWORD, "APP_BASE_URL": BASE_URL}
        enviar(crear_notificador(Mock(), entorno), resultado(FormaPago.EFECTIVO))
        texto, _ = texto_y_html(mail_enviado(smtp))
        assert f"{BASE_URL}/entradas/cod-uno" in texto

    def test_la_app_manda_por_gmail_si_estan_las_variables(self, smtp, monkeypatch, registrar):
        monkeypatch.setenv("GMAIL_USER", USUARIO_GMAIL)
        monkeypatch.setenv("GMAIL_APP_PASSWORD", APP_PASSWORD)
        cliente = create_app(reloj=lambda: HOY, testing=True, repo=RepositorioMemoria()).test_client()
        email = registrar(cliente)
        cliente.post("/comprar", data={
            "fecha_visita": "2026-10-08", "cantidad": "1", "edades": ["30"],
            "tipo_pase": "REGULAR", "forma_pago": "EFECTIVO",
        })
        assert mail_enviado(smtp)["To"] == email



def adjuntos_pdf(mail):
    return [p for p in mail.iter_attachments() if p.get_content_type() == "application/pdf"]


def resultado_sin_cargo():
    return ResultadoCompra(
        cantidad=2, fecha_visita=date(2026, 10, 8), monto=0, tipo_pase=TipoPase.REGULAR,
        forma_pago=FormaPago.TARJETA,
        entradas=[Entrada(1, 1, "cod-bebe", precio=0, descuento=100, tarifa="Hasta 3 años"),
                  Entrada(2, 3, "cod-nene", precio=0, descuento=100, tarifa="Hasta 3 años")],
    )


class TestPdfDeEntradas:
    """FAQ 5: el mail con las entradas lleva un PDF adjunto (fpdf2)."""

    def test_mail_tus_entradas_lleva_un_pdf_adjunto(self, smtp, notificador_qr):
        notificador_qr.enviar_entradas("ana@mail.com", resultado(FormaPago.TARJETA))
        pdfs = adjuntos_pdf(mail_enviado(smtp))
        assert len(pdfs) == 1
        assert pdfs[0].get_filename().endswith(".pdf")
        assert pdfs[0].get_content().startswith(b"%PDF")

    def test_mail_de_confirmacion_en_efectivo_lleva_el_pdf(self, smtp, notificador_qr):
        enviar(notificador_qr, resultado(FormaPago.EFECTIVO))
        assert len(adjuntos_pdf(mail_enviado(smtp))) == 1

    def test_mail_con_tarjeta_pendiente_no_lleva_pdf(self, smtp, notificador_qr):
        enviar(notificador_qr, resultado(FormaPago.TARJETA))
        assert adjuntos_pdf(mail_enviado(smtp)) == []

    def test_compra_sin_cargo_el_mail_lleva_los_qr_y_el_pdf(self, smtp, notificador_qr):
        r = resultado_sin_cargo()
        enviar(notificador_qr, r)
        mail = mail_enviado(smtp)
        texto, html = texto_y_html(mail)
        assert len(imagenes(mail)) == 2 and len(adjuntos_pdf(mail)) == 1
        assert "pago pendiente" not in texto.lower() and "pago pendiente" not in html.lower()
        assert "Sin cargo" in texto

    def test_el_pdf_se_genera_y_contiene_el_codigo_de_cada_entrada(self):
        from web.pdf_entradas import generar_pdf_entradas
        pdf = generar_pdf_entradas(resultado(FormaPago.EFECTIVO), BASE_URL)
        assert pdf.startswith(b"%PDF")
        for e in ENTRADAS:
            assert e.codigo.encode() in pdf

    def test_el_pdf_tiene_un_resumen_y_una_pagina_por_entrada(self):
        from web.pdf_entradas import generar_pdf_entradas
        pdf = generar_pdf_entradas(resultado(FormaPago.EFECTIVO), BASE_URL)
        paginas = pdf.count(b"/Type /Page") - pdf.count(b"/Type /Pages")
        assert paginas == 1 + len(ENTRADAS)  # resumen + una página por entrada


class TestDesgloseEnElMail:
    """El cuerpo del mail incluye el desglose por visitante y el total."""

    @pytest.mark.parametrize("forma_pago", [FormaPago.TARJETA, FormaPago.EFECTIVO])
    def test_el_cuerpo_tiene_el_desglose_y_el_total(self, smtp, notificador_qr, forma_pago):
        enviar(notificador_qr, resultado(forma_pago))
        texto, html = texto_y_html(mail_enviado(smtp))
        for parte in (texto, html):
            assert "38 años" in parte and "De 4 a 15 años" in parte and "50%" in parte
            assert "$20.000" in parte and "$10.000" in parte
            assert "$50.000" in parte



class TestMarcaEnElMail:
    """FAQ 3: el mail usa Lato (con fallback) y el logo de web/static."""

    def test_el_mail_usa_lato_con_fallback(self, smtp, notificador_qr):
        enviar(notificador_qr)
        _, html = texto_y_html(mail_enviado(smtp))
        assert re.search(r"font-family:\s*Lato,[^;\"]*(Arial|Helvetica|sans-serif)", html)

    def test_el_mail_lleva_el_logo_inline(self, smtp, notificador_qr):
        enviar(notificador_qr)
        mail = mail_enviado(smtp)
        _, html = texto_y_html(mail)
        logos = [p for p in mail.walk() if (p.get_filename() or "").startswith("logo")]
        assert len(logos) == 1
        cid = logos[0]["Content-ID"].strip("<>")
        assert f'src="cid:{cid}"' in html
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "static", "logo-mail.png"), "rb") as f:
            assert logos[0].get_content() == f.read()
