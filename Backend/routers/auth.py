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

#----------------------------------------------------------------------------------------------------------------------
# LOGIN BARBERO
#----------------------------------------------------------------------------------------------------------------------

@router.post(
    "/login-barbero",
    response_model=LoginBarberoOut
)
def login_barbero(
    data: LoginBarberoIn,
    db: Session = Depends(get_db)
):
    login = authenticate_barbero(db, data.email, data.password)

    if not login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    # El token identifica al LOGIN (no al barbero directamente)
    token = create_access_token({
        "sub": str(login.id_login)
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "barbero": {
            "id_barbero": login.barbero.id_barbero,
            "nombre": login.barbero.nombre
        }
    }

#----------------------------------------------------------------------------------------------------------------------
# ME (BARBERO LOGUEADO)
#----------------------------------------------------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=BarberoAuthOut
)
def me(
    login = Depends(get_current_login_barbero)
):
    """
    Devuelve el barbero asociado al login actual.
    Se usa para:
    - refrescar sesión
    - mantener login en frontend
    """
    return {
        "id_barbero": login.barbero.id_barbero,
        "nombre": login.barbero.nombre
    }
