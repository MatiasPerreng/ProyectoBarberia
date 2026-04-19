from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, or_
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime, timedelta, time, date
import decimal
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
    """Umbral para liberar turnos MP abandonados (sin id de pago en BD). Config: MERCADOPAGO_RESERVA_MINUTOS."""
    raw = os.getenv("MERCADOPAGO_RESERVA_MINUTOS", "15").strip()
    try:
        n = int(raw)
    except ValueError:
        return 15
    return max(5, min(n, 180))


def eliminar_visitas_mp_abandonadas(db: Session) -> int:
    """
    Elimina reservas en PENDIENTE_CONFIRMACION_MP cuando no hubo pago iniciado en MP
    (sin mercadopago_payment_id) tras el umbral en minutos. Libera el horario para otros clientes.

    No borra filas que ya tengan id de pago (pago en curso o pendiente de acreditación en MP),
    para no romper la asociación pago–visita cuando el webhook/sync llega tarde.

    Importante: no invocar esta función inmediatamente antes de sincronizar_pago_mercadopago ni en el
    webhook de MP: un usuario puede tardar > umbral en el checkout y aún así pagar; borrar antes
    rompería la asociación. Usar solo en disponibilidad, crear visita, marcar completadas, etc.
    """
    mins = _minutos_expiracion_reserva_mp()
    try:
        deleted = (
            db.query(Visita)
            .filter(Visita.estado == "PENDIENTE_CONFIRMACION_MP")
            .filter(or_(Visita.medio_pago == "mercadopago", Visita.medio_pago.is_(None)))
            .filter(Visita.mercadopago_payment_id.is_(None))
            .filter(Visita.created_at.isnot(None))
            .filter(text("TIMESTAMPDIFF(MINUTE, visita.created_at, NOW()) >= :m").bindparams(m=mins))
            .delete(synchronize_session=False)
        )
        if deleted:
            db.commit()
            logger.info(
                "MP cleanup: eliminadas %s reserva(s) pendiente(s) sin pago (>= %s min)",
                deleted,
                mins,
            )
        return int(deleted or 0)
    except Exception as e:
        db.rollback()
        logger.warning("MP cleanup: error (no bloquea la petición): %s", e)
        return 0


def marcar_visitas_completadas(db: Session) -> None:
    eliminar_visitas_mp_abandonadas(db)
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
    eliminar_visitas_mp_abandonadas(db)
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
        raise ValueError("Lo sentimos, alguien se agendó ese turno segundos antes que vos.")

    if visita_in.id_barbero is None:
        visita_in.id_barbero = asignar_barbero_automatico(db, visita_in.fecha_hora, servicio.duracion_min)
        if not visita_in.id_barbero: raise ValueError("No hay barberos disponibles")

    mp = getattr(visita_in, "medio_pago", None) == "mercadopago"
    visita = Visita(
        fecha_hora=visita_in.fecha_hora,
        id_cliente=visita_in.id_cliente,
        id_barbero=visita_in.id_barbero,
        id_servicio=visita_in.id_servicio,
        precio_al_reservar=servicio.precio,
        estado="PENDIENTE_CONFIRMACION_MP" if mp else "CONFIRMADO",
        medio_pago="mercadopago" if mp else None,
        token_seguimiento=secrets.token_urlsafe(16) if mp else None,
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
    eliminar_visitas_mp_abandonadas(db)
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
    if st == "approved":
        return True
    # Algunas respuestas traen fecha de acreditación sin status normalizado
    if pay.get("date_approved"):
        return True
    return False


def _pago_mp_pendiente(pay: dict) -> bool:
    st = (pay.get("status") or "").strip().lower()
    return st in ("pending", "in_process", "in_mediation")


def _volcar_estado_pago_mp_en_visita(
    visita: Visita,
    pay: dict,
    *,
    skip_seller_activity_url: bool = False,
    skip_receipt_url: bool = False,
) -> None:
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
        visita.mercadopago_referencia = pay_id_str
        if str(visita.estado or "").upper() == "PENDIENTE_CONFIRMACION_MP":
            visita.estado = "CONFIRMADO"
    elif _pago_mp_pendiente(pay):
        if not visita.mercadopago_payment_id:
            visita.mercadopago_payment_id = pay_id_str
            visita.mercadopago_referencia = pay_id_str
    else:
        if not visita.mercadopago_payment_id:
            visita.mercadopago_payment_id = pay_id_str
            visita.mercadopago_referencia = pay_id_str


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
        _volcar_estado_pago_mp_en_visita(visita, pay, skip_seller_activity_url=True)
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
                visita, pay, skip_seller_activity_url=True, skip_receipt_url=True
            )
            db.add(visita)
            db.commit()


def sincronizar_pago_mercadopago(
    db: Session,
    sync: MercadoPagoSyncIn,
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

    ref_en_pago = mp_api.external_reference_de_pago(pay)
    if ref_en_pago is not None and ref_en_pago != id_visita:
        return None, "Los datos del pago no coinciden con el turno (referencia distinta)."

    visita = (
        db.query(Visita)
        .options(joinedload(Visita.servicio), joinedload(Visita.cliente), joinedload(Visita.barbero))
        .filter(Visita.id_visita == id_visita)
        .first()
    )
    if not visita:
        return None, f"No existe el turno #{id_visita} en la base."

    medio = (getattr(visita, "medio_pago", None) or "").strip()
    pendiente_mp = str(visita.estado or "").upper() == "PENDIENTE_CONFIRMACION_MP"
    if medio and medio != "mercadopago":
        return None, "Ese turno no fue registrado con Mercado Pago."
    if not medio and not pendiente_mp:
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

    _volcar_estado_pago_mp_en_visita(visita, pay)

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
    if not medio_v and not pend_mp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este turno no fue hecho con Mercado Pago.",
        )
    if str(visita.estado).upper() == "CANCELADO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este turno ya no admite asociar pagos.",
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

    _volcar_estado_pago_mp_en_visita(visita, pay)
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
    return visita


def checkout_mercadopago_para_visita(db: Session, visita: Visita) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Tras crear visita MP: preferencia Checkout Pro, link de respaldo, o (None, None, mensaje).
    El tercer valor es un texto corto para mostrar al cliente si no hay URL de pago.
    """
    from utils import mercadopago_api as mp_api

    if (getattr(visita, "medio_pago", None) or "") != "mercadopago":
        return None, None, None

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