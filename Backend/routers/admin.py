from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date, time
from zoneinfo import ZoneInfo # Nativo en Python 3.9+

from database import get_db
from models import Visita, Barbero, Cliente, Servicio

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# --- CONFIGURACIÓN DE HORA URUGUAY ---
# Usamos ZoneInfo para no depender de librerías externas como pytz
def get_now_uy():
    """Retorna el datetime actual de Uruguay (naive) para comparar en DB."""
    return datetime.now(ZoneInfo("America/Montevideo")).replace(tzinfo=None)

# =====================================================================================
# DASHBOARD - MÉTRICAS GENERALES
# =====================================================================================

@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db)):
    ahora = get_now_uy()
    hoy = ahora.date()

    inicio_hoy = datetime.combine(hoy, time.min)
    fin_hoy = datetime.combine(hoy, time.max)

    # Barberos Activos
    barberos_activos = db.query(Barbero).filter(Barbero.activo == True).count()

    # Turnos de hoy (Confirmados en el rango horario de UY)
    turnos_hoy = db.query(Visita).filter(
        Visita.estado.ilike("confirmado"),
        Visita.fecha_hora >= inicio_hoy,
        Visita.fecha_hora <= fin_hoy
    ).count()

    # Turnos Pendientes (A partir de este minuto exacto en UY)
    turnos_pendientes = db.query(Visita).filter(
        Visita.estado.ilike("confirmado"),
        Visita.fecha_hora > ahora
    ).count()

    # Turnos Cancelados (Total)
    turnos_cancelados = db.query(Visita).filter(
        Visita.estado.ilike("cancelado")
    ).count()

    return {
        "barberos_activos": barberos_activos,
        "turnos_hoy": turnos_hoy,
        "turnos_pendientes": turnos_pendientes,
        "turnos_cancelados": turnos_cancelados
    }

# =====================================================================================
# DASHBOARD - LISTADO DE TURNOS (DRAWER Y FILTROS)
# =====================================================================================

@router.get("/turnos")
def admin_turnos(
    filtro: str = Query(..., regex="^(pendientes|hoy|cancelados)$"),
    fecha: date | None = None, 
    db: Session = Depends(get_db)
):
    ahora = get_now_uy()
    hoy = ahora.date()

    # Query base con Joins para cargar los datos de las otras tablas
    query = (
        db.query(Visita)
        .join(Cliente)
        .join(Servicio)
        .join(Barbero)
    )

    # 1. Filtro por Calendario
    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(Visita.fecha_hora >= inicio, Visita.fecha_hora <= fin)
    
    # 2. Filtros Rápidos
    else:
        if filtro == "pendientes":
            query = query.filter(
                Visita.estado.ilike("confirmado"), 
                Visita.fecha_hora > ahora
            )
        elif filtro == "hoy":
            inicio = datetime.combine(hoy, time.min)
            fin = datetime.combine(hoy, time.max)
            query = query.filter(
                Visita.estado.ilike("confirmado"),
                Visita.fecha_hora >= inicio,
                Visita.fecha_hora <= fin
            )
        elif filtro == "cancelados":
            query = query.filter(Visita.estado.ilike("cancelado"))

    # Orden lógico según el filtro
    if filtro == "pendientes":
        turnos = query.order_by(Visita.fecha_hora.asc()).all()
    else:
        turnos = query.order_by(Visita.fecha_hora.desc()).all()

    return [
        {
            "id_visita": t.id_visita,
            "fecha_hora": t.fecha_hora.strftime("%Y-%m-%d %H:%M"),
            "cliente_nombre": t.cliente.nombre,
            "cliente_apellido": t.cliente.apellido,
            "cliente_telefono": t.cliente.telefono, # Para el WhatsApp que arreglamos
            "servicio": t.servicio.nombre,
            "servicio_duracion": t.servicio.duracion_min,
            "barbero": t.barbero.nombre,
            "estado": t.estado.upper()
        }
        for t in turnos
    ]

# =====================================================================================
# GESTIÓN DE TURNOS - ACCIONES
# =====================================================================================

@router.patch("/turnos/{id_visita}/cancelar")
def cancelar_turno_admin(id_visita: int, db: Session = Depends(get_db)):
    turno = db.query(Visita).filter(Visita.id_visita == id_visita).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    turno.estado = "cancelado"
    db.commit()
    return {"status": "success", "message": "Turno cancelado"}

@router.patch("/turnos/{id_visita}/confirmar")
def confirmar_turno_admin(id_visita: int, db: Session = Depends(get_db)):
    turno = db.query(Visita).filter(Visita.id_visita == id_visita).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    turno.estado = "confirmado"
    db.commit()
    return {"status": "success", "message": "Turno confirmado"}

# =====================================================================================
# LISTADOS AUXILIARES
# =====================================================================================

@router.get("/barberos/listado")
def admin_listar_barberos(db: Session = Depends(get_db)):
    return db.query(Barbero).all()

@router.get("/servicios/listado")
def admin_listar_servicios(db: Session = Depends(get_db)):
    return db.query(Servicio).all()