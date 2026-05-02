"""
Validación de origen de Webhooks Mercado Pago (header x-signature, secret del panel).

Plantilla oficial del manifest:
  id:[data_id];request-id:[x-request-id];ts:[ts];

- `id` debe coincidir con el identificador del evento (query `data.id` o equivalente);
  si es alfanumérico, en minúsculas.
- Documentación: notificaciones Webhooks > secret signature.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any, Optional

from starlette.requests import Request

logger = logging.getLogger(__name__)


def _parse_x_signature_parts(header_val: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in header_val.split(","):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip().lower()] = v.strip()
    return out


def notification_manifest_data_id(
    request: Request,
    body: dict[str, Any],
    *,
    payment_id: Optional[str],
    merchant_order_id: Optional[str],
) -> Optional[str]:
    """Id usado en el manifest: prioriza query `data.id`, luego cuerpo, luego ids parseados."""
    q = request.query_params
    for key in ("data.id",):
        v = q.get(key)
        if v:
            return str(v)
    v = q.get("id")
    if v:
        return str(v)
    data = body.get("data")
    if isinstance(data, dict) and data.get("id") is not None:
        return str(data.get("id"))
    if payment_id:
        return str(payment_id)
    if merchant_order_id:
        return str(merchant_order_id)
    return None


def verify_mercadopago_webhook_signature(
    request: Request,
    body: dict[str, Any],
    *,
    manifest_data_id: Optional[str],
    secret: str,
    max_ts_skew_ms: int = 600_000,
) -> bool:
    """
    Devuelve True si la firma es válida.
    Si `secret` está vacío, no valida (compatibilidad dev); el caller debe decidir si exige secret.
    """
    if not secret.strip():
        return True

    if not manifest_data_id:
        logger.warning("MP webhook firma: sin manifest_data_id (query/body)")
        return False

    sig_raw = (request.headers.get("x-signature") or "").strip()
    request_id = (request.headers.get("x-request-id") or "").strip()
    if not sig_raw or not request_id:
        logger.warning("MP webhook firma: faltan x-signature o x-request-id")
        return False

    parts = _parse_x_signature_parts(sig_raw)
    ts = parts.get("ts")
    v1 = parts.get("v1")
    if not ts or not v1:
        logger.warning("MP webhook firma: x-signature sin ts o v1 parseable")
        return False

    try:
        ts_ms = int(ts)
    except ValueError:
        return False

    now_ms = int(time.time() * 1000)
    if abs(now_ms - ts_ms) > max_ts_skew_ms:
        logger.warning(
            "MP webhook firma: ts fuera de tolerancia (skew>%sms) ts=%s",
            max_ts_skew_ms,
            ts,
        )
        return False

    mid = manifest_data_id.lower() if manifest_data_id.isalnum() else manifest_data_id
    manifest = f"id:{mid};request-id:{request_id};ts:{ts};"
    key = secret.encode("utf-8")
    expected = hmac.new(key, manifest.encode("utf-8"), hashlib.sha256).hexdigest()

    ok = hmac.compare_digest(expected, v1)
    if not ok:
        logger.warning(
            "MP webhook firma: HMAC no coincide (manifest len=%s request_id=%s)",
            len(manifest),
            request_id[:24] if request_id else "",
        )
    return ok
