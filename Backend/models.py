from typing import Optional
import datetime
import decimal

from sqlalchemy import CheckConstraint, DECIMAL, DateTime, Enum, ForeignKeyConstraint, Index, String, TIMESTAMP, Time, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Barbero(Base):
    __tablename__ = 'barbero'

    id_barbero: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    horario_barbero: Mapped[list['HorarioBarbero']] = relationship('HorarioBarbero', back_populates='barbero')
    visita: Mapped[list['Visita']] = relationship('Visita', back_populates='barbero')


class Cliente(Base):
    __tablename__ = 'cliente'

    id_cliente: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    visita: Mapped[list['Visita']] = relationship('Visita', back_populates='cliente')


class Servicio(Base):
    __tablename__ = 'servicio'

    id_servicio: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    duracion_min: Mapped[int] = mapped_column(INTEGER, nullable=False)
    precio: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    activo: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))

    visita: Mapped[list['Visita']] = relationship('Visita', back_populates='servicio')


class HorarioBarbero(Base):
    __tablename__ = 'horario_barbero'
    __table_args__ = (
        CheckConstraint('(`hora_desde` < `hora_hasta`)', name='chk_hora_valida'),
        ForeignKeyConstraint(['id_barbero'], ['barbero.id_barbero'], ondelete='CASCADE', name='fk_horario_barbero'),
        Index('fk_horario_barbero', 'id_barbero')
    )

    id_horario: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    id_barbero: Mapped[int] = mapped_column(INTEGER, nullable=False)
    dia_semana: Mapped[int] = mapped_column(TINYINT, nullable=False, comment='1=Lunes ... 7=Domingo')
    hora_desde: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    hora_hasta: Mapped[datetime.time] = mapped_column(Time, nullable=False)

    barbero: Mapped['Barbero'] = relationship('Barbero', back_populates='horario_barbero')


class Visita(Base):
    __tablename__ = 'visita'
    __table_args__ = (
        ForeignKeyConstraint(['id_barbero'], ['barbero.id_barbero'], name='fk_visita_barbero'),
        ForeignKeyConstraint(['id_cliente'], ['cliente.id_cliente'], name='fk_visita_cliente'),
        ForeignKeyConstraint(['id_servicio'], ['servicio.id_servicio'], name='fk_visita_servicio'),
        Index('fk_visita_barbero', 'id_barbero'),
        Index('fk_visita_cliente', 'id_cliente'),
        Index('fk_visita_servicio', 'id_servicio')
    )

    id_visita: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    fecha_hora: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    id_cliente: Mapped[int] = mapped_column(INTEGER, nullable=False)
    id_barbero: Mapped[int] = mapped_column(INTEGER, nullable=False)
    id_servicio: Mapped[int] = mapped_column(INTEGER, nullable=False)
    estado: Mapped[Optional[str]] = mapped_column(Enum('reservado', 'cancelado', 'completado'), server_default=text("'reservado'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    barbero: Mapped['Barbero'] = relationship('Barbero', back_populates='visita')
    cliente: Mapped['Cliente'] = relationship('Cliente', back_populates='visita')
    servicio: Mapped['Servicio'] = relationship('Servicio', back_populates='visita')
