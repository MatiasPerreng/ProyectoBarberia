-- Mercado Pago (agenda): re-agendado por pago tardío en estado REQUIERE_ACCION.
-- Ejecutar si la base ya tenía las columnas de Mercado Pago creadas.

ALTER TABLE visita
  ADD COLUMN mp_reagendar_aviso_enviado TINYINT(1) NOT NULL DEFAULT 0 AFTER mp_conflicto_aviso_enviado,
  ADD COLUMN reagendar_token_hash VARCHAR(64) NULL DEFAULT NULL AFTER token_seguimiento,
  ADD COLUMN reagendar_token_expires_at DATETIME NULL DEFAULT NULL AFTER reagendar_token_hash,
  ADD COLUMN reagendar_token_used_at DATETIME NULL DEFAULT NULL AFTER reagendar_token_expires_at;

CREATE UNIQUE INDEX uq_visita_reagendar_token_hash ON visita (reagendar_token_hash);
