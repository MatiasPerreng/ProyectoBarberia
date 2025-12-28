from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import LoginBarberoIn, LoginBarberoOut, BarberoAuthOut
from crud.auth import authenticate_barbero
from auth_jwt import create_access_token
from core.dependencias import get_current_login_barbero

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@router.post(
    "/login-barbero",
    response_model=LoginBarberoOut
)
def login_barbero(
    data: LoginBarberoIn,
    db: Session = Depends(get_db)
):
    barbero = authenticate_barbero(db, data.email, data.password)

    if not barbero:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    token = create_access_token({
        "sub": str(barbero.id),
        "role": barbero.role
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "barbero": {
            "id_barbero": barbero.id,
            "nombre": barbero.nombre
        }
    }

# ---------------------------------------------------------
# ME (usuario logueado)
# ---------------------------------------------------------

@router.get(
    "/me",
    response_model=BarberoAuthOut
)
def me(
    barbero = Depends(get_current_login_barbero)
):
    return {
        "id_barbero": barbero.id,
        "nombre": barbero.nombre,
        "role": barbero.role
    }
