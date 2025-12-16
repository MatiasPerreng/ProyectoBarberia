from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database import get_db
from auth_jwt import SECRET_KEY, ALGORITHM
from models import LoginBarberos

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_login_barbero(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    login = db.query(LoginBarberos).get(login_id)

    if not login:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return login
