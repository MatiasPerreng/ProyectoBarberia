from models import Visita


def generar_email_confirmacion(visita: Visita) -> str:
    cliente = visita.cliente
    servicio = visita.servicio
    barbero = visita.barbero

    fecha = visita.fecha_hora.strftime("%d/%m/%Y")
    hora = visita.fecha_hora.strftime("%H:%M")

    return f"""
Hola {cliente.nombre},

Tu turno fue confirmado con éxito ✅

📅 Fecha: {fecha}
⏰ Hora: {hora}
✂️ Servicio: {servicio.nombre}
👤 Barbero: {barbero.nombre}

Te esperamos en la barbería.

Saludos,
Barbería
"""
