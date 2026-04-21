import logging
import os
import smtplib
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

# Mismo .env que database.py (si load_dotenv() usa solo el CWD, MAIL_* puede quedar vacío al arrancar uvicorn desde otra carpeta).
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env", override=True)

logger = logging.getLogger(__name__)

_mail_port_raw = os.getenv("MAIL_PORT", "587").strip()
try:
    _mail_port = int(_mail_port_raw)
except ValueError:
    _mail_port = 587


def _mail_password_normalizado() -> str:
    """Gmail a veces muestra la clave de aplicación con espacios; SMTP usa los 16 caracteres seguidos."""
    return (os.getenv("MAIL_PASSWORD") or "").replace(" ", "").strip()


conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=_mail_password_normalizado() or os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_SERVER=os.getenv("MAIL_SERVER") or "smtp.gmail.com",
    MAIL_PORT=_mail_port,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


def _mail_config_ok() -> bool:
    u = os.getenv("MAIL_USERNAME", "").strip()
    p = _mail_password_normalizado() or (os.getenv("MAIL_PASSWORD") or "").strip()
    f = os.getenv("MAIL_FROM", "").strip()
    return bool(u and p and f)


def enviar_email_texto_sync(destinatario: str, asunto: str, cuerpo: str) -> None:
    """
    Envío SMTP síncrono (smtplib). Útil en hilos daemon o fuera del event loop de FastAPI
    (asyncio.run en threads secundarios suele fallar en Windows).
    """
    if not _mail_config_ok():
        raise RuntimeError("Configuración de correo incompleta (MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM).")

    user = os.getenv("MAIL_USERNAME", "").strip()
    password = _mail_password_normalizado() or (os.getenv("MAIL_PASSWORD") or "").strip()
    from_hdr = os.getenv("MAIL_FROM", "").strip()
    server = os.getenv("MAIL_SERVER", "smtp.gmail.com").strip()
    port = _mail_port

    msg = MIMEText(cuerpo, "plain", "utf-8")
    msg["Subject"] = asunto
    msg["From"] = from_hdr
    msg["To"] = destinatario

    try:
        with smtplib.SMTP(server, port, timeout=45) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        logger.info("SMTP sync ok asunto=%r dest=%r", asunto, destinatario[:3] + "***")
    except Exception:
        logger.exception("SMTP sync falló (Gmail: contraseña de aplicación, 2 pasos, firewall)")
        raise


async def enviar_email_confirmacion(
    destinatario: EmailStr,
    asunto: str,
    cuerpo: str,
) -> None:
    if not _mail_config_ok():
        logger.error(
            "Correo no enviado: faltan MAIL_USERNAME, MAIL_PASSWORD o MAIL_FROM en %s",
            _backend_dir / ".env",
        )
        raise RuntimeError("Configuración de correo incompleta (revisá MAIL_* en Backend/.env).")

    message = MessageSchema(
        subject=asunto,
        recipients=[destinatario],
        body=cuerpo,
        subtype="plain",
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        logger.info("Correo enviado ok asunto=%r dest=%r", asunto, str(destinatario)[:3] + "***")
    except Exception as e:
        logger.exception("Falló el envío SMTP (Gmail: contraseña de aplicación, 2FA, revisá spam): %s", e)
        raise
