"""
Cliente mínimo Checkout Pro (preferencias + consulta de pago).
Variables: MERCADOPAGO_ACCESS_TOKEN, PUBLIC_FRONTEND_URL (o override abajo),
MERCADOPAGO_RETURN_FRONTEND_URL, BACKEND_PUBLIC_URL.

Base de back_urls (solo .env, sin IPs fijas en código):
  1) MERCADOPAGO_RETURN_FRONTEND_URL si está definida
  2) si no, PUBLIC_FRONTEND_URL
Al cambiar DNS o dominio, actualizá esas variables y reiniciá el API; las
preferencias MP ya creadas siguen con las URLs viejas hasta que expiren o
se genere un checkout nuevo.

notification_url se arma con MERCADOPAGO_TUNNEL_URL o NGROK_PUBLIC_URL si existen (dev: ngrok al
puerto del API), si no con BACKEND_PUBLIC_URL (producción: https://api.tudominio.com). Así podés
dejar BACKEND_PUBLIC_URL=http://127.0.0.1:8000 para el resto y usar el túnel solo para MP.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Optional
from urllib.parse import urlencode, urlparse, urljoin
from zoneinfo import ZoneInfo

import requests

_MP_BASE = "https://api.mercadopago.com"
_UY_TZ = ZoneInfo("America/Montevideo")
logger = logging.getLogger(__name__)


def _checkout_return_base_url() -> str:
    """Base HTTPS del front para back_urls de Checkout Pro (todo desde env)."""
    explicit = (os.getenv("MERCADOPAGO_RETURN_FRONTEND_URL") or "").strip().rstrip("/")
    if explicit:
        return explicit
    pub = (os.getenv("PUBLIC_FRONTEND_URL") or "").strip().rstrip("/")
    if pub:
        return pub
    raise RuntimeError(
        "Definí PUBLIC_FRONTEND_URL o MERCADOPAGO_RETURN_FRONTEND_URL en .env (HTTPS). "
        "Es la URL base del sitio que el usuario abre en el navegador; Mercado Pago "
        "la usa en back_urls al crear cada preferencia."
    )


def preference_expiration_minutes() -> int:
    """Minutos de validez del checkout (preferencia MP + cancelación pendiente en BD)."""
    try:
        v = int((os.getenv("MERCADOPAGO_PREFERENCE_EXPIRATION_MINUTES") or "10").strip())
        return max(1, min(v, 120))
    except ValueError:
        return 10


def _preference_expiration_fields(minutes: int) -> dict[str, Any]:
    """Campos oficiales de vigencia de preferencia (Checkout Pro)."""
    now = datetime.now(_UY_TZ)
    end = now + timedelta(minutes=max(1, minutes))
    return {
        "expires": True,
        "expiration_date_from": now.isoformat(timespec="milliseconds"),
        "expiration_date_to": end.isoformat(timespec="milliseconds"),
    }


def _token() -> str:
    t = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "").strip()
    if not t:
        raise RuntimeError("Falta MERCADOPAGO_ACCESS_TOKEN en el entorno")
    return t


def public_key() -> str:
    return os.getenv("MERCADOPAGO_PUBLIC_KEY", "").strip()


def _public_api_base_for_mp_notification_url() -> str:
    """
    Origen HTTPS público del API solo para notification_url en la preferencia MP.
    Prioridad: MERCADOPAGO_TUNNEL_URL → NGROK_PUBLIC_URL → BACKEND_PUBLIC_URL.
    """
    tunnel = (
        os.getenv("MERCADOPAGO_TUNNEL_URL") or os.getenv("NGROK_PUBLIC_URL") or ""
    ).strip().rstrip("/")
    backend = (os.getenv("BACKEND_PUBLIC_URL") or "").strip().rstrip("/")
    if tunnel:
        logger.info(
            "Mercado Pago: notification_url usará túnel MERCADOPAGO_TUNNEL_URL/NGROK_PUBLIC_URL=%r",
            tunnel[:120],
        )
        return tunnel
    return backend


def _notification_webhook_url(backend_base: str) -> Optional[str]:
    """
    URL canónica para notification_url (ej. ngrok):
    https://SUBDOMINIO.ngrok-free.app/visitas/mercadopago/webhook
    Definí BACKEND_PUBLIC_URL solo con el origen, p. ej. https://abc123.ngrok-free.app
    """
    b = (backend_base or "").strip().rstrip("/")
    if not b:
        return None
    raw = b if "://" in b else f"https://{b}"
    parsed = urlparse(raw)
    if not parsed.netloc:
        return urljoin(b.rstrip("/") + "/", "visitas/mercadopago/webhook")
    scheme = (parsed.scheme or "https").lower()
    path = (parsed.path or "").strip("/")
    origin = f"{scheme}://{parsed.netloc}"
    if path:
        origin = f"{origin}/{path}"
    origin = origin.rstrip("/")
    return urljoin(origin + "/", "visitas/mercadopago/webhook")


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
    expiration_minutes: Optional[int] = None,
) -> dict[str, Any]:
    public_raw = _checkout_return_base_url()
    notification_base = _public_api_base_for_mp_notification_url()

    if not public_raw.lower().startswith("https://"):
        raise RuntimeError(
            "La base de back_urls debe ser HTTPS (Mercado Pago ya no acepta http). "
            "Definí MERCADOPAGO_RETURN_FRONTEND_URL o PUBLIC_FRONTEND_URL en .env, "
            "p. ej. https://localhost:5174 en dev o ngrok https://….ngrok-free.app "
            f"(recibido: {public_raw!r})"
        )

    logger.info("Mercado Pago back_urls base: %s", public_raw)

    back = f"{public_raw}/agenda/pago-resultado"

    def _return_url(mp_return: str) -> str:
        q = urlencode({"token": token_seguimiento, "mp_return": mp_return})
        return f"{back}?{q}"

    if id_visita is None or int(id_visita) < 1:
        raise RuntimeError(f"id_visita inválido para preferencia MP: {id_visita!r}")
    ext_ref = str(int(id_visita))

    payload: dict[str, Any] = {
        "items": [
            {
                "title": (title or "Turno barbería")[:256],
                "quantity": 1,
                "unit_price": round(float(unit_price), 2) if float(unit_price) > 0 else 1.0,
                "currency_id": "UYU",
            }
        ],
        "external_reference": ext_ref,
        "metadata": {"token_seguimiento": token_seguimiento, "id_visita": ext_ref},
        "back_urls": {
            "success": _return_url("ok"),
            "failure": _return_url("fail"),
            "pending": _return_url("pending"),
        },
        "auto_return": "approved",
    }

    exp_min = expiration_minutes if expiration_minutes is not None else preference_expiration_minutes()
    payload.update(_preference_expiration_fields(exp_min))

    notif = _notification_webhook_url(notification_base)
    if notif:
        payload["notification_url"] = notif
        if not notif.lower().startswith("https://"):
            logger.warning(
                "Mercado Pago: notification_url no usa https (%r). MP suele rechazarla; "
                "usá MERCADOPAGO_TUNNEL_URL o BACKEND_PUBLIC_URL con https://…",
                notif[:200],
            )
        logger.info(
            "Mercado Pago preference notification_url EXACTA=%r external_reference=%r",
            notif,
            ext_ref,
        )
    else:
        logger.warning(
            "Mercado Pago: sin MERCADOPAGO_TUNNEL_URL / BACKEND_PUBLIC_URL para notification_url; "
            "preferencia sin webhook IPN. En dev: MERCADOPAGO_TUNNEL_URL=https://xxx.ngrok-free.app",
        )

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
            detail_obj: Any = r.json()
        except Exception:
            detail_obj = r.text
        err_code = None
        msg_l = ""
        if isinstance(detail_obj, dict):
            err_code = detail_obj.get("error")
            msg_l = str(detail_obj.get("message") or "").lower()
        # MP a veces escribe "notificaction_url" en el mensaje (typo oficial).
        if r.status_code == 400 and "notification_url" in payload and (
            err_code == "invalid_notification_url"
            or "notificaction_url" in msg_l
            or ("notification_url" in msg_l and "valid url" in msg_l)
        ):
            dropped = payload.pop("notification_url", None)
            logger.error(
                "Mercado Pago rechazó notification_url=%r. Reintentando preferencia SIN webhook. "
                "En .env usá BACKEND_PUBLIC_URL con HTTPS y host que MP acepte (p. ej. https://xxx.ngrok-free.app).",
                dropped,
            )
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


def get_merchant_order(order_id: str) -> dict[str, Any]:
    """Detalle de orden comercial Checkout Pro (notificaciones topic merchant_order)."""
    r = requests.get(
        f"{_MP_BASE}/merchant_orders/{order_id}",
        headers={"Authorization": f"Bearer {_token()}"},
        timeout=45,
    )
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Mercado Pago merchant_orders HTTP {r.status_code}: {detail}")
    return r.json()


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
