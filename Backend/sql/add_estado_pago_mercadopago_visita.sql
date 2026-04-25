-- Mercado Pago (agenda): separar estado del turno y estado del pago.
-- Ejecutar si ya habías aplicado add_mercadopago_visita.sql antes de este cambio.

ALTER TABLE visita
  ADD COLUMN estado_pago ENUM(
    'PENDIENTE',
    'APROBADO',
    'RECHAZADO',
    'REQUIERE_ACCION'
  ) NULL DEFAULT NULL AFTER medio_pago,
  ADD COLUMN pago_tardio TINYINT(1) NOT NULL DEFAULT 0 AFTER estado_pago;

UPDATE visita
SET estado_pago = CASE
  WHEN mercadopago_payment_id IS NOT NULL AND estado IN ('CONFIRMADO', 'COMPLETADO') THEN 'APROBADO'
  WHEN medio_pago = 'mercadopago' AND estado = 'PENDIENTE_CONFIRMACION_MP' THEN 'PENDIENTE'
  WHEN medio_pago = 'mercadopago' AND estado = 'CANCELADO' THEN 'PENDIENTE'
  ELSE estado_pago
END
WHERE medio_pago = 'mercadopago' OR mercadopago_payment_id IS NOT NULL;
