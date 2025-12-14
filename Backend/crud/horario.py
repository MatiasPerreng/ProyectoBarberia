from sqlalchemy.orm import Session
from typing import List, Optional

from models import HorarioBarbero
from schemas import HorarioBarberoCreate

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

def get_horarios(db: Session) -> List[HorarioBarbero]:
    return db.query(HorarioBarbero).all()

#----------------------------------------------------------------------------------------------------------------------

def get_horarios_by_barbero(db: Session, barbero_id: int) -> List[HorarioBarbero]:
    return (
        db.query(HorarioBarbero)
        .filter(HorarioBarbero.id_barbero == barbero_id)
        .all()
    )

#----------------------------------------------------------------------------------------------------------------------

def get_horario_by_id(db: Session, horario_id: int) -> Optional[HorarioBarbero]:
    return (
        db.query(HorarioBarbero)
        .filter(HorarioBarbero.id_horario == horario_id)
        .first()
    )

#----------------------------------------------------------------------------------------------------------------------

def delete_horario(db: Session, horario: HorarioBarbero) -> None:
    db.delete(horario)
    db.commit()

#----------------------------------------------------------------------------------------------------------------------
