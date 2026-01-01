from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta, time, date
import random

from models import Visita, Servicio, HorarioBarbero, Barbero
from schemas import VisitaCreate


# ----------------------------------------------------------------------------------------------------------------------
# UTILIDADES
# ----------------------------------------------------------------------------------------------------------------------

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


# ----------------------------------------------------------------------------------------------------------------------
# ASIGNACIÓN AUTOMÁTICA DE BARBERO
# ----------------------------------------------------------------------------------------------------------------------

def asignar_barbero_automatico(
    db: Session,
    fecha_hora: datetime,
    duracion_min: int
) -> Optional[int]:

    fecha = fecha_hora.date()
    hora_str = fecha_hora.strftime("%H:%M")

    inicio_dia = datetime.combine(fecha, time.min)
    fin_dia = datetime.combine(fecha, time.max)

    barberos = db.query(Barbero).all()
    candidatos = []

    for barbero in barberos:
        disponibilidad = get_disponibilidad(
            db=db,
            fecha=fecha,
            id_servicio=None,
            id_barbero=barbero.id_barbero,
            duracion_override=duracion_min
        )

        if hora_str not in disponibilidad["turnos"]:
            continue

        cantidad_turnos = (
            db.query(Visita)
            .filter(
                Visita.id_barbero == barbero.id_barbero,
                Visita.fecha_hora >= inicio_dia,
                Visita.fecha_hora <= fin_dia,
                Visita.estado != "CANCELADO"
            )
            .count()
        )

        candidatos.append({
            "id_barbero": barbero.id_barbero,
            "turnos": cantidad_turnos
        })

    if not candidatos:
        return None

    min_turnos = min(c["turnos"] for c in candidatos)
    menos_cargados = [
        c["id_barbero"] for c in candidatos if c["turnos"] == min_turnos
    ]

    return random.choice(menos_cargados)


# ----------------------------------------------------------------------------------------------------------------------
# CRUD VISITA
# ----------------------------------------------------------------------------------------------------------------------

def create_visita(db: Session, visita_in: VisitaCreate) -> Visita:
    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == visita_in.id_servicio
    ).first()

    if not servicio:
        raise ValueError("Servicio no existe")

    if visita_in.id_barbero is None:
        id_auto = asignar_barbero_automatico(
            db,
            visita_in.fecha_hora,
            servicio.duracion_min
        )

        if not id_auto:
            raise ValueError("No hay barberos disponibles para ese horario")

        visita_in.id_barbero = id_auto

    inicio_nuevo = visita_in.fecha_hora
    fin_nuevo = inicio_nuevo + timedelta(minutes=servicio.duracion_min)

    inicio_dia = datetime.combine(inicio_nuevo.date(), time.min)
    fin_dia = datetime.combine(inicio_nuevo.date(), time.max)

    visitas_existentes = (
        db.query(Visita)
        .options(joinedload(Visita.servicio))
        .filter(
            Visita.id_barbero == visita_in.id_barbero,
            Visita.fecha_hora >= inicio_dia,
            Visita.fecha_hora <= fin_dia,
            Visita.estado != "CANCELADO"
        )
        .all()
    )

    for visita in visitas_existentes:
        duracion_existente = visita.servicio.duracion_min
        inicio_existente = visita.fecha_hora
        fin_existente = inicio_existente + timedelta(minutes=duracion_existente)

        if overlaps(inicio_nuevo, fin_nuevo, inicio_existente, fin_existente):
            raise ValueError("Horario no disponible")

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

    visita.cliente
    visita.servicio
    visita.barbero

    return visita


def update_estado_visita(db: Session, visita_id: int, nuevo_estado: str) -> Visita:
    visita = db.query(Visita).filter(
        Visita.id_visita == visita_id
    ).first()

    if not visita:
        raise ValueError("Visita no encontrada")

    visita.estado = nuevo_estado
    db.commit()
    db.refresh(visita)

    return visita


def get_visitas(db: Session):
    return db.query(Visita).filter(
        Visita.estado != "CANCELADO"
    ).all()


# --------------------------------------------------------------------------------------------------
# AGENDA BARBERO
# --------------------------------------------------------------------------------------------------

def get_visitas_by_barbero(
    db: Session,
    barbero_id: int,
    fecha: Optional[date] = None
):
    query = (
        db.query(Visita)
        .options(
            joinedload(Visita.cliente),
            joinedload(Visita.servicio),
        )
        .filter(
            Visita.id_barbero == barbero_id,
            Visita.estado != "CANCELADO"
        )
    )

    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)

        query = query.filter(
            Visita.fecha_hora >= inicio,
            Visita.fecha_hora <= fin
        )

    visitas = query.order_by(Visita.fecha_hora).all()

    resultado = []

    for v in visitas:
        resultado.append({
            "id_visita": v.id_visita,
            "fecha_hora": v.fecha_hora,
            "estado": v.estado,
            "created_at": v.created_at,

            "cliente_nombre": v.cliente.nombre if v.cliente else "",
            "cliente_apellido": v.cliente.apellido if v.cliente else "",
            "cliente_telefono": v.cliente.telefono if v.cliente else "",

            "servicio_nombre": v.servicio.nombre if v.servicio else "",
            "servicio_duracion": v.servicio.duracion_min if v.servicio else 0,
        })

    return resultado


def get_visita_by_id(db: Session, visita_id: int) -> Optional[Visita]:
    return db.query(Visita).filter(
        Visita.id_visita == visita_id
    ).first()


def delete_visita(db: Session, visita: Visita) -> None:
    db.delete(visita)
    db.commit()


# ----------------------------------------------------------------------------------------------------------------------
# DISPONIBILIDAD
# ----------------------------------------------------------------------------------------------------------------------

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
