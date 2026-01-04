from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta

from database import get_db
from models import Visita

router = APIRouter(prefix="/tv", tags=["TV"])


@router.get("/agenda-estado")
def agenda_estado_tv(db: Session = Depends(get_db)):
    ahora = datetime.now()
    inicio_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)

    visitas = (
        db.query(Visita)
        .options(
            joinedload(Visita.barbero),
            joinedload(Visita.servicio),
            joinedload(Visita.cliente),
        )
        .filter(
            Visita.fecha_hora >= inicio_dia,
            Visita.estado != "cancelado",
        )
        .order_by(Visita.fecha_hora.asc())
        .all()
    )

    en_curso = []
    proximos = []

    for visita in visitas:
        inicio = visita.fecha_hora
        fin = inicio + timedelta(minutes=visita.servicio.duracion_min)

        nombre_cliente = (
            f"{visita.cliente.nombre} {visita.cliente.apellido}"
            if visita.cliente.apellido
            else visita.cliente.nombre
        )

        if inicio <= ahora < fin:
            en_curso.append({
                "barbero": visita.barbero.nombre,
                "cliente": nombre_cliente,
                "servicio": visita.servicio.nombre,
            })
        elif inicio > ahora:
            proximos.append({
                "hora": visita.fecha_hora.strftime("%H:%M"),
                "cliente": nombre_cliente,
                "barbero": visita.barbero.nombre,
                "servicio": visita.servicio.nombre,
            })

    return {
        "en_curso": en_curso,
        "proximos": proximos,
    }
