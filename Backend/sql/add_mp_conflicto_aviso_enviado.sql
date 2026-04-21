-- Aviso por email si el cliente pagó en MP pero otro turno ya ocupó el horario (deduplicar con sincronizar).
ALTER TABLE visita
  ADD COLUMN mp_conflicto_aviso_enviado TINYINT(1) NOT NULL DEFAULT 0 AFTER notificado_wsp;
