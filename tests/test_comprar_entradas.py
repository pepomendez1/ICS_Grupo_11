from datetime import date, timedelta
from unittest.mock import patch

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

    # FAQ 25: se puede comprar hasta 1 mes calendario desde hoy (06/10 -> 06/11 inclusive).
    def test_comprar_entrada_fecha_a_un_mes_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.fecha_visita = date(2026, 11, 6)  # viernes
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.fecha_visita == date(2026, 11, 6)

    def test_comprar_entrada_fecha_a_un_mes_y_un_dia_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.fecha_visita = date(2026, 11, 7)  # sábado, abierto pero fuera del horizonte
        with pytest.raises(FechaInvalidaError, match="06/11/2026"):
            servicio.comprar(usuario_registrado, solicitud_valida)

    # FAQ 26: para el mismo día se puede comprar hasta las 17:30 inclusive (hora de Córdoba).
    def test_comprar_entrada_para_hoy_a_las_17_30_pasa(self, servicio_con_reloj, usuario_registrado, solicitud_valida):
        servicio = servicio_con_reloj(HOY.replace(hour=17, minute=30))
        solicitud_valida.fecha_visita = HOY.date()
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.fecha_visita == HOY.date()

    def test_comprar_entrada_para_hoy_a_las_17_31_falla(self, servicio_con_reloj, usuario_registrado, solicitud_valida):
        servicio = servicio_con_reloj(HOY.replace(hour=17, minute=31))
        solicitud_valida.fecha_visita = HOY.date()
        with pytest.raises(FechaInvalidaError, match="17:30"):
            servicio.comprar(usuario_registrado, solicitud_valida)

    def test_comprar_entrada_para_manana_a_las_18_pasa(self, servicio_con_reloj, usuario_registrado, solicitud_valida):
        servicio = servicio_con_reloj(HOY.replace(hour=18, minute=0))
        manana = HOY.date() + timedelta(days=1)  # miércoles
        solicitud_valida.fecha_visita = manana
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.fecha_visita == manana


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

    def test_comprar_entrada_edad_negativa_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.edades = [35, -1, 8]
        with pytest.raises(EdadesInvalidasError):
            servicio.comprar(usuario_registrado, solicitud_valida)

    def test_comprar_entrada_edad_cero_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.edades = [35, 33, 0]
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == 3

    def test_comprar_entrada_edad_150_pasa(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.edades = [35, 33, 150]
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert resultado.cantidad == 3

    def test_comprar_entrada_edad_151_falla(self, servicio, usuario_registrado, solicitud_valida):
        solicitud_valida.edades = [35, 33, 151]
        with pytest.raises(EdadesInvalidasError, match="entre 0 y 150"):
            servicio.comprar(usuario_registrado, solicitud_valida)


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
        # Regular, edades 35, 33 y 8: $10.000 + $10.000 + $5.000 (FAQ 6, 7 y 21).
        pasarela_mp.crear_pago.assert_called_once_with(
            25_000, usuario_registrado.email, referencia="compra-123"
        )

    def test_comprar_entrada_exitosa_envia_detalle_de_compra_al_mail_pasa(self, servicio, usuario_registrado, solicitud_valida, notificador):
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        notificador.enviar_confirmacion.assert_called_once_with(
            usuario_registrado.email, resultado.mensaje, resultado=resultado
        )


def comprar_con_edades(servicio, usuario, solicitud, edades, pase=TipoPase.REGULAR):
    solicitud.cantidad, solicitud.edades, solicitud.tipo_pase = len(edades), edades, pase
    return servicio.comprar(usuario, solicitud)


class TestPrecios:
    """FAQ 6, 7 y 21: Regular $10.000 y VIP $20.000, con descuento según la edad."""

    def test_precio_regular_adulto_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [30])
        assert resultado.monto == 10_000
        assert resultado.entradas[0].precio == 10_000

    def test_precio_vip_adulto_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [30], TipoPase.VIP)
        assert resultado.monto == 20_000

    def test_precio_edad_3_gratis_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [3, 30])
        assert resultado.entradas[0].precio == 0
        assert resultado.entradas[0].descuento == 100

    def test_precio_edad_4_mitad_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [4])
        assert resultado.entradas[0].precio == 5_000

    def test_precio_edad_15_mitad_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [15])
        assert resultado.entradas[0].precio == 5_000

    def test_precio_edad_16_completo_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [16])
        assert resultado.entradas[0].precio == 10_000

    def test_precio_edad_59_completo_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [59])
        assert resultado.entradas[0].precio == 10_000

    def test_precio_edad_60_mitad_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [60])
        assert resultado.entradas[0].precio == 5_000

    def test_total_compra_mixta_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [2, 10, 35, 70], TipoPase.VIP)
        assert [e.precio for e in resultado.entradas] == [0, 10_000, 20_000, 10_000]
        assert resultado.monto == 40_000

    def test_compra_total_cero_con_tarjeta_no_redirige_mp_pasa(self, servicio, usuario_registrado, solicitud_valida, pasarela_mp):
        solicitud_valida.forma_pago = FormaPago.TARJETA
        resultado = comprar_con_edades(servicio, usuario_registrado, solicitud_valida, [1, 3])
        assert resultado.monto == 0
        assert resultado.sin_cargo is True
        assert resultado.url_pago is None
        pasarela_mp.crear_pago.assert_not_called()


class TestEntradas:
    """Cada entrada de la compra es individual y tiene su propio código."""

    def test_comprar_tres_entradas_genera_tres_entradas_con_la_edad_de_cada_visitante_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert [e.numero for e in resultado.entradas] == [1, 2, 3]
        assert [e.edad for e in resultado.entradas] == [35, 33, 8]

    def test_comprar_entradas_cada_una_tiene_codigo_unico_pasa(self, servicio, usuario_registrado, solicitud_valida):
        resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        codigos = [e.codigo for e in resultado.entradas]
        assert len(set(codigos)) == 3

    def test_comprar_entradas_codigo_no_adivinable_pasa(self, servicio, usuario_registrado, solicitud_valida):
        with patch("parque.compra.secrets.token_urlsafe", side_effect=["c1", "c2", "c3"]) as token:
            resultado = servicio.comprar(usuario_registrado, solicitud_valida)
        assert [e.codigo for e in resultado.entradas] == ["c1", "c2", "c3"]
        token.assert_called_with(16)  # 128 bits de azar criptográfico
