"""
Mercado Pago — Checkout Pro (preferencias) y consulta de pagos (REST).
Requiere MERCADOPAGO_ACCESS_TOKEN en el entorno (credencial de la app en developers.mercadopago.com).
Adaptado para agendas (external_reference = id_visita).
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import re
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

MP_API = "https://api.mercadopago.com"


def url_link_pago_negocio() -> Optional[str]:
    """
    Respaldo: URL del link de cobro si no se pudo usar Checkout Pro (preferencia).
    - Variable no definida → sin link por defecto (configurá MERCADOPAGO_LINK_PAGO en .env).
    - MERCADOPAGO_LINK_PAGO vacío o checkout_pro / preferencia / api → no usar link en el fallback.
    """
    raw = os.getenv("MERCADOPAGO_LINK_PAGO")
    if raw is None:
        return None
    s = raw.strip()
    if not s or s.lower() in ("checkout_pro", "preferencia", "api"):
        return None
    return s


def url_link_pago_con_visita(id_visita: int) -> str:
    """Link de cobro con ?visita=ID (referencia visual; MP puede ignorar el query)."""
    base = url_link_pago_negocio()
    if not base:
        raise ValueError("url_link_pago_negocio no configurado")
    sep = "&" if "?" in base else "?"
    return f"{base.rstrip('/')}{sep}visita={int(id_visita)}"


def mp_token_configurado() -> bool:
    return bool(os.getenv("MERCADOPAGO_ACCESS_TOKEN", "").strip())


def _headers() -> Dict[str, str]:
    token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "").strip()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def frontend_base_url() -> str:
    default = "http://localhost:5173"
    raw = os.getenv("PUBLIC_FRONTEND_URL", default)
    s = (raw or "").strip().rstrip("/")
    if not s:
        s = default.rstrip("/")
    if not (s.startswith("http://") or s.startswith("https://")):
        s = f"http://{s}"
    return s


def backend_public_url() -> Optional[str]:
    u = os.getenv("BACKEND_PUBLIC_URL", "").strip().rstrip("/")
    return u or None


def webhook_secret() -> str:
    return os.getenv("MERCADOPAGO_WEBHOOK_SECRET", "").strip()


def statement_descriptor() -> str:
    raw = os.getenv("MERCADOPAGO_STATEMENT_DESCRIPTOR", "KING BARBER").strip()
    return (raw or "KING BARBER")[:22]


def _mercadopago_permite_auto_return(url_retorno: str) -> bool:
    try:
        p = urlparse(url_retorno)
        host = (p.hostname or "").lower()
        if not host:
            return False
        if host in ("localhost", "127.0.0.1", "::1"):
            return False
    except Exception:
        return False
    return True


def crear_preferencia_checkout_pro(
    id_visita: int,
    total: Decimal,
    titulo: str,
    payer_email: Optional[str],
    return_base: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Crea una preferencia Checkout Pro. Devuelve (init_point, preference_id, error).
    external_reference = id_visita.
    """
    if not mp_token_configurado():
        return None, None, "Token MP no configurado"

    rb = (return_base or "").strip().rstrip("/")
    if rb.startswith(("http://", "https://")) and len(rb) <= 512:
        front = rb
    else:
        front = frontend_base_url().rstrip("/")
    retorno = f"{front}/agenda/pago-resultado"
    body: Dict[str, Any] = {
        "items": [
            {
                "title": titulo[:127],
                "quantity": 1,
                "currency_id": "UYU",
                "unit_price": float(Decimal(total).quantize(Decimal("0.01"))),
            }
        ],
        "external_reference": str(id_visita),
        "back_urls": {
            "success": retorno,
            "failure": retorno,
            "pending": retorno,
        },
        "statement_descriptor": statement_descriptor(),
    }
    if _mercadopago_permite_auto_return(retorno):
        body["auto_return"] = "approved"
    else:
        logger.info(
            "MP preference: sin auto_return (URL local/private); back_urls.success=%s",
            retorno,
        )

    if payer_email:
        body["payer"] = {"email": payer_email}

    bpub = backend_public_url()
    sec = webhook_secret()
    if bpub:
        path = "/visitas/mercadopago/webhook"
        q = f"?s={sec}" if sec else ""
        body["notification_url"] = f"{bpub}{path}{q}"

    try:
        r = requests.post(
            f"{MP_API}/checkout/preferences",
            headers=_headers(),
            json=body,
            timeout=45,
        )
        if r.status_code == 400:
            try:
                err_json = r.json()
            except (json.JSONDecodeError, ValueError):
                err_json = {}
            if (
                err_json.get("error") == "invalid_auto_return"
                and body.pop("auto_return", None) == "approved"
            ):
                logger.info(
                    "MP preference: reintentando sin auto_return (back_urls.success=%s)",
                    retorno,
                )
                r = requests.post(
                    f"{MP_API}/checkout/preferences",
                    headers=_headers(),
                    json=body,
                    timeout=45,
                )
        if not r.ok:
            err = r.text[:500] if r.text else r.reason
            logger.warning("MP preference HTTP %s: %s", r.status_code, err)
            return None, None, f"Mercado Pago ({r.status_code})"

        try:
            data = r.json()
        except json.JSONDecodeError:
            logger.warning("MP preference: cuerpo no JSON: %s", (r.text or "")[:400])
            return None, None, "Respuesta de Mercado Pago inválida"
        init = data.get("sandbox_init_point") or data.get("init_point")
        pref_id = data.get("id")
        if not init:
            return None, None, "Respuesta MP sin init_point"
        return str(init), str(pref_id) if pref_id else None, None
    except requests.RequestException as e:
        logger.warning("MP preference red: %s", e)
        return None, None, str(e)[:200]


def obtener_pago(payment_id: str) -> Optional[Dict[str, Any]]:
    if not mp_token_configurado():
        return None
    try:
        r = requests.get(
            f"{MP_API}/v1/payments/{payment_id}",
            headers=_headers(),
            timeout=30,
        )
        if not r.ok:
            logger.warning("MP GET payment %s: %s %s", payment_id, r.status_code, r.text[:300])
            return None
        try:
            return r.json()
        except json.JSONDecodeError:
            logger.warning("MP GET payment %s: cuerpo no JSON", payment_id)
            return None
    except requests.RequestException as e:
        logger.warning("MP obtener_pago: %s", e)
        return None


def obtener_pago_por_id_o_merchant_order(raw_id: str) -> Optional[Dict[str, Any]]:
    """
    Tras Checkout Pro, a veces `collection_id` en la URL es el id de merchant_order y no el de payment.
    Primero intenta GET /v1/payments/{id}; si falla, GET /merchant_orders/{id} y toma el primer pago.
    """
    pid = normalizar_payment_id_input(raw_id)
    if not pid:
        return None
    pay = obtener_pago(pid)
    if pay:
        return pay
    try:
        r = requests.get(
            f"{MP_API}/merchant_orders/{pid}",
            headers=_headers(),
            timeout=30,
        )
        if not r.ok:
            logger.warning(
                "MP GET merchant_orders/%s (fallback tras payment 404): %s %s",
                pid,
                r.status_code,
                (r.text or "")[:200],
            )
            return None
        try:
            mo = r.json()
        except json.JSONDecodeError:
            return None
        payments = mo.get("payments") if isinstance(mo, dict) else None
        if not isinstance(payments, list):
            return None
        for p in payments:
            if not isinstance(p, dict):
                continue
            inner = p.get("id")
            if inner is None:
                continue
            pay = obtener_pago(str(inner).strip())
            if pay:
                return pay
    except requests.RequestException as e:
        logger.warning("MP merchant_order fallback: %s", e)
    return None


def buscar_ultimo_pago_por_external_reference(external_reference: str) -> Optional[Dict[str, Any]]:
    ref = (external_reference or "").strip()
    if not ref or not mp_token_configurado():
        return None
    end = datetime.now(timezone.utc)
    begin = end - timedelta(days=120)
    param_sets = (
        {
            "sort": "date_created",
            "criteria": "desc",
            "external_reference": ref,
            "range": "date_created",
            "begin_date": begin.strftime("%Y-%m-%dT%H:%M:%S.000-00:00"),
            "end_date": end.strftime("%Y-%m-%dT%H:%M:%S.000-00:00"),
        },
        {
            "sort": "date_created",
            "criteria": "desc",
            "external_reference": ref,
        },
    )
    try:
        data = None
        for params in param_sets:
            r = requests.get(
                f"{MP_API}/v1/payments/search",
                headers=_headers(),
                params=params,
                timeout=30,
            )
            if r.ok:
                try:
                    data = r.json()
                except json.JSONDecodeError:
                    continue
                break
            logger.warning(
                "MP search payments ref=%s intento params=%s: %s %s",
                ref,
                list(params.keys()),
                r.status_code,
                r.text[:300],
            )
        if not isinstance(data, dict):
            return None
        results = data.get("results")
        if not results:
            return None
        first = results[0]
        return first if isinstance(first, dict) else None
    except requests.RequestException as e:
        logger.warning("MP buscar_pago external_reference: %s", e)
        return None


def external_reference_de_pago(payment: Dict[str, Any]) -> Optional[int]:
    from decimal import Decimal, InvalidOperation

    ref = payment.get("external_reference")
    if ref is None or ref == "":
        return None
    try:
        return int(Decimal(str(ref)))
    except (TypeError, ValueError, InvalidOperation):
        try:
            return int(float(str(ref)))
        except (TypeError, ValueError):
            return None


def external_reference_desde_preferencia(preference_id: str) -> Optional[int]:
    pid = (preference_id or "").strip()
    if not pid or not mp_token_configurado():
        return None
    try:
        r = requests.get(
            f"{MP_API}/checkout/preferences/{pid}",
            headers=_headers(),
            timeout=30,
        )
        if not r.ok:
            logger.warning("MP GET preference %s: %s", pid, r.status_code)
            return None
        data = r.json()
        ref = data.get("external_reference")
        if ref is None or ref == "":
            return None
        from decimal import Decimal as D, InvalidOperation

        try:
            return int(D(str(ref)))
        except (ValueError, TypeError, InvalidOperation):
            try:
                return int(float(str(ref)))
            except (ValueError, TypeError):
                return None
    except (requests.RequestException,) as e:
        logger.warning("MP preferencia external_reference: %s", e)
        return None


def normalizar_payment_id_input(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    if s.isdigit():
        return s[:64]
    digits = "".join(c for c in s if c.isdigit())
    if len(digits) >= 4:
        return digits[:64]
    m = re.search(r"(\d{4,})", s)
    return (m.group(1) if m else s)[:64]


def activities_host_vendedor() -> str:
    raw = os.getenv("MERCADOPAGO_ACTIVITIES_HOST", "www.mercadopago.com.uy").strip()
    raw = raw.replace("https://", "").replace("http://", "").split("/")[0]
    return raw or "www.mercadopago.com.uy"


def _primer_id_merchant_order_en_busqueda(data: Any) -> Optional[str]:
    if not isinstance(data, dict):
        return None
    for key in ("elements", "results"):
        arr = data.get(key)
        if not isinstance(arr, list) or not arr:
            continue
        el = arr[0]
        if isinstance(el, dict) and el.get("id") is not None:
            s = str(el["id"]).strip()
            return s or None
    return None


def _merchant_order_id_por_external_reference(ref: str) -> Optional[str]:
    rref = (ref or "").strip()
    if not rref or not mp_token_configurado():
        return None
    try:
        r = requests.get(
            f"{MP_API}/merchant_orders/search",
            headers=_headers(),
            params={"external_reference": rref, "limit": 5},
            timeout=30,
        )
        if not r.ok:
            logger.warning(
                "MP merchant_orders/search ref=%s: %s %s",
                rref,
                r.status_code,
                r.text[:200],
            )
            return None
        try:
            data = r.json()
        except json.JSONDecodeError:
            return None
        return _primer_id_merchant_order_en_busqueda(data)
    except requests.RequestException as e:
        logger.warning("MP merchant_orders/search: %s", e)
        return None


def url_actividad_vendedor_desde_pago(pay: Dict[str, Any]) -> Optional[str]:
    try:
        if not isinstance(pay, dict):
            return None
        host = activities_host_vendedor()
        base = f"https://{host}".rstrip("/")

        slug: Optional[str] = None
        order = pay.get("order")
        if isinstance(order, dict) and order.get("id") is not None:
            slug = str(order["id"]).strip()
        if not slug:
            mo = pay.get("merchant_order_id")
            if mo is not None and str(mo).strip():
                slug = str(mo).strip()
        if not slug:
            ext = pay.get("external_reference")
            if ext is not None and str(ext).strip():
                slug = _merchant_order_id_por_external_reference(str(ext).strip())

        if not slug:
            return None
        return f"{base}/activities/detail/checkout_merchant_order-{slug}"[:512]
    except Exception as e:
        logger.warning("MP url_actividad_vendedor_desde_pago: %s", e)
        return None


def receipt_url_de_pago(pay: Dict[str, Any]) -> Optional[str]:
    if not isinstance(pay, dict):
        return None
    td = pay.get("transaction_details")
    if isinstance(td, dict):
        u = td.get("external_resource_url")
        if isinstance(u, str) and u.startswith("http"):
            return u[:512]
    poi = pay.get("point_of_interaction")
    if isinstance(poi, dict):
        tdata = poi.get("transaction_data")
        if isinstance(tdata, dict):
            v = tdata.get("ticket_url")
            if isinstance(v, str) and v.startswith("http"):
                return v[:512]
    return None
