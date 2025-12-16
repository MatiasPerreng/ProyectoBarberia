from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import LoginBarberoIn, LoginBarberoOut
from crud.login_barbero import authenticate_login_barbero
from auth_jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginBarberoOut)
def login_barbero(
    data: LoginBarberoIn,
    db: Session = Depends(get_db)
):
    login = authenticate_login_barbero(db, data.email, data.password)

    if not login:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({
        "sub": str(login.id),
        "id_barbero": login.id_barbero,
        "nombre": login.nombre
    })

    return {"access_token": token}
