from sqlalchemy.orm import Session
from typing import List, Optional

from models import Barbero
from schemas import BarberoCreate, BarberoUpdate

#----------------------------------------------------------------------------------------------------------------------

def create_barbero(db: Session, barbero_in: BarberoCreate) -> Barbero:
    barbero = Barbero(nombre=barbero_in.nombre)

    db.add(barbero)
    db.commit()
    db.refresh(barbero)

    return barbero


def get_barberos(db: Session) -> List[Barbero]:
    return db.query(Barbero).all()

#----------------------------------------------------------------------------------------------------------------------

def get_barbero_by_id(db: Session, barbero_id: int) -> Optional[Barbero]:
    return db.query(Barbero).filter(Barbero.id_barbero == barbero_id).first()

#----------------------------------------------------------------------------------------------------------------------

def update_barbero(
    db: Session,
    barbero: Barbero,
    barbero_in: BarberoUpdate
) -> Barbero:

    if barbero_in.nombre is not None:
        barbero.nombre = barbero_in.nombre

    db.commit()
    db.refresh(barbero)

    return barbero

#----------------------------------------------------------------------------------------------------------------------

def delete_barbero(db: Session, barbero: Barbero) -> None:
    db.delete(barbero)
    db.commit()

#----------------------------------------------------------------------------------------------------------------------
