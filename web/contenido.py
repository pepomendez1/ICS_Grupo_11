"""Textos del bioparque que se muestran en la web y en los mails."""
from parque import config
from parque.calendario import nombre_del_dia, texto_horario

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
    # FAQ 6: la única diferencia entre los pases es el precio.
    "REGULAR": {
        "nombre": "Regular",
        "descripcion": "Acceso al parque, senderos y exhibiciones.",
        "resumen": "Parque, senderos y exhibiciones",
    },
    "VIP": {
        "nombre": "VIP",
        "descripcion": "Acceso al parque, senderos y exhibiciones.",
        "resumen": "Parque, senderos y exhibiciones",
    },
}

FORMAS_DE_PAGO = {
    "TARJETA": "Tarjeta (Mercado Pago)",
    "EFECTIVO": "Efectivo en boletería",
}


def pesos(monto: int) -> str:
    return "$" + f"{monto:,}".replace(",", ".")


def dia_de_cierre() -> str:
    """"lunes": sale de parque.config.DIA_CIERRE."""
    return nombre_del_dia(config.DIA_CIERRE)


def horario() -> str:
    """"Abierto de martes a domingo, de 8:30 a 19:00": sale de parque.config."""
    cierre = config.DIA_CIERRE
    return (f"Abierto de {nombre_del_dia((cierre + 1) % 7)} a {nombre_del_dia((cierre - 1) % 7)}, "
            f"{texto_horario()}")


def texto_descuentos() -> str:
    """"Hasta 3 años: sin cargo; de 4 a 15 años: 50% off; 60 años o más: 50% off"."""
    partes = []
    for _desde, _hasta, descuento, nombre in config.DESCUENTOS_POR_EDAD:
        detalle = "sin cargo" if descuento == 100 else f"{descuento}% off"
        partes.append(f"{nombre}: {detalle}")
    texto = "; ".join(partes)
    return texto[0].upper() + texto[1:]
