from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from models import HorarioBarbero
from schemas import HorarioBarberoCreate

router = APIRouter(
    prefix="/barberos",
    tags=["Barberos"]
)
#----------------------------------------------------------------------------------------------------------------------

def create_horario(db: Session, horario_in: HorarioBarberoCreate) -> HorarioBarbero:
    horario = HorarioBarbero(
        id_barbero=horario_in.id_barbero,
        dia_semana=horario_in.dia_semana,
        hora_desde=horario_in.hora_desde,
        hora_hasta=horario_in.hora_hasta
    )

    db.add(horario)
    db.commit()
    db.refresh(horario)

    return horario

#----------------------------------------------------------------------------------------------------------------------

def get_horarios_by_barbero(db: Session, barbero_id: int) -> List[HorarioBarbero]:
    return (
        db.query(HorarioBarbero)
        .filter(HorarioBarbero.id_barbero == barbero_id)
        .all()
    )

#----------------------------------------------------------------------------------------------------------------------

def delete_horario(db: Session, horario: HorarioBarbero) -> None:
    db.delete(horario)
    db.commit()

#----------------------------------------------------------------------------------------------------------------------
