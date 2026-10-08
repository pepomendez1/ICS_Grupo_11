"""Textos del bioparque que se muestran en la web y en los mails."""
import parque.compra

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

SECTORES = [
    {"clave": "terrestre", "nombre": "Terrestre",
     "descripcion": "Senderos entre pastizales y monte nativo, con mamíferos y reptiles de la región."},
    {"clave": "acuatico", "nombre": "Acuático",
     "descripcion": "Lagunas y exhibiciones de peces, anfibios y tortugas, con miradores sobre el agua."},
    {"clave": "aereo", "nombre": "Aéreo",
     "descripcion": "Un aviario de recorrido libre para observar aves de cerca, sin rejas de por medio."},
]

HORARIOS_ALIMENTACION = [
    {"hora": "10:30", "sector": "Aéreo", "detalle": "Aves del aviario"},
    {"hora": "12:00", "sector": "Acuático", "detalle": "Peces y tortugas"},
    {"hora": "16:00", "sector": "Terrestre", "detalle": "Mamíferos del monte nativo"},
]

# Se hacen en el parque con inscripción aparte: no se venden con la entrada.
ACTIVIDADES = [
    {"nombre": "Tirolesa", "descripcion": "Recorrido en altura sobre la copa de los árboles."},
    {"nombre": "Safari", "descripcion": "Visita guiada en vehículo por el sector terrestre."},
    {"nombre": "Palestra", "descripcion": "Muro de escalada para distintas edades."},
    {"nombre": "Jardinería", "descripcion": "Taller en el vivero de plantas nativas."},
]

PASES = {
    "REGULAR": {
        "nombre": "Regular",
        "descripcion": "Acceso al parque, senderos y exhibiciones.",
        "resumen": "Parque, senderos y exhibiciones",
    },
    "VIP": {
        "nombre": "VIP",
        "descripcion": "Acceso al parque, senderos y exhibiciones, con ingreso por fila preferencial.",
        "resumen": "Lo mismo que el Regular + ingreso por fila preferencial",
    },
}

FORMAS_DE_PAGO = {
    "TARJETA": "Tarjeta (Mercado Pago)",
    "EFECTIVO": "Efectivo en boletería",
}


def pesos(monto: int) -> str:
    return "$" + f"{monto:,}".replace(",", ".")


def dia_de_cierre() -> str:
    """"lunes": sale de parque.compra.DIA_CIERRE."""
    return DIAS[parque.compra.DIA_CIERRE]


def horario() -> str:
    """"Abierto de martes a domingo": sale de parque.compra.DIA_CIERRE."""
    cierre = parque.compra.DIA_CIERRE
    return f"Abierto de {DIAS[(cierre + 1) % 7]} a {DIAS[(cierre - 1) % 7]}"
