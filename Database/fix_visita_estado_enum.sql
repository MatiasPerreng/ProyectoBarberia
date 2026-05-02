-- Ejecutar si la tabla `visita` quedó con estados de Mercado Pago u otros valores
-- que el código actual (sin MP) no define en el modelo SQLAlchemy.
-- Ajustá los valores del UPDATE si tu enum tenía otros nombres.

-- 1) Pasar turnos "pendientes de MP" a confirmados (o a CANCELADO si preferís)
UPDATE visita
SET estado = 'CONFIRMADO'
WHERE estado IN ('PENDIENTE_CONFIRMACION_MP', 'pendiente_confirmacion_mp');

-- 2) Cualquier otro valor raro → cancelado (revisá antes en producción)
-- UPDATE visita SET estado = 'CANCELADO' WHERE estado NOT IN ('CONFIRMADO','CANCELADO','COMPLETADO');

-- 3) Dejar el ENUM alineado con Backend/models/visita.py
ALTER TABLE visita
MODIFY COLUMN estado ENUM('CONFIRMADO','CANCELADO','COMPLETADO')
NOT NULL DEFAULT 'CONFIRMADO';
