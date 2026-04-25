from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime, timedelta, time, date
import decimal
import hashlib
import json
import logging
import os
import random
import secrets
import time as time_module
from pathlib import Path
from time import sleep

from fastapi import HTTPException, status
from sqlalchemy.exc import OperationalError, ProgrammingError

from models import Visita, Servicio, HorarioBarbero, Barbero
from schemas import VisitaCreate
from schemas.mercadopago import MercadoPagoSyncIn

logger = logging.getLogger(__name__)


def _agent_dbg_mp(hypothesis_id: str, location: str, message: str, data: Dict[str, Any]) -> None:
    # #region agent log
    try:
        p = Path(__file__).resolve().parents[2] / "debug-ce45ae.log"
        line = (
            json.dumps(
                {
                    "sessionId": "ce45ae",
                    "hypothesisId": hypothesis_id,
                    "location": location,
                    "message": message,
                    "data": data,
                    "timestamp": int(time_module.time() * 1000),
                    "runId": "pre-fix",
                },
                ensure_ascii=False,
            )
            + "\n"
        )
        p.open("a", encoding="utf-8").write(line)
    except Exception:
        pass
    # #endregion


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


def _hay_conflicto_turno_activo(
    db: Session,
    id_barbero: int,
    inicio_turno: datetime,
    duracion_min: int,
    excluir_id_visita: int,
) -> bool:
    """Otro turno CONFIRMADO o PENDIENTE_CONFIRMACION_MP del mismo barbero solapa con este horario."""
    # Camino rápido: mismo barbero y misma fecha_hora (otro cliente tomó exactamente ese hueco).
    misma_hora = (
        db.query(Visita.id_visita)
        .filter(Visita.id_barbero == id_barbero)
        .filter(Visita.id_visita != excluir_id_visita)
        .filter(Visita.estado.in_(("CONFIRMADO", "PENDIENTE_CONFIRMACION_MP")))
        .filter(Visita.fecha_hora == inicio_turno)
        .first()
    )
    if misma_hora:
        return True

    fin_turno = inicio_turno + timedelta(minutes=duracion_min)
    inicio_dia = datetime.combine(inicio_turno.date(), time.min)
    fin_dia = datetime.combine(inicio_turno.date(), time.max)
    otras = (
        db.query(Visita)
        .options(joinedload(Visita.servicio))
        .filter(Visita.id_barbero == id_barbero)
        .filter(Visita.fecha_hora >= inicio_dia, Visita.fecha_hora <= fin_dia)
        .filter(Visita.id_visita != excluir_id_visita)
        .filter(Visita.estado.in_(("CONFIRMADO", "PENDIENTE_CONFIRMACION_MP")))
        .all()
    )
    for v in otras:
        v_dur = v.servicio.duracion_min if v.servicio else 30
        v_inicio = v.fecha_hora
        v_fin = v_inicio + timedelta(minutes=v_dur)
        if overlaps(inicio_turno, fin_turno, v_inicio, v_fin):
            return True
    return False


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
    except Exception:
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

def _minutos_expiracion_reserva_mp() -> int:
    """Umbral para cancelar turnos MP abandonados (sin id de pago en BD). Config: MERCADOPAGO_RESERVA_MINUTOS."""
    raw = os.getenv("MERCADOPAGO_RESERVA_MINUTOS", "15").strip()
    try:
        n = int(raw)
    except ValueError:
        return 15
    return max(5, min(n, 180))


def cancelar_visitas_mp_abandonadas(db: Session) -> int:
    """
    Marca como CANCELADO las visitas que siguen en PENDIENTE_CONFIRMACION_MP pasado el umbral:
    no hubo pago **aprobado** (el estado no pasó a CONFIRMADO).

    Incluye el caso en que Mercado Pago ya creó un pago ``pending`` y guardamos ``mercadopago_payment_id``:
    si el usuario no termina de pagar, el estado sigue pendiente y aquí se cancela igual.

    Criterio de tiempo: ``created_at`` (Uruguay, ``obtener_ahora_local()`` al crear la visita) <= ahora − umbral.

    Importante: no invocar esta función inmediatamente antes de sincronizar_pago_mercadopago ni en el
    webhook de MP: un usuario puede tardar > umbral en el checkout y aún así pagar; cancelar antes
    rompería la asociación. Usar solo en disponibilidad, crear visita, marcar completadas, o el loop en background.
    """
    mins = _minutos_expiracion_reserva_mp()
    ahora_uy = obtener_ahora_local()
    cutoff = ahora_uy - timedelta(minutes=mins)
    try:
        updated = (
            db.query(Visita)
            .filter(Visita.estado == "PENDIENTE_CONFIRMACION_MP")
            .filter(or_(Visita.medio_pago == "mercadopago", Visita.medio_pago.is_(None)))
            .filter(or_(Visita.estado_pago.is_(None), Visita.estado_pago == "PENDIENTE"))
            .filter(Visita.created_at.isnot(None))
            .filter(Visita.created_at <= cutoff)
            .update({Visita.estado: "CANCELADO"}, synchronize_session=False)
        )
        if updated:
            db.commit()
            logger.info(
                "MP cleanup: canceladas %s reserva(s) pendiente(s) sin pago (>= %s min)",
                updated,
                mins,
            )
        return int(updated or 0)
    except Exception as e:
        db.rollback()
        logger.warning("MP cleanup: error (no bloquea la petición): %s", e)
        return 0


def _limite_sync_automatico_mp() -> int:
    raw = os.getenv("MERCADOPAGO_AUTO_SYNC_LIMIT", "10").strip()
    try:
        n = int(raw)
    except ValueError:
        return 10
    return max(1, min(n, 50))


def _dias_sync_automatico_mp() -> int:
    raw = os.getenv("MERCADOPAGO_AUTO_SYNC_DIAS", "2").strip()
    try:
        n = int(raw)
    except ValueError:
        return 2
    return max(1, min(n, 30))


def _visita_mp_vencida(visita: Visita) -> bool:
    if not visita.created_at:
        return False
    cutoff = obtener_ahora_local() - timedelta(minutes=_minutos_expiracion_reserva_mp())
    return visita.created_at <= cutoff


def _marcar_pago_aprobado_requiere_accion_desde_auto_sync(
    db: Session,
    id_visita: int,
    pay: dict,
) -> Optional[Visita]:
    """Registra un pago aprobado tardío sin confirmar el turno."""
    from utils import mercadopago_api as mp_api

    visita = (
        db.query(Visita)
        .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
        .filter(Visita.id_visita == id_visita)
        .with_for_update()
        .first()
    )
    if not visita:
        logger.warning("MP auto-sync: visita no encontrada para requiere_accion id=%s", id_visita)
        return None

    estado_u = str(visita.estado or "").upper()
    vencida = _visita_mp_vencida(visita)
    if estado_u == "PENDIENTE_CONFIRMACION_MP" and not vencida:
        logger.info(
            "MP auto-sync: pago aprobado visita=%s pero sigue pendiente dentro del plazo; no confirma sin webhook",
            visita.id_visita,
        )
        return None
    if estado_u != "CANCELADO" and not vencida:
        logger.info(
            "MP auto-sync: pago aprobado visita=%s estado=%s no requiere accion; no hace cambios",
            visita.id_visita,
            visita.estado,
        )
        return None

    if not _pago_mercadopago_coincide_con_visita(visita, pay):
        logger.warning("MP auto-sync: pago aprobado no coincide con visita=%s", visita.id_visita)
        return None

    pay_id_str = str(pay.get("id", "")).strip()
    if not pay_id_str:
        logger.warning("MP auto-sync: pago aprobado sin payment_id visita=%s", visita.id_visita)
        return None

    dup = (
        db.query(Visita)
        .filter(
            Visita.mercadopago_payment_id == pay_id_str,
            Visita.id_visita != visita.id_visita,
        )
        .first()
    )
    if dup:
        logger.warning(
            "MP auto-sync: payment_id aprobado ya asociado payment_id=%s visita=%s dup=%s",
            pay_id_str,
            visita.id_visita,
            dup.id_visita,
        )
        return None

    rec = mp_api.receipt_url_de_pago(pay)
    if rec:
        visita.mercadopago_receipt_url = rec
    try:
        act = mp_api.url_actividad_vendedor_desde_pago(pay)
        if act:
            visita.mercadopago_seller_activity_url = act
    except Exception as e:
        logger.warning("MP auto-sync: actividad vendedor no disponible visita=%s: %s", visita.id_visita, e)

    visita.medio_pago = "mercadopago"
    visita.mercadopago_payment_id = pay_id_str
    visita.pago_tardio = True
    visita.estado = "CANCELADO"
    visita.estado_pago = "REQUIERE_ACCION"

    db.add(visita)
    db.commit()
    db.refresh(visita)
    logger.info(
        "MP auto-sync: marcado REQUIERE_ACCION visita=%s payment_id=%s vencida=%s estado_anterior=%s",
        visita.id_visita,
        pay_id_str,
        vencida,
        estado_u,
    )

    try:
        _enviar_aviso_conflicto_horario_ocupado_y_marcar(db, visita, pay_id_str)
    except Exception as e:
        logger.exception("MP auto-sync: falló aviso email requiere_accion visita=%s: %s", visita.id_visita, e)
        db.rollback()
    try:
        _enviar_whatsapp_requiere_accion_y_marcar(db, visita)
    except Exception as e:
        logger.exception("MP auto-sync: falló WhatsApp requiere_accion visita=%s: %s", visita.id_visita, e)
        db.rollback()

    return get_visita_by_id(db, visita.id_visita) or visita


def sincronizar_visitas_mp_automaticamente(db: Session) -> int:
    """
    Respaldo automático para observar pagos no aprobados sin confirmar turnos.

    Busca en MP pagos asociados por external_reference para visitas MP pendientes o canceladas
    que aún no tienen un pago aprobado/requiere_accion guardado. Si encuentra un pago aprobado,
    solo lo loguea: la confirmación queda reservada al webhook.
    """
    from utils import mercadopago_api as mp_api

    if not mp_api.mp_token_configurado():
        return 0

    desde = obtener_ahora_local() - timedelta(days=_dias_sync_automatico_mp())
    candidatos = (
        db.query(Visita.id_visita)
        .filter(Visita.estado.in_(("PENDIENTE_CONFIRMACION_MP", "CANCELADO")))
        .filter(or_(Visita.medio_pago == "mercadopago", Visita.medio_pago.is_(None)))
        .filter(or_(Visita.estado_pago.is_(None), Visita.estado_pago == "PENDIENTE"))
        .filter(Visita.created_at.isnot(None))
        .filter(Visita.created_at >= desde)
        .order_by(Visita.created_at.desc())
        .limit(_limite_sync_automatico_mp())
        .all()
    )

    sincronizadas = 0
    for row in candidatos:
        id_visita = int(row[0])
        try:
            pay = mp_api.buscar_ultimo_pago_por_external_reference(str(id_visita))
            if not pay:
                logger.debug("MP auto-sync: sin pago para visita=%s", id_visita)
                continue
            payment_id = str(pay.get("id", "")).strip()
            logger.info(
                "MP auto-sync: pago encontrado visita=%s payment_id=%s status=%s",
                id_visita,
                payment_id or None,
                pay.get("status"),
            )
            if _pago_mp_aprobado(pay):
                logger.warning(
                    "MP auto-sync: pago aprobado detectado visita=%s payment_id=%s; evaluando requiere_accion sin confirmar",
                    id_visita,
                    payment_id or None,
                )
                visita = _marcar_pago_aprobado_requiere_accion_desde_auto_sync(db, id_visita, pay)
                if visita:
                    sincronizadas += 1
                    logger.info(
                        "MP auto-sync OK requiere_accion visita=%s payment_id=%s estado=%s estado_pago=%s",
                        visita.id_visita,
                        visita.mercadopago_payment_id,
                        visita.estado,
                        getattr(visita, "estado_pago", None),
                    )
                continue
            visita, err = sincronizar_pago_mercadopago(
                db,
                MercadoPagoSyncIn(
                    payment_id=payment_id or None,
                    external_reference=str(id_visita),
                ),
                origen="auto_sync",
            )
            if visita:
                sincronizadas += 1
                logger.info(
                    "MP auto-sync OK visita=%s payment_id=%s estado=%s estado_pago=%s",
                    visita.id_visita,
                    visita.mercadopago_payment_id,
                    visita.estado,
                    getattr(visita, "estado_pago", None),
                )
            elif err:
                logger.warning("MP auto-sync: no se pudo sincronizar visita=%s (%s)", id_visita, err)
        except Exception as e:
            logger.exception("MP auto-sync: error visita=%s: %s", id_visita, e)
            try:
                db.rollback()
            except Exception:
                pass

    return sincronizadas


def marcar_visitas_completadas(db: Session) -> None:
    cancelar_visitas_mp_abandonadas(db)
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
            Visita.estado == "CONFIRMADO"
        ).count()
        candidatos.append((barbero.id_barbero, turnos))

    if not candidatos: return None
    min_turnos = min(t[1] for t in candidatos)
    menos_cargados = [idb for idb, t in candidatos if t == min_turnos]
    return random.choice(menos_cargados)

def create_visita(db: Session, visita_in: VisitaCreate) -> Visita:
    cancelar_visitas_mp_abandonadas(db)
    servicio = db.query(Servicio).filter(Servicio.id_servicio == visita_in.id_servicio).first()
    if not servicio: raise ValueError("Servicio no existe")

    # 🔥 VALIDACIÓN: No reservar en el pasado
    ahora_local = obtener_ahora_local()
    if visita_in.fecha_hora < ahora_local:
        raise ValueError("No se pueden reservar turnos en el pasado.")

    # 🔥 VALIDACIÓN: Máximo 2 agendas por día
    if cliente_tiene_limite_turnos(db, visita_in.id_cliente, visita_in.fecha_hora.date()):
        raise ValueError("Ya tenés 2 turnos reservados para hoy.")

    # 🔥 VALIDACIÓN DE ÚLTIMO SEGUNDO: Verificar disponibilidad real antes de insertar
    disponibilidad_actual = get_disponibilidad(
        db, 
        visita_in.fecha_hora.date(), 
        visita_in.id_servicio, 
        visita_in.id_barbero
    )
    hora_solicitada = visita_in.fecha_hora.strftime("%H:%M")
    
    if hora_solicitada not in disponibilidad_actual["turnos"]:
        logger.info(
            "crear_visita: hueco ya ocupado (no es flujo MP conflicto). cliente=%s barbero=%s fecha_hora=%s",
            visita_in.id_cliente,
            visita_in.id_barbero,
            visita_in.fecha_hora,
        )
        raise ValueError("Lo sentimos, alguien se agendó ese turno segundos antes que vos.")

    if visita_in.id_barbero is None:
        visita_in.id_barbero = asignar_barbero_automatico(db, visita_in.fecha_hora, servicio.duracion_min)
        if not visita_in.id_barbero: raise ValueError("No hay barberos disponibles")

    mp = getattr(visita_in, "medio_pago", None) == "mercadopago"
    logger.info(
        "crear_visita: creando visita medio_pago=%s estado_inicial=%s estado_pago_inicial=%s cliente=%s fecha_hora=%s",
        "mercadopago" if mp else None,
        "PENDIENTE_CONFIRMACION_MP" if mp else "CONFIRMADO",
        "PENDIENTE" if mp else None,
        visita_in.id_cliente,
        visita_in.fecha_hora,
    )
    visita = Visita(
        fecha_hora=visita_in.fecha_hora,
        id_cliente=visita_in.id_cliente,
        id_barbero=visita_in.id_barbero,
        id_servicio=visita_in.id_servicio,
        precio_al_reservar=servicio.precio,
        estado="PENDIENTE_CONFIRMACION_MP" if mp else "CONFIRMADO",
        medio_pago="mercadopago" if mp else None,
        estado_pago="PENDIENTE" if mp else None,
        pago_tardio=False,
        token_seguimiento=secrets.token_urlsafe(16) if mp else None,
        # Misma hora Uruguay que usa cancelar_visitas_mp_abandonadas (no depender solo del default MySQL).
        created_at=obtener_ahora_local(),
    )
    db.add(visita)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        mp = getattr(visita_in, "medio_pago", None) == "mercadopago"
        if mp:
            _lanzar_si_falta_estado_mp_en_mysql(e)
        raise
    db.refresh(visita)
    visita = get_visita_by_id(db, visita.id_visita) or visita
    try:
        _notificar_cancelados_mp_si_nuevo_turno_ocupa_slot(db, visita)
    except Exception as e:
        logger.exception("MP: notificación conflicto tras crear visita (no bloquea la reserva): %s", e)
        try:
            db.rollback()
        except Exception:
            pass
    return visita

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
    cancelar_visitas_mp_abandonadas(db)
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


# ======================================================================================
# MERCADO PAGO
# ======================================================================================

def _lanzar_si_falta_estado_mp_en_mysql(exc: Exception) -> None:
    orig = getattr(exc, "orig", None)
    texto = f"{exc} {orig or ''}".lower()
    sospecha_enum = any(
        s in texto
        for s in (
            "truncated",
            "1265",
            "1366",
            "incorrect",
            "data truncated",
            "pendiente_confirmacion",
        )
    )
    if not sospecha_enum:
        return
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "Hay que actualizar la columna `visita.estado` y las columnas MP en MySQL. "
            "Ejecutá `Backend/sql/add_mercadopago_visita.sql` y reiniciá el backend."
        ),
    ) from exc


def _parse_id_visita_ref(raw: Optional[str]) -> Optional[int]:
    if not raw:
        return None
    s = str(raw).strip()
    if not s:
        return None
    try:
        return int(decimal.Decimal(s))
    except (decimal.InvalidOperation, ValueError, TypeError):
        try:
            return int(float(s))
        except (ValueError, TypeError):
            return None


def _monto_transaccion_mp(pay: dict) -> Optional[decimal.Decimal]:
    for key in ("transaction_amount", "total_paid_amount", "net_amount", "transaction_net_received_amount"):
        v = pay.get(key)
        if v is None:
            continue
        try:
            return decimal.Decimal(str(v)).quantize(decimal.Decimal("0.01"))
        except (decimal.InvalidOperation, ValueError, TypeError):
            continue
    td = pay.get("transaction_details")
    if isinstance(td, dict):
        for key in ("net_received_amount", "total_paid_amount", "installment_amount"):
            v = td.get(key)
            if v is None:
                continue
            try:
                return decimal.Decimal(str(v)).quantize(decimal.Decimal("0.01"))
            except (decimal.InvalidOperation, ValueError, TypeError):
                continue
    return None


def _precio_esperado_visita(visita: Visita) -> Optional[decimal.Decimal]:
    if visita.precio_al_reservar is not None:
        try:
            return decimal.Decimal(str(visita.precio_al_reservar)).quantize(decimal.Decimal("0.01"))
        except (decimal.InvalidOperation, ValueError, TypeError):
            pass
    if visita.servicio and visita.servicio.precio is not None:
        try:
            return decimal.Decimal(str(visita.servicio.precio)).quantize(decimal.Decimal("0.01"))
        except (decimal.InvalidOperation, ValueError, TypeError):
            pass
    return None


def _pago_mercadopago_coincide_con_visita(visita: Visita, pay: dict) -> bool:
    currency = (pay.get("currency_id") or "").strip().upper()
    if currency and currency != "UYU":
        logger.warning("MP moneda != UYU (visita %s): %s", visita.id_visita, currency)
        return False

    st = (pay.get("status") or "").lower()
    pay_dec = _monto_transaccion_mp(pay)
    total_q = _precio_esperado_visita(visita)

    if pay_dec is None:
        if st in ("approved", "pending", "in_process", "in_mediation"):
            return True
        return False
    if total_q is None:
        return True
    diff = abs(pay_dec - total_q)
    if pay_dec != total_q and diff > decimal.Decimal("0.02"):
        logger.warning(
            "MP monto no coincide con visita %s: MP=%s esperado=%s",
            visita.id_visita,
            pay_dec,
            total_q,
        )
        return False
    return True


def _mysql_columna_mp_opcional_falta(exc: Exception) -> bool:
    """Columnas MP opcionales no migradas (1054) — mismo criterio amplio que en Burgers/pedido."""
    texto = f"{exc} {getattr(exc, 'orig', '')}".lower()
    if "mercadopago_" in texto and "unknown column" in texto:
        return True
    return "1054" in texto and "unknown column" in texto


def _pago_mp_aprobado(pay: dict) -> bool:
    st = (pay.get("status") or "").strip().lower()
    return st == "approved"


def _pago_mp_pendiente(pay: dict) -> bool:
    st = (pay.get("status") or "").strip().lower()
    return st in ("pending", "in_process", "in_mediation")


def _enviar_aviso_conflicto_horario_ocupado_y_marcar(
    db: Session,
    visita: Visita,
    payment_id: str,
) -> None:
    """Envía el mail de conflicto MP y persiste mp_conflicto_aviso_enviado para no duplicar."""
    if getattr(visita, "mp_conflicto_aviso_enviado", False):
        logger.info("MP conflicto: aviso ya enviado (omitido) visita=%s", visita.id_visita)
        return
    from services.mp_conflicto_notificacion import enviar_aviso_pago_horario_ocupado_sync

    enviar_aviso_pago_horario_ocupado_sync(visita, payment_id)
    visita.mp_conflicto_aviso_enviado = True
    db.add(visita)
    db.commit()


def _horas_expiracion_reagendar_mp() -> int:
    raw = os.getenv("MERCADOPAGO_REAGENDAR_TOKEN_HORAS", "24").strip()
    try:
        n = int(raw)
    except ValueError:
        return 24
    return max(1, min(n, 168))


def _hash_token_reagendar(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _generar_token_reagendar(visita: Visita) -> str:
    token = secrets.token_urlsafe(32)
    visita.reagendar_token_hash = _hash_token_reagendar(token)
    visita.reagendar_token_expires_at = obtener_ahora_local() + timedelta(hours=_horas_expiracion_reagendar_mp())
    visita.reagendar_token_used_at = None
    return token


def _link_reagendar_mp(token: str) -> str:
    from utils import mercadopago_api as mp_api

    base = mp_api.frontend_base_url().rstrip("/")
    path = os.getenv("MERCADOPAGO_REAGENDAR_PATH", "/reagendar").strip() or "/reagendar"
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{base}{path}?token={token}"


def _enviar_whatsapp_requiere_accion_y_marcar(
    db: Session,
    visita: Visita,
) -> None:
    """Genera link one-time y avisa por WhatsApp que el pago tardío requiere re-agendar."""
    if getattr(visita, "mp_reagendar_aviso_enviado", False):
        logger.info("MP reagendar: WhatsApp ya enviado (omitido) visita=%s", visita.id_visita)
        return
    if not visita.cliente or not getattr(visita.cliente, "telefono", None):
        logger.warning("MP reagendar: sin teléfono, no se envía WhatsApp visita=%s", visita.id_visita)
        return

    token = _generar_token_reagendar(visita)
    link = _link_reagendar_mp(token)

    from services.whatsapp import enviar_pago_tardio_reagendar_whatsapp

    nombre = f"{visita.cliente.nombre or ''} {getattr(visita.cliente, 'apellido', None) or ''}".strip()
    resp = enviar_pago_tardio_reagendar_whatsapp(visita.cliente.telefono, nombre, link)
    if resp is None:
        return

    visita.mp_reagendar_aviso_enviado = True
    db.add(visita)
    db.commit()
    logger.info("MP reagendar: WhatsApp enviado visita=%s", visita.id_visita)


def _notificar_cancelados_mp_si_nuevo_turno_ocupa_slot(db: Session, visita_nueva: Visita) -> None:
    """
    Cuando una reserva CONFIRMADA / PENDIENTE_MP ocupa un horario, revisa turnos CANCELADO (MP)
    solapados: si en Mercado Pago ya hay pago aprobado para ese id_visita y la sync no corrió,
    envía el mismo aviso por correo (no depende de POST /mercadopago/sincronizar).
    """
    from utils import mercadopago_api as mp_api

    if not mp_api.mp_token_configurado():
        return
    st_n = str(visita_nueva.estado or "").upper()
    if st_n not in ("CONFIRMADO", "PENDIENTE_CONFIRMACION_MP"):
        return
    if not visita_nueva.servicio:
        return

    inicio_n = visita_nueva.fecha_hora
    dur_n = visita_nueva.servicio.duracion_min
    fin_n = inicio_n + timedelta(minutes=dur_n)
    inicio_dia = datetime.combine(inicio_n.date(), time.min)
    fin_dia = datetime.combine(inicio_n.date(), time.max)

    cancelados = (
        db.query(Visita)
        .options(joinedload(Visita.servicio), joinedload(Visita.cliente))
        .filter(Visita.id_barbero == visita_nueva.id_barbero)
        .filter(Visita.estado == "CANCELADO")
        .filter(Visita.id_visita != visita_nueva.id_visita)
        .filter(Visita.fecha_hora >= inicio_dia, Visita.fecha_hora <= fin_dia)
        .filter(or_(Visita.medio_pago == "mercadopago", Visita.token_seguimiento.isnot(None)))
        .filter(Visita.mp_conflicto_aviso_enviado.is_(False))
        .all()
    )
    for cand in cancelados:
        v_dur = cand.servicio.duracion_min if cand.servicio else 30
        v_inicio = cand.fecha_hora
        v_fin = v_inicio + timedelta(minutes=v_dur)
        if not overlaps(inicio_n, fin_n, v_inicio, v_fin):
            continue
        pay = mp_api.buscar_ultimo_pago_por_external_reference(str(cand.id_visita))
        if not pay or not _pago_mp_aprobado(pay):
            continue
        if not _pago_mercadopago_coincide_con_visita(cand, pay):
            continue
        try:
            _enviar_aviso_conflicto_horario_ocupado_y_marcar(
                db, cand, str(pay.get("id", ""))
            )
            logger.info(
                "MP conflicto: correo tras nueva reserva que ocupa hueco (cancelada=%s nueva=%s)",
                cand.id_visita,
                visita_nueva.id_visita,
            )
        except Exception as e:
            logger.exception(
                "MP conflicto: falló aviso post-reserva visita_cancelada=%s err=%s",
                cand.id_visita,
                e,
            )
            db.rollback()


def _volcar_estado_pago_mp_en_visita(
    visita: Visita,
    pay: dict,
    *,
    db: Optional[Session] = None,
    skip_seller_activity_url: bool = False,
    skip_receipt_url: bool = False,
) -> str:
    from utils import mercadopago_api as mp_api

    pay_id_str = str(pay.get("id", ""))
    if not skip_receipt_url:
        rec = mp_api.receipt_url_de_pago(pay)
        if rec:
            visita.mercadopago_receipt_url = rec

    if not skip_seller_activity_url:
        try:
            act = mp_api.url_actividad_vendedor_desde_pago(pay)
            if act:
                visita.mercadopago_seller_activity_url = act
        except Exception as e:
            logger.warning("MP actividad vendedor (no bloquea): %s", e)

    if not getattr(visita, "medio_pago", None):
        visita.medio_pago = "mercadopago"

    if _pago_mp_aprobado(pay):
        visita.mercadopago_payment_id = pay_id_str
        visita.estado_pago = "APROBADO"
        est_u = str(visita.estado or "").upper()
        logger.info(
            "MP volcar: pago aprobado payment_id=%s visita=%s estado_actual=%s",
            pay_id_str,
            visita.id_visita,
            est_u,
        )
        if est_u == "PENDIENTE_CONFIRMACION_MP":
            visita.estado = "CONFIRMADO"
            return "confirmado"
        if est_u == "CANCELADO":
            visita.pago_tardio = True
            if db is None:
                visita.estado_pago = "REQUIERE_ACCION"
                return "requiere_accion"
            dur_min = visita.servicio.duracion_min if visita.servicio else 30
            if _hay_conflicto_turno_activo(db, visita.id_barbero, visita.fecha_hora, dur_min, visita.id_visita):
                visita.estado_pago = "REQUIERE_ACCION"
                try:
                    _enviar_aviso_conflicto_horario_ocupado_y_marcar(db, visita, pay_id_str)
                except Exception as e:
                    logger.exception("MP conflicto: falló aviso por email visita=%s: %s", visita.id_visita, e)
                try:
                    _enviar_whatsapp_requiere_accion_y_marcar(db, visita)
                except Exception as e:
                    logger.exception("MP reagendar: falló WhatsApp visita=%s: %s", visita.id_visita, e)
                return "requiere_accion"
            visita.estado = "CONFIRMADO"
            return "reactivado"
        return "sin_cambios"
    elif _pago_mp_pendiente(pay):
        if not visita.mercadopago_payment_id:
            visita.mercadopago_payment_id = pay_id_str
        visita.estado_pago = "PENDIENTE"
        logger.info("MP volcar: pago pendiente payment_id=%s visita=%s", pay_id_str, visita.id_visita)
        return "pendiente"
    else:
        if not visita.mercadopago_payment_id:
            visita.mercadopago_payment_id = pay_id_str
        visita.estado_pago = "RECHAZADO"
        # Rechazado / cancelado / otros: id interno por si hace falta trazar; sin "referencia" de comprobante.
        logger.info("MP volcar: pago rechazado/otro payment_id=%s visita=%s", pay_id_str, visita.id_visita)
        return "rechazado"


def _commit_visita_tras_volcar_mp(db: Session, visita: Visita, pay: dict) -> None:
    id_visita = visita.id_visita
    try:
        db.add(visita)
        db.commit()
    except (OperationalError, ProgrammingError) as e:
        db.rollback()
        if not _mysql_columna_mp_opcional_falta(e):
            raise
        logger.warning(
            "MP: columna opcional ausente; reintentando sin URL Actividades vendedor. Ejecutá add_mercadopago_visita.sql — %s",
            e,
        )
        visita = (
            db.query(Visita)
            .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
            .filter(Visita.id_visita == id_visita)
            .first()
        )
        if not visita:
            raise RuntimeError(f"visita {id_visita} no encontrada tras rollback") from e
        _volcar_estado_pago_mp_en_visita(visita, pay, db=db, skip_seller_activity_url=True)
        try:
            db.add(visita)
            db.commit()
        except (OperationalError, ProgrammingError) as e2:
            db.rollback()
            if not _mysql_columna_mp_opcional_falta(e2):
                raise
            logger.warning(
                "MP: columna opcional ausente; reintentando sin URLs recibo/actividades — %s",
                e2,
            )
            visita = (
                db.query(Visita)
                .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
                .filter(Visita.id_visita == id_visita)
                .first()
            )
            if not visita:
                raise RuntimeError(f"visita {id_visita} no encontrada tras rollback") from e2
            _volcar_estado_pago_mp_en_visita(
                visita, pay, db=db, skip_seller_activity_url=True, skip_receipt_url=True
            )
            db.add(visita)
            db.commit()


def sincronizar_pago_mercadopago(
    db: Session,
    sync: MercadoPagoSyncIn,
    *,
    confirmar_aprobado: bool = False,
    origen: str = "manual",
) -> Tuple[Optional[Visita], str]:
    from utils import mercadopago_api as mp_api

    if not mp_api.mp_token_configurado():
        return None, "Configurá MERCADOPAGO_ACCESS_TOKEN en el servidor."

    pid_raw = (sync.payment_id or "").strip()
    pid = mp_api.normalizar_payment_id_input(pid_raw) if pid_raw else ""

    ext_str = str(sync.external_reference).strip() if sync.external_reference else ""
    pref_str = str(sync.preference_id).strip() if sync.preference_id else ""
    ext_desde_pref: Optional[int] = None
    if pref_str:
        ext_desde_pref = mp_api.external_reference_desde_preferencia(pref_str)

    logger.info(
        "MP sincronizar: inicio origen=%s confirmar_aprobado=%s pid=%s external_reference=%s preference_id=%s ext_desde_pref=%s",
        origen,
        confirmar_aprobado,
        pid or None,
        ext_str or None,
        pref_str or None,
        ext_desde_pref,
    )

    # #region agent log
    _agent_dbg_mp(
        "H1-H3",
        "visita.py:sincronizar_pago_mercadopago:inputs",
        "sync_in",
        {
            "has_pid": bool(pid),
            "has_ext_str": bool(ext_str),
            "has_pref": bool(pref_str),
            "ext_desde_pref": ext_desde_pref,
        },
    )
    # #endregion

    pay: Optional[Dict[str, Any]] = None
    resolucion: Optional[str] = None
    for intento in range(6):
        if intento:
            sleep(1.0)
        # Mismo orden que ProyectoBurgers/pedido: payment_id primero (MP indexa la búsqueda por ref con más demora).
        if pid:
            pay = mp_api.obtener_pago_por_id_o_merchant_order(pid_raw)
            if pay:
                resolucion = "payment_id"
                break
        if ext_str:
            pay = mp_api.buscar_ultimo_pago_por_external_reference(ext_str)
            if pay:
                resolucion = "ext_str"
                break
        if ext_desde_pref is not None:
            pay = mp_api.buscar_ultimo_pago_por_external_reference(str(ext_desde_pref))
            if pay:
                resolucion = "ext_desde_pref"
                break

    if not pay:
        # #region agent log
        _agent_dbg_mp(
            "H1-H5",
            "visita.py:sincronizar_pago_mercadopago:no_pay",
            "no_payment_after_retries",
            {"intentos": 6},
        )
        # #endregion
        return (
            None,
            "Mercado Pago no devolvió el pago (revisá payment_id o esperá unos segundos y reintentá).",
        )

    logger.info(
        "MP sincronizar: pago resuelto por=%s payment_id=%s status=%s external_reference=%s",
        resolucion,
        pay.get("id"),
        pay.get("status"),
        pay.get("external_reference"),
    )

    # #region agent log
    _agent_dbg_mp(
        "H1-H5",
        "visita.py:sincronizar_pago_mercadopago:pay_found",
        "payment_resolved",
        {
            "resolucion": resolucion,
            "pay_id": pay.get("id"),
            "pay_status": pay.get("status"),
            "pay_external_reference": pay.get("external_reference"),
        },
    )
    # #endregion

    id_visita = mp_api.external_reference_de_pago(pay)
    if id_visita is None and sync.external_reference:
        id_visita = _parse_id_visita_ref(str(sync.external_reference))
    if id_visita is None and sync.preference_id:
        id_visita = mp_api.external_reference_desde_preferencia(str(sync.preference_id).strip())

    if id_visita is None:
        # #region agent log
        _agent_dbg_mp(
            "H5",
            "visita.py:sincronizar_pago_mercadopago:id_visita_none",
            "cannot_resolve_id_visita",
            {"pay_id": pay.get("id")},
        )
        # #endregion
        return (
            None,
            "El pago no está vinculado al turno (external_reference). Pagá desde el checkout de la agenda.",
        )

    logger.info(
        "MP sincronizar: external_reference resuelto id_visita=%s payment_id=%s",
        id_visita,
        pay.get("id"),
    )

    ref_en_pago = mp_api.external_reference_de_pago(pay)
    if ref_en_pago is not None and ref_en_pago != id_visita:
        return None, "Los datos del pago no coinciden con el turno (referencia distinta)."

    visita = (
        db.query(Visita)
        .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
        .filter(Visita.id_visita == id_visita)
        .with_for_update()
        .first()
    )
    if not visita:
        logger.warning("MP sincronizar: visita no encontrada id_visita=%s payment_id=%s", id_visita, pay.get("id"))
        return None, f"No existe el turno #{id_visita} en la base."

    logger.info(
        "MP sincronizar: visita encontrada id_visita=%s estado=%s estado_pago=%s payment_actual=%s",
        visita.id_visita,
        visita.estado,
        getattr(visita, "estado_pago", None),
        getattr(visita, "mercadopago_payment_id", None),
    )

    est_visita_u = str(visita.estado or "").upper()
    if est_visita_u == "CANCELADO":
        if not _pago_mp_aprobado(pay):
            return None, "Este turno fue cancelado por falta de confirmación de pago a tiempo."

    medio = (getattr(visita, "medio_pago", None) or "").strip()
    pendiente_mp = str(visita.estado or "").upper() == "PENDIENTE_CONFIRMACION_MP"
    cancelado_aprobado = est_visita_u == "CANCELADO" and _pago_mp_aprobado(pay)
    if medio and medio != "mercadopago":
        return None, "Ese turno no fue registrado con Mercado Pago."
    if not medio and not pendiente_mp and not cancelado_aprobado:
        return None, "Ese turno no está pendiente de confirmación de pago."

    if not _pago_mercadopago_coincide_con_visita(visita, pay):
        esp = _precio_esperado_visita(visita)
        # #region agent log
        _agent_dbg_mp(
            "H4",
            "visita.py:sincronizar_pago_mercadopago:monto_rechazado",
            "amount_or_currency_mismatch",
            {
                "id_visita": id_visita,
                "esperado": str(esp) if esp is not None else None,
                "pay_currency": (pay.get("currency_id") or "")[:8],
            },
        )
        # #endregion
        return (
            None,
            f"El monto o moneda del pago no coincide con el servicio reservado (esperado ${esp}).",
        )

    if _pago_mp_aprobado(pay) and not confirmar_aprobado:
        logger.warning(
            "MP sincronizar: pago aprobado ignorado por origen no autorizado origen=%s visita=%s payment_id=%s",
            origen,
            visita.id_visita,
            pay.get("id"),
        )
        return (
            None,
            "Pago aprobado detectado, pero este origen no confirma turnos. Esperando webhook de Mercado Pago.",
        )

    pay_id_str = str(pay.get("id", ""))
    if pay_id_str:
        dup = (
            db.query(Visita)
            .filter(
                Visita.mercadopago_payment_id == pay_id_str,
                Visita.id_visita != visita.id_visita,
            )
            .first()
        )
        if dup:
            logger.warning(
                "MP sincronizar: payment_id duplicado payment_id=%s visita_actual=%s visita_dup=%s",
                pay_id_str,
                visita.id_visita,
                dup.id_visita,
            )
            return None, "Este pago ya está asociado a otro turno."

    resultado_mp = _volcar_estado_pago_mp_en_visita(visita, pay, db=db)
    logger.info(
        "MP sincronizar: antes de commit visita=%s payment_id=%s estado=%s estado_pago=%s resultado=%s",
        visita.id_visita,
        visita.mercadopago_payment_id,
        visita.estado,
        getattr(visita, "estado_pago", None),
        resultado_mp,
    )

    try:
        _commit_visita_tras_volcar_mp(db, visita, pay)
    except Exception as e:
        logger.exception("MP sincronizar: error al guardar visita %s", id_visita)
        return None, f"Error al guardar en la base: {e!s}"

    visita = (
        db.query(Visita)
        .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
        .filter(Visita.id_visita == id_visita)
        .first()
    )
    if not visita:
        return None, "Error interno al recargar el turno."
    if resultado_mp == "requiere_accion":
        logger.info(
            "MP sincronizar OK requiere_accion visita=%s payment_id=%s estado=%s estado_pago=%s",
            visita.id_visita,
            visita.mercadopago_payment_id,
            visita.estado,
            getattr(visita, "estado_pago", None),
        )
        return (
            visita,
            "El pago fue aprobado, pero el horario ya no está disponible. "
            "Quedó registrado como REQUIERE_ACCION para reagendar o devolver luego.",
        )
    logger.info(
        "MP sincronizar OK visita=%s payment_id=%s estado=%s",
        visita.id_visita,
        pay.get("id"),
        visita.estado,
    )
    return visita, ""


def obtener_visita_por_token(db: Session, token: str) -> Optional[Visita]:
    if not token or not str(token).strip():
        return None
    t = str(token).strip()
    return (
        db.query(Visita)
        .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
        .filter(Visita.token_seguimiento == t)
        .first()
    )


def _obtener_visita_reagendar_por_token(db: Session, token: str, *, lock: bool = False) -> Visita:
    tok = (token or "").strip()
    if len(tok) < 24 or len(tok) > 256:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de re-agendado inválido.")

    q = (
        db.query(Visita)
        .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
        .filter(Visita.reagendar_token_hash == _hash_token_reagendar(tok))
    )
    if lock:
        q = q.with_for_update()
    visita = q.first()
    if not visita:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token de re-agendado inválido.")

    if visita.reagendar_token_used_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este link ya fue utilizado.")
    if not visita.reagendar_token_expires_at or visita.reagendar_token_expires_at <= obtener_ahora_local():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="El link de re-agendado expiró.")
    if str(visita.estado_pago or "").upper() != "REQUIERE_ACCION":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este pago ya no requiere re-agendado.")
    if not visita.mercadopago_payment_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No hay un pago aprobado asociado.")
    return visita


def obtener_info_reagendar_mp(
    db: Session,
    token: str,
    fecha: Optional[date] = None,
    id_barbero: Optional[int] = None,
) -> Dict[str, Any]:
    visita = _obtener_visita_reagendar_por_token(db, token)
    disponibilidad = None
    if fecha:
        disponibilidad = get_disponibilidad(
            db,
            fecha=fecha,
            id_servicio=visita.id_servicio,
            id_barbero=id_barbero or visita.id_barbero,
        )

    return {
        "ok": True,
        "visita_id": visita.id_visita,
        "estado_pago": visita.estado_pago,
        "pago_tardio": bool(visita.pago_tardio),
        "payment_id": visita.mercadopago_payment_id,
        "servicio": visita.servicio.nombre if visita.servicio else "",
        "servicio_duracion": visita.servicio.duracion_min if visita.servicio else 0,
        "cliente_nombre": visita.cliente.nombre if visita.cliente else "",
        "barbero_actual_id": visita.id_barbero,
        "fecha_hora_original": visita.fecha_hora,
        "token_expires_at": visita.reagendar_token_expires_at,
        "disponibilidad": disponibilidad,
    }


def reagendar_visita_mp_con_pago_existente(
    db: Session,
    token: str,
    fecha_hora: datetime,
    id_barbero: Optional[int] = None,
) -> Visita:
    visita = _obtener_visita_reagendar_por_token(db, token, lock=True)
    barbero_id = id_barbero or visita.id_barbero
    if not barbero_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seleccioná un barbero.")

    ahora = obtener_ahora_local()
    if fecha_hora < ahora:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede re-agendar en el pasado.")

    dur_min = visita.servicio.duracion_min if visita.servicio else 30
    dia_semana = fecha_hora.date().isoweekday()
    horarios = (
        db.query(HorarioBarbero)
        .filter(
            HorarioBarbero.id_barbero == barbero_id,
            HorarioBarbero.dia_semana == dia_semana,
            HorarioBarbero.fecha_desde <= fecha_hora.date(),
            HorarioBarbero.fecha_hasta >= fecha_hora.date(),
        )
        .all()
    )
    barbero = db.query(Barbero).get(barbero_id)
    hora_solicitada = fecha_hora.strftime("%H:%M")
    en_jornada = False
    for horario in horarios:
        slots = generar_slots(horario.hora_desde, horario.hora_hasta, dur_min)
        if hora_solicitada not in [slot.strftime("%H:%M") for slot in slots]:
            continue
        if barbero and validar_conflicto_descanso(
            fecha_hora,
            dur_min,
            barbero.descanso_inicio,
            barbero.descanso_fin,
        ):
            continue
        en_jornada = True
        break
    if not en_jornada:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ese horario no está disponible.")

    if _hay_conflicto_turno_activo(db, barbero_id, fecha_hora, dur_min, visita.id_visita):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ese horario ya fue reservado.")

    dup = (
        db.query(Visita)
        .filter(
            Visita.mercadopago_payment_id == visita.mercadopago_payment_id,
            Visita.id_visita != visita.id_visita,
        )
        .first()
    )
    if dup:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este pago ya está asociado a otro turno.")

    visita.fecha_hora = fecha_hora
    visita.id_barbero = barbero_id
    visita.estado = "CONFIRMADO"
    visita.estado_pago = "APROBADO"
    visita.pago_tardio = True
    visita.medio_pago = "mercadopago"
    visita.reagendar_token_used_at = obtener_ahora_local()

    db.add(visita)
    db.commit()
    db.refresh(visita)
    return get_visita_by_id(db, visita.id_visita) or visita


def asociar_pago_link_mercadopago(db: Session, token: str, payment_id_raw: str) -> Visita:
    from utils import mercadopago_api as mp_api

    tok = (token or "").strip()
    pid = mp_api.normalizar_payment_id_input(payment_id_raw)
    if not tok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falta el token de seguimiento.")
    if not pid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ingresá el número de operación.")
    if not mp_api.mp_token_configurado():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mercado Pago no está configurado en el servidor.",
        )

    visita = (
        db.query(Visita)
        .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
        .filter(Visita.token_seguimiento == tok)
        .with_for_update()
        .first()
    )
    if not visita:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado.")

    medio_v = (getattr(visita, "medio_pago", None) or "").strip()
    pend_mp = str(visita.estado or "").upper() == "PENDIENTE_CONFIRMACION_MP"
    if medio_v and medio_v != "mercadopago":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este turno no fue hecho con Mercado Pago.",
        )
    est_u = str(visita.estado or "").upper()
    if not medio_v and not pend_mp and est_u != "CANCELADO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este turno no fue hecho con Mercado Pago.",
        )

    pay = None
    for intento in range(6):
        if intento:
            sleep(1.0)
        pay = mp_api.obtener_pago(pid)
        if pay:
            break
    if not pay:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No encontramos ese pago en Mercado Pago. Revisá el número de operación.",
        )

    if est_u == "CANCELADO":
        if not _pago_mp_aprobado(pay):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este turno fue cancelado por falta de confirmación de pago a tiempo.",
            )

    ext = mp_api.external_reference_de_pago(pay)
    if ext is not None and ext != visita.id_visita:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este pago está asociado a otro turno en Mercado Pago.",
        )

    if not _pago_mercadopago_coincide_con_visita(visita, pay):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto del pago no coincide con el servicio reservado.",
        )

    if _pago_mp_aprobado(pay):
        logger.warning(
            "MP asociar link: pago aprobado detectado por origen manual visita=%s payment_id=%s; esperando webhook",
            visita.id_visita,
            pay.get("id"),
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pago aprobado detectado, pero la confirmación del turno queda reservada al webhook de Mercado Pago.",
        )

    pay_id_str = str(pay.get("id", ""))
    dup = (
        db.query(Visita)
        .filter(
            Visita.mercadopago_payment_id == pay_id_str,
            Visita.id_visita != visita.id_visita,
        )
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este pago ya está asociado a otro turno.",
        )

    resultado_mp = _volcar_estado_pago_mp_en_visita(visita, pay, db=db)
    try:
        _commit_visita_tras_volcar_mp(db, visita, pay)
    except Exception as e:
        logger.exception("MP asociar link: error al guardar visita %s", visita.id_visita)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar: {e!s}",
        ) from e

    visita = (
        db.query(Visita)
        .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
        .filter(Visita.id_visita == visita.id_visita)
        .first()
    )
    if not visita:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al guardar el turno.")
    if resultado_mp == "requiere_accion":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El pago fue aprobado, pero el horario ya no está disponible. "
                "Quedó registrado para reagendar o devolver luego."
            ),
        )
    return visita


def checkout_mercadopago_para_visita(
    db: Session,
    visita: Visita,
    frontend_return_base: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Tras crear visita MP: preferencia Checkout Pro, link de respaldo, o (None, None, mensaje).
    El tercer valor es un texto corto para mostrar al cliente si no hay URL de pago.
    """
    from utils import mercadopago_api as mp_api

    if (getattr(visita, "medio_pago", None) or "") != "mercadopago":
        return None, None, None

    logger.info(
        "MP checkout: creando preferencia visita=%s estado=%s estado_pago=%s",
        visita.id_visita,
        visita.estado,
        getattr(visita, "estado_pago", None),
    )

    init_point: Optional[str] = None
    pref_id: Optional[str] = None
    last_err: Optional[str] = None

    servicio = visita.servicio
    nombre_srv = servicio.nombre if servicio else "Servicio"
    titulo = f"Turno #{visita.id_visita} — {nombre_srv} — King Barber"
    total = _precio_esperado_visita(visita) or decimal.Decimal("0.00")
    if total <= 0:
        return (
            None,
            None,
            "El servicio no tiene precio válido; no se puede cobrar con Mercado Pago.",
        )

    email = visita.cliente.email if visita.cliente and visita.cliente.email else None

    if mp_api.mp_token_configurado():
        init_point, pref_id, err = mp_api.crear_preferencia_checkout_pro(
            visita.id_visita,
            total,
            titulo,
            email.strip() if isinstance(email, str) else None,
            return_base=frontend_return_base,
        )
        if err:
            logger.info("Checkout MP visita no generado: %s", err)
            last_err = err if len(str(err)) < 400 else str(err)[:400]
            init_point = None
            pref_id = None
    else:
        last_err = "Mercado Pago no está configurado: falta MERCADOPAGO_ACCESS_TOKEN en el servidor."

    if not init_point:
        link_base = mp_api.url_link_pago_negocio()
        if link_base:
            try:
                init_point = mp_api.url_link_pago_con_visita(visita.id_visita)
                pref_id = None
                last_err = None
            except ValueError:
                init_point = None
        elif last_err is None:
            last_err = (
                "No hay Access Token de Mercado Pago ni MERCADOPAGO_LINK_PAGO de respaldo. "
                "Configurá al menos uno en el archivo .env del backend."
            )

    if not init_point and last_err is None:
        last_err = "No se pudo obtener el enlace de pago. Revisá las credenciales y los logs del servidor."

    return init_point, pref_id, last_err if not init_point else None