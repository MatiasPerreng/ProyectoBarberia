from sqlalchemy import String, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class LoginBarberos(Base):
    __tablename__ = 'barberos'
    __table_args__ = (
        Index('email', 'email', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
