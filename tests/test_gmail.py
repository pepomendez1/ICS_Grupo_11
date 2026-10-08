"""Tests del envío de mail por Gmail. smtplib siempre está mockeado:
nunca se manda un mail de verdad."""
import smtplib
from datetime import date
from unittest.mock import Mock, patch

import pytest

from parque.compra import FormaPago, ResultadoCompra, ServicioCompraEntradas, TipoPase, Usuario
from tests.conftest import HOY, CalendarioFake
from web import create_app
from web.repositorio import RepositorioMemoria
from web.servicios import NotificadorGmail, NotificadorMailSimulado, crear_notificador

USUARIO_GMAIL = "ecoharmony.park@gmail.com"
APP_PASSWORD = "abcd efgh ijkl mnop"


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


def resultado(forma_pago=FormaPago.TARJETA):
    return ResultadoCompra(
        cantidad=3, fecha_visita=date(2026, 10, 8), monto=45000,
        tipo_pase=TipoPase.VIP, forma_pago=forma_pago,
    )


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
        assert [p.get_content_type() for p in mail.iter_parts()] == ["text/plain", "text/html"]

    @pytest.mark.parametrize("dato", [
        "EcoHarmony Park", "3", "08/10/2026", "VIP", "$45.000", "Tarjeta (Mercado Pago)",
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
            calendario=CalendarioFake(), pasarela_pago=Mock(), notificador=notificador, hoy=lambda: HOY,
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

    def test_la_app_manda_por_gmail_si_estan_las_variables(self, smtp, monkeypatch, registrar):
        monkeypatch.setenv("GMAIL_USER", USUARIO_GMAIL)
        monkeypatch.setenv("GMAIL_APP_PASSWORD", APP_PASSWORD)
        cliente = create_app(hoy=lambda: HOY, testing=True, repo=RepositorioMemoria()).test_client()
        email = registrar(cliente)
        cliente.post("/comprar", data={
            "fecha_visita": "2026-10-08", "cantidad": "1", "edades": ["30"],
            "tipo_pase": "REGULAR", "forma_pago": "EFECTIVO",
        })
        assert mail_enviado(smtp)["To"] == email
