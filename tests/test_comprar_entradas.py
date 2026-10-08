from datetime import timedelta

import pytest

from parque.compra import (
    PRECIOS,
    CantidadInvalidaError,
    EdadesInvalidasError,
    FechaInvalidaError,
    FormaPago,
    FormaPagoInvalidaError,
    ParqueCerradoError,
    TipoPase,
    TipoPaseInvalidoError,
    Usuario,
    UsuarioNoRegistradoError,
)
from tests.conftest import DIA_CERRADO, HOY, URL_MP


class TestAcceso:
    """Se debe permitir la compra de entradas solo a usuarios registrados."""

    def test_comprar_entrada_sin_estar_logueado_falla(self, servicio, solicitud_valida):
        usuario_no_registrado = Usuario(email="anonimo@mail.com", registrado=False)
        with pytest.raises(UsuarioNoRegistradoError):
            servicio.comprar(usuario_no_registrado, solicitud_valida)

    def test_comprar_entrada_usuario_registrado_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == solicitud_valida.cantidad


class TestCantidad:
    """Debe indicar la cantidad de entradas, que no debe ser mayor a 10."""

    def test_comprar_entrada_sin_seleccionar_cantidad_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.cantidad = None
        with pytest.raises(CantidadInvalidaError):
            servicio.comprar(usuario_registrado, solicitud_valida)

    def test_comprar_cero_entradas_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.cantidad = 0
        solicitud_valida.edades = []
        with pytest.raises(CantidadInvalidaError):
            servicio.comprar(usuario_registrado, solicitud_valida)

    def test_comprar_una_entrada_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.cantidad = 1
        solicitud_valida.edades = [30]
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == 1

    def test_comprar_diez_entradas_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.cantidad = 10
        solicitud_valida.edades = [30] * 10
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == 10

    def test_comprar_once_entradas_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.cantidad = 11
        solicitud_valida.edades = [30] * 11
        with pytest.raises(CantidadInvalidaError):
            servicio.comprar(usuario_registrado, solicitud_valida)


class TestFechaVisita:
    """La fecha debe ser del día actual o futuro y el parque debe estar abierto."""

    def test_comprar_entrada_con_fecha_anterior_a_actual_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.fecha_visita = HOY - timedelta(days=1)
        with pytest.raises(FechaInvalidaError):
            servicio.comprar(usuario_registrado, solicitud_valida)

    def test_comprar_entrada_fecha_actual_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.fecha_visita = HOY
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.fecha_visita == HOY

    def test_comprar_entrada_fecha_futura_pasa(self, servicio, usuario_registrado, solicitud_valida):
        fecha_futura = HOY + timedelta(days=2)  # jueves, parque abierto
        solicitud_valida.fecha_visita = fecha_futura
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.fecha_visita == fecha_futura

    def test_comprar_entrada_fecha_parque_cerrado_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.fecha_visita = DIA_CERRADO
        with pytest.raises(ParqueCerradoError):
            servicio.comprar(usuario_registrado, solicitud_valida)


class TestDatosVisitantes:
    """Debe indicar la edad de cada visitante."""

    def test_comprar_entrada_sin_asignar_edad_todos_visitantes_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.edades = [35, None, 8]
        with pytest.raises(EdadesInvalidasError):
            servicio.comprar(usuario_registrado, solicitud_valida)

    def test_comprar_entrada_cantidad_edades_no_coincide_cantidad_entradas_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.cantidad = 3
        solicitud_valida.edades = [35, 33]
        with pytest.raises(EdadesInvalidasError):
            servicio.comprar(usuario_registrado, solicitud_valida)

    def test_comprar_entrada_con_edad_de_todos_los_visitantes_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.cantidad = 3
        solicitud_valida.edades = [35, 33, 8]
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == 3


class TestTipoPase:
    """Debe indicar el tipo de pase (VIP o regular)."""

    def test_comprar_entrada_sin_indicar_tipo_de_pase_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.tipo_pase = None
        with pytest.raises(TipoPaseInvalidoError):
            servicio.comprar(usuario_registrado, solicitud_valida)

    def test_comprar_entrada_pase_vip_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.tipo_pase = TipoPase.VIP
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == solicitud_valida.cantidad

    def test_comprar_entrada_pase_regular_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.tipo_pase = TipoPase.REGULAR
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == solicitud_valida.cantidad


class TestFormaPago:
    """Debe seleccionar forma de pago; con tarjeta redirige a Mercado Pago."""

    def test_comprar_entrada_sin_indicar_forma_de_pago_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.forma_pago = None
        with pytest.raises(FormaPagoInvalidaError):
            servicio.comprar(usuario_registrado, solicitud_valida)

    def test_comprar_entrada_con_tarjeta_redirige_mp_pasa(self, servicio, usuario_registrado, solicitud_valida, pasarela_mp):
        solicitud_valida.forma_pago = FormaPago.TARJETA
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        pasarela_mp.crear_pago.assert_called_once()
        assert resultado.url_pago == URL_MP

    def test_comprar_entrada_con_efectivo_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.forma_pago = FormaPago.EFECTIVO
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == solicitud_valida.cantidad

    def test_comprar_entrada_con_efectivo_no_redirige_mp_pasa(self, servicio, usuario_registrado, solicitud_valida, pasarela_mp):
        solicitud_valida.forma_pago = FormaPago.EFECTIVO
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        pasarela_mp.crear_pago.assert_not_called()
        assert resultado.url_pago is None


class TestConfirmacion:
    """Debe enviar mail de confirmación e informar cantidad y fecha al finalizar."""

    def test_comprar_entrada_exitosa_envia_mail_confirmacion_pasa(self, servicio, usuario_registrado, solicitud_valida, notificador):
        servicio.comprar(usuario_registrado, solicitud_valida)
        notificador.enviar_confirmacion.assert_called_once()
        email_destino, _mensaje = notificador.enviar_confirmacion.call_args.args
        assert email_destino == usuario_registrado.email

    def test_comprar_entrada_exitosa_informa_cantidad_y_fecha_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == 3
        assert resultado.fecha_visita == solicitud_valida.fecha_visita
        assert "3 entrada" in resultado.mensaje
        assert solicitud_valida.fecha_visita.strftime("%d/%m/%Y") in resultado.mensaje

    def test_comprar_entrada_fallida_no_envia_mail_falla(self, servicio, usuario_registrado, solicitud_valida, notificador):
        solicitud_valida.cantidad = 11
        solicitud_valida.edades = [30] * 11
        with pytest.raises(CantidadInvalidaError):
            servicio.comprar(usuario_registrado, solicitud_valida)
        notificador.enviar_confirmacion.assert_not_called()


class TestIntegraciones:
    """Datos que la compra le pasa a Mercado Pago y al mail de confirmación."""

    def test_comprar_entrada_con_tarjeta_envia_referencia_de_compra_a_mp_pasa(self, servicio, usuario_registrado, solicitud_valida, pasarela_mp):
        solicitud_valida.forma_pago = FormaPago.TARJETA
        solicitud_valida.referencia = "compra-123"
        servicio.comprar(usuario_registrado, solicitud_valida)
        pasarela_mp.crear_pago.assert_called_once_with(
            3 * PRECIOS["REGULAR"], usuario_registrado.email, referencia="compra-123"
        )

    def test_comprar_entrada_exitosa_envia_detalle_de_compra_al_mail_pasa(self, servicio, usuario_registrado, solicitud_valida, notificador):
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        notificador.enviar_confirmacion.assert_called_once_with(
            usuario_registrado.email, resultado.mensaje, resultado=resultado
        )
