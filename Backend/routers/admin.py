from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, date, time

from database import get_db
from models import Visita, Barbero

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# =====================================================================================
# DASHBOARD - MÉTRICAS GENERALES
# =====================================================================================

@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db)):
    ahora = datetime.now()
    hoy = date.today()

    inicio_hoy = datetime.combine(hoy, time.min)
    fin_hoy = datetime.combine(hoy, time.max)

    # ------------------
    # BARBEROS ACTIVOS
    # ------------------
    barberos_activos = (
        db.query(Barbero)
        .filter(Barbero.activo == True)
        .count()
    )

    # ------------------
    # TURNOS HOY (confirmados)
    # ------------------
    turnos_hoy = (
        db.query(Visita)
        .filter(
            Visita.estado.ilike("confirmado"),
            Visita.fecha_hora >= inicio_hoy,
            Visita.fecha_hora <= fin_hoy
        )
        .count()
    )

    # ------------------
    # TURNOS PENDIENTES (confirmados futuros)
    # ------------------
    turnos_pendientes = (
        db.query(Visita)
        .filter(
            Visita.estado.ilike("confirmado"),
            Visita.fecha_hora > ahora
        )
        .count()
    )

    # ------------------
    # TURNOS CANCELADOS (HISTÓRICOS)
    # ------------------
    turnos_cancelados = (
        db.query(Visita)
        .filter(Visita.estado.ilike("cancelado"))
        .count()
    )

    return {
        "barberos_activos": barberos_activos,
        "turnos_hoy": turnos_hoy,
        "turnos_pendientes": turnos_pendientes,
        "turnos_cancelados": turnos_cancelados
    }


# =====================================================================================
# DASHBOARD - LISTADO DE TURNOS (DRAWER)
# =====================================================================================

@router.get("/turnos")
def admin_turnos(
    filtro: str = Query(..., regex="^(pendientes|hoy|cancelados)$"),
    db: Session = Depends(get_db)
):
    ahora = datetime.now()
    hoy = date.today()

    query = (
        db.query(Visita)
        .join(Visita.cliente)
        .join(Visita.servicio)
        .join(Visita.barbero)
    )

    # ------------------
    # PENDIENTES (confirmados futuros)
    # ------------------
    if filtro == "pendientes":
        query = query.filter(
            Visita.estado.ilike("confirmado"),
            Visita.fecha_hora > ahora
        )

    # ------------------
    # HOY (confirmados del día)
    # ------------------
    elif filtro == "hoy":
        inicio = datetime.combine(hoy, time.min)
        fin = datetime.combine(hoy, time.max)

        query = query.filter(
            Visita.estado.ilike("confirmado"),
            Visita.fecha_hora >= inicio,
            Visita.fecha_hora <= fin
        )

    # ------------------
    # CANCELADOS (HISTÓRICOS)
    # ------------------
    elif filtro == "cancelados":
        query = query.filter(
            Visita.estado.ilike("cancelado")
        )

    turnos = query.order_by(Visita.fecha_hora.desc()).all()

    return [
        {
            "id_visita": t.id_visita,
            "fecha_hora": t.fecha_hora.strftime("%Y-%m-%d %H:%M"),
            "cliente": t.cliente.nombre,
            "servicio": t.servicio.nombre,
            "servicio_duracion": t.servicio.duracion_min,
            "barbero": t.barbero.nombre,
            "estado": t.estado.upper()
        }
        for t in turnos
    ]
