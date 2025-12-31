# routers/test.py

from fastapi import APIRouter
from services.whatsapp import enviar_template_hello_world

router = APIRouter(
    prefix="/test",
    tags=["Test"]
)


@router.post("/whatsapp")
def test_whatsapp():
    return enviar_template_hello_world("59895064060")
