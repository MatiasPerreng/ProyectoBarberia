from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from database import get_db
from auth_jwt import decode_access_token
from models import LoginBarberos

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login-barbero")

def get_current_login_barbero(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(token)
        barbero_id = payload.get("sub")

        if barbero_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    barbero = (
        db.query(LoginBarberos)
        .filter(
            LoginBarberos.id == int(barbero_id),
            LoginBarberos.activo == True
        )
        .first()
    )

    if not barbero:
        raise HTTPException(status_code=401, detail="Usuario no válido")

    return barbero
