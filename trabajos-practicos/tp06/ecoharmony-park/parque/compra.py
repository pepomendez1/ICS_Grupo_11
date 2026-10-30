"""EcoHarmony Park — User story: Comprar entradas.

COMO visitante QUIERO comprar una entrada PARA asegurar mi visita al parque.

Las dependencias externas (calendario del parque, Mercado Pago, envío de mail
y el reloj) se inyectan para poder reemplazarlas por dobles en los tests.
"""
import secrets
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Callable, Optional, Protocol

from parque import config
from parque.calendario import ahora_en_el_parque, motivo_sin_venta
from parque.precios import tarifa_para

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


class LimitePorFechaError(CantidadInvalidaError):
    """FAQ 27: el visitante superaría las 10 entradas para esa fecha."""

    def __init__(self, mensaje: str, disponibles: int, pendientes=()):
        super().__init__(mensaje)
        self.disponibles = disponibles
        self.pendientes = list(pendientes)  # ids de las compras con pago pendiente


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
    precio: int = 0       # precio final de esta entrada (FAQ 6, 7 y 21)
    descuento: int = 0    # porcentaje aplicado por la edad
    tarifa: str = ""      # "General", "De 4 a 15 años", ...


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
    def sin_cargo(self) -> bool:
        """Todas las entradas son gratis (por ejemplo, todos <= 3 años): no se paga."""
        return self.monto == 0

    @property
    def mensaje(self) -> str:
        return (
            f"Compraste {self.cantidad} entrada(s) para el "
            f"{self.fecha_visita.strftime('%d/%m/%Y')}"
        )


@dataclass
class CompraExistente:
    """Una compra anterior del visitante, tal como la guarda la base."""
    id: str
    cantidad: int
    forma_pago: FormaPago
    pagada: bool
    estado: str        # "activa" | "rechazada" | ...
    monto: int
    creado: datetime


class EstadoCompra(Enum):
    CONFIRMADA = "confirmada"  # en efectivo, sin cargo o pagada con tarjeta
    PENDIENTE = "pendiente"    # con tarjeta, todavía sin aprobar y sin vencer
    VENCIDA = "vencida"        # con tarjeta, sin aprobar después del plazo
    RECHAZADA = "rechazada"    # volvió de Mercado Pago sin pagar
    CANCELADA = "cancelada"    # la canceló el visitante


ESTADOS_QUE_CUENTAN = {EstadoCompra.CONFIRMADA, EstadoCompra.PENDIENTE}


def estado_de_compra(compra: CompraExistente, ahora: datetime) -> EstadoCompra:
    """El estado de una compra en este momento. "Pendiente" es SOLO una compra
    con tarjeta que todavía no fue aprobada: el efectivo nunca lo es. El
    vencimiento se calcula por la fecha de creación (no hace falta un cron)."""
    if compra.pagada:
        return EstadoCompra.CONFIRMADA  # si MP cobró, la compra vale
    if compra.estado == "rechazada":
        return EstadoCompra.RECHAZADA
    if compra.estado == "cancelada":
        return EstadoCompra.CANCELADA
    if compra.forma_pago == FormaPago.EFECTIVO or compra.monto == 0:
        return EstadoCompra.CONFIRMADA
    if ahora >= compra.creado + timedelta(minutes=config.VENCIMIENTO_PAGO_MINUTOS):
        return EstadoCompra.VENCIDA
    return EstadoCompra.PENDIENTE


def se_puede_cancelar(compra: CompraExistente, ahora: datetime) -> bool:
    """Solo una compra pendiente se cancela desde la app: una pagada o en
    efectivo no (y una vencida o rechazada ya no cuenta para nada)."""
    return estado_de_compra(compra, ahora) == EstadoCompra.PENDIENTE


# ---------- Dependencias externas ----------

class CalendarioParque(Protocol):
    def esta_abierto(self, fecha: date) -> bool: ...


class PasarelaMercadoPago(Protocol):
    def crear_pago(self, monto: int, email: str, referencia: Optional[str] = None) -> str:
        """Devuelve la URL a la que se redirige al usuario."""


class ComprasDelVisitante(Protocol):
    def compras_para(self, email: str, fecha: date) -> list:
        """Las compras (CompraExistente) de ese visitante para esa fecha de visita."""


class SinComprasPrevias:
    """Puerto vacío por defecto: el visitante no tiene compras anteriores."""

    def compras_para(self, email: str, fecha: date) -> list:
        return []


class Notificador(Protocol):
    def enviar_confirmacion(
        self, email: str, mensaje: str, resultado: Optional[ResultadoCompra] = None
    ) -> None: ...


# ---------- Servicio ----------

def _entradas(n: int) -> str:
    return f"{n} entrada" if n == 1 else f"{n} entradas"


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
        compras: Optional[ComprasDelVisitante] = None,
    ):
        self._calendario = calendario
        self._pasarela_pago = pasarela_pago
        self._notificador = notificador
        self._reloj = reloj
        self._compras = compras or SinComprasPrevias()

    def comprar(self, usuario: Usuario, solicitud: SolicitudCompra) -> ResultadoCompra:
        self._validar(usuario, solicitud)

        entradas = []
        for numero, edad in enumerate(solicitud.edades, start=1):
            tarifa = tarifa_para(solicitud.tipo_pase, edad)
            entradas.append(Entrada(
                numero=numero, edad=edad, codigo=secrets.token_urlsafe(16),
                precio=tarifa.precio, descuento=tarifa.descuento, tarifa=tarifa.nombre,
            ))
        monto = sum(e.precio for e in entradas)

        # Con total $0 no hay nada que cobrar: no se pasa por Mercado Pago.
        url_pago = None
        if solicitud.forma_pago == FormaPago.TARJETA and monto > 0:
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

        self._validar_limite_por_fecha(usuario.email, _como_fecha(s.fecha_visita), s.cantidad)

    def _validar_limite_por_fecha(self, email: str, fecha: date, cantidad: int) -> None:
        """FAQ 27: máximo de entradas por usuario y por fecha, sumando sus compras
        confirmadas y pendientes (las rechazadas, canceladas y vencidas no cuentan)."""
        ahora = self._reloj()
        confirmadas, pendientes = 0, []
        for compra in self._compras.compras_para(email, fecha):
            estado = estado_de_compra(compra, ahora)
            if estado == EstadoCompra.CONFIRMADA:
                confirmadas += compra.cantidad
            elif estado == EstadoCompra.PENDIENTE:
                pendientes.append(compra)
        en_pendientes = sum(c.cantidad for c in pendientes)
        ya_tiene = confirmadas + en_pendientes
        disponibles = max(CANTIDAD_MAXIMA_ENTRADAS - ya_tiene, 0)
        if cantidad <= disponibles:
            return

        dia = fecha.strftime("%d/%m")
        quedan = f"Te quedan {disponibles} disponibles para esa fecha (máximo {CANTIDAD_MAXIMA_ENTRADAS} por persona)."
        if not pendientes:
            mensaje = f"Ya tenés {_entradas(ya_tiene)} para el {dia}. {quedan}"
        else:
            cual = "la compra pendiente" if len(pendientes) == 1 else "las compras pendientes"
            mensaje = (
                f"Ya tenés {_entradas(ya_tiene)} para el {dia}: "
                f"{confirmadas} {'confirmada' if confirmadas == 1 else 'confirmadas'} y "
                f"{en_pendientes} con pago pendiente. Pagá o cancelá {cual} para liberar lugar. {quedan}"
            )
        raise LimitePorFechaError(mensaje, disponibles, [c.id for c in pendientes])

    def _validar_fecha(self, fecha_visita) -> None:
        if fecha_visita is None:
            raise FechaInvalidaError("La fecha de visita debe ser hoy o una fecha futura")
        motivo = motivo_sin_venta(_como_fecha(fecha_visita), self._reloj(), self._calendario)
        if motivo is None:
            return
        if motivo.tipo == "cerrado":
            raise ParqueCerradoError(motivo.mensaje)
        raise FechaInvalidaError(motivo.mensaje)
