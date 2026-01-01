from fastapi import APIRouter
from services.whatsapp import enviar_turno_confirmado

router = APIRouter(
    prefix="/test",
    tags=["Test"]
)

@router.post("/whatsapp")
def test_whatsapp():
    return enviar_turno_confirmado(
        telefono="59895064060",
        nombre="Matías",
        fecha="15/01/2026",
        hora="14:30"
    )
