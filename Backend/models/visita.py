from typing import Optional
import datetime
import decimal

from sqlalchemy import DateTime, DECIMAL, Enum, ForeignKeyConstraint, Index, String, TIMESTAMP, text, Boolean
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Visita(Base):
    __tablename__ = 'visita'
    __table_args__ = (
        ForeignKeyConstraint(['id_barbero'], ['barbero.id_barbero'], name='fk_visita_barbero'),
        ForeignKeyConstraint(['id_cliente'], ['cliente.id_cliente'], name='fk_visita_cliente'),
        ForeignKeyConstraint(['id_servicio'], ['servicio.id_servicio'], name='fk_visita_servicio'),
        Index('fk_visita_barbero', 'id_barbero'),
        Index('fk_visita_cliente', 'id_cliente'),
        Index('fk_visita_servicio', 'id_servicio'),
    )

    id_visita: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    fecha_hora: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    id_cliente: Mapped[int] = mapped_column(INTEGER, nullable=False)
    id_barbero: Mapped[int] = mapped_column(INTEGER, nullable=False)
    id_servicio: Mapped[int] = mapped_column(INTEGER, nullable=False)

    # Precio del servicio al momento de la reserva (estad?sticas no cambian si se edita el servicio)
    precio_al_reservar: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True
    )
    
    # Campo para controlar el env?o de WhatsApp
    notificado_wsp: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        server_default=text("0")  # En MySQL/MariaDB 0 es False
    )

    # Evita reenviar el mail de "pagaste pero el horario ya estaba tomado" (sync + creación de la reserva que ocupa).
    mp_conflicto_aviso_enviado: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0"),
    )
    mp_reagendar_aviso_enviado: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0"),
    )

    estado: Mapped[Optional[str]] = mapped_column(
        Enum(
            "CONFIRMADO",
            "PENDIENTE_CONFIRMACION_MP",
            "CANCELADO",
            "COMPLETADO",
        ),
        server_default=text("'CONFIRMADO'"),
    )

    medio_pago: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    estado_pago: Mapped[Optional[str]] = mapped_column(
        Enum(
            "PENDIENTE",
            "APROBADO",
            "RECHAZADO",
            "REQUIERE_ACCION",
        ),
        nullable=True,
    )
    pago_tardio: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0"),
    )
    mercadopago_payment_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    mercadopago_receipt_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    mercadopago_seller_activity_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    token_seguimiento: Mapped[Optional[str]] = mapped_column(String(48), nullable=True, unique=True)
    reagendar_token_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, unique=True)
    reagendar_token_expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    reagendar_token_used_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP')
    )

    # Relaciones
    barbero: Mapped["Barbero"] = relationship("Barbero", back_populates="visita")
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="visita")
    servicio: Mapped["Servicio"] = relationship("Servicio", back_populates="visita")