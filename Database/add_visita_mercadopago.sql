-- Mercado Pago Checkout Pro sobre tabla `visita` (equivalente a "pedido" en otros proyectos).
-- Ejecutar una vez en MySQL/MariaDB sobre la base `barber` (o la que uses).

ALTER TABLE visita
  MODIFY COLUMN estado ENUM(
    'CONFIRMADO',
    'CANCELADO',
    'COMPLETADO',
    'PENDIENTE_CONFIRMACION_MP'
  ) NOT NULL DEFAULT 'CONFIRMADO';

ALTER TABLE visita
  ADD COLUMN medio_pago VARCHAR(24) NOT NULL DEFAULT 'EFECTIVO' AFTER estado,
  ADD COLUMN mp_preference_id VARCHAR(255) NULL DEFAULT NULL AFTER medio_pago,
  ADD COLUMN mp_payment_id VARCHAR(255) NULL DEFAULT NULL,
  ADD COLUMN mp_status VARCHAR(64) NULL DEFAULT NULL,
  ADD COLUMN token_seguimiento VARCHAR(64) NULL DEFAULT NULL,
  ADD UNIQUE INDEX ux_visita_token_seguimiento (token_seguimiento);
