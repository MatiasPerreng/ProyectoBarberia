"""
Aviso al cliente cuando MP acreditó el pago pero el turno ya no puede reactivarse
(horario tomado por otro). Cubre el caso en que no vuelve a la web de King Barber.

El envío es síncrono en el mismo hilo del request: un hilo daemon terminaba antes
de completar SMTP y el correo no salía (especialmente en Windows).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import EmailStr, TypeAdapter

if TYPE_CHECKING:
    from models.visita import Visita

_email_adapter = TypeAdapter(EmailStr)

logger = logging.getLogger(__name__)


def enviar_aviso_pago_horario_ocupado_sync(visita: Visita, payment_id: str) -> None:
    """Envía el mail en el mismo hilo (antes de responder error al cliente / webhook)."""
    cliente = visita.cliente
    if not cliente:
        logger.warning("MP conflicto: sin cliente cargado, no se envía mail visita=%s", visita.id_visita)
        return
    raw = (getattr(cliente, "email", None) or "").strip()
    try:
        destinatario = _email_adapter.validate_python(raw)
    except Exception:
        logger.warning(
            "MP conflicto: email inválido o vacío; no se envía aviso visita=%s email=%r",
            visita.id_visita,
            raw[:20] if raw else "",
        )
        return

    nombre = f"{cliente.nombre or ''} {getattr(cliente, 'apellido', None) or ''}".strip() or "Hola"
    fecha_str = visita.fecha_hora.strftime("%d/%m/%Y %H:%M")
    srv = visita.servicio.nombre if visita.servicio else "tu servicio"
    pid = (payment_id or "").strip() or "(sin número aún)"

    asunto = "King Barber — Pago recibido; el horario ya no estaba disponible"
    cuerpo = (
        f"Hola {nombre},\n\n"
        f"Recibimos el pago en Mercado Pago (operación {pid}) vinculado a un turno que ya había sido liberado "
        f"por tiempo de espera, y en ese horario ya había otra reserva.\n\n"
        f"Qué podés hacer: escribinos por WhatsApp o respondiendo este mail para coordinar otro turno "
        f"o un reembolso, según corresponda.\n\n"
        f"Referencia del turno original: #{visita.id_visita} · {srv} · {fecha_str}\n\n"
        f"Saludos,\nKing Barber\n"
    )

    dest_str = str(destinatario)
    logger.info(
        "MP conflicto: enviando aviso SMTP visita=%s payment_id=%s dest=%s***",
        visita.id_visita,
        pid,
        dest_str[:3],
    )

    from core.email import enviar_email_texto_sync

    enviar_email_texto_sync(dest_str, asunto, cuerpo)
    logger.info("MP conflicto: mail enviado (SMTP sync) visita=%s payment_id=%s", visita.id_visita, pid)
