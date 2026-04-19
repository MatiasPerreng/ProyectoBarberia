"""
Comprueba qué cuenta de Mercado Pago está ligada al MERCADOPAGO_ACCESS_TOKEN del .env.

Uso (desde la carpeta Backend):
  .\\venv\\Scripts\\python.exe scripts\\mp_verificar_token.py

Si el "nickname" o datos del usuario siguen siendo de otro negocio, el token no es de la app
correcta o la app sigue bajo la misma cuenta MP que "La buena vida".
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from dotenv import load_dotenv

load_dotenv(_backend / ".env", override=True)

TOKEN = (os.getenv("MERCADOPAGO_ACCESS_TOKEN") or "").strip()
MP = "https://api.mercadopago.com"


def main() -> None:
    if not TOKEN:
        print("ERROR: MERCADOPAGO_ACCESS_TOKEN vacío en Backend/.env")
        sys.exit(1)

    r = requests.get(
        f"{MP}/users/me",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=30,
    )
    print(f"HTTP {r.status_code}")
    try:
        data = r.json()
    except json.JSONDecodeError:
        print(r.text[:800])
        sys.exit(1)

    # Campos útiles para ver "quién cobra"
    uid = data.get("id")
    nick = data.get("nickname")
    email = data.get("email")
    site = data.get("site_id")
    print("--- Cuenta asociada al Access Token ---")
    print(f"  user_id:     {uid}")
    print(f"  nickname:    {nick}")
    print(f"  email:       {email}")
    print(f"  site_id:     {site}")
    print()
    print("El nombre que ves arriba en el checkout de MP suele ser el de ESTA cuenta / tu negocio en MP,")
    print("no el título del ítem ni el statement_descriptor del código.")
    print()
    if r.status_code != 200:
        print("Respuesta completa:", json.dumps(data, indent=2, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
