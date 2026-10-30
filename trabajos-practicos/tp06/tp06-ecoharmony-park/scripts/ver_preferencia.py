"""Muestra cómo quedó guardada una preferencia en Mercado Pago (GET /checkout/preferences/<id>).

    MP_ACCESS_TOKEN=... python scripts/ver_preferencia.py <pref_id>

El <pref_id> está en la URL del checkout de Mercado Pago (parámetro pref_id=...)
o en compras.url_pago. El token se lee del entorno y nunca se imprime.
"""
import json
import os
import sys
from datetime import datetime, timezone

import mercadopago

CAMPOS = ["id", "date_created", "expires", "expiration_date_from", "expiration_date_to",
          "payment_methods", "external_reference", "back_urls", "auto_return",
          "notification_url", "items", "payer", "collector_id", "operation_type"]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    token = os.environ.get("MP_ACCESS_TOKEN")
    if not token:
        sys.exit("Falta MP_ACCESS_TOKEN en el entorno.")
    respuesta = mercadopago.SDK(token).preference().get(sys.argv[1])
    if respuesta.get("status") != 200:
        sys.exit(f"Mercado Pago respondió {respuesta.get('status')}: {json.dumps(respuesta.get('response'), ensure_ascii=False)}")
    pref = respuesta["response"]
    print(json.dumps({c: pref.get(c) for c in CAMPOS}, indent=2, ensure_ascii=False))

    ahora = datetime.now(timezone.utc)
    print(f"\nAhora (UTC): {ahora.isoformat(timespec='seconds')}")
    if pref.get("expires"):
        desde = datetime.fromisoformat(pref["expiration_date_from"]) if pref.get("expiration_date_from") else None
        hasta = datetime.fromisoformat(pref["expiration_date_to"]) if pref.get("expiration_date_to") else None
        if desde and desde > ahora:
            print("⚠ Todavía no está vigente: expiration_date_from es posterior a ahora.")
        if hasta and hasta <= ahora:
            print("⚠ Está vencida: expiration_date_to ya pasó.")
        if (not desde or desde <= ahora) and (not hasta or hasta > ahora):
            print("✓ Está vigente.")
    else:
        print("La preferencia no vence (expires = false).")
    excluidos = {t.get("id") for t in (pref.get("payment_methods") or {}).get("excluded_payment_types", [])}
    if excluidos & {"credit_card", "debit_card", "prepaid_card"}:
        print(f"⚠ Excluye tarjetas: {sorted(excluidos)}")
    else:
        print(f"✓ No excluye tarjetas (excluidos: {sorted(excluidos) or 'ninguno'}).")


if __name__ == "__main__":
    main()
