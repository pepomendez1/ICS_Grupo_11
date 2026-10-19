"""EcoHarmony Park — User story: Comprar entradas.

COMO visitante QUIERO comprar una entrada PARA asegurar mi visita al parque.

Las dependencias externas (calendario del parque, Mercado Pago, envío de mail
y el reloj) se inyectan para poder reemplazarlas por dobles en los tests.
"""
import secrets
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Callable, Optional, Protocol

from parque import config
from parque.calendario import ahora_en_el_parque, fecha_maxima_de_compra, se_vende_para_hoy, texto_hora

from parque.config import (  # noqa: F401  (se re-exportan para la web y los tests)
    CANTIDAD_MAXIMA_ENTRADAS,
    DIA_CIERRE,
    EDAD_MAXIMA,
    PRECIOS,
)


class TipoPase(Enum):
    VIP = "VIP"
    REGULAR = "REGULAR"


class FormaPago(Enum):
    EFECTIVO = "EFECTIVO"  # se paga en boletería
    TARJETA = "TARJETA"    # se paga con Mercado Pago


# ---------- Errores ----------

class CompraError(Exception):
    """Error base de la compra de entradas."""


class UsuarioNoRegistradoError(CompraError):
    pass


class CantidadInvalidaError(CompraError):
    pass


class FechaInvalidaError(CompraError):
    pass


class ParqueCerradoError(CompraError):
    pass


class EdadesInvalidasError(CompraError):
    pass


class TipoPaseInvalidoError(CompraError):
    pass


class FormaPagoInvalidaError(CompraError):
    pass


# ---------- Modelos ----------

@dataclass
class Usuario:
    email: str
    registrado: bool


@dataclass
class SolicitudCompra:
    fecha_visita: Optional[date] = None
    cantidad: Optional[int] = None
    edades: list = field(default_factory=list)
    tipo_pase: Optional[TipoPase] = None
    forma_pago: Optional[FormaPago] = None
    referencia: Optional[str] = None  # id de la compra, viaja a Mercado Pago


@dataclass
class Entrada:
    """Una entrada individual: una por visitante, con su propio código."""
    numero: int   # 1..cantidad
    edad: int
    codigo: str   # secrets.token_urlsafe: no se puede adivinar ni enumerar


@dataclass
class ResultadoCompra:
    cantidad: int
    fecha_visita: date
    url_pago: Optional[str] = None
    monto: int = 0
    tipo_pase: Optional["TipoPase"] = None
    forma_pago: Optional["FormaPago"] = None
    entradas: list = field(default_factory=list)

    @property
    def mensaje(self) -> str:
        return (
            f"Compraste {self.cantidad} entrada(s) para el "
            f"{self.fecha_visita.strftime('%d/%m/%Y')}"
        )


# ---------- Dependencias externas ----------

class CalendarioParque(Protocol):
    def esta_abierto(self, fecha: date) -> bool: ...


class PasarelaMercadoPago(Protocol):
    def crear_pago(self, monto: int, email: str, referencia: Optional[str] = None) -> str:
        """Devuelve la URL a la que se redirige al usuario."""


class Notificador(Protocol):
    def enviar_confirmacion(
        self, email: str, mensaje: str, resultado: Optional[ResultadoCompra] = None
    ) -> None: ...


# ---------- Servicio ----------

def _como_fecha(valor) -> date:
    """La fecha de visita es un date; si llega un datetime (por ejemplo el HOY de
    los tests, que es un datetime de las 10:00), se toma su día."""
    return valor.date() if isinstance(valor, datetime) else valor


class ServicioCompraEntradas:
    def __init__(
        self,
        calendario: CalendarioParque,
        pasarela_pago: PasarelaMercadoPago,
        notificador: Notificador,
        reloj: Callable[[], datetime] = ahora_en_el_parque,
    ):
        self._calendario = calendario
        self._pasarela_pago = pasarela_pago
        self._notificador = notificador
        self._reloj = reloj

    def comprar(self, usuario: Usuario, solicitud: SolicitudCompra) -> ResultadoCompra:
        self._validar(usuario, solicitud)

        monto = solicitud.cantidad * PRECIOS[solicitud.tipo_pase.value]

        url_pago = None
        if solicitud.forma_pago == FormaPago.TARJETA:
            url_pago = self._pasarela_pago.crear_pago(
                monto, usuario.email, referencia=solicitud.referencia
            )

        entradas = [
            Entrada(numero=i, edad=edad, codigo=secrets.token_urlsafe(16))
            for i, edad in enumerate(solicitud.edades, start=1)
        ]

        resultado = ResultadoCompra(
            cantidad=solicitud.cantidad,
            fecha_visita=solicitud.fecha_visita,
            url_pago=url_pago,
            monto=monto,
            tipo_pase=solicitud.tipo_pase,
            forma_pago=solicitud.forma_pago,
            entradas=entradas,
        )
        self._notificador.enviar_confirmacion(usuario.email, resultado.mensaje, resultado=resultado)
        return resultado

    def _validar(self, usuario: Usuario, s: SolicitudCompra) -> None:
        if usuario is None or not usuario.registrado:
            raise UsuarioNoRegistradoError("Solo usuarios registrados pueden comprar entradas")

        if s.cantidad is None:
            raise CantidadInvalidaError("Debe indicar la cantidad de entradas")
        if s.cantidad < 1 or s.cantidad > CANTIDAD_MAXIMA_ENTRADAS:
            raise CantidadInvalidaError(
                f"La cantidad debe estar entre 1 y {CANTIDAD_MAXIMA_ENTRADAS}"
            )

        self._validar_fecha(s.fecha_visita)

        if len(s.edades) != s.cantidad:
            raise EdadesInvalidasError("Debe indicar la edad de cada visitante")
        if any(e is None for e in s.edades):
            raise EdadesInvalidasError("Debe indicar la edad de cada visitante")
        if any(e < 0 or e > EDAD_MAXIMA for e in s.edades):
            raise EdadesInvalidasError(
                f"La edad de cada visitante debe estar entre 0 y {EDAD_MAXIMA} años"
            )

        if not isinstance(s.tipo_pase, TipoPase):
            raise TipoPaseInvalidoError("Debe indicar el tipo de pase (VIP o regular)")

        if not isinstance(s.forma_pago, FormaPago):
            raise FormaPagoInvalidaError("Debe seleccionar la forma de pago")

    def _validar_fecha(self, fecha_visita) -> None:
        ahora = self._reloj()
        hoy = ahora.date()
        if fecha_visita is None or _como_fecha(fecha_visita) < hoy:
            raise FechaInvalidaError("La fecha de visita debe ser hoy o una fecha futura")
        fecha = _como_fecha(fecha_visita)
        maxima = fecha_maxima_de_compra(hoy)
        if fecha > maxima:  # FAQ 25
            raise FechaInvalidaError(
                f"Se pueden comprar entradas hasta el {maxima.strftime('%d/%m/%Y')} (un mes desde hoy)"
            )
        if fecha == hoy and not se_vende_para_hoy(ahora):  # FAQ 26
            raise FechaInvalidaError(
                f"Para hoy se pueden comprar entradas hasta las "
                f"{texto_hora(config.HORA_LIMITE_COMPRA_PARA_HOY)}. Elegí otra fecha."
            )
        if not self._calendario.esta_abierto(fecha):  # FAQ 1
            raise ParqueCerradoError("El parque está cerrado en la fecha elegida")
