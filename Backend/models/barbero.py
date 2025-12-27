from typing import Optional, List
import datetime

from sqlalchemy import String, TIMESTAMP, text, Boolean
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Barbero(Base):
    __tablename__ = "barbero"

    id_barbero: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    # 👇 NUEVO ESTADO
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1")
    )

    foto_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )

    horario_barbero: Mapped[List["HorarioBarbero"]] = relationship(
        "HorarioBarbero",
        back_populates="barbero",
        cascade="all, delete"
    )

    horario_excepcion: Mapped[List["HorarioExcepcion"]] = relationship(
        "HorarioExcepcion",
        back_populates="barbero",
        cascade="all, delete"
    )

    visita: Mapped[List["Visita"]] = relationship(
        "Visita",
        back_populates="barbero"
    )
