"""Tests de integración de la app web: recorren el flujo completo por HTTP."""
import os
from datetime import date, timedelta

import pytest

from web import create_app
from web.repositorio import RepositorioMemoria, RepositorioPostgres

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

HOY = date(2026, 10, 6)  # martes
JUEVES = (HOY + timedelta(days=2)).isoformat()
LUNES = date(2026, 10, 12).isoformat()


@pytest.fixture(params=["memoria", "postgres"])
def repo(request):
    """Corre cada test web con memoria y, si hay TEST_DATABASE_URL, también con Postgres."""
    if request.param == "memoria":
        return RepositorioMemoria()
    if not TEST_DATABASE_URL:
        pytest.skip("Definí TEST_DATABASE_URL para probar contra Postgres")
    repo = RepositorioPostgres(TEST_DATABASE_URL)
    repo.crear_tablas()
    with repo._conexion() as con:
        con.execute("truncate mails, compras, pagos, usuarios")
    return repo


@pytest.fixture
def app(repo):
    return create_app(hoy=lambda: HOY, testing=True, repo=repo)


@pytest.fixture
def cliente(app):
    return app.test_client()


@pytest.fixture
def cliente_logueado(cliente):
    cliente.post("/login", data={"email": "demo@ecoharmony.com", "password": "demo123"})
    return cliente


def datos_compra(**cambios):
    datos = {
        "fecha_visita": JUEVES,
        "cantidad": "2",
        "edades": ["30", "8"],
        "tipo_pase": "REGULAR",
        "forma_pago": "EFECTIVO",
    }
    datos.update(cambios)
    return datos


class TestWeb:
    def test_web_comprar_sin_estar_logueado_redirige_a_login(self, cliente):
        respuesta = cliente.get("/comprar")
        assert respuesta.status_code == 302
        assert "/login" in respuesta.headers["Location"]

    def test_web_compra_en_efectivo_muestra_cantidad_y_fecha(self, cliente_logueado):
        respuesta = cliente_logueado.post("/comprar", data=datos_compra(), follow_redirects=True)
        html = respuesta.get_data(as_text=True)
        assert respuesta.status_code == 200
        assert "Compraste 2 entrada(s) para el 08/10/2026" in html

    def test_web_compra_con_tarjeta_redirige_a_mercado_pago(self, cliente_logueado):
        respuesta = cliente_logueado.post("/comprar", data=datos_compra(forma_pago="TARJETA"))
        assert respuesta.status_code == 302
        assert "/mercadopago/checkout/" in respuesta.headers["Location"]

    def test_web_pago_aprobado_en_mercado_pago_vuelve_a_confirmacion(self, cliente_logueado):
        redireccion = cliente_logueado.post("/comprar", data=datos_compra(forma_pago="TARJETA"))
        respuesta = cliente_logueado.post(redireccion.headers["Location"], follow_redirects=True)
        assert "(aprobado)" in respuesta.get_data(as_text=True)

    def test_web_compra_exitosa_llega_mail_a_la_bandeja(self, cliente_logueado, app):
        cliente_logueado.post("/comprar", data=datos_compra())
        mails = app.extensions["ecoharmony"]["repo"].todos_los_mails()
        assert len(mails) == 1
        assert mails[0]["para"] == "demo@ecoharmony.com"

    def test_web_compra_parque_cerrado_muestra_error(self, cliente_logueado):
        respuesta = cliente_logueado.post("/comprar", data=datos_compra(fecha_visita=LUNES))
        assert respuesta.status_code == 400
        assert "cerrado" in respuesta.get_data(as_text=True)

    def test_web_compra_once_entradas_muestra_error(self, cliente_logueado):
        respuesta = cliente_logueado.post(
            "/comprar", data=datos_compra(cantidad="11", edades=["30"] * 11)
        )
        assert respuesta.status_code == 400
        assert "entre 1 y 10" in respuesta.get_data(as_text=True)

    def test_web_registro_permite_comprar(self, cliente):
        cliente.post("/registro", data={"nombre": "Ana", "email": "ana@mail.com", "password": "secreta1"})
        respuesta = cliente.post("/comprar", data=datos_compra(), follow_redirects=True)
        assert "Compraste 2 entrada(s)" in respuesta.get_data(as_text=True)


ATRACCIONES = [
    "Calesita", "Montaña rusa", "Rueda de la fortuna",
    "Casa del terror", "Autitos chocadores", "Hamacas",
]
PALABRAS_DE_PARQUE_NATURAL = [
    "bosque", "sendero", "laguna", "kayak", "avistaje", "picnic", "mirador", "naturaleza",
]


class TestParqueDeDiversiones:
    """La web se presenta como parque de diversiones, no como parque natural."""

    def test_web_inicio_muestra_las_seis_atracciones(self, cliente):
        html = cliente.get("/").get_data(as_text=True)
        for atraccion in ATRACCIONES:
            assert atraccion in html

    def test_web_inicio_describe_los_pases(self, cliente):
        html = cliente.get("/").get_data(as_text=True)
        assert "fila común" in html
        assert "fila rápida" in html
        assert "vueltas ilimitadas en la montaña rusa" in html

    @pytest.mark.parametrize("ruta", ["/", "/comprar", "/login"])
    def test_web_no_quedan_referencias_a_parque_natural(self, cliente_logueado, ruta):
        html = cliente_logueado.get(ruta).get_data(as_text=True).lower()
        for palabra in PALABRAS_DE_PARQUE_NATURAL:
            assert palabra not in html, f"'{palabra}' aparece en {ruta}"
