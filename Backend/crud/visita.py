import logging
import random
import secrets
from datetime import datetime, timedelta, time, date
from typing import Any, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

logger = logging.getLogger(__name__)

from models import Visita, Servicio, HorarioBarbero, Barbero, Cliente
from schemas import VisitaCreate

# ======================================================================================
# CONFIGURACIÓN DE HORA LOCAL (URUGUAY UTC-3)
# ======================================================================================

def obtener_ahora_local() -> datetime:
    """Calcula la hora de Uruguay basándose en UTC (Servidor - 3 horas)."""
    return datetime.utcnow() - timedelta(hours=3)

def obtener_hoy_local() -> date:
    """Retorna la fecha actual de Uruguay."""
    return obtener_ahora_local().date()

# ======================================================================================
# UTILIDADES Y VALIDACIONES
# ======================================================================================

def overlaps(inicio_a: datetime, fin_a: datetime, inicio_b: datetime, fin_b: datetime) -> bool:
    """Detecta si dos rangos de tiempo se solapan."""
    return inicio_a < fin_b and fin_a > inicio_b

def validar_conflicto_descanso(inicio_slot: datetime, duracion_min: int, inicio_desc_str: Optional[str], fin_desc_str: Optional[str]) -> bool:
    """Verifica si el servicio invade el horario de descanso."""
    if not inicio_desc_str or not fin_desc_str:
        return False
    try:
        fecha = inicio_slot.date()
        desc_inicio = datetime.combine(fecha, datetime.strptime(inicio_desc_str, "%H:%M").time())
        desc_fin = datetime.combine(fecha, datetime.strptime(fin_desc_str, "%H:%M").time())
        fin_slot = inicio_slot + timedelta(minutes=duracion_min)
        return overlaps(inicio_slot, fin_slot, desc_inicio, desc_fin)
    except:
        return False

def generar_slots(hora_desde: time, hora_hasta: time, duracion_min: int):
    """Genera los espacios de turnos disponibles."""
    slots = []
    paso = timedelta(minutes=45)
    duracion = timedelta(minutes=duracion_min)
    hoy = obtener_hoy_local()
    actual = datetime.combine(hoy, hora_desde)
    fin_jornada = datetime.combine(hoy, hora_hasta)

    while actual + duracion <= fin_jornada:
        slots.append(actual.time())
        actual += paso
    return slots

# ======================================================================================
# 🔥 LÓGICA DE NEGOCIO: AUTO-COMPLETAR Y ANTI-SPAM
# ======================================================================================

def cancelar_visitas_mp_expiradas(db: Session) -> int:
    """
    Pasa a CANCELADO las visitas PENDIENTE_CONFIRMACION_MP cuyo created_at en MySQL
    es anterior a NOW() - N minutos (MERCADOPAGO_PREFERENCE_EXPIRATION_MINUTES, default 10).

    La comparación usa DATE_SUB(NOW(), ...) (mismo reloj que la columna).
    El INTERVAL va con minutos literales (entero acotado): algunos drivers no enlazan bien :m dentro de INTERVAL.
    Siempre se hace commit tras el UPDATE: en casos raros rowcount llega 0 aunque hubo cambios y sin commit el close() de la sesión hacía rollback.
    """
    from utils.mercadopago_api import preference_expiration_minutes

    minutes = int(preference_expiration_minutes())
    if minutes < 1 or minutes > 120:
        minutes = 10

    where_sql = (
        "estado = 'PENDIENTE_CONFIRMACION_MP' "
        "AND created_at IS NOT NULL "
        f"AND created_at < DATE_SUB(NOW(), INTERVAL {minutes} MINUTE)"
    )

    r = db.execute(text(f"UPDATE visita SET estado = 'CANCELADO' WHERE {where_sql}"))
    n = r.rowcount
    if n is None or n < 0:
        n = 0

    db.commit()
    db.expire_all()
    return int(n)


def check_payment_timeout(db: Session) -> int:
    """Alias de la regla de negocio de expiración MP (~10 min)."""
    return cancelar_visitas_mp_expiradas(db)


def _merchant_order_implica_fin_sin_pago(order: dict[str, Any]) -> bool:
    """True si MP informa orden vencida/cerrada sin pago acreditado."""
    order_status = (order.get("order_status") or "").lower()
    status = (order.get("status") or "").lower()
    payments = order.get("payments") or []
    approved = any(
        isinstance(p, dict) and (p.get("status") or "").lower() in ("approved", "authorized")
        for p in payments
    )
    if approved or order_status == "paid":
        return False
    if order_status in ("expired",) or status in ("expired",):
        return True
    if order_status in ("cancelled", "canceled") or status in ("cancelled", "canceled"):
        return True
    if status == "closed" and not approved:
        paid = float(order.get("paid_amount") or 0)
        if paid <= 0:
            return True
    return False


def procesar_merchant_order_mp(db: Session, order: dict[str, Any]) -> bool:
    """
    Cancela visita PENDIENTE ligada por mp_preference_id cuando la merchant_order
    indica vencimiento o cierre sin pago (notificación MP).
    """
    if not _merchant_order_implica_fin_sin_pago(order):
        return False
    pref = order.get("preference_id")
    if not pref:
        return False
    visita = (
        db.query(Visita)
        .filter(
            Visita.mp_preference_id == str(pref),
            Visita.estado == "PENDIENTE_CONFIRMACION_MP",
        )
        .first()
    )
    if not visita:
        return False
    visita.estado = "CANCELADO"
    visita.mp_status = str(order.get("order_status") or order.get("status") or "expired")[:64]
    db.commit()
    return True


def marcar_visitas_completadas(db: Session) -> None:
    cancelar_visitas_mp_expiradas(db)
    ahora = obtener_ahora_local()
    visitas = db.query(Visita).options(joinedload(Visita.servicio)).filter(Visita.estado == "CONFIRMADO").all()
    for v in visitas:
        if not v.servicio: continue
        fin_turno = v.fecha_hora + timedelta(minutes=v.servicio.duracion_min)
        if fin_turno <= ahora:
            v.estado = "COMPLETADO"
    db.commit()

def cliente_tiene_limite_turnos(db: Session, cliente_id: int, fecha: date) -> bool:
    """Verifica si el cliente ya alcanzó el límite de 2 turnos CONFIRMADOS en el día."""
    inicio = datetime.combine(fecha, time.min)
    fin = datetime.combine(fecha, time.max)
    cantidad = db.query(Visita).filter(
        Visita.id_cliente == cliente_id,
        Visita.fecha_hora >= inicio,
        Visita.fecha_hora <= fin,
        Visita.estado.in_(("CONFIRMADO", "PENDIENTE_CONFIRMACION_MP")),
    ).count()
    return cantidad >= 2

# ======================================================================================
# ASIGNACIÓN Y CRUD
# ======================================================================================

def asignar_barbero_automatico(db: Session, fecha_hora: datetime, duracion_min: int) -> Optional[int]:
    fecha = fecha_hora.date()
    hora_str = fecha_hora.strftime("%H:%M")
    inicio = datetime.combine(fecha, time.min)
    fin = datetime.combine(fecha, time.max)
    candidatos = []

    for barbero in db.query(Barbero).filter(Barbero.activo == True).all():
        disponibilidad = get_disponibilidad(db, fecha, None, barbero.id_barbero, duracion_min)
        if hora_str not in disponibilidad["turnos"]: continue
        turnos = db.query(Visita).filter(
            Visita.id_barbero == barbero.id_barbero,
            Visita.fecha_hora >= inicio,
            Visita.fecha_hora <= fin,
            Visita.estado.in_(("CONFIRMADO", "PENDIENTE_CONFIRMACION_MP")),
        ).count()
        candidatos.append((barbero.id_barbero, turnos))

    if not candidatos: return None
    min_turnos = min(t[1] for t in candidatos)
    menos_cargados = [idb for idb, t in candidatos if t == min_turnos]
    return random.choice(menos_cargados)

def create_visita(db: Session, visita_in: VisitaCreate) -> Tuple[Visita, Optional[str]]:
    cancelar_visitas_mp_expiradas(db)
    servicio = db.query(Servicio).filter(Servicio.id_servicio == visita_in.id_servicio).first()
    if not servicio:
        raise ValueError("Servicio no existe")

    ahora_local = obtener_ahora_local()
    if visita_in.fecha_hora < ahora_local:
        raise ValueError("No se pueden reservar turnos en el pasado.")

    if cliente_tiene_limite_turnos(db, visita_in.id_cliente, visita_in.fecha_hora.date()):
        raise ValueError("Ya tenés 2 turnos reservados para hoy.")

    disponibilidad_actual = get_disponibilidad(
        db,
        visita_in.fecha_hora.date(),
        visita_in.id_servicio,
        visita_in.id_barbero,
    )
    hora_solicitada = visita_in.fecha_hora.strftime("%H:%M")

    if hora_solicitada not in disponibilidad_actual["turnos"]:
        raise ValueError("Lo sentimos, alguien se agendó ese turno segundos antes que vos.")

    if visita_in.id_barbero is None:
        visita_in.id_barbero = asignar_barbero_automatico(db, visita_in.fecha_hora, servicio.duracion_min)
        if not visita_in.id_barbero:
            raise ValueError("No hay barberos disponibles")

    medio = (visita_in.medio_pago or "efectivo").lower()
    if medio == "mercadopago":
        estado = "PENDIENTE_CONFIRMACION_MP"
        medio_col = "MERCADOPAGO"
        token_seg = secrets.token_urlsafe(32)
    else:
        estado = "CONFIRMADO"
        medio_col = "EFECTIVO"
        token_seg = None

    visita = Visita(
        fecha_hora=visita_in.fecha_hora,
        id_cliente=visita_in.id_cliente,
        id_barbero=visita_in.id_barbero,
        id_servicio=visita_in.id_servicio,
        precio_al_reservar=servicio.precio,
        estado=estado,
        medio_pago=medio_col,
        token_seguimiento=token_seg,
    )
    db.add(visita)
    init_point: Optional[str] = None

    if estado == "PENDIENTE_CONFIRMACION_MP":
        db.flush()
        cliente = db.query(Cliente).filter(Cliente.id_cliente == visita_in.id_cliente).first()
        payer_email = (cliente.email or "").strip() if cliente and cliente.email else None
        precio = float(servicio.precio) if servicio.precio is not None else 0.0
        from utils import mercadopago_api as mp

        pref = mp.create_checkout_preference(
            id_visita=visita.id_visita,
            title=f"Turno — {servicio.nombre}",
            unit_price=precio,
            payer_email=payer_email or None,
            token_seguimiento=token_seg or "",
            expiration_minutes=mp.preference_expiration_minutes(),
        )
        visita.mp_preference_id = pref["id"]
        init_point = pref["init_point"]

    db.commit()
    db.refresh(visita)
    return visita, init_point


def _otro_turno_activo_solapa(db: Session, visita: Visita) -> bool:
    """True si ya hay otra visita (no cancelada) del mismo barbero que solapa en el tiempo con esta."""
    if visita.id_barbero is None or visita.fecha_hora is None:
        return False
    inicio = visita.fecha_hora
    dur = visita.servicio.duracion_min if visita.servicio else 45
    fin = inicio + timedelta(minutes=dur)
    otros = (
        db.query(Visita)
        .options(joinedload(Visita.servicio))
        .filter(
            Visita.id_barbero == visita.id_barbero,
            Visita.id_visita != visita.id_visita,
            Visita.estado.in_(("CONFIRMADO", "PENDIENTE_CONFIRMACION_MP")),
        )
        .all()
    )
    for o in otros:
        od = o.servicio.duracion_min if o.servicio else 45
        o_fin = o.fecha_hora + timedelta(minutes=od)
        if overlaps(inicio, fin, o.fecha_hora, o_fin):
            return True
    return False


def get_visita_por_token(db: Session, token: str) -> Optional[Visita]:
    cancelar_visitas_mp_expiradas(db)
    db.expire_all()
    return (
        db.query(Visita)
        .options(joinedload(Visita.cliente), joinedload(Visita.servicio), joinedload(Visita.barbero))
        .filter(Visita.token_seguimiento == token)
        .first()
    )


def aplicar_pago_mercadopago(db: Session, visita: Visita, payment_data: dict[str, Any]) -> bool:
    """
    Actualiza la visita según el pago de MP.
    Devuelve True si conviene enviar email de confirmación (pasó a CONFIRMADO desde pendiente o reactivación tras timeout).
    """
    ext = payment_data.get("external_reference")
    if ext is not None and str(ext) != str(visita.id_visita):
        raise ValueError("external_reference no coincide con la visita")

    prev = visita.estado
    status = (payment_data.get("status") or "").lower()
    detail = (payment_data.get("status_detail") or "").lower()
    pid = payment_data.get("id")
    pid_str = str(pid) if pid is not None else None

    if status in ("approved", "authorized"):
        if visita.estado == "PENDIENTE_CONFIRMACION_MP":
            visita.estado = "CONFIRMADO"
        elif (
            visita.estado == "CANCELADO"
            and (visita.medio_pago or "").upper() == "MERCADOPAGO"
        ):
            # Pago acreditado después de cancelar por tiempo de MP: reactivar si el hueco sigue libre
            if not _otro_turno_activo_solapa(db, visita):
                visita.estado = "CONFIRMADO"
            else:
                logger.warning(
                    "MP pago approved pero visita %s sigue CANCELADO: slot ocupado por otro turno; revisar manualmente.",
                    visita.id_visita,
                )
        if pid_str:
            visita.mp_payment_id = pid_str
        visita.mp_status = status
    elif status in ("rejected", "cancelled", "canceled", "refunded", "charged_back", "expired") or (
        "expired" in detail
    ):
        if visita.estado == "PENDIENTE_CONFIRMACION_MP":
            visita.estado = "CANCELADO"
        if pid_str:
            visita.mp_payment_id = pid_str
        visita.mp_status = status or (detail[:64] if detail else visita.mp_status)
    else:
        if pid_str:
            visita.mp_payment_id = pid_str
        visita.mp_status = status or visita.mp_status

    db.commit()
    db.refresh(visita)
    return visita.estado == "CONFIRMADO" and prev in ("PENDIENTE_CONFIRMACION_MP", "CANCELADO")

def update_estado_visita(db: Session, visita_id: int, nuevo_estado: str) -> Visita:
    visita = db.query(Visita).get(visita_id)
    if not visita: raise ValueError("Visita no encontrada")
    visita.estado = nuevo_estado
    db.commit()
    db.refresh(visita)
    return visita

def get_visita_by_id(db: Session, visita_id: int) -> Optional[Visita]:
    return (
        db.query(Visita)
        .options(joinedload(Visita.cliente), joinedload(Visita.servicio), joinedload(Visita.barbero))
        .filter(Visita.id_visita == visita_id)
        .first()
    )

def get_agenda_by_barbero(db: Session, barbero_id: int, fecha: Optional[date] = None):
    marcar_visitas_completadas(db)
    query = (
        db.query(Visita)
        .options(joinedload(Visita.cliente), joinedload(Visita.servicio))
        .filter(Visita.id_barbero == barbero_id, Visita.estado == "CONFIRMADO")
    )
    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(Visita.fecha_hora >= inicio, Visita.fecha_hora <= fin)
    return query.order_by(Visita.fecha_hora).all()

def get_visitas_by_barbero(db: Session, barbero_id: int, fecha: Optional[date] = None):
    return get_agenda_by_barbero(db, barbero_id, fecha)

def get_visitas_completadas(db: Session, fecha: Optional[date] = None):
    marcar_visitas_completadas(db)
    query = (
        db.query(Visita)
        .options(joinedload(Visita.cliente), joinedload(Visita.servicio), joinedload(Visita.barbero))
        .filter(Visita.estado == "COMPLETADO")
    )
    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(Visita.fecha_hora >= inicio, Visita.fecha_hora <= fin)
    return query.order_by(Visita.fecha_hora.desc()).all()

def get_visitas_completadas_por_barbero(db: Session, barbero_id: int, fecha: Optional[date] = None):
    marcar_visitas_completadas(db)
    query = (
        db.query(Visita)
        .options(joinedload(Visita.cliente), joinedload(Visita.servicio))
        .filter(Visita.estado == "COMPLETADO", Visita.id_barbero == barbero_id)
    )
    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(Visita.fecha_hora >= inicio, Visita.fecha_hora <= fin)
    return query.order_by(Visita.fecha_hora.desc()).all()

def get_disponibilidad(db: Session, fecha: date, id_servicio: Optional[int], id_barbero: Optional[int] = None, duracion_override: Optional[int] = None):
    cancelar_visitas_mp_expiradas(db)
    if duracion_override:
        duracion = duracion_override
    else:
        servicio = db.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
        if not servicio: raise ValueError("Servicio no existe")
        duracion = servicio.duracion_min

    dia_semana = fecha.isoweekday()
    q_horarios = db.query(HorarioBarbero).filter(
        HorarioBarbero.dia_semana == dia_semana,
        HorarioBarbero.fecha_desde <= fecha,
        HorarioBarbero.fecha_hasta >= fecha
    )

    if id_barbero: q_horarios = q_horarios.filter(HorarioBarbero.id_barbero == id_barbero)
    horarios_laborales = q_horarios.all()
    if not horarios_laborales: return {"fecha": fecha, "turnos": []}

    inicio_dia = datetime.combine(fecha, time.min)
    fin_dia = datetime.combine(fecha, time.max)
    q_visitas = db.query(Visita).filter(
        Visita.fecha_hora >= inicio_dia,
        Visita.fecha_hora <= fin_dia,
        Visita.estado != "CANCELADO"
    )
    if id_barbero: q_visitas = q_visitas.filter(Visita.id_barbero == id_barbero)
    visitas = q_visitas.all()

    slots_disponibles = []
    ahora_local = obtener_ahora_local()
    hoy_local = obtener_hoy_local()

    for horario in horarios_laborales:
        barbero = db.query(Barbero).get(horario.id_barbero)
        slots = generar_slots(horario.hora_desde, horario.hora_hasta, duracion)
        for slot in slots:
            inicio_slot = datetime.combine(fecha, slot)
            if fecha == hoy_local and inicio_slot < ahora_local: continue
            if barbero and validar_conflicto_descanso(inicio_slot, duracion, barbero.descanso_inicio, barbero.descanso_fin): continue
            
            fin_slot = inicio_slot + timedelta(minutes=duracion)
            conflicto = False
            visitas_del_barbero = [v for v in visitas if v.id_barbero == horario.id_barbero]
            for visita in visitas_del_barbero:
                inicio_visita = visita.fecha_hora
                v_dur = visita.servicio.duracion_min if visita.servicio else 30
                fin_visita = inicio_visita + timedelta(minutes=v_dur)
                if overlaps(inicio_slot, fin_slot, inicio_visita, fin_visita):
                    conflicto = True
                    break
            if not conflicto: slots_disponibles.append(slot.strftime("%H:%M"))

    return {"fecha": fecha, "turnos": sorted(set(slots_disponibles))}