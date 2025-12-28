from sqlalchemy.orm import Session
from typing import List, Optional

from models import Barbero, Visita, Cliente, Servicio
from schemas import BarberoCreate, BarberoUpdate


# ----------------------------------------------------------------------------------------------------------------------
# SERIALIZER (BLINDADO)
# ----------------------------------------------------------------------------------------------------------------------

def serialize_barbero(barbero: Barbero) -> dict:
    """
    Convierte un Barbero ORM en dict compatible con BarberoOut.
    Garantiza que foto_url NUNCA sea null.
    """
    return {
        "id_barbero": barbero.id_barbero,
        "nombre": barbero.nombre,
        "activo": barbero.activo,
        # 🔥 BLINDAJE CLAVE
        "foto_url": barbero.foto_url or "/media/barberos/default.jpg",
        "created_at": barbero.created_at,
        "tiene_usuario": barbero.login is not None
    }


# ----------------------------------------------------------------------------------------------------------------------
# BARBEROS
# ----------------------------------------------------------------------------------------------------------------------

def create_barbero(db: Session, barbero_in: BarberoCreate) -> Barbero:
    barbero = Barbero(
        nombre=barbero_in.nombre,
        activo=True,
        # 🔥 DEFAULT REAL DESDE EL BACKEND
        foto_url="/media/barberos/default.jpg"
    )

    db.add(barbero)
    db.commit()
    db.refresh(barbero)
    return barbero


def get_barberos(
    db: Session,
    solo_activos: bool = False
) -> List[dict]:
    """
    Devuelve barberos con campo calculado:
    - tiene_usuario
    - foto_url siempre válida
    """

    query = db.query(Barbero)

    if solo_activos:
        query = query.filter(Barbero.activo == True)

    barberos = query.order_by(Barbero.nombre).all()

    return [serialize_barbero(b) for b in barberos]


def get_barbero_by_id(db: Session, barbero_id: int) -> Optional[Barbero]:
    return (
        db.query(Barbero)
        .filter(Barbero.id_barbero == barbero_id)
        .first()
    )


def update_barbero(
    db: Session,
    barbero: Barbero,
    barbero_in: BarberoUpdate
) -> Barbero:

    if barbero_in.nombre is not None:
        barbero.nombre = barbero_in.nombre

    if barbero_in.foto_url is not None:
        barbero.foto_url = barbero_in.foto_url

    if barbero_in.activo is not None:
        barbero.activo = barbero_in.activo

    db.commit()
    db.refresh(barbero)
    return barbero


def toggle_barbero_estado(db: Session, barbero: Barbero) -> Barbero:
    barbero.activo = not barbero.activo
    db.commit()
    db.refresh(barbero)
    return barbero


def delete_barbero(db: Session, barbero: Barbero) -> None:
    db.delete(barbero)
    db.commit()


# ----------------------------------------------------------------------------------------------------------------------
# AGENDA DEL BARBERO (LECTURA)
# ----------------------------------------------------------------------------------------------------------------------

def get_agenda_barbero(db: Session, barbero_id: int):
    return (
        db.query(
            Visita.fecha_hora.label("fecha_hora"),
            Cliente.nombre.label("cliente_nombre"),
            Cliente.telefono.label("cliente_telefono"),
            Servicio.nombre.label("servicio_nombre"),
            Servicio.duracion_min.label("servicio_duracion"),
            Visita.estado.label("estado"),
        )
        .join(Cliente, Cliente.id_cliente == Visita.id_cliente)
        .join(Servicio, Servicio.id_servicio == Visita.id_servicio)
        .filter(Visita.id_barbero == barbero_id)
        .order_by(Visita.fecha_hora)
        .all()
    )
