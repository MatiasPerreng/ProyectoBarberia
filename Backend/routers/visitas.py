from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, time, timedelta
from calendar import monthrange

from database import get_db
import crud.visita as crud_visita
import crud.horario as crud_horario

from schemas import VisitaCreate, VisitaOut, VisitaUpdate
from core.dependencias import get_current_login_barbero
from core.email import enviar_email_confirmacion
from core.email_templates import (
    generar_email_confirmacion,
    generar_email_cancelacion,
)

# IMPORTACIÓN UNIFICADA: Importamos ambos servicios de WhatsApp
from services.whatsapp import enviar_recordatorio_whatsapp, enviar_cancelacion_whatsapp

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

        "barbero_id": visita.barbero.id_barbero if visita.barbero else None,
        "barbero_nombre": visita.barbero.nombre if visita.barbero else "",
    }

# ======================================================================================
# MI AGENDA (CONFIRMADOS FUTUROS)
# ======================================================================================

@router.get("/mi-agenda", response_model=List[VisitaOut])
def mi_agenda(
    fecha: Optional[date] = None,
    login=Depends(get_current_login_barbero),
    db: Session = Depends(get_db)
):
    crud_visita.marcar_visitas_completadas(db)

    visitas = crud_visita.get_visitas_by_barbero(
        db=db,
        barbero_id=login.barbero_id,
        fecha=fecha
    )

    return [visita_to_out(v) for v in visitas]

# ======================================================================================
# HISTORIAL (SOLO COMPLETADOS)
# ======================================================================================

@router.get("/historial", response_model=List[VisitaOut])
def historial_agenda(
    fecha: Optional[date] = None,
    login=Depends(get_current_login_barbero),
    db: Session = Depends(get_db)
):
    crud_visita.marcar_visitas_completadas(db)

    if login.role == "admin":
        visitas = crud_visita.get_visitas_completadas(
            db=db,
            fecha=fecha
        )
    else:
        visitas = crud_visita.get_visitas_completadas_por_barbero(
            db=db,
            barbero_id=login.barbero_id,
            fecha=fecha
        )

    return [visita_to_out(v) for v in visitas]

# ======================================================================================
# ACTUALIZAR ESTADO (MANUAL)
# ======================================================================================

@router.patch("/{visita_id}/estado", response_model=VisitaOut)
def actualizar_estado_visita(
    visita_id: int,
    data: VisitaUpdate,
    db: Session = Depends(get_db)
):
    try:
        visita = crud_visita.update_estado_visita(
            db, visita_id, data.estado
        )
        return visita_to_out(visita)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# ======================================================================================
# DISPONIBILIDAD POR FECHA
# ======================================================================================

@router.get("/disponibilidad")
def obtener_disponibilidad(
    fecha: date,
    id_servicio: int,
    id_barbero: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        return crud_visita.get_disponibilidad(
            db=db,
            fecha=fecha,
            id_servicio=id_servicio,
            id_barbero=id_barbero
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ======================================================================================
# DISPONIBILIDAD MENSUAL
# ======================================================================================

@router.get("/disponibilidad-mes")
def disponibilidad_mes(
    mes: int,
    anio: int,
    id_servicio: int,
    id_barbero: int,
    db: Session = Depends(get_db)
):
    hoy = obtener_hoy_local()
    _, last_day = monthrange(anio, mes)

    resultado = []

    for dia in range(1, last_day + 1):
        fecha_dia = date(anio, mes, dia)
        dia_semana = fecha_dia.isoweekday()

        if fecha_dia < hoy:
            resultado.append({
                "fecha": fecha_dia.isoformat(),
                "estado": "pasado"
            })
            continue

        horarios = crud_horario.get_horarios_barbero_para_fecha(
            db=db,
            id_barbero=id_barbero,
            dia_semana=dia_semana,
            fecha=fecha_dia
        )

        if not horarios:
            resultado.append({
                "fecha": fecha_dia.isoformat(),
                "estado": "sin_horario"
            })
            continue

        turnos = crud_visita.get_disponibilidad(
            db=db,
            fecha=fecha_dia,
            id_servicio=id_servicio,
            id_barbero=id_barbero
        )

        estado = "disponible" if len(turnos["turnos"]) > 0 else "completo"

        resultado.append({
            "fecha": fecha_dia.isoformat(),
            "estado": estado
        })

    return resultado

# ======================================================================================
# CREAR VISITA
# ======================================================================================

@router.post("/", response_model=VisitaOut, status_code=status.HTTP_201_CREATED)
def crear_visita(
    visita_in: VisitaCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        visita = crud_visita.create_visita(db, visita_in)

        # Envío de Email
        if visita.cliente and visita.cliente.email:
            background_tasks.add_task(
                enviar_email_confirmacion,
                visita.cliente.email,
                "✅ Turno confirmado - King Barber",
                generar_email_confirmacion(visita)
            )

        return visita_to_out(visita)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ======================================================================================
# CANCELAR VISITA (UNIFICADO CORREO + WHATSAPP)
# ======================================================================================

@router.post("/{visita_id}/cancelar", status_code=status.HTTP_200_OK)
def cancelar_visita(
    visita_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Logs para depuración en Uvicorn
    print(f"\n🚀 EJECUTANDO ACCIÓN DE CANCELACIÓN - ID VISITA: {visita_id}")
    
    visita = crud_visita.get_visita_by_id(db, visita_id)

    if not visita:
        print(f"❌ Error: No se encontró la visita {visita_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita no encontrada"
        )

    # 1. Captura de datos para notificaciones
    nombre_cliente = visita.cliente.nombre
    email_cliente = visita.cliente.email
    telefono_cliente = visita.cliente.telefono
    nombre_servicio = visita.servicio.nombre
    # Formato para la plantilla de WhatsApp {{3}}
    fecha_msg = visita.fecha_hora.strftime("%d/%m a las %H:%M")

    # 2. Actualizamos estado en DB
    visita.estado = "CANCELADO"
    db.commit()
    db.refresh(visita)
    print(f"💾 DB: Visita {visita_id} marcada como CANCELADA")

    # 3. Envío de Email (Background Task)
    if email_cliente:
        background_tasks.add_task(
            enviar_email_confirmacion,
            email_cliente,
            "❌ Turno cancelado - King Barber",
            generar_email_cancelacion(visita)
        )
        print(f"📧 Tarea de Email encolada para: {email_cliente}")

    # 4. Envío de WhatsApp (Background Task)
    if telefono_cliente:
        print(f"📲 Encolando WhatsApp de cancelación para {nombre_cliente} al {telefono_cliente}")
        background_tasks.add_task(
            enviar_cancelacion_whatsapp,
            telefono_cliente=telefono_cliente,
            nombre_cliente=nombre_cliente,
            servicio=nombre_servicio,
            fecha_hora_str=fecha_msg
        )

    return {"ok": True}

# ======================================================================================
# LISTAR TODAS (ADMIN)
# ======================================================================================

@router.get("/", response_model=List[VisitaOut])
def listar_visitas(db: Session = Depends(get_db)):
    crud_visita.marcar_visitas_completadas(db)
    visitas = crud_visita.get_visitas(db) if hasattr(crud_visita, 'get_visitas') else []
    return [visita_to_out(v) for v in visitas]

# ======================================================================================
# OBTENER POR ID
# ======================================================================================

@router.get("/{visita_id}", response_model=VisitaOut)
def obtener_visita(visita_id: int, db: Session = Depends(get_db)):
    visita = crud_visita.get_visita_by_id(db, visita_id)

    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita no encontrada"
        )

    return visita_to_out(visita)