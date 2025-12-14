from sqlalchemy.orm import Session
from typing import List, Optional

from models import Visita
from schemas import VisitaCreate

#----------------------------------------------------------------------------------------------------------------------

def create_visita(db: Session, visita_in: VisitaCreate) -> Visita:
    visita = Visita(
        fecha_hora=visita_in.fecha_hora,
        id_cliente=visita_in.id_cliente,
        id_barbero=visita_in.id_barbero,
        id_servicio=visita_in.id_servicio
    )

    db.add(visita)
    db.commit()
    db.refresh(visita)

    return visita

#----------------------------------------------------------------------------------------------------------------------

def get_visitas(db: Session) -> List[Visita]:
    return db.query(Visita).all()

#----------------------------------------------------------------------------------------------------------------------

def get_visitas_by_barbero(db: Session, barbero_id: int) -> List[Visita]:
    return db.query(Visita).filter(Visita.id_barbero == barbero_id).all()

#----------------------------------------------------------------------------------------------------------------------

def get_visita_by_id(db: Session, visita_id: int) -> Optional[Visita]:
    return db.query(Visita).filter(Visita.id_visita == visita_id).first()

#----------------------------------------------------------------------------------------------------------------------

def delete_visita(db: Session, visita: Visita) -> None:
    db.delete(visita)
    db.commit()

#----------------------------------------------------------------------------------------------------------------------
