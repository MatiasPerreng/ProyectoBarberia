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
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.barbero: ~2 rows (aproximadamente)
INSERT INTO `barbero` (`id_barbero`, `nombre`, `created_at`, `foto_url`, `activo`) VALUES
	(3, 'Enzo', '2025-12-14 15:38:28', 'barbero_3_1767279334.jpg', 1),
	(73, 'Nacho', '2025-12-31 14:43:57', 'barbero_73_1767279331.jpg', 1),
	(77, 'jose', '2026-01-01 14:55:41', 'barbero_77_1767279342.png', 1);

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
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.barberos: ~3 rows (aproximadamente)
INSERT INTO `barberos` (`id`, `nombre`, `email`, `password_hash`, `role`, `is_active`, `barbero_id`) VALUES
	(3, 'Enzo', 'enzo@kingbarber.com', '$2b$12$qW0gCsugpE6EaVlQCjMm3eSyA/Z2sncP7RY7BOi6RUtqcPR3hXh9u', 'admin', 1, 3),
	(34, 'Nacho', 'nacho@kingbarber.com', '$2b$12$Mzl8Ey1ycv3OsR/ginwSoOoVZgfNL97aZ/L58PMSnyVTVDSa2HGtO', 'admin', 1, 73),
	(36, 'jose', 'jose@kingbarber.com', '$2b$12$P3x9E5UcSNeuMA2UZBbZSeggHvT0NDM/npDRJXIR/sLK2BdfQw0da', 'barbero', 1, 77);

-- Volcando estructura para tabla barber.cliente
CREATE TABLE IF NOT EXISTS `cliente` (
  `id_cliente` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.cliente: ~26 rows (aproximadamente)
INSERT INTO `cliente` (`id_cliente`, `nombre`, `apellido`, `telefono`, `email`, `created_at`) VALUES
	(1, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 12:36:04'),
	(2, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 12:36:40'),
	(3, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 14:20:46'),
	(4, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 14:21:27'),
	(5, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 14:53:00'),
	(6, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 15:09:49'),
	(7, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 16:16:33'),
	(8, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 16:22:14'),
	(9, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 16:24:06'),
	(10, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 16:25:48'),
	(11, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 16:26:06'),
	(12, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 16:28:48'),
	(13, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 16:40:05'),
	(14, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 17:00:38'),
	(15, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2025-12-31 22:52:45'),
	(16, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 14:58:11'),
	(17, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 14:58:20'),
	(18, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 14:58:47'),
	(19, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 14:59:45'),
	(20, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 15:00:10'),
	(21, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 15:01:56'),
	(22, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 15:04:30'),
	(23, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 15:07:24'),
	(24, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 15:08:41'),
	(25, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 15:10:04'),
	(26, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-01 15:19:19');

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
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.horario_barbero: ~4 rows (aproximadamente)
INSERT INTO `horario_barbero` (`id_horario`, `id_barbero`, `dia_semana`, `hora_desde`, `hora_hasta`, `fecha_desde`, `fecha_hasta`) VALUES
	(30, 3, 1, '09:00:00', '18:00:00', '2025-12-01', '2026-01-26'),
	(35, 73, 1, '07:16:00', '19:16:00', '2025-12-01', '2026-12-28'),
	(36, 73, 2, '07:16:00', '19:16:00', '2025-12-02', '2026-12-29'),
	(37, 73, 3, '07:16:00', '19:16:00', '2025-12-03', '2026-12-30'),
	(38, 77, 1, '09:00:00', '18:00:00', '2025-12-29', '2026-07-06'),
	(39, 77, 2, '09:00:00', '18:00:00', '2025-12-30', '2026-07-07'),
	(40, 77, 3, '09:00:00', '18:00:00', '2025-12-31', '2026-07-08');

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
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.servicio: ~3 rows (aproximadamente)
INSERT INTO `servicio` (`id_servicio`, `nombre`, `duracion_min`, `precio`, `activo`, `imagen`) VALUES
	(1, 'Corte rasurado', 45, 410.00, 1, '0a646127-ed2b-4f25-9c4e-cfe4975c22f0.jpg'),
	(2, 'Color', 90, 1300.00, 1, 'e7b8fc01-4ab0-443a-a116-98683d0d968b.jpeg'),
	(3, 'Corte + Barba', 60, 400.00, 1, '636eff8a-e9c7-4f02-b9d0-11db74483127.jpg');

-- Volcando estructura para tabla barber.visita
CREATE TABLE IF NOT EXISTS `visita` (
  `id_visita` int unsigned NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL,
  `estado` enum('CONFIRMADO','CANCELADO','COMPLETADO') NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.visita: ~1 rows (aproximadamente)
INSERT INTO `visita` (`id_visita`, `fecha_hora`, `estado`, `id_cliente`, `id_barbero`, `id_servicio`, `created_at`) VALUES
	(1, '2026-01-19 09:00:00', 'CANCELADO', 25, 77, 1, '2026-01-01 15:10:04'),
	(2, '2026-01-26 10:30:00', 'CONFIRMADO', 26, 3, 3, '2026-01-01 15:19:19');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
