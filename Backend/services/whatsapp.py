# services/whatsapp.py

import os
import requests
from dotenv import load_dotenv

from core.telefonos import normalizar_telefono_uy

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

BASE_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

print("🔧 WHATSAPP CONFIG")
print("TOKEN CARGADO:", "SI" if WHATSAPP_TOKEN else "NO")
print("PHONE_NUMBER_ID:", PHONE_NUMBER_ID)
print("BASE_URL:", BASE_URL)


# ==========================================================
# TEMPLATE HELLO WORLD (PRUEBA)
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
            "language": {
                "code": "en_US"
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            BASE_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        print("📩 STATUS CODE:", response.status_code)
        print("📩 RESPUESTA META:", response.text)

        return response.json()

    except Exception as e:
        print("❌ ERROR EN REQUEST WHATSAPP:", e)
        return None


# ==========================================================
# TEMPLATE REAL (CUANDO LO TENGAS APROBADO)
# ==========================================================

def enviar_turno_confirmado(
    telefono: str,
    nombre: str,
    fecha: str,
    hora: str
):
    print("📲 ENVIAR TURNO CONFIRMADO (TEMPLATE REAL)")
    print("📞 TELEFONO:", telefono)
    print("👤 NOMBRE:", nombre)
    print("📅 FECHA:", fecha)
    print("⏰ HORA:", hora)

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "template",
        "template": {
            "name": "turno_confirmado",
            "language": {
                "code": "es"
            },
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

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            BASE_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        print("📩 STATUS CODE:", response.status_code)
        print("📩 RESPUESTA META:", response.text)

        return response.json()

    except Exception as e:
        print("❌ ERROR EN REQUEST WHATSAPP:", e)
        return None


# ==========================================================
# 🔥 FUNCIÓN PUENTE (LA QUE USA routers/visitas.py)
# ==========================================================

def enviar_turno_confirmado_whatsapp(visita):
    """
    Función que importa routers/visitas.py.
    Recibe la visita completa, normaliza el teléfono
    y decide qué template enviar.
    """

    print("📲 INTENTANDO ENVIAR WHATSAPP DESDE VISITA")

    if not visita.cliente:
        print("❌ VISITA SIN CLIENTE")
        return None

    if not visita.cliente.telefono:
        print("❌ CLIENTE SIN TELEFONO")
        return None

    telefono_original = visita.cliente.telefono
    telefono = normalizar_telefono_uy(telefono_original)

    print("📞 TELEFONO ORIGINAL:", telefono_original)
    print("📞 TELEFONO NORMALIZADO:", telefono)

    # 🔥 POR AHORA USAMOS HELLO WORLD
    return enviar_template_hello_world(telefono)

    # 👉 Cuando tengas el template real:
    #
    # nombre = visita.cliente.nombre
    # fecha = visita.fecha_hora.strftime("%d/%m/%Y")
    # hora = visita.fecha_hora.strftime("%H:%M")
    #
    # return enviar_turno_confirmado(
    #     telefono=telefono,
    #     nombre=nombre,
    #     fecha=fecha,
    #     hora=hora
    # )
