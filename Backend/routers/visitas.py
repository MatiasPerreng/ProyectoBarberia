import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, time, timedelta
from calendar import monthrange

from database import get_db
# Importaciones de modelos para la lógica de validación
from models.blacklist import Blacklist
from models import Cliente, Visita # Importamos Cliente para buscar el teléfono

# Importaciones directas de archivos para evitar círculos viciosos de inicialización
from schemas.visita import VisitaCreate, VisitaOut, VisitaUpdate
from schemas.mercadopago import MercadoPagoAsociarLinkIn, MercadoPagoReagendarIn, MercadoPagoSyncIn
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

    medio = getattr(visita, "medio_pago", None)
    estado_pago = getattr(visita, "estado_pago", None)
    pago_tardio = bool(getattr(visita, "pago_tardio", False))
    mp_pay = getattr(visita, "mercadopago_payment_id", None)
    mp_rec = getattr(visita, "mercadopago_receipt_url", None)
    mp_sell = getattr(visita, "mercadopago_seller_activity_url", None)
    tok = getattr(visita, "token_seguimiento", None)
    estado_u = str(getattr(visita, "estado", "") or "").upper()
    # Igual criterio que pedido en Burgers: mostrar datos MP si el turno es MP o hay datos guardados
    # (evita que el front/admin reciban null aunque la fila tenga payment_id).
    mp_visible = (
        (medio or "").strip() == "mercadopago"
        or estado_u == "PENDIENTE_CONFIRMACION_MP"
        or bool(mp_pay or mp_rec or mp_sell)
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
        "estado_pago": estado_pago if mp_visible else None,
        "pago_tardio": pago_tardio if mp_visible else False,
        "mercadopago_payment_id": mp_pay if mp_visible else None,
        "mercadopago_receipt_url": mp_rec if mp_visible else None,
        "mercadopago_seller_activity_url": mp_sell if mp_visible else None,
        "mercadopago_init_point": None,
        "mercadopago_preference_id": None,
        "token_seguimiento": tok if mp_visible else None,
        "mercadopago_checkout_error": None,
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

        if not (cliente.email and str(cliente.email).strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requiere un email válido en la ficha del cliente para reservar.",
            )

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

        # 3. CREAR VISITA
        visita = crud_v.create_visita(db, visita_in)
        visita = crud_v.get_visita_by_id(db, visita.id_visita) or visita

        # 4. EMAIL DE CONFIRMACIÓN (solo turno ya confirmado; MP pendiente se confirma al pagar)
        if str(visita.estado).upper() == "CONFIRMADO" and visita.cliente and visita.cliente.email:
            background_tasks.add_task(
                enviar_email_confirmacion,
                visita.cliente.email,
                "✅ Turno confirmado - King Barber",
                generar_email_confirmacion(visita)
            )

        out = visita_to_out(visita)
        if getattr(visita_in, "medio_pago", None) == "mercadopago":
            init, pref, checkout_err = crud_v.checkout_mercadopago_para_visita(
                db,
                visita,
                frontend_return_base=getattr(visita_in, "frontend_return_base", None),
            )
            out["mercadopago_init_point"] = init
            out["mercadopago_preference_id"] = pref
            out["mercadopago_checkout_error"] = checkout_err

        return out

    except HTTPException as he:
        raise he
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("crear_visita: error no controlado")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo completar la reserva. Reintentá en unos momentos.",
        ) from e


@router.post("/mercadopago/sincronizar", response_model=VisitaOut)
def mercadopago_sincronizar(
    body: MercadoPagoSyncIn,
    db: Session = Depends(get_db),
):
    from crud import visita as crud_v

    # No llamar cancelar_visitas_mp_abandonadas aquí: si el usuario tardó en el checkout de MP,
    # cancelar pendientes antes de sincronizar podría marcar CANCELADO y romper la asociación pago–turno.

    try:
        visita, err = crud_v.sincronizar_pago_mercadopago(db, body)
    except Exception as e:
        logger.exception("MP sincronizar: error no controlado")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error al contactar Mercado Pago o guardar el turno. Reintentá en unos segundos.",
        ) from e

    if not visita:
        logger.warning("MP sincronizar visita: %s", err or "sin detalle")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err or "No se pudo sincronizar el pago.")

    return visita_to_out(visita)


@router.post("/mercadopago/asociar-link", response_model=VisitaOut)
def mercadopago_asociar_link(
    body: MercadoPagoAsociarLinkIn,
    db: Session = Depends(get_db),
):
    from crud import visita as crud_v

    visita = crud_v.asociar_pago_link_mercadopago(db, body.token_seguimiento, body.payment_id)
    return visita_to_out(visita)


@router.api_route("/mercadopago/webhook", methods=["GET", "POST"])
async def mercadopago_webhook(request: Request, db: Session = Depends(get_db)):
    from utils.mercadopago_api import webhook_secret
    from crud import visita as crud_v

    # Sin cleanup previo: el webhook debe poder asociar el pago aunque la reserva lleve varios minutos.

    sec = webhook_secret()
    if sec and request.query_params.get("s") != sec:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Webhook no autorizado")

    payment_id = None
    webhook_topic = request.query_params.get("topic") or request.query_params.get("type")
    if request.method == "GET":
        if request.query_params.get("topic") in ("payment", "merchant_order"):
            payment_id = request.query_params.get("id")
    else:
        body = None
        try:
            body = await request.json()
        except (json.JSONDecodeError, ValueError) as e:
            logger.info("Webhook MP: cuerpo no JSON (%s)", e)
        if isinstance(body, dict):
            webhook_topic = str(body.get("type") or body.get("topic") or webhook_topic or "")
            data = body.get("data")
            if isinstance(data, dict) and data.get("id") is not None:
                payment_id = str(data["id"])
            if not payment_id and body.get("id") is not None:
                payment_id = str(body["id"])

    logger.info(
        "Webhook MP recibido method=%s topic=%s payment_or_order_id=%s",
        request.method,
        webhook_topic,
        payment_id,
    )

    if payment_id:
        try:
            _v, err = crud_v.sincronizar_pago_mercadopago(
                db,
                MercadoPagoSyncIn(payment_id=str(payment_id)),
                confirmar_aprobado=True,
                origen="webhook",
            )
            if _v:
                logger.info(
                    "Webhook MP: visita sincronizada id_visita=%s payment_id=%s estado=%s estado_pago=%s",
                    _v.id_visita,
                    getattr(_v, "mercadopago_payment_id", None),
                    getattr(_v, "estado", None),
                    getattr(_v, "estado_pago", None),
                )
            elif err:
                logger.warning("Webhook MP: no se actualizó visita (%s)", err)
        except Exception:
            logger.exception("Webhook MP: error al sincronizar payment_id=%s", payment_id)
    else:
        logger.debug("Webhook MP: sin payment_id (GET/POST)")

    return {"received": True}


@router.get("/reagendar")
def mercadopago_reagendar_info(
    token: str,
    fecha: Optional[date] = None,
    id_barbero: Optional[int] = None,
    db: Session = Depends(get_db),
):
    from crud import visita as crud_v

    return crud_v.obtener_info_reagendar_mp(db, token, fecha=fecha, id_barbero=id_barbero)


@router.post("/reagendar", response_model=VisitaOut)
def mercadopago_reagendar_confirmar(
    body: MercadoPagoReagendarIn,
    db: Session = Depends(get_db),
):
    from crud import visita as crud_v

    visita = crud_v.reagendar_visita_mp_con_pago_existente(
        db,
        token=body.token,
        fecha_hora=body.fecha_hora,
        id_barbero=body.id_barbero,
    )
    return visita_to_out(visita)


@router.get("/seguimiento/{token}", response_model=VisitaOut)
def seguimiento_por_token(token: str, db: Session = Depends(get_db)):
    from crud import visita as crud_v

    visita = crud_v.obtener_visita_por_token(db, token)
    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enlace inválido o turno no encontrado",
        )
    return visita_to_out(visita)

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