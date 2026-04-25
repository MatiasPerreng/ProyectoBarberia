import os
import logging
import requests
from dotenv import load_dotenv
from core.telefonos import normalizar_telefono_uy

load_dotenv()

logger = logging.getLogger(__name__)

# Configuración de credenciales
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") 

# URL de la API de Meta
# Nota: Se eliminaron los corchetes si es que venían en el .env
BASE_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}


def _env_true(nombre: str) -> bool:
    return os.getenv(nombre, "").strip().lower() in ("1", "true", "yes", "on")


def _post_meta_whatsapp(payload, contexto: str):
    to = str(payload.get("to", ""))
    auth_preview = "Bearer ***" if WHATSAPP_TOKEN else "(sin token)"
    logger.info(
        "WhatsApp %s: enviando phone_number_id=%s url=%s token=%s to=%s*** type=%s payload=%s",
        contexto,
        PHONE_NUMBER_ID,
        BASE_URL,
        auth_preview,
        to[:4],
        payload.get("type"),
        payload,
    )
    try:
        response = requests.post(BASE_URL, json=payload, headers=HEADERS, timeout=10)
        if response.ok:
            logger.info("WhatsApp %s: OK status=%s body=%s", contexto, response.status_code, response.text[:1000])
        else:
            logger.error("WhatsApp %s: ERROR status=%s body=%s", contexto, response.status_code, response.text[:1000])
        return response.json()
    except Exception as e:
        logger.exception("WhatsApp %s: error de conexión: %s", contexto, e)
        return None

# ==========================================================
# TEMPLATE 1: RECORDATORIO (4 PARÁMETROS)
# ==========================================================
def enviar_recordatorio_whatsapp(visita):
    """
    Plantilla: recordatorio_cita
    Estructura esperada: Hola {{1}}, te recordamos que a las {{2}} tenés {{3}} con {{4}}.
    Idioma: es (Español)
    """
    if not visita.cliente or not visita.cliente.telefono:
        print("❌ ERROR: Cliente o teléfono no encontrados.")
        return None

    telefono = normalizar_telefono_uy(visita.cliente.telefono)
    hora_agenda = visita.fecha_hora.strftime("%H:%M")
    nombre_servicio = visita.servicio.nombre if visita.servicio else "Servicio"
    nombre_barbero = visita.barbero.nombre if visita.barbero else "Barbero"

    print(f"📲 ENVIANDO RECORDATORIO PROGRAMADO A: {telefono}")

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "template",
        "template": {
            "name": "recordatorio_cita", 
            "language": {"code": "es"},  
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(visita.cliente.nombre)}, # {{1}}
                        {"type": "text", "text": str(hora_agenda)},           # {{2}}
                        {"type": "text", "text": str(nombre_servicio)},       # {{3}}
                        {"type": "text", "text": f"el barbero {nombre_barbero}"} # {{4}}
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(BASE_URL, json=payload, headers=HEADERS, timeout=10)
        print("📩 RESPUESTA META RECORDATORIO:", response.text)
        return response.json()
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN RECORDATORIO: {e}")
        return None

# ==========================================================
# TEMPLATE 2: CANCELACIÓN (3 PARÁMETROS)
# ==========================================================
def enviar_cancelacion_whatsapp(telefono_cliente, nombre_cliente, servicio, fecha_hora_str):
    """
    Plantilla: cancelacion_turno_barberia
    Estructura esperada: Hola {{1}}, te informamos que tu turno para {{2}} el día {{3}} ha sido cancelado.
    Idioma: es (Español)
    """
    if not telefono_cliente:
        print("❌ ERROR: Falta el teléfono del cliente para cancelación.")
        return None

    telefono = normalizar_telefono_uy(telefono_cliente)
    
    print(f"📲 ENVIANDO AVISO DE CANCELACIÓN A: {telefono}")

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "template",
        "template": {
            "name": "cancelacion_barberia", 
            "language": {"code": "es"},  
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(nombre_cliente)}, # {{1}}
                        {"type": "text", "text": str(servicio)},       # {{2}}
                        {"type": "text", "text": str(fecha_hora_str)}  # {{3}}
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(BASE_URL, json=payload, headers=HEADERS, timeout=10)
        print("📩 RESPUESTA META CANCELACIÓN:", response.text)
        return response.json()
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN CANCELACIÓN: {e}")
        return None


def enviar_pago_tardio_reagendar_whatsapp(telefono_cliente, nombre_cliente, link_reagendar):
    """
    Prueba técnica: reutiliza un template aprobado existente cuando el pago tardío queda en requiere_accion.
    Por defecto usa cancelacion_barberia (3 parámetros), igual que enviar_cancelacion_whatsapp.
    """
    if not telefono_cliente:
        print("❌ ERROR: Falta el teléfono del cliente para pago tardío.")
        logger.warning("WhatsApp pago tardío: falta teléfono")
        return None

    telefono = normalizar_telefono_uy(telefono_cliente)
    nombre = str(nombre_cliente or "").strip() or "Hola"
    template_name = os.getenv("WHATSAPP_REQUIERE_ACCION_TEMPLATE_NAME", "cancelacion_barberia").strip() or "cancelacion_barberia"
    language = os.getenv("WHATSAPP_REQUIERE_ACCION_TEMPLATE_LANGUAGE", "es").strip() or "es"
    link_param = os.getenv("WHATSAPP_TEST_REAGENDAR_LINK", "").strip() or str(link_reagendar or "Link de prueba")
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": nombre},
                        {"type": "text", "text": "Pago recibido. Caso requiere accion."},
                        {"type": "text", "text": link_param},
                    ],
                }
            ],
        },
    }

    print(f"📲 ENVIANDO PAGO TARDÍO CON TEMPLATE {template_name} A: {telefono}")
    return _post_meta_whatsapp(payload, "pago_tardio_template")