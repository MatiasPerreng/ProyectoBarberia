-- Si ya migraste con add_mercadopago_visita.sql antiguo (columna mercadopago_referencia),
-- ejecutá esto una vez: el ID de operación queda solo en mercadopago_payment_id.

ALTER TABLE visita DROP COLUMN mercadopago_referencia;
