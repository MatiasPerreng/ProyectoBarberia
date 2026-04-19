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
  ADD COLUMN medio_pago VARCHAR(32) NULL DEFAULT NULL AFTER estado,
  ADD COLUMN mercadopago_referencia VARCHAR(128) NULL DEFAULT NULL AFTER medio_pago,
  ADD COLUMN mercadopago_payment_id VARCHAR(64) NULL DEFAULT NULL AFTER mercadopago_referencia,
  ADD COLUMN mercadopago_receipt_url VARCHAR(512) NULL DEFAULT NULL AFTER mercadopago_payment_id,
  ADD COLUMN mercadopago_seller_activity_url VARCHAR(512) NULL DEFAULT NULL AFTER mercadopago_receipt_url,
  ADD COLUMN token_seguimiento VARCHAR(48) NULL DEFAULT NULL AFTER mercadopago_seller_activity_url;

CREATE UNIQUE INDEX uq_visita_token_seguimiento ON visita (token_seguimiento);
