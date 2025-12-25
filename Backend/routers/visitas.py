from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from calendar import monthrange

from database import get_db
import crud.visita as crud_visita
import crud.horario as crud_horario

from schemas import VisitaCreate, VisitaOut, VisitaUpdate
from core.dependencias import get_current_login_barbero
from core.email import enviar_email_confirmacion
from core.email_templates import generar_email_confirmacion

router = APIRouter(
    prefix="/visitas",
    tags=["Visitas"]
)

# ----------------------------------------------------------------------------------------------------------------------
# AGENDA DEL BARBERO LOGUEADO
# ----------------------------------------------------------------------------------------------------------------------

@router.get("/mi-agenda", response_model=List[VisitaOut])
def mi_agenda(
    login=Depends(get_current_login_barbero),
    db: Session = Depends(get_db)
):
    return crud_visita.get_visitas_by_barbero(
        db=db,
        barbero_id=login.id_barbero
    )

# ----------------------------------------------------------------------------------------------------------------------
# ACTUALIZAR ESTADO
# ----------------------------------------------------------------------------------------------------------------------

@router.patch("/{visita_id}/estado", response_model=VisitaOut)
def actualizar_estado_visita(
    visita_id: int,
    data: VisitaUpdate,
    db: Session = Depends(get_db)
):
    try:
        return crud_visita.update_estado_visita(
            db, visita_id, data.estado
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# ----------------------------------------------------------------------------------------------------------------------
# DISPONIBILIDAD POR FECHA (EXISTENTE - NO SE TOCA)
# ----------------------------------------------------------------------------------------------------------------------

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

# ----------------------------------------------------------------------------------------------------------------------
# 🆕 DISPONIBILIDAD MENSUAL (CALENDARIO)
# ----------------------------------------------------------------------------------------------------------------------

@router.get("/disponibilidad-mes")
def disponibilidad_mes(
    mes: int,
    anio: int,
    id_servicio: int,
    id_barbero: int,
    db: Session = Depends(get_db)
):
    hoy = date.today()
    _, last_day = monthrange(anio, mes)

    resultado = []

    for dia in range(1, last_day + 1):
        fecha_dia = date(anio, mes, dia)
        dia_semana = fecha_dia.isoweekday()  # 1 = lunes

        # 1️⃣ Día pasado
        if fecha_dia < hoy:
            resultado.append({
                "fecha": fecha_dia.isoformat(),
                "estado": "pasado"
            })
            continue

        # 2️⃣ Ver si el barbero trabaja ese día
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

        # 3️⃣ Ver si existen slots disponibles
        turnos = crud_visita.get_disponibilidad(
            db=db,
            fecha=fecha_dia,
            id_servicio=id_servicio,
            id_barbero=id_barbero
        )

        estado = "disponible" if len(turnos) > 0 else "completo"

        resultado.append({
            "fecha": fecha_dia.isoformat(),
            "estado": estado
        })

    return resultado

# ----------------------------------------------------------------------------------------------------------------------
# CREAR VISITA + EMAIL
# ----------------------------------------------------------------------------------------------------------------------

@router.post(
    "/",
    response_model=VisitaOut,
    status_code=status.HTTP_201_CREATED
)
def crear_visita(
    visita_in: VisitaCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        visita = crud_visita.create_visita(db, visita_in)

        if visita.cliente.email:
            background_tasks.add_task(
                enviar_email_confirmacion,
                visita.cliente.email,
                "✅ Turno confirmado - Barbería",
                generar_email_confirmacion(visita)
            )

        return visita

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ----------------------------------------------------------------------------------------------------------------------
# LISTAR TODAS
# ----------------------------------------------------------------------------------------------------------------------

@router.get("/", response_model=List[VisitaOut])
def listar_visitas(db: Session = Depends(get_db)):
    return crud_visita.get_visitas(db)

# ----------------------------------------------------------------------------------------------------------------------
# OBTENER POR ID
# ----------------------------------------------------------------------------------------------------------------------

@router.get("/{visita_id}", response_model=VisitaOut)
def obtener_visita(visita_id: int, db: Session = Depends(get_db)):
    visita = crud_visita.get_visita_by_id(db, visita_id)

    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita no encontrada"
        )

    return visita

# ----------------------------------------------------------------------------------------------------------------------
# CANCELAR
# ----------------------------------------------------------------------------------------------------------------------

@router.delete("/{visita_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_visita(visita_id: int, db: Session = Depends(get_db)):
    visita = crud_visita.get_visita_by_id(db, visita_id)

    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita no encontrada"
        )

    crud_visita.delete_visita(db, visita)
    return None
