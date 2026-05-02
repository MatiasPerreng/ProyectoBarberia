import logging
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

load_dotenv()

logger = logging.getLogger(__name__)


def _mail_enabled() -> bool:
    v = (os.getenv("MAIL_ENABLED") or "true").strip().lower()
    return v in ("true", "1", "yes", "")


def _build_connection_config() -> Optional[ConnectionConfig]:
    """
    Gmail: MAIL_USERNAME = correo completo, MAIL_PASSWORD = contraseña de aplicación
    (no la contraseña de inicio de sesión). Verificación en 2 pasos obligatoria.
    """
    if not _mail_enabled():
        return None

    user = (os.getenv("MAIL_USERNAME") or "").strip()
    password = (os.getenv("MAIL_PASSWORD") or "").strip()
    from_addr = (os.getenv("MAIL_FROM") or "").strip()
    server = (os.getenv("MAIL_SERVER") or "smtp.gmail.com").strip()

    try:
        port = int((os.getenv("MAIL_PORT") or "587").strip())
    except ValueError:
        port = 587

    if not user or not password or not from_addr:
        logger.warning(
            "Correo no enviado: defini MAIL_USERNAME, MAIL_PASSWORD y MAIL_FROM en .env "
            "(o poné MAIL_ENABLED=false para silenciar este aviso)."
        )
        return None

    starttls = (os.getenv("MAIL_STARTTLS") or "true").strip().lower() in ("true", "1", "yes")
    ssl_tls = (os.getenv("MAIL_SSL_TLS") or "false").strip().lower() in ("true", "1", "yes")

    return ConnectionConfig(
        MAIL_USERNAME=user,
        MAIL_PASSWORD=password,
        MAIL_FROM=from_addr,
        MAIL_SERVER=server,
        MAIL_PORT=port,
        MAIL_STARTTLS=starttls,
        MAIL_SSL_TLS=ssl_tls,
        USE_CREDENTIALS=True,
    )


async def enviar_email_confirmacion(
    destinatario: EmailStr,
    asunto: str,
    cuerpo: str,
) -> None:
    conf = _build_connection_config()
    if conf is None:
        return

    message = MessageSchema(
        subject=asunto,
        recipients=[destinatario],
        body=cuerpo,
        subtype="plain",
    )

    try:
        fm = FastMail(conf)
        await fm.send_message(message)
    except ConnectionErrors as e:
        # Gmail 534 "WebLoginRequired": cuenta bloquea SMTP hasta usar contraseña de aplicación.
        logger.error(
            "SMTP falló al enviar a %s (%s). Si es Gmail: cuenta Google → Seguridad → "
            "Verificación en 2 pasos → Contraseñas de aplicaciones; usá esa clave de 16 "
            "caracteres en MAIL_PASSWORD (no la contraseña del correo). "
            "https://support.google.com/mail/?p=WebLoginRequired",
            destinatario,
            getattr(e, "expression", e),
        )
