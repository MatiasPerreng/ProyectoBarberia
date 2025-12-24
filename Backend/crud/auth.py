from sqlalchemy.orm import Session

from models import LoginBarberos
from security import verify_password


def get_login_by_email(db: Session, email: str):
    return (
        db.query(LoginBarberos)
        .filter(
            LoginBarberos.email == email,
            LoginBarberos.activo == True
        )
        .first()
    )


def authenticate_barbero(
    db: Session,
    email: str,
    password: str
):
    login = get_login_by_email(db, email)

    if not login:
        return None

    if not verify_password(password, login.password_hash):
        return None

    return login
