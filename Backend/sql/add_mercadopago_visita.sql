-- Mercado Pago (agenda): columnas y estado PENDIENTE_CONFIRMACION_MP
-- Ejecutar en la base del proyecto barbería antes de usar el cobro anticipado.

ALTER TABLE visita
  MODIFY COLUMN estado ENUM(
    'CONFIRMADO',
    'PENDIENTE_CONFIRMACION_MP',
    'CANCELADO',
    'COMPLETADO'
  ) NOT NULL DEFAULT 'CONFIRMADO';

ALTER TABLE visita
  ADD COLUMN mp_conflicto_aviso_enviado TINYINT(1) NOT NULL DEFAULT 0 AFTER notificado_wsp,
  ADD COLUMN mp_reagendar_aviso_enviado TINYINT(1) NOT NULL DEFAULT 0 AFTER mp_conflicto_aviso_enviado,
  ADD COLUMN medio_pago VARCHAR(32) NULL DEFAULT NULL AFTER estado,
  ADD COLUMN estado_pago ENUM(
    'PENDIENTE',
    'APROBADO',
    'RECHAZADO',
    'REQUIERE_ACCION'
  ) NULL DEFAULT NULL AFTER medio_pago,
  ADD COLUMN pago_tardio TINYINT(1) NOT NULL DEFAULT 0 AFTER estado_pago,
  ADD COLUMN mercadopago_payment_id VARCHAR(64) NULL DEFAULT NULL AFTER pago_tardio,
  ADD COLUMN mercadopago_receipt_url VARCHAR(512) NULL DEFAULT NULL AFTER mercadopago_payment_id,
  ADD COLUMN mercadopago_seller_activity_url VARCHAR(512) NULL DEFAULT NULL AFTER mercadopago_receipt_url,
  ADD COLUMN token_seguimiento VARCHAR(48) NULL DEFAULT NULL AFTER mercadopago_seller_activity_url,
  ADD COLUMN reagendar_token_hash VARCHAR(64) NULL DEFAULT NULL AFTER token_seguimiento,
  ADD COLUMN reagendar_token_expires_at DATETIME NULL DEFAULT NULL AFTER reagendar_token_hash,
  ADD COLUMN reagendar_token_used_at DATETIME NULL DEFAULT NULL AFTER reagendar_token_expires_at;

CREATE UNIQUE INDEX uq_visita_token_seguimiento ON visita (token_seguimiento);
CREATE UNIQUE INDEX uq_visita_reagendar_token_hash ON visita (reagendar_token_hash);
