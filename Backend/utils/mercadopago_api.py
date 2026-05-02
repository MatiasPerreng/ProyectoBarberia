"""
Cliente mínimo Checkout Pro (preferencias + consulta de pago).
Variables: MERCADOPAGO_ACCESS_TOKEN, PUBLIC_FRONTEND_URL, BACKEND_PUBLIC_URL.

Mercado Pago (2025) rechaza HTTP en back_urls y notification_url: usá HTTPS
(p. ej. ngrok http 5174 y ngrok http 8000) y pegá esas URLs en .env.
"""
from __future__ import annotations

import os
from typing import Any, Optional
from urllib.parse import urlencode

import requests

_MP_BASE = "https://api.mercadopago.com"


def _token() -> str:
    t = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "").strip()
    if not t:
        raise RuntimeError("Falta MERCADOPAGO_ACCESS_TOKEN en el entorno")
    return t


def public_key() -> str:
    return os.getenv("MERCADOPAGO_PUBLIC_KEY", "").strip()


def comprobante_url_public(payment_id: Optional[str]) -> Optional[str]:
    """Recibo / comprobante MP (número de operación = id del pago)."""
    if not payment_id:
        return None
    tpl = os.getenv(
        "MERCADOPAGO_COMPROBANTE_URL",
        "https://www.mercadopago.com.uy/tools/receipt-view/{payment_id}",
    )
    try:
        return tpl.format(payment_id=payment_id)
    except Exception:
        return f"https://www.mercadopago.com.uy/tools/receipt-view/{payment_id}"


def create_checkout_preference(
    *,
    id_visita: int,
    title: str,
    unit_price: float,
    payer_email: Optional[str],
    token_seguimiento: str,
) -> dict[str, Any]:
    public_raw = (os.getenv("PUBLIC_FRONTEND_URL") or "").strip().rstrip("/")
    backend_raw = (os.getenv("BACKEND_PUBLIC_URL") or "").strip().rstrip("/")

    if not public_raw.lower().startswith("https://"):
        raise RuntimeError(
            "PUBLIC_FRONTEND_URL debe ser HTTPS (Mercado Pago ya no acepta http en back_urls). "
            "Opciones: (1) En .env: PUBLIC_FRONTEND_URL=https://localhost:5174 y arrancá el front "
            "con `npm run dev` (Vite usa certificado de prueba @vitejs/plugin-basic-ssl). "
            "(2) O ngrok: PUBLIC_FRONTEND_URL=https://….ngrok-free.app "
            f"(recibido: {public_raw!r})"
        )

    back = f"{public_raw}/agenda/pago-resultado"

    def _return_url(mp_return: str) -> str:
        q = urlencode({"token": token_seguimiento, "mp_return": mp_return})
        return f"{back}?{q}"

    payload: dict[str, Any] = {
        "items": [
            {
                "title": (title or "Turno barbería")[:256],
                "quantity": 1,
                "unit_price": round(float(unit_price), 2) if float(unit_price) > 0 else 1.0,
                "currency_id": "UYU",
            }
        ],
        "external_reference": str(id_visita),
        "metadata": {"token_seguimiento": token_seguimiento},
        "back_urls": {
            "success": _return_url("ok"),
            "failure": _return_url("fail"),
            "pending": _return_url("pending"),
        },
        "auto_return": "approved",
    }

    if backend_raw.lower().startswith("https://"):
        payload["notification_url"] = f"{backend_raw}/visitas/mercadopago/webhook"

    if payer_email:
        payload["payer"] = {"email": payer_email.strip()}

    r = requests.post(
        f"{_MP_BASE}/checkout/preferences",
        json=payload,
        headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"},
        timeout=45,
    )
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Mercado Pago preferences HTTP {r.status_code}: {detail}")

    data = r.json()
    init_point = data.get("init_point") or data.get("sandbox_init_point")
    if not init_point:
        raise RuntimeError("Mercado Pago no devolvió init_point")
    return {"id": data["id"], "init_point": init_point, "raw": data}


def get_payment(payment_id: str) -> dict[str, Any]:
    r = requests.get(
        f"{_MP_BASE}/v1/payments/{payment_id}",
        headers={"Authorization": f"Bearer {_token()}"},
        timeout=45,
    )
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Mercado Pago payment HTTP {r.status_code}: {detail}")
    return r.json()
