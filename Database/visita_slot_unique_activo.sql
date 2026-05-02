-- =============================================================================
-- Cancelados no cuentan como duplicado (barbero + fecha_hora).
-- Script idempotente: no falla si ya borraste uk_barbero_fecha o ya migraste.
-- Tabla: visita (singular).
-- =============================================================================
-- (Opcional) Ver índices actuales:
-- SHOW INDEX FROM visita;

SET @db = DATABASE();

-- 1) Quitar el UNIQUE viejo solo si existe (evita SQL 1091)
SET @ddl := (
  SELECT IF(
    EXISTS (
      SELECT 1 FROM information_schema.statistics
      WHERE table_schema = @db AND table_name = 'visita' AND index_name = 'uk_barbero_fecha'
    ),
    'ALTER TABLE visita DROP INDEX uk_barbero_fecha',
    'SELECT ''Migración: no hay índice uk_barbero_fecha (omitido).'' AS paso_1'
  )
);
PREPARE ps FROM @ddl;
EXECUTE ps;
DEALLOCATE PREPARE ps;

-- 2) Columna generada solo si aún no está
SET @ddl := (
  SELECT IF(
    EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_schema = @db AND table_name = 'visita' AND column_name = 'uq_slot_activo'
    ),
    'SELECT ''Migración: uq_slot_activo ya existe (omitido).'' AS paso_2',
    'ALTER TABLE visita ADD COLUMN uq_slot_activo VARCHAR(96) NULL GENERATED ALWAYS AS (IF(estado = ''CANCELADO'', NULL, CONCAT_WS(''|'', id_barbero, DATE_FORMAT(fecha_hora, ''%Y-%m-%d %H:%i:%s'')))) STORED'
  )
);
PREPARE ps FROM @ddl;
EXECUTE ps;
DEALLOCATE PREPARE ps;

-- 3) UNIQUE sobre la columna generada solo si falta el índice
SET @ddl := (
  SELECT IF(
    EXISTS (
      SELECT 1 FROM information_schema.statistics
      WHERE table_schema = @db AND table_name = 'visita' AND index_name = 'ux_visita_slot_activo'
    ),
    'SELECT ''Migración: ux_visita_slot_activo ya existe (omitido).'' AS paso_3',
    'CREATE UNIQUE INDEX ux_visita_slot_activo ON visita (uq_slot_activo)'
  )
);
PREPARE ps FROM @ddl;
EXECUTE ps;
DEALLOCATE PREPARE ps;
