-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         8.0.43 - MySQL Community Server - GPL
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.14.0.7165
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para barber
CREATE DATABASE IF NOT EXISTS `barber` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `barber`;

-- Volcando estructura para tabla barber.barbero
CREATE TABLE IF NOT EXISTS `barbero` (
  `id_barbero` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `foto_url` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_barbero`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.barbero: ~4 rows (aproximadamente)
INSERT INTO `barbero` (`id_barbero`, `nombre`, `created_at`, `foto_url`, `activo`) VALUES
	(3, 'Enzo', '2025-12-14 15:38:28', '/media/barberos/barbero_3.png', 1),
	(43, 'ELNUEVO', '2025-12-28 23:18:37', '/media/barberos/barbero_43.png', 1),
	(54, 'Jona', '2025-12-29 00:09:51', '/media/barberos/barbero_54.png', 1);

-- Volcando estructura para tabla barber.barberos
CREATE TABLE IF NOT EXISTS `barberos` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL DEFAULT 'barbero',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `barbero_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_barberos_email` (`email`),
  KEY `fk_barberos_barbero` (`barbero_id`),
  CONSTRAINT `fk_barberos_barbero` FOREIGN KEY (`barbero_id`) REFERENCES `barbero` (`id_barbero`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.barberos: ~3 rows (aproximadamente)
INSERT INTO `barberos` (`id`, `nombre`, `email`, `password_hash`, `role`, `is_active`, `barbero_id`) VALUES
	(3, 'Enzo', 'enzo@barberia.com', '$2b$12$qW0gCsugpE6EaVlQCjMm3eSyA/Z2sncP7RY7BOi6RUtqcPR3hXh9u', 'admin', 1, 3),
	(20, 'ELNUEVO', 'EN@barberia.com', '$2b$12$4VcNieWN5ePf.7v0HX0R8.rgyzjn8ummTrVBEBsVFLdND8MNWYU22', 'barbero', 1, 43),
	(24, 'Jona', 'j@barberia.com', '$2b$12$eiOjlEpe6jKtkVkl4WQ2Cu8KE7Gtrsn5VeCmYOTGuQ5neESIDnzQm', 'barbero', 1, 54);

-- Volcando estructura para tabla barber.cliente
CREATE TABLE IF NOT EXISTS `cliente` (
  `id_cliente` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.cliente: ~34 rows (aproximadamente)
INSERT INTO `cliente` (`id_cliente`, `nombre`, `apellido`, `telefono`, `email`, `created_at`) VALUES
	(1, 'Matias', '', NULL, 'csmatiperreng@gmail.com', '2025-12-14 18:34:26'),
	(2, 'Matias', '', NULL, 'a@g', '2025-12-14 18:39:43'),
	(3, 'Roberto', '', NULL, 'rperez@gmail.com', '2025-12-14 18:42:53'),
	(4, 'rosario', '', NULL, 'as@gmail.com', '2025-12-14 19:06:59'),
	(5, 'romina', '', NULL, 'romediana@maqwe', '2025-12-14 19:11:23'),
	(6, 'jacinto', '', NULL, 'qma@gmail.com', '2025-12-14 19:14:05'),
	(7, 'Matias', '', NULL, 'asesa@gmail.com', '2025-12-14 19:50:04'),
	(8, 'Matias', '', '0981231', 'mp@gmail.com', '2025-12-22 19:40:39'),
	(9, 'Manuel', '', '2131321321', 'mv@gmail.com', '2025-12-22 20:03:57'),
	(10, 'Matiaw', '', '095065060', 'csmatiperreng@gmail.com', '2025-12-22 20:36:06'),
	(11, 'Rodri', '', '095921321', 'rodridls@gmail.com', '2025-12-22 21:31:44'),
	(12, 'ase', '', '12321321', 'a@gmail.com', '2025-12-22 21:51:32'),
	(13, 'a', '', '12321321', 'a@gmail.com', '2025-12-22 21:56:05'),
	(14, 'S', '', '091232131', 'aver@gmail.com', '2025-12-22 22:05:30'),
	(15, '1', '', '09122322', 'csmatiperreng@live.com', '2025-12-22 22:26:28'),
	(16, 'Matias', '', '095064060', 'csmatiperreng@gmail.com', '2025-12-23 15:51:02'),
	(17, 'Adrian', '', '03221321', 'adrian@gmail.com', '2025-12-23 15:54:51'),
	(18, 'Lolo', '', '01232131', 'laur@gmail.com', '2025-12-24 00:39:31'),
	(19, 'Francisco', 'Ferre', '09623432', 'csmatiperreng@gmail.com', '2025-12-24 12:15:02'),
	(20, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-24 20:39:24'),
	(21, 'Kike ', 'Olivera', '092123452', 'matiperreng2019@gmail.com', '2025-12-24 20:46:12'),
	(22, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-24 20:52:13'),
	(23, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-25 20:08:21'),
	(24, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-25 20:19:44'),
	(25, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-25 20:22:35'),
	(26, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-25 20:25:38'),
	(27, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-26 02:42:17'),
	(28, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-27 17:22:10'),
	(29, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-27 19:55:38'),
	(30, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-28 00:02:03'),
	(31, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-28 18:27:44'),
	(32, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-28 20:38:59'),
	(33, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-28 22:52:14'),
	(34, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-28 23:19:52');

-- Volcando estructura para tabla barber.horario_barbero
CREATE TABLE IF NOT EXISTS `horario_barbero` (
  `id_horario` int unsigned NOT NULL AUTO_INCREMENT,
  `id_barbero` int unsigned NOT NULL,
  `dia_semana` tinyint NOT NULL COMMENT '1=Lunes ... 7=Domingo',
  `hora_desde` time NOT NULL,
  `hora_hasta` time NOT NULL,
  `fecha_desde` date NOT NULL,
  `fecha_hasta` date NOT NULL,
  PRIMARY KEY (`id_horario`),
  KEY `fk_horario_barbero` (`id_barbero`),
  CONSTRAINT `fk_horario_barbero` FOREIGN KEY (`id_barbero`) REFERENCES `barbero` (`id_barbero`) ON DELETE CASCADE,
  CONSTRAINT `chk_hora_valida` CHECK ((`hora_desde` < `hora_hasta`))
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.horario_barbero: ~7 rows (aproximadamente)
INSERT INTO `horario_barbero` (`id_horario`, `id_barbero`, `dia_semana`, `hora_desde`, `hora_hasta`, `fecha_desde`, `fecha_hasta`) VALUES
	(1, 3, 1, '09:00:00', '18:00:00', '2026-01-05', '2026-01-26'),
	(6, 3, 2, '09:00:00', '18:00:00', '2026-01-06', '2026-01-27'),
	(7, 3, 3, '09:00:00', '18:00:00', '2026-01-07', '2026-01-28'),
	(8, 3, 6, '09:00:00', '18:00:00', '2026-01-10', '2026-01-31'),
	(10, 43, 2, '09:00:00', '11:00:00', '2026-01-06', '2026-01-27'),
	(14, 43, 1, '08:00:00', '21:36:00', '2026-02-02', '2026-02-23'),
	(15, 43, 2, '08:00:00', '21:36:00', '2026-02-03', '2026-02-24'),
	(16, 43, 3, '08:00:00', '21:36:00', '2026-02-04', '2026-02-25'),
	(17, 43, 4, '08:00:00', '21:36:00', '2026-02-05', '2026-02-26'),
	(18, 43, 5, '08:00:00', '21:36:00', '2026-02-06', '2026-02-27');

-- Volcando estructura para tabla barber.horario_excepcion
CREATE TABLE IF NOT EXISTS `horario_excepcion` (
  `id_excepcion` int NOT NULL AUTO_INCREMENT,
  `id_barbero` int unsigned NOT NULL,
  `fecha` date NOT NULL,
  `hora_desde` time DEFAULT NULL,
  `hora_hasta` time DEFAULT NULL,
  `tipo` enum('cierre','horario_especial') NOT NULL,
  PRIMARY KEY (`id_excepcion`),
  KEY `id_barbero` (`id_barbero`),
  CONSTRAINT `horario_excepcion_ibfk_1` FOREIGN KEY (`id_barbero`) REFERENCES `barbero` (`id_barbero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.horario_excepcion: ~0 rows (aproximadamente)

-- Volcando estructura para tabla barber.servicio
CREATE TABLE IF NOT EXISTS `servicio` (
  `id_servicio` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `duracion_min` int unsigned NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `imagen` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.servicio: ~3 rows (aproximadamente)
INSERT INTO `servicio` (`id_servicio`, `nombre`, `duracion_min`, `precio`, `activo`, `imagen`) VALUES
	(1, 'Corte rasurado', 45, 10.00, 1, 'corte-rasurado.jpg'),
	(2, 'Color', 90, 1300.00, 1, 'mechas.jpeg'),
	(3, 'Corte + Barba', 60, 400.00, 1, 'barba.jpg');

-- Volcando estructura para tabla barber.visita
CREATE TABLE IF NOT EXISTS `visita` (
  `id_visita` int unsigned NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL,
  `estado` enum('reservado','cancelado','completado') DEFAULT 'reservado',
  `id_cliente` int unsigned NOT NULL,
  `id_barbero` int unsigned NOT NULL,
  `id_servicio` int unsigned NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_visita`),
  KEY `fk_visita_cliente` (`id_cliente`),
  KEY `fk_visita_barbero` (`id_barbero`),
  KEY `fk_visita_servicio` (`id_servicio`),
  CONSTRAINT `fk_visita_barbero` FOREIGN KEY (`id_barbero`) REFERENCES `barbero` (`id_barbero`),
  CONSTRAINT `fk_visita_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`),
  CONSTRAINT `fk_visita_servicio` FOREIGN KEY (`id_servicio`) REFERENCES `servicio` (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.visita: ~2 rows (aproximadamente)
INSERT INTO `visita` (`id_visita`, `fecha_hora`, `estado`, `id_cliente`, `id_barbero`, `id_servicio`, `created_at`) VALUES
	(2, '2025-12-30 10:00:00', 'reservado', 33, 3, 1, '2025-12-28 22:52:14'),
	(3, '2025-12-29 09:00:00', 'reservado', 34, 43, 1, '2025-12-28 23:19:52');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
