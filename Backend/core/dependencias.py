from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

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
        login_id = payload.get("sub")

        if login_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    login = db.query(LoginBarberos).filter(
        LoginBarberos.id_login == int(login_id),
        LoginBarberos.activo == True
    ).first()

    if not login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    return login
