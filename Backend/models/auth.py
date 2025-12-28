from sqlalchemy import String, Integer, Index, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class LoginBarberos(Base):
    __tablename__ = "barberos"
    __table_args__ = (
        Index("email", "email", unique=True),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="barbero"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    # 🔗 FK hacia barbero (agenda / negocio)
    barbero_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("barbero.id_barbero"),
        nullable=True
    )

    # relación ORM (opcional pero muy útil)
    barbero = relationship("Barbero")
