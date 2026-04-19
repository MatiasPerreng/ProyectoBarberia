"""
Ayuda a ubicar de dónde puede salir el nombre del comercio en el checkout (ej. "La buena vida").

1) Ejecutá (desde la carpeta Backend):
   .\\venv\\Scripts\\python.exe scripts\\mp_auditar_nombre_checkout.py

2) Revisá la salida: busca "COINCIDENCIA" (texto que contiene buena/vida/labuen).

3) En Mercado Pago (panel web), el nombre grande del checkout suele venir de:
   - Tu cuenta vendedor / datos del negocio (nombre comercial), no del título del ítem.
   - El nombre de la "aplicación" en developers.mercadopago.com (Tu integración → tu app).
   - Si la app nueva comparte la MISMA cuenta MP que otro negocio, puede reutilizar el mismo nombre público.

4) En tu código:
   - ProyectoBarberia NO define "La buena vida" en el flujo MP (solo King Barber en el ítem).
   - ProyectoBurgers sí usa "La Buena Vida" en la web y un link default link.mercadopago.com.uy/labuenvida
     en mercadopago_api.py — eso NO afecta al backend de la barbería si usás otro .env.

Uso: mismo MERCADOPAGO_ACCESS_TOKEN que Backend/.env
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import requests

_backend = Path(__file__).resolve().parent.parent
load_dotenv = __import__("dotenv", fromlist=["load_dotenv"]).load_dotenv
load_dotenv(_backend / ".env", override=True)

TOKEN = (os.getenv("MERCADOPAGO_ACCESS_TOKEN") or "").strip()
PUB = (os.getenv("MERCADOPAGO_PUBLIC_KEY") or "").strip()
MP = "https://api.mercadopago.com"

PAT = re.compile(r"buena|labuen|vida", re.I)


def _walk_strings(obj, path=""):
    """Yield (path, value) for string leaves."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            yield from _walk_strings(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def main() -> None:
    if not TOKEN:
        print("ERROR: MERCADOPAGO_ACCESS_TOKEN vacío en Backend/.env")
        sys.exit(1)

    print("=== Public key (primeros 40 chars) ===")
    print((PUB[:40] + "...") if len(PUB) > 40 else PUB or "(no definido en .env)")
    print()

    r = requests.get(
        f"{MP}/users/me",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=30,
    )
    print(f"GET /users/me -> HTTP {r.status_code}")
    try:
        data = r.json()
    except json.JSONDecodeError:
        print(r.text[:1200])
        sys.exit(1)

    print()
    print("=== Respuesta completa users/me (revisá nickname, company, etc.) ===")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:12000])
    if len(json.dumps(data)) > 12000:
        print("\n… (respuesta truncada para consola; si hace falta, guardá a un archivo)")
    print()

    print("=== Campos cuyo texto coincide con buena / labuen / vida ===")
    found = False
    for path, s in _walk_strings(data):
        if PAT.search(s):
            print(f"  COINCIDENCIA {path}: {s[:500]}")
            found = True
    if not found:
        print("  (ninguno en users/me — el nombre del checkout puede venir solo del panel / otra API)")
    print()

    print("=== Donde cambiarlo (MP usa company.brand_name del vendedor) ===")
    print("  El checkout muestra el nombre de marca configurado en la CUENTA vendedor (datos empresa).")
    print("  En MP: busca editar 'nombre de marca' / datos fiscales o empresa (no solo el nombre de la app en Developers).")
    print("  developers.mercadopago.com - tu integracion - nombre de aplicacion (secundario respecto al brand_name).")
    print("  Credenciales de prueba vs produccion deben coincidir con tu .env")
    print()


if __name__ == "__main__":
    main()
