from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, time, date
import random

from models import Visita, Servicio, HorarioBarbero, Barbero
from schemas import VisitaCreate


#----------------------------------------------------------------------------------------------------------------------
# UTILIDADES
#----------------------------------------------------------------------------------------------------------------------

def overlaps(inicio_a: datetime, fin_a: datetime, inicio_b: datetime, fin_b: datetime) -> bool:
    """
    Devuelve True si dos rangos horarios se solapan
    """
    return inicio_a < fin_b and fin_a > inicio_b


def generar_slots(hora_desde: time, hora_hasta: time, duracion_min: int) -> List[time]:
    """
    Genera slots cada 30 minutos respetando la duración del servicio
    """
    slots = []

    paso = timedelta(minutes=30)
    duracion = timedelta(minutes=duracion_min)

    actual = datetime.combine(date.today(), hora_desde)
    fin_jornada = datetime.combine(date.today(), hora_hasta)

    while actual + duracion <= fin_jornada:
        slots.append(actual.time())
        actual += paso

    return slots

#----------------------------------------------------------------------------------------------------------------------
# ASIGNACIÓN AUTOMÁTICA DE BARBERO (MENOS TURNOS DEL DÍA)
#----------------------------------------------------------------------------------------------------------------------

def asignar_barbero_automatico(
    db: Session,
    fecha_hora: datetime,
    duracion_min: int
) -> Optional[int]:
    """
    Asigna automáticamente el barbero con MENOS turnos ese día
    (si hay empate, elige random).
    """

    fecha = fecha_hora.date()
    hora_str = fecha_hora.strftime("%H:%M")

    inicio_dia = datetime.combine(fecha, time.min)
    fin_dia = datetime.combine(fecha, time.max)

    barberos = db.query(Barbero).all()
    candidatos = []

    for barbero in barberos:
        # 1️⃣ Ver disponibilidad horaria real
        disponibilidad = get_disponibilidad(
            db=db,
            fecha=fecha,
            id_servicio=None,
            id_barbero=barbero.id_barbero,
            duracion_override=duracion_min
        )

        if hora_str not in disponibilidad["turnos"]:
            continue

        # 2️⃣ Contar turnos del barbero ese día
        cantidad_turnos = (
            db.query(Visita)
            .filter(
                Visita.id_barbero == barbero.id_barbero,
                Visita.fecha_hora >= inicio_dia,
                Visita.fecha_hora <= fin_dia
            )
            .count()
        )

        candidatos.append({
            "id_barbero": barbero.id_barbero,
            "turnos": cantidad_turnos
        })

    if not candidatos:
        return None

    # 3️⃣ Elegir el/los de menor carga
    min_turnos = min(c["turnos"] for c in candidatos)
    menos_cargados = [
        c["id_barbero"] for c in candidatos if c["turnos"] == min_turnos
    ]

    # 4️⃣ Si hay empate → random
    return random.choice(menos_cargados)

#----------------------------------------------------------------------------------------------------------------------
# CRUD VISITA
#----------------------------------------------------------------------------------------------------------------------

def create_visita(db: Session, visita_in: VisitaCreate) -> Visita:
    """
    Crea una visita validando solapamiento y asignando barbero automático si es necesario
    """

    # Obtener servicio
    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == visita_in.id_servicio
    ).first()

    if not servicio:
        raise ValueError("Servicio no existe")

    # 🟢 SIN PREFERENCIA DE BARBERO
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

    # Validar solapamiento con visitas existentes
    inicio_dia = datetime.combine(inicio_nuevo.date(), time.min)
    fin_dia = datetime.combine(inicio_nuevo.date(), time.max)

    visitas_existentes = (
        db.query(Visita)
        .filter(
            Visita.id_barbero == visita_in.id_barbero,
            Visita.fecha_hora >= inicio_dia,
            Visita.fecha_hora <= fin_dia
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
        id_servicio=visita_in.id_servicio
    )

    db.add(visita)
    db.commit()
    db.refresh(visita)

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
# DISPONIBILIDAD DE HORARIOS
#----------------------------------------------------------------------------------------------------------------------

def get_disponibilidad(
    db: Session,
    fecha: date,
    id_servicio: Optional[int],
    id_barbero: Optional[int] = None,
    duracion_override: Optional[int] = None
):
    """
    Devuelve horarios disponibles para una fecha dada.
    Permite duración override para sin preferencia de barbero.
    """

    # Duración
    if duracion_override:
        duracion = duracion_override
    else:
        servicio = db.query(Servicio).filter(
            Servicio.id_servicio == id_servicio
        ).first()

        if not servicio:
            raise ValueError("Servicio no existe")

        duracion = servicio.duracion_min

    dia_semana = fecha.isoweekday()  # 1=Lunes ... 7=Domingo

    # Horarios laborales
    q_horarios = db.query(HorarioBarbero).filter(
        HorarioBarbero.dia_semana == dia_semana
    )

    if id_barbero:
        q_horarios = q_horarios.filter(
            HorarioBarbero.id_barbero == id_barbero
        )

    horarios_laborales = q_horarios.all()

    if not horarios_laborales:
        return {"fecha": fecha, "turnos": []}

    # Visitas existentes
    inicio_dia = datetime.combine(fecha, time.min)
    fin_dia = datetime.combine(fecha, time.max)

    q_visitas = db.query(Visita).filter(
        Visita.fecha_hora >= inicio_dia,
        Visita.fecha_hora <= fin_dia
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
