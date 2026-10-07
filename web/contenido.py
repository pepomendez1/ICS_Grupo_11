"""Textos del parque que se muestran en la web y en el mail de confirmación."""

ATRACCIONES = [
    {"nombre": "Montaña rusa", "tipo": "Adrenalina",
     "descripcion": "Subidas, caídas libres y curvas cerradas a toda velocidad."},
    {"nombre": "Casa del terror", "tipo": "Adrenalina",
     "descripcion": "Un recorrido a oscuras con sustos en cada pasillo."},
    {"nombre": "Autitos chocadores", "tipo": "Para todos",
     "descripcion": "La pista clásica para chocar con amigos y familia."},
    {"nombre": "Rueda de la fortuna", "tipo": "Para todos",
     "descripcion": "La mejor vista del parque desde lo más alto."},
    {"nombre": "Hamacas", "tipo": "Para todos",
     "descripcion": "Las sillas voladoras que giran por encima del parque."},
    {"nombre": "Calesita", "tipo": "Para los más chicos",
     "descripcion": "Caballitos, música y la sortija de siempre."},
]

PASES = {
    "REGULAR": {
        "nombre": "Regular",
        "descripcion": "Acceso a las 6 atracciones haciendo la fila común.",
        "resumen": "Las 6 atracciones · fila común",
    },
    "VIP": {
        "nombre": "VIP",
        "descripcion": (
            "Todo lo del Regular, más fila rápida en todas las atracciones "
            "y vueltas ilimitadas en la montaña rusa."
        ),
        "resumen": "Fila rápida + vueltas ilimitadas en la montaña rusa",
    },
}


FORMAS_DE_PAGO = {
    "TARJETA": "Tarjeta (Mercado Pago)",
    "EFECTIVO": "Efectivo en boletería",
}


def pesos(monto: int) -> str:
    return "$" + f"{monto:,}".replace(",", ".")
