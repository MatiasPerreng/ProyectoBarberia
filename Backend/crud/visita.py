from sqlalchemy.orm import Session, joinedload
from typing import Optional
from datetime import datetime, timedelta, time, date
import random

from models import Visita, Servicio, HorarioBarbero, Barbero
from schemas import VisitaCreate


# ======================================================================================
# UTILIDADES
# ======================================================================================

def overlaps(inicio_a: datetime, fin_a: datetime, inicio_b: datetime, fin_b: datetime) -> bool:
    return inicio_a < fin_b and fin_a > inicio_b


def generar_slots(hora_desde: time, hora_hasta: time, duracion_min: int):
    slots = []
    paso = timedelta(minutes=30)
    duracion = timedelta(minutes=duracion_min)

    actual = datetime.combine(date.today(), hora_desde)
    fin_jornada = datetime.combine(date.today(), hora_hasta)

    while actual + duracion <= fin_jornada:
        slots.append(actual.time())
        actual += paso

    return slots


# ======================================================================================
# 🔥 AUTO-COMPLETAR VISITAS
# ======================================================================================

def marcar_visitas_completadas(db: Session) -> None:
    ahora = datetime.now()

    visitas = (
        db.query(Visita)
        .options(joinedload(Visita.servicio))
        .filter(Visita.estado == "CONFIRMADO")
        .all()
    )

    for v in visitas:
        if not v.servicio:
            continue

        fin_turno = v.fecha_hora + timedelta(minutes=v.servicio.duracion_min)

        if fin_turno <= ahora:
            v.estado = "COMPLETADO"

    db.commit()


# ======================================================================================
# VALIDACIÓN ANTI-SPAM
# ======================================================================================

def cliente_tiene_turno_en_dia(db: Session, cliente_id: int, fecha: date) -> bool:
    inicio = datetime.combine(fecha, time.min)
    fin = datetime.combine(fecha, time.max)

    return (
        db.query(Visita)
        .filter(
            Visita.id_cliente == cliente_id,
            Visita.fecha_hora >= inicio,
            Visita.fecha_hora <= fin,
            Visita.estado == "CONFIRMADO"
        )
        .first()
        is not None
    )


# ======================================================================================
# ASIGNACIÓN AUTOMÁTICA DE BARBERO
# ======================================================================================

def asignar_barbero_automatico(
    db: Session,
    fecha_hora: datetime,
    duracion_min: int
) -> Optional[int]:

    fecha = fecha_hora.date()
    hora_str = fecha_hora.strftime("%H:%M")

    inicio = datetime.combine(fecha, time.min)
    fin = datetime.combine(fecha, time.max)

    candidatos = []

    for barbero in db.query(Barbero).all():
        disponibilidad = get_disponibilidad(
            db=db,
            fecha=fecha,
            id_servicio=None,
            id_barbero=barbero.id_barbero,
            duracion_override=duracion_min
        )

        if hora_str not in disponibilidad["turnos"]:
            continue

        turnos = (
            db.query(Visita)
            .filter(
                Visita.id_barbero == barbero.id_barbero,
                Visita.fecha_hora >= inicio,
                Visita.fecha_hora <= fin,
                Visita.estado == "CONFIRMADO"
            )
            .count()
        )

        candidatos.append((barbero.id_barbero, turnos))

    if not candidatos:
        return None

    min_turnos = min(t[1] for t in candidatos)
    menos_cargados = [idb for idb, t in candidatos if t == min_turnos]

    return random.choice(menos_cargados)


# ======================================================================================
# CRUD VISITA
# ======================================================================================

def create_visita(db: Session, visita_in: VisitaCreate) -> Visita:
    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == visita_in.id_servicio
    ).first()

    if not servicio:
        raise ValueError("Servicio no existe")

    if cliente_tiene_turno_en_dia(db, visita_in.id_cliente, visita_in.fecha_hora.date()):
        raise ValueError("Ya tenés un turno reservado para ese día")

    if visita_in.id_barbero is None:
        visita_in.id_barbero = asignar_barbero_automatico(
            db,
            visita_in.fecha_hora,
            servicio.duracion_min
        )

        if not visita_in.id_barbero:
            raise ValueError("No hay barberos disponibles")

    visita = Visita(
        fecha_hora=visita_in.fecha_hora,
        id_cliente=visita_in.id_cliente,
        id_barbero=visita_in.id_barbero,
        id_servicio=visita_in.id_servicio,
        estado="CONFIRMADO"
    )

    db.add(visita)
    db.commit()
    db.refresh(visita)

    return visita


def update_estado_visita(db: Session, visita_id: int, nuevo_estado: str) -> Visita:
    visita = db.query(Visita).get(visita_id)

    if not visita:
        raise ValueError("Visita no encontrada")

    visita.estado = nuevo_estado
    db.commit()
    db.refresh(visita)

    return visita


def get_visita_by_id(db: Session, visita_id: int) -> Optional[Visita]:
    return (
        db.query(Visita)
        .options(
            joinedload(Visita.cliente),
            joinedload(Visita.servicio),
            joinedload(Visita.barbero),
        )
        .filter(Visita.id_visita == visita_id)
        .first()
    )


# ======================================================================================
# AGENDA (SOLO CONFIRMADOS)
# ======================================================================================

def get_agenda_by_barbero(
    db: Session,
    barbero_id: int,
    fecha: Optional[date] = None
):
    marcar_visitas_completadas(db)

    query = (
        db.query(Visita)
        .options(
            joinedload(Visita.cliente),
            joinedload(Visita.servicio),
        )
        .filter(
            Visita.id_barbero == barbero_id,
            Visita.estado == "CONFIRMADO"
        )
    )

    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(
            Visita.fecha_hora >= inicio,
            Visita.fecha_hora <= fin
        )

    return query.order_by(Visita.fecha_hora).all()


def get_visitas_by_barbero(
    db: Session,
    barbero_id: int,
    fecha: Optional[date] = None
):
    return get_agenda_by_barbero(db, barbero_id, fecha)


# ======================================================================================
# HISTORIAL (SOLO COMPLETADOS) 🔥 FIX
# ======================================================================================

def get_visitas_completadas(
    db: Session,
    fecha: Optional[date] = None
):
    marcar_visitas_completadas(db)

    query = (
        db.query(Visita)
        .options(
            joinedload(Visita.cliente),
            joinedload(Visita.servicio),
            joinedload(Visita.barbero),
        )
        .filter(Visita.estado == "COMPLETADO")
    )

    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(
            Visita.fecha_hora >= inicio,
            Visita.fecha_hora <= fin
        )

    return query.order_by(Visita.fecha_hora.desc()).all()


def get_visitas_completadas_por_barbero(
    db: Session,
    barbero_id: int,
    fecha: Optional[date] = None
):
    marcar_visitas_completadas(db)

    query = (
        db.query(Visita)
        .options(
            joinedload(Visita.cliente),
            joinedload(Visita.servicio),
        )
        .filter(
            Visita.estado == "COMPLETADO",
            Visita.id_barbero == barbero_id
        )
    )

    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(
            Visita.fecha_hora >= inicio,
            Visita.fecha_hora <= fin
        )

    return query.order_by(Visita.fecha_hora.desc()).all()


# ======================================================================================
# DISPONIBILIDAD
# ======================================================================================

def get_disponibilidad(
    db: Session,
    fecha: date,
    id_servicio: Optional[int],
    id_barbero: Optional[int] = None,
    duracion_override: Optional[int] = None
):

    if duracion_override:
        duracion = duracion_override
    else:
        servicio = db.query(Servicio).filter(
            Servicio.id_servicio == id_servicio
        ).first()

        if not servicio:
            raise ValueError("Servicio no existe")

        duracion = servicio.duracion_min

    dia_semana = fecha.isoweekday()

    q_horarios = db.query(HorarioBarbero).filter(
        HorarioBarbero.dia_semana == dia_semana,
        HorarioBarbero.fecha_desde <= fecha,
        HorarioBarbero.fecha_hasta >= fecha
    )

    if id_barbero:
        q_horarios = q_horarios.filter(
            HorarioBarbero.id_barbero == id_barbero
        )

    horarios_laborales = q_horarios.all()

    if not horarios_laborales:
        return {"fecha": fecha, "turnos": []}

    inicio_dia = datetime.combine(fecha, time.min)
    fin_dia = datetime.combine(fecha, time.max)

    q_visitas = db.query(Visita).filter(
        Visita.fecha_hora >= inicio_dia,
        Visita.fecha_hora <= fin_dia,
        Visita.estado != "CANCELADO"
    )

    if id_barbero:
        q_visitas = q_visitas.filter(
            Visita.id_barbero == id_barbero
        )

    visitas = q_visitas.all()

    slots_disponibles = []

    for horario in horarios_laborales:
        slots = generar_slots(
            horario.hora_desde,
            horario.hora_hasta,
            duracion
        )

        for slot in slots:
            inicio_slot = datetime.combine(fecha, slot)
            fin_slot = inicio_slot + timedelta(minutes=duracion)

            conflicto = False

            for visita in visitas:
                inicio_visita = visita.fecha_hora
                fin_visita = inicio_visita + timedelta(
                    minutes=visita.servicio.duracion_min
                )

                if overlaps(inicio_slot, fin_slot, inicio_visita, fin_visita):
                    conflicto = True
                    break

            if not conflicto:
                slots_disponibles.append(slot.strftime("%H:%M"))

    return {
        "fecha": fecha,
        "turnos": sorted(set(slots_disponibles))
    }
