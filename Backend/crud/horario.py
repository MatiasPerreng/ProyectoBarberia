from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from models import HorarioBarbero
from schemas import HorarioBarberoCreate

# ----------------------------------------------------------------------------------------------------------------------
# CREAR HORARIO
# ----------------------------------------------------------------------------------------------------------------------

def create_horario(
    db: Session,
    horario_in: HorarioBarberoCreate
) -> HorarioBarbero:

    horario = HorarioBarbero(
        id_barbero=horario_in.id_barbero,
        dia_semana=horario_in.dia_semana,
        hora_desde=horario_in.hora_desde,
        hora_hasta=horario_in.hora_hasta,
        fecha_desde=horario_in.fecha_desde,
        fecha_hasta=horario_in.fecha_hasta,
    )

    db.add(horario)
    db.commit()
    db.refresh(horario)

    return horario

# ----------------------------------------------------------------------------------------------------------------------
# LISTAR TODOS
# ----------------------------------------------------------------------------------------------------------------------

def get_horarios(db: Session) -> List[HorarioBarbero]:
    return db.query(HorarioBarbero).all()

# ----------------------------------------------------------------------------------------------------------------------
# LISTAR POR BARBERO
# ----------------------------------------------------------------------------------------------------------------------

def get_horarios_by_barbero(
    db: Session,
    barbero_id: int
) -> List[HorarioBarbero]:

    return (
        db.query(HorarioBarbero)
        .filter(HorarioBarbero.id_barbero == barbero_id)
        .order_by(HorarioBarbero.dia_semana, HorarioBarbero.hora_desde)
        .all()
    )

# ----------------------------------------------------------------------------------------------------------------------
# OBTENER POR ID
# ----------------------------------------------------------------------------------------------------------------------

def get_horario_by_id(
    db: Session,
    horario_id: int
) -> Optional[HorarioBarbero]:

    return (
        db.query(HorarioBarbero)
        .filter(HorarioBarbero.id_horario == horario_id)
        .first()
    )

# ----------------------------------------------------------------------------------------------------------------------
# ELIMINAR
# ----------------------------------------------------------------------------------------------------------------------

def delete_horario(
    db: Session,
    horario: HorarioBarbero
) -> None:
    db.delete(horario)
    db.commit()

# ----------------------------------------------------------------------------------------------------------------------
# 🆕 HORARIOS VÁLIDOS PARA UNA FECHA (CLAVE PARA CALENDARIO)
# ----------------------------------------------------------------------------------------------------------------------

def get_horarios_barbero_para_fecha(
    db: Session,
    id_barbero: int,
    dia_semana: int,
    fecha: date
) -> List[HorarioBarbero]:
    """
    Devuelve los horarios activos de un barbero para una fecha específica
    """

    return (
        db.query(HorarioBarbero)
        .filter(
            HorarioBarbero.id_barbero == id_barbero,
            HorarioBarbero.dia_semana == dia_semana,
            HorarioBarbero.fecha_desde <= fecha,
            HorarioBarbero.fecha_hasta >= fecha,
        )
        .order_by(HorarioBarbero.hora_desde)
        .all()
    )
