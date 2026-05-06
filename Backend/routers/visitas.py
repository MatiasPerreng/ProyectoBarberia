import asyncio
import json
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Tuple, Dict
from datetime import date, datetime, time, timedelta
from calendar import monthrange

from database import get_db, SessionLocal
from utils.mercadopago_api import comprobante_url_public
# Importaciones de modelos para la lógica de validación
from models.blacklist import Blacklist
from models import Cliente, Visita # Importamos Cliente para buscar el teléfono

# Importaciones directas de archivos para evitar círculos viciosos de inicialización
from schemas.visita import VisitaCreate, VisitaOut, VisitaUpdate
from core.dependencias import get_current_login_barbero, get_current_staff
from core.email import enviar_email_confirmacion
from core.email_templates import (
    generar_email_confirmacion,
    generar_email_cancelacion,
)

# Servicios de WhatsApp
from services.whatsapp import enviar_recordatorio_whatsapp, enviar_cancelacion_whatsapp

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/visitas",
    tags=["Visitas"]
)

# ======================================================================================
# CONFIGURACIÓN DE HORA LOCAL (URUGUAY UTC-3)
# ======================================================================================

def obtener_hoy_local() -> date:
    """Retorna la fecha actual de Uruguay (UTC-3) para evitar desfases del servidor."""
    return (datetime.utcnow() - timedelta(hours=3)).date()

# ======================================================================================
# SERIALIZADOR
# ======================================================================================

def visita_to_out(visita):
    if isinstance(visita, dict):
        return visita

    servicio_precio = None
    frozen = getattr(visita, "precio_al_reservar", None)
    if frozen is not None:
        servicio_precio = float(frozen)
    elif visita.servicio and visita.servicio.precio is not None:
        servicio_precio = float(visita.servicio.precio)

    medio = getattr(visita, "medio_pago", None) or "EFECTIVO"
    mpid = getattr(visita, "mp_payment_id", None)
    comp_url = (
        comprobante_url_public(str(mpid))
        if medio == "MERCADOPAGO" and mpid
        else None
    )

    return {
        "id_visita": visita.id_visita,
        "fecha_hora": visita.fecha_hora,
        "created_at": getattr(visita, "created_at", None),
        "estado": visita.estado,

        "cliente_nombre": visita.cliente.nombre if visita.cliente else "",
        "cliente_apellido": visita.cliente.apellido if visita.cliente else "",
        "cliente_telefono": visita.cliente.telefono if visita.cliente else "",
        "servicio_nombre": visita.servicio.nombre if visita.servicio else "",
        "servicio_duracion": visita.servicio.duracion_min if visita.servicio else 0,
        "servicio_precio": servicio_precio,

        "barbero_id": visita.barbero.id_barbero if visita.barbero else None,
        "barbero_nombre": visita.barbero.nombre if visita.barbero else "",
        "medio_pago": medio,
        "mp_payment_id": mpid,
        "comprobante_mp_url": comp_url,
        "init_point": None,
        "public_key": None,
    }

# ======================================================================================
# MI AGENDA Y HISTORIAL
# ======================================================================================

@router.get("/mi-agenda", response_model=List[VisitaOut])
def mi_agenda(
    fecha: Optional[date] = None,
    login=Depends(get_current_login_barbero),
    db: Session = Depends(get_db)
):
    from crud import visita as crud_v
    crud_v.marcar_visitas_completadas(db)
    visitas = crud_v.get_visitas_by_barbero(db=db, barbero_id=login.barbero_id, fecha=fecha)
    return [visita_to_out(v) for v in visitas]

@router.get("/historial", response_model=List[VisitaOut])
def historial_agenda(
    fecha: Optional[date] = None,
    login=Depends(get_current_login_barbero),
    db: Session = Depends(get_db)
):
    from crud import visita as crud_v
    crud_v.marcar_visitas_completadas(db)
    if login.role == "admin":
        visitas = crud_v.get_visitas_completadas(db=db, fecha=fecha)
    else:
        visitas = crud_v.get_visitas_completadas_por_barbero(db=db, barbero_id=login.barbero_id, fecha=fecha)
    return [visita_to_out(v) for v in visitas]

# ======================================================================================
# DISPONIBILIDAD
# ======================================================================================

@router.get("/disponibilidad")
def obtener_disponibilidad(fecha: date, id_servicio: int, id_barbero: Optional[int] = None, db: Session = Depends(get_db)):
    from crud import visita as crud_v
    try:
        return crud_v.get_disponibilidad(db=db, fecha=fecha, id_servicio=id_servicio, id_barbero=id_barbero)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/disponibilidad-mes")
def disponibilidad_mes(mes: int, anio: int, id_servicio: int, id_barbero: int, db: Session = Depends(get_db)):
    from crud import horario as crud_h
    from crud import visita as crud_v
    hoy = obtener_hoy_local()
    _, last_day = monthrange(anio, mes)
    resultado = []
    for dia in range(1, last_day + 1):
        fecha_dia = date(anio, mes, dia)
        if fecha_dia < hoy:
            resultado.append({"fecha": fecha_dia.isoformat(), "estado": "pasado"})
            continue
        horarios = crud_h.get_horarios_barbero_para_fecha(db=db, id_barbero=id_barbero, dia_semana=fecha_dia.isoweekday(), fecha=fecha_dia)
        if not horarios:
            resultado.append({"fecha": fecha_dia.isoformat(), "estado": "sin_horario"})
            continue
        turnos = crud_v.get_disponibilidad(db=db, fecha=fecha_dia, id_servicio=id_servicio, id_barbero=id_barbero)
        estado = "disponible" if len(turnos["turnos"]) > 0 else "completo"
        resultado.append({"fecha": fecha_dia.isoformat(), "estado": estado})
    return resultado


# ======================================================================================
# MERCADO PAGO — seguimiento público (sin JWT; el token es el secreto compartido)
# ======================================================================================

@router.get("/seguimiento/sincronizar", response_model=VisitaOut)
def sincronizar_pago_seguimiento(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    token: str = Query(..., min_length=8),
    payment_id: str = Query(..., min_length=1),
):
    """
    Respaldo frente al webhook: mismo aplicar_pago_mercadopago cuando el usuario vuelve por back_url
    con payment_id (idempotente si el IPN ya confirmó la visita).
    """
    from crud import visita as crud_v
    from utils import mercadopago_api as mp

    visita = crud_v.get_visita_por_token(db, token)
    if not visita:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    try:
        pdata = mp.get_payment(str(payment_id))
    except Exception as e:
        logger.exception("MP get_payment falló")
        raise HTTPException(status_code=502, detail=str(e)) from e

    try:
        # Si estaba CANCELADO por timeout pero MP acreditó igual, aplicar_pago puede reactivar a CONFIRMADO.
        enviar_mail = crud_v.aplicar_pago_mercadopago(db, visita, pdata)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    visita = crud_v.get_visita_by_id(db, visita.id_visita)
    if enviar_mail and visita and visita.cliente and visita.cliente.email:
        background_tasks.add_task(
            enviar_email_confirmacion,
            visita.cliente.email,
            "✅ Turno confirmado - King Barber",
            generar_email_confirmacion(visita),
        )
    return visita_to_out(visita)


@router.get("/seguimiento/{token}", response_model=VisitaOut)
def obtener_visita_por_token_seguimiento(token: str, db: Session = Depends(get_db)):
    from crud import visita as crud_v

    visita = crud_v.get_visita_por_token(db, token)
    if not visita:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return visita_to_out(visita)


def _parse_mp_notification_ids_parts(qp: Dict[str, str], body: Any) -> Tuple[Optional[str], Optional[str]]:
    """
    Devuelve (payment_id, merchant_order_id) desde query dict (IPN GET) y/o body JSON (POST).
    """
    topic = (qp.get("topic") or qp.get("type") or "").lower()
    qid = qp.get("id")

    payment_id: Optional[str] = None
    merchant_order_id: Optional[str] = None

    if topic == "merchant_order" and qid:
        merchant_order_id = str(qid)
    elif topic == "payment" and qid:
        payment_id = str(qid)

    if isinstance(body, dict):
        b_type = (body.get("type") or body.get("topic") or "").lower()
        data = body.get("data")
        did: Optional[str] = None
        if isinstance(data, dict) and data.get("id") is not None:
            did = str(data.get("id"))
        if did:
            if "merchant_order" in b_type:
                merchant_order_id = did
            elif "payment" in b_type or "payment" in (body.get("action") or "").lower():
                payment_id = did
            elif not b_type:
                payment_id = did
        resource = body.get("resource")
        if isinstance(resource, str):
            if "/merchant_orders/" in resource:
                merchant_order_id = resource.rstrip("/").split("/")[-1].split("?")[0]
            elif "/payments/" in resource and not payment_id:
                payment_id = resource.rstrip("/").split("/")[-1].split("?")[0]

    if not payment_id and not merchant_order_id:
        payment_id = qp.get("data.id") or qp.get("id")

    return payment_id, merchant_order_id


def _parse_mp_notification_ids(request: Request, body: Any) -> Tuple[Optional[str], Optional[str]]:
    return _parse_mp_notification_ids_parts(dict(request.query_params), body)


def _payment_ids_from_merchant_order(order: Dict[str, Any]) -> List[str]:
    """IDs de pago embebidos en merchant_orders (Checkout Pro notifica a veces solo este tópico)."""
    seen: set[str] = set()
    out: List[str] = []
    for p in order.get("payments") or []:
        pid: Any = None
        if isinstance(p, dict):
            pid = p.get("id")
        elif isinstance(p, (int, float, str)):
            pid = p
        if pid is None:
            continue
        s = str(int(pid)) if isinstance(pid, float) and pid == int(pid) else str(pid).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def _apply_mp_payment_notification(
    db: Session,
    background_tasks: Optional[BackgroundTasks],
    payment_id: str,
) -> None:
    """Obtiene el pago en MP, valida external_reference y aplica a la visita (idempotente)."""
    from crud import visita as crud_v
    from utils import mercadopago_api as mp

    pdata = mp.get_payment(payment_id)
    vid = pdata.get("external_reference")
    logger.info(
        "MP webhook get_payment payment_id=%s external_reference=%r status=%s",
        payment_id,
        vid,
        pdata.get("status"),
    )
    if not vid:
        logger.warning(
            "MP webhook: pago %s sin external_reference en respuesta MP; no se actualiza ninguna visita",
            payment_id,
        )
        return
    try:
        vid_int = int(vid)
    except (TypeError, ValueError):
        logger.warning("MP webhook: external_reference no es id numérico de visita: %r", vid)
        return

    visita = crud_v.get_visita_by_id(db, vid_int)
    if not visita:
        logger.warning("MP webhook: no existe visita id=%s (external_reference)", vid_int)
        return

    try:
        enviar_mail = crud_v.aplicar_pago_mercadopago(db, visita, pdata)
    except ValueError as e:
        logger.warning("MP webhook aplicar_pago_mercadopago: %s", e)
        return

    visita = crud_v.get_visita_by_id(db, visita.id_visita)
    if enviar_mail and visita and visita.cliente and visita.cliente.email:
        if background_tasks is not None:
            background_tasks.add_task(
                enviar_email_confirmacion,
                visita.cliente.email,
                "✅ Turno confirmado - King Barber",
                generar_email_confirmacion(visita),
            )
        else:
            try:
                asyncio.run(
                    enviar_email_confirmacion(
                        visita.cliente.email,
                        "✅ Turno confirmado - King Barber",
                        generar_email_confirmacion(visita),
                    )
                )
            except RuntimeError as re:
                logger.warning("MP webhook email (asyncio.run): %s", re)


class _HeadersShim:
    """Cabeceras copiadas (claves en minúsculas) para validar x-signature en el worker."""

    def __init__(self, lower_map: Dict[str, str]):
        self._d = lower_map

    def get(self, key: str, default=None):
        return self._d.get(str(key).lower(), default)


class _FakeRequestForSig:
    """Solo query_params + headers para verificación HMAC si MERCADOPAGO_WEBHOOK_ENFORCE_SIGNATURE=true."""

    def __init__(self, qp: Dict[str, str], headers_lower: Dict[str, str]):
        self.query_params = qp
        self.headers = _HeadersShim(headers_lower)


def _mercadopago_webhook_worker(
    qp: Dict[str, str],
    raw_body: bytes,
    headers_lower: Dict[str, str],
) -> None:
    """
    Camino principal de acreditación MP: sesión de BD propia (SessionLocal), no la del request.
    Resuelve visita vía external_reference en get_payment + aplicar_pago_mercadopago.
    """
    from crud import visita as crud_v
    from utils import mercadopago_api as mp
    from utils import mercadopago_webhook_sig as mwsig

    body_obj: Any = {}
    if raw_body.strip():
        try:
            body_obj = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            body_obj = {
                "_webhook_non_json": raw_body.decode("utf-8", errors="replace")[:20000],
            }

    payment_id, merchant_order_id = _parse_mp_notification_ids_parts(qp, body_obj)
    logger.info(
        "MP webhook worker ids payment_id=%r merchant_order_id=%r",
        payment_id,
        merchant_order_id,
    )

    secret = os.getenv("MERCADOPAGO_WEBHOOK_SECRET", "").strip()
    raw_enforce = (os.getenv("MERCADOPAGO_WEBHOOK_ENFORCE_SIGNATURE") or "").strip().lower()
    if raw_enforce in ("false", "0", "no"):
        enforce_sig = False
    elif raw_enforce in ("true", "1", "yes"):
        enforce_sig = True
    else:
        # Producción: con secret configurado, validar firma salvo que se fuerce lo contrario.
        enforce_sig = bool(secret)

    if enforce_sig and secret:
        body_dict: dict[str, Any] = body_obj if isinstance(body_obj, dict) else {}
        fake_req = _FakeRequestForSig(qp, headers_lower)
        mid = mwsig.notification_manifest_data_id(
            fake_req,
            body_dict,
            payment_id=payment_id,
            merchant_order_id=merchant_order_id,
        )
        if not mwsig.verify_mercadopago_webhook_signature(
            fake_req,
            body_dict,
            manifest_data_id=mid,
            secret=secret,
        ):
            logger.error(
                "MP webhook worker: firma inválida (manifest_data_id=%r); no se aplica pago. "
                "Desactivá MERCADOPAGO_WEBHOOK_ENFORCE_SIGNATURE en diagnóstico.",
                mid,
            )
            return
    elif secret and not enforce_sig:
        logger.warning(
            "MP webhook worker: firma desactivada (MERCADOPAGO_WEBHOOK_ENFORCE_SIGNATURE=false); no usar en producción"
        )

    db = SessionLocal()
    try:
        crud_v.cancelar_visitas_mp_expiradas(db)

        if merchant_order_id:
            order = mp.get_merchant_order(merchant_order_id)
            logger.info(
                "MP webhook worker merchant_order id=%s preference_id=%s payments_count=%s",
                merchant_order_id,
                order.get("preference_id"),
                len(order.get("payments") or []),
            )
            for pid in _payment_ids_from_merchant_order(order):
                _apply_mp_payment_notification(db, None, pid)
            crud_v.procesar_merchant_order_mp(db, order)

        if payment_id:
            _apply_mp_payment_notification(db, None, str(payment_id))
    except ValueError as e:
        logger.warning("MP webhook worker validación: %s", e)
    except Exception:
        logger.exception("MP webhook worker error")
    finally:
        db.close()


@router.api_route("/mercadopago/webhook", methods=["GET", "POST"])
async def mercadopago_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    IPN/Webhook MP. Tras leer el body (rápido), responde 200 y JSON vacío sin esperar a MP/DB;
    el trabajo pesado corre en segundo plano (SessionLocal propia).
    """
    raw_body = await request.body()
    qp = dict(request.query_params)
    headers_dict = {k: v for k, v in request.headers.items()}
    headers_lower = {str(k).lower(): v for k, v in request.headers.items()}

    body_for_print: Any = {}
    if raw_body.strip():
        try:
            body_for_print = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            body_for_print = raw_body.decode("utf-8", errors="replace")[:20000]

    sig = headers_lower.get("x-signature") or headers_dict.get("x-signature") or "(ausente)"
    ua = headers_lower.get("user-agent") or "(ausente)"
    _console_diag = os.getenv("MERCADOPAGO_WEBHOOK_CONSOLE_DIAG", "true").lower() in ("true", "1", "yes")
    if _console_diag:
        print("=== MERCADO PAGO WEBHOOK DIAG ===", flush=True)
        try:
            print("HEADERS:", json.dumps(headers_dict, ensure_ascii=False, default=str), flush=True)
        except Exception:
            print("HEADERS:", repr(headers_dict), flush=True)
        if isinstance(body_for_print, dict):
            try:
                print("BODY:", json.dumps(body_for_print, ensure_ascii=False, default=str), flush=True)
            except Exception:
                print("BODY:", repr(body_for_print), flush=True)
        else:
            print("BODY:", body_for_print, flush=True)
        print("x-signature:", sig, flush=True)
        print("user-agent:", ua, flush=True)
        print("=== FIN DIAG ===", flush=True)

    logger.info(
        "MP webhook diag method=%s x-signature=%r user-agent=%r query_keys=%s",
        request.method,
        sig,
        ua,
        list(qp.keys()),
    )

    background_tasks.add_task(_mercadopago_webhook_worker, qp, raw_body, headers_lower)
    return JSONResponse(content={}, status_code=200)


# ======================================================================================
# CREAR VISITA (CORREGIDO PARA EVITAR EL ATTRIBUTE ERROR)
# ======================================================================================

@router.post("/", response_model=VisitaOut, status_code=status.HTTP_201_CREATED)
def crear_visita(
    visita_in: VisitaCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    from crud import visita as crud_v
    try:
        # 1. BUSCAR AL CLIENTE PARA OBTENER SU TELÉFONO (Esto evita el AttributeError)
        cliente = db.query(Cliente).filter(Cliente.id_cliente == visita_in.id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # 2. VALIDACIÓN DE LISTA NEGRA
        if cliente.telefono:
            tel_limpio = "".join(filter(str.isdigit, cliente.telefono))
            bloqueado = db.query(Blacklist).filter(Blacklist.telefono == tel_limpio).first()
            
            if bloqueado:
                print(f"🚫 BLOQUEO: Intento de reserva de número bloqueado: {tel_limpio}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Lo sentimos, no es posible realizar la reserva con este número."
                )

        # 3. CREAR VISITA (efectivo confirmado al instante; MP queda pendiente hasta el pago)
        visita, init_point = crud_v.create_visita(db, visita_in)

        out = visita_to_out(visita)
        if init_point:
            out["init_point"] = init_point
            out["public_key"] = os.getenv("MERCADOPAGO_PUBLIC_KEY", "").strip()
        elif visita.estado == "CONFIRMADO" and visita.cliente and visita.cliente.email:
            background_tasks.add_task(
                enviar_email_confirmacion,
                visita.cliente.email,
                "✅ Turno confirmado - King Barber",
                generar_email_confirmacion(visita),
            )

        return out

    except HTTPException as he:
        raise he
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ======================================================================================
# CANCELAR VISITA
# ======================================================================================

@router.post("/{visita_id}/cancelar", status_code=status.HTTP_200_OK)
def cancelar_visita(
    visita_id: int,
    background_tasks: BackgroundTasks,
    staff=Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    from crud import visita as crud_v
    visita = crud_v.get_visita_by_id(db, visita_id)
    if not visita:
        raise HTTPException(status_code=404, detail="Visita no encontrada")

    # Evitar re-cancelar y reenviar notificaciones
    if str(visita.estado).upper() == "CANCELADO":
        return {"ok": True, "message": "El turno ya estaba cancelado"}

    visita.estado = "CANCELADO"
    db.commit()
    db.refresh(visita)

    # Notificaciones
    if visita.cliente and visita.cliente.email:
        background_tasks.add_task(enviar_email_confirmacion, visita.cliente.email, "❌ Turno cancelado", generar_email_cancelacion(visita))
    
    if visita.cliente and visita.cliente.telefono:
        background_tasks.add_task(
            enviar_cancelacion_whatsapp,
            telefono_cliente=visita.cliente.telefono,
            nombre_cliente=visita.cliente.nombre,
            servicio=visita.servicio.nombre if visita.servicio else "Servicio",
            fecha_hora_str=visita.fecha_hora.strftime("%d/%m a las %H:%M")
        )

    return {"ok": True}

# ======================================================================================
# OTROS (PATCH, GET BY ID, LISTAR)
# ======================================================================================

@router.patch("/{visita_id}/estado", response_model=VisitaOut)
def actualizar_estado_visita(
    visita_id: int,
    data: VisitaUpdate,
    staff=Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    from crud import visita as crud_v
    try:
        visita = crud_v.update_estado_visita(db, visita_id, data.estado)
        return visita_to_out(visita)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{visita_id}", response_model=VisitaOut)
def obtener_visita(
    visita_id: int,
    staff=Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    from crud import visita as crud_v
    visita = crud_v.get_visita_by_id(db, visita_id)
    if not visita:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    return visita_to_out(visita)

@router.get("/", response_model=List[VisitaOut])
def listar_visitas(
    staff=Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    from crud import visita as crud_v
    crud_v.marcar_visitas_completadas(db)
    # Suponiendo que tienes un método get_visitas general en crud
    visitas = db.query(Visita).all()
    return [visita_to_out(v) for v in visitas]