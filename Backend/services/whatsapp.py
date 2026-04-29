import os
import requests
from dotenv import load_dotenv
from core.telefonos import normalizar_telefono_uy

load_dotenv()

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
            "language": {"code": "es"},  # <--- CAMBIADO DE es_LA A es
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
            "language": {"code": "es"},  # <--- CAMBIADO DE es_LA A es
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