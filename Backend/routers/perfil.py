from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from core.dependencias import get_current_login_barbero
from schemas.perfil import PerfilOut, PerfilUpdateIn
from crud.perfil import update_perfil

router = APIRouter(
    prefix="/perfil",
    tags=["Perfil"]
)


@router.get("/me", response_model=PerfilOut)
def get_mi_perfil(
    login=Depends(get_current_login_barbero)
):
    barbero = login.barbero

    return {
        "id_barbero": barbero.id_barbero,
        "nombre": barbero.nombre,
        "email": login.email,
        "foto_url": barbero.foto_url
    }


@router.put("/me", response_model=PerfilOut)
def update_mi_perfil(
    data: PerfilUpdateIn,
    db: Session = Depends(get_db),
    login=Depends(get_current_login_barbero)
):
    barbero = update_perfil(db, login.barbero, data)

    return {
        "id_barbero": barbero.id_barbero,
        "nombre": barbero.nombre,
        "email": barbero.login.email,
        "foto_url": barbero.foto_url
    }
