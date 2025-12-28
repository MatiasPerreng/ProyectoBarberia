from sqlalchemy.orm import Session
from models import LoginBarberos
from core.security import verify_password

def authenticate_barbero(
    db: Session,
    email: str,
    password: str
):
    barbero = (
        db.query(LoginBarberos)
        .filter(
            LoginBarberos.email == email,
            LoginBarberos.is_active == True
        )
        .first()
    )

    if not barbero:
        return None

    if not verify_password(password, barbero.password_hash):
        return None

    return barbero
