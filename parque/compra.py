"""EcoHarmony Park — User story: Comprar entradas.

COMO visitante QUIERO comprar una entrada PARA asegurar mi visita al parque.

Las dependencias externas (calendario del parque, Mercado Pago, envío de mail
y fecha actual) se inyectan para poder reemplazarlas por dobles en los tests.
"""
import calendar
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Callable, Optional, Protocol

# ---------- Configuración del parque ----------
# Valores a confirmar con la PO (ver README > Supuestos): se cambian solo acá.

CANTIDAD_MAXIMA_ENTRADAS = 10

EDAD_MAXIMA = 150  # años; la edad 0 (bebés) es válida

DIA_CIERRE = calendar.MONDAY  # el parque cierra los lunes

PRECIOS = {  # por entrada, en pesos
    "REGULAR": 50_000,
    "VIP": 75_000,
}


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
class ResultadoCompra:
    cantidad: int
    fecha_visita: date
    url_pago: Optional[str] = None
    monto: int = 0
    tipo_pase: Optional["TipoPase"] = None
    forma_pago: Optional["FormaPago"] = None

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

class ServicioCompraEntradas:
    def __init__(
        self,
        calendario: CalendarioParque,
        pasarela_pago: PasarelaMercadoPago,
        notificador: Notificador,
        hoy: Callable[[], date] = date.today,
    ):
        self._calendario = calendario
        self._pasarela_pago = pasarela_pago
        self._notificador = notificador
        self._hoy = hoy

    def comprar(self, usuario: Usuario, solicitud: SolicitudCompra) -> ResultadoCompra:
        self._validar(usuario, solicitud)

        monto = solicitud.cantidad * PRECIOS[solicitud.tipo_pase.value]

        url_pago = None
        if solicitud.forma_pago == FormaPago.TARJETA:
            url_pago = self._pasarela_pago.crear_pago(
                monto, usuario.email, referencia=solicitud.referencia
            )

        resultado = ResultadoCompra(
            cantidad=solicitud.cantidad,
            fecha_visita=solicitud.fecha_visita,
            url_pago=url_pago,
            monto=monto,
            tipo_pase=solicitud.tipo_pase,
            forma_pago=solicitud.forma_pago,
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

        if s.fecha_visita is None or s.fecha_visita < self._hoy():
            raise FechaInvalidaError("La fecha de visita debe ser hoy o una fecha futura")
        if not self._calendario.esta_abierto(s.fecha_visita):
            raise ParqueCerradoError("El parque está cerrado en la fecha elegida")

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
