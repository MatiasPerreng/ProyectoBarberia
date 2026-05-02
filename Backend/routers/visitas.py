import os
import logging

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import date, datetime, time, timedelta
from calendar import monthrange

from database import get_db
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


@router.post("/mercadopago/webhook")
async def mercadopago_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """IPN Mercado Pago (payment). Responder 200 rápido; MP reintenta si falla."""
    from crud import visita as crud_v
    from utils import mercadopago_api as mp

    payment_id: Optional[str] = None
    try:
        body: Any = await request.json()
    except Exception:
        body = {}

    if isinstance(body, dict):
        data = body.get("data")
        if isinstance(data, dict) and data.get("id") is not None:
            payment_id = str(data.get("id"))
        if not payment_id and isinstance(body.get("resource"), str):
            res = body["resource"]
            if "/payments/" in res:
                payment_id = res.rstrip("/").split("/")[-1]

    if not payment_id:
        payment_id = request.query_params.get("data.id") or request.query_params.get("id")

    if not payment_id:
        return {"ok": True, "ignored": True}

    try:
        pdata = mp.get_payment(payment_id)
        vid = pdata.get("external_reference")
        if not vid:
            return {"ok": True}
        visita = crud_v.get_visita_by_id(db, int(vid))
        if not visita:
            return {"ok": True}
        enviar_mail = crud_v.aplicar_pago_mercadopago(db, visita, pdata)
        visita = crud_v.get_visita_by_id(db, visita.id_visita)
        if enviar_mail and visita and visita.cliente and visita.cliente.email:
            background_tasks.add_task(
                enviar_email_confirmacion,
                visita.cliente.email,
                "✅ Turno confirmado - King Barber",
                generar_email_confirmacion(visita),
            )
    except Exception:
        logger.exception("Webhook MP no procesado payment_id=%s", payment_id)
    return {"ok": True}


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