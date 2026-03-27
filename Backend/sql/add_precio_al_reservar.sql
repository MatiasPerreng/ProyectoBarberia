-- Ejecutar una vez en la base (MySQL/MariaDB): columna para precio congelado al reservar.
ALTER TABLE visita
  ADD COLUMN precio_al_reservar DECIMAL(10,2) NULL DEFAULT NULL
  AFTER id_servicio;
