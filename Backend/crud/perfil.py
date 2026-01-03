from sqlalchemy.orm import Session
from passlib.context import CryptContext

from schemas.perfil import PerfilUpdateIn
from models.barbero import Barbero

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def update_perfil(
    db: Session,
    barbero: Barbero,
    data: PerfilUpdateIn
):
    # -------------------------
    # BARBERO
    # -------------------------
    if data.nombre is not None:
        barbero.nombre = data.nombre

    if data.foto_url is not None:
        barbero.foto_url = data.foto_url

    # -------------------------
    # LOGIN
    # -------------------------
    if barbero.login:
        if data.email is not None:
            barbero.login.email = data.email

        if data.password:
            barbero.login.password = pwd_context.hash(data.password)

    db.commit()
    db.refresh(barbero)
    return barbero
