"""
Estadísticas de ganancias - trazabilidad de dinero ganado.
Barbero: solo sus ganancias.
Admin: total de todos los barberos (puede filtrar por barbero).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import Optional, List

from database import get_db
from core.dependencias import get_current_staff
from models import Visita, Servicio

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])


def get_now_uy():
    """Fecha/hora Uruguay. Usa zoneinfo si está disponible, sino UTC."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Montevideo")).replace(tzinfo=None)
    except Exception:
        return datetime.now()


def _query_ganancias(db: Session, id_barbero: Optional[int], desde: date, hasta: date):
    """Base query: visitas COMPLETADAS con precio congelado al reservar (fallback: precio actual del servicio)."""
    q = (
        db.query(
            Visita.fecha_hora,
            Visita.id_barbero,
            func.coalesce(Visita.precio_al_reservar, Servicio.precio, 0).label("precio"),
        )
        .join(Servicio, Servicio.id_servicio == Visita.id_servicio)
        .filter(
            Visita.estado == "COMPLETADO",
            func.date(Visita.fecha_hora) >= desde,
            func.date(Visita.fecha_hora) <= hasta,
        )
    )
    if id_barbero is not None:
        q = q.filter(Visita.id_barbero == id_barbero)
    return q


@router.get("/ganancias")
def get_ganancias(
    desde: Optional[date] = Query(None, description="Inicio del período"),
    hasta: Optional[date] = Query(None, description="Fin del período"),
    agrupacion: str = Query("mes", regex="^(dia|mes|anio)$"),
    id_barbero: Optional[int] = Query(None, description="Solo admin: filtrar por barbero"),
    login=Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """
    Estadísticas de ganancias.
    - Barbero: solo sus datos (id_barbero ignorado).
    - Admin: total general o filtrado por id_barbero.
    """
    now = get_now_uy()
    hoy = now.date()

    # Default: últimos 12 meses
    if hasta is None:
        hasta = hoy
    if desde is None:
        if agrupacion == "dia":
            desde = hasta - timedelta(days=30)
        elif agrupacion == "mes":
            desde = hasta - timedelta(days=365)
        else:
            desde = date(hasta.year - 2, 1, 1)

    # Barbero: solo sus datos. Admin: todos o filtro por id_barbero.
    filtro_barbero = login.barbero_id if login.role == "barbero" else id_barbero

    # Obtener todas las visitas completadas en el rango
    rows = (
        _query_ganancias(db, filtro_barbero, desde, hasta)
        .all()
    )

    # Agrupar y sumar
    grupos = {}
    for r in rows:
        fh = r.fecha_hora
        if isinstance(fh, datetime):
            fh = fh.date() if hasattr(fh, "date") else fh
        precio = float(r.precio) if r.precio is not None else 0

        if agrupacion == "dia":
            key = str(fh)
        elif agrupacion == "mes":
            key = f"{fh.year}-{fh.month:02d}"
        else:
            key = str(fh.year)

        if key not in grupos:
            grupos[key] = {"total": 0, "cantidad": 0}
        grupos[key]["total"] += precio
        grupos[key]["cantidad"] += 1

    # Ordenar por periodo
    por_periodo = [
        {"periodo": k, "total": round(v["total"], 2), "cantidad_turnos": v["cantidad"]}
        for k, v in sorted(grupos.items())
    ]

    # Resumen rápido
    rows_hoy = _query_ganancias(db, filtro_barbero, hoy, hoy).all()
    rows_mes = _query_ganancias(
        db, filtro_barbero, date(hoy.year, hoy.month, 1), hoy
    ).all()
    rows_anio = _query_ganancias(
        db, filtro_barbero, date(hoy.year, 1, 1), hoy
    ).all()

    total_hoy = sum(float(r.precio or 0) for r in rows_hoy)
    total_mes = sum(float(r.precio or 0) for r in rows_mes)
    total_anio = sum(float(r.precio or 0) for r in rows_anio)

    return {
        "resumen": {
            "hoy": round(total_hoy, 2),
            "este_mes": round(total_mes, 2),
            "este_anio": round(total_anio, 2),
        },
        "por_periodo": por_periodo,
        "total_general": round(sum(p["total"] for p in por_periodo), 2),
    }
