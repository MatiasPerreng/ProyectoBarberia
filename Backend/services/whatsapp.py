import os
import requests
from dotenv import load_dotenv

from core.telefonos import normalizar_telefono_uy

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

BASE_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}

print("🔧 WHATSAPP CONFIG")
print("TOKEN CARGADO:", "SI" if WHATSAPP_TOKEN else "NO")
print("PHONE_NUMBER_ID:", PHONE_NUMBER_ID)
print("BASE_URL:", BASE_URL)


# ==========================================================
# TEMPLATE HELLO WORLD (PRUEBA INICIAL)
# ==========================================================

def enviar_template_hello_world(telefono: str):
    print("📲 ENVIAR HELLO WORLD")
    print("📞 TELEFONO:", telefono)

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {"code": "en_US"}
        }
    }

    response = requests.post(
        BASE_URL,
        json=payload,
        headers=HEADERS,
        timeout=10
    )

    print("📩 STATUS CODE:", response.status_code)
    print("📩 RESPUESTA META:", response.text)

    return response.json()


# ==========================================================
# TEMPLATE TURNO CONFIRMADO
# ==========================================================

def enviar_turno_confirmado(
    telefono: str,
    nombre: str,
    fecha: str,
    hora: str
):
    print("📲 ENVIAR TURNO CONFIRMADO")
    print("📞 TELEFONO:", telefono)

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "template",
        "template": {
            "name": "turno_confirmado_king_barber",
            "language": {"code": "es"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": nombre},
                        {"type": "text", "text": fecha},
                        {"type": "text", "text": hora}
                    ]
                }
            ]
        }
    }

    response = requests.post(
        BASE_URL,
        json=payload,
        headers=HEADERS,
        timeout=10
    )

    print("📩 STATUS CODE:", response.status_code)
    print("📩 RESPUESTA META:", response.text)

    return response.json()


def enviar_turno_confirmado_whatsapp(visita):
    print("📲 INTENTANDO ENVIAR WHATSAPP (CONFIRMACIÓN)")

    if not visita.cliente or not visita.cliente.telefono:
        print("❌ CLIENTE SIN TELÉFONO")
        return

    telefono = normalizar_telefono_uy(visita.cliente.telefono)

    return enviar_turno_confirmado(
        telefono=telefono,
        nombre=visita.cliente.nombre,
        fecha=visita.fecha_hora.strftime("%d/%m/%Y"),
        hora=visita.fecha_hora.strftime("%H:%M"),
    )


# ==========================================================
# TEMPLATE TURNO CANCELADO 🔥 (ESTO FALTABA)
# ==========================================================

def enviar_turno_cancelado_whatsapp(visita):
    print("📲 INTENTANDO ENVIAR WHATSAPP (CANCELACIÓN)")

    if not visita.cliente or not visita.cliente.telefono:
        print("❌ CLIENTE SIN TELÉFONO")
        return

    telefono = normalizar_telefono_uy(visita.cliente.telefono)

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "template",
        "template": {
            "name": "turno_cancelado_king_barber",
            "language": {"code": "es"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": visita.cliente.nombre},
                        {
                            "type": "text",
                            "text": visita.fecha_hora.strftime("%d/%m/%Y")
                        },
                        {
                            "type": "text",
                            "text": visita.fecha_hora.strftime("%H:%M")
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(
        BASE_URL,
        json=payload,
        headers=HEADERS,
        timeout=10
    )

    print("📩 STATUS CODE:", response.status_code)
    print("📩 RESPUESTA META:", response.text)

    return response.json()
