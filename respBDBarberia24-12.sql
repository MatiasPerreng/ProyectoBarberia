-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         8.0.43 - MySQL Community Server - GPL
-- SO del servidor:              Win64
-- HeidiSQL Versión:             11.0.0.5919
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Volcando estructura de base de datos para barber
CREATE DATABASE IF NOT EXISTS `barber` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `barber`;

-- Volcando estructura para tabla barber.barbero
CREATE TABLE IF NOT EXISTS `barbero` (
  `id_barbero` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_barbero`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.barbero: ~3 rows (aproximadamente)
/*!40000 ALTER TABLE `barbero` DISABLE KEYS */;
INSERT INTO `barbero` (`id_barbero`, `nombre`, `created_at`) VALUES
	(1, 'Nacho', '2025-12-14 12:38:14'),
	(2, 'Amilkar', '2025-12-14 12:38:23'),
	(3, 'Enzo', '2025-12-14 12:38:28');
/*!40000 ALTER TABLE `barbero` ENABLE KEYS */;

-- Volcando estructura para tabla barber.barberos
CREATE TABLE IF NOT EXISTS `barberos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.barberos: ~0 rows (aproximadamente)
/*!40000 ALTER TABLE `barberos` DISABLE KEYS */;
/*!40000 ALTER TABLE `barberos` ENABLE KEYS */;

-- Volcando estructura para tabla barber.cliente
CREATE TABLE IF NOT EXISTS `cliente` (
  `id_cliente` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.cliente: ~16 rows (aproximadamente)
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` (`id_cliente`, `nombre`, `apellido`, `telefono`, `email`, `created_at`) VALUES
	(1, 'Matias', '', NULL, 'csmatiperreng@gmail.com', '2025-12-14 15:34:26'),
	(2, 'Matias', '', NULL, 'a@g', '2025-12-14 15:39:43'),
	(3, 'Roberto', '', NULL, 'rperez@gmail.com', '2025-12-14 15:42:53'),
	(4, 'rosario', '', NULL, 'as@gmail.com', '2025-12-14 16:06:59'),
	(5, 'romina', '', NULL, 'romediana@maqwe', '2025-12-14 16:11:23'),
	(6, 'jacinto', '', NULL, 'qma@gmail.com', '2025-12-14 16:14:05'),
	(7, 'Matias', '', NULL, 'asesa@gmail.com', '2025-12-14 16:50:04'),
	(8, 'Matias', '', '0981231', 'mp@gmail.com', '2025-12-22 16:40:39'),
	(9, 'Manuel', '', '2131321321', 'mv@gmail.com', '2025-12-22 17:03:57'),
	(10, 'Matiaw', '', '095065060', 'csmatiperreng@gmail.com', '2025-12-22 17:36:06'),
	(11, 'Rodri', '', '095921321', 'rodridls@gmail.com', '2025-12-22 18:31:44'),
	(12, 'ase', '', '12321321', 'a@gmail.com', '2025-12-22 18:51:32'),
	(13, 'a', '', '12321321', 'a@gmail.com', '2025-12-22 18:56:05'),
	(14, 'S', '', '091232131', 'aver@gmail.com', '2025-12-22 19:05:30'),
	(15, '1', '', '09122322', 'csmatiperreng@live.com', '2025-12-22 19:26:28'),
	(16, 'Matias', '', '095064060', 'csmatiperreng@gmail.com', '2025-12-23 12:51:02'),
	(17, 'Adrian', '', '03221321', 'adrian@gmail.com', '2025-12-23 12:54:51'),
	(18, 'Lolo', '', '01232131', 'laur@gmail.com', '2025-12-23 21:39:31'),
	(19, 'Francisco', 'Ferre', '09623432', 'csmatiperreng@gmail.com', '2025-12-24 09:15:02');
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;

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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.horario_barbero: ~15 rows (aproximadamente)
/*!40000 ALTER TABLE `horario_barbero` DISABLE KEYS */;
INSERT INTO `horario_barbero` (`id_horario`, `id_barbero`, `dia_semana`, `hora_desde`, `hora_hasta`, `fecha_desde`, `fecha_hasta`) VALUES
	(1, 2, 1, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(2, 2, 2, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(3, 2, 3, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(4, 2, 4, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(5, 2, 5, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(6, 1, 1, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(7, 1, 2, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(8, 1, 3, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(9, 1, 4, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(10, 1, 5, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(11, 3, 1, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(12, 3, 2, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(13, 3, 3, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(14, 3, 4, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31'),
	(15, 3, 5, '10:00:00', '19:00:00', '2020-01-01', '2099-12-31');
/*!40000 ALTER TABLE `horario_barbero` ENABLE KEYS */;

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.horario_excepcion: ~0 rows (aproximadamente)
/*!40000 ALTER TABLE `horario_excepcion` DISABLE KEYS */;
INSERT INTO `horario_excepcion` (`id_excepcion`, `id_barbero`, `fecha`, `hora_desde`, `hora_hasta`, `tipo`) VALUES
	(1, 1, '2025-12-25', NULL, NULL, 'cierre');
/*!40000 ALTER TABLE `horario_excepcion` ENABLE KEYS */;

-- Volcando estructura para tabla barber.servicio
CREATE TABLE IF NOT EXISTS `servicio` (
  `id_servicio` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `duracion_min` int unsigned NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `imagen` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.servicio: ~3 rows (aproximadamente)
/*!40000 ALTER TABLE `servicio` DISABLE KEYS */;
INSERT INTO `servicio` (`id_servicio`, `nombre`, `duracion_min`, `precio`, `activo`, `imagen`) VALUES
	(1, 'Corte rasurado', 45, 330.00, 1, 'corte-rasurado.jpg'),
	(2, 'Color', 90, 1300.00, 1, 'mechas.jpeg'),
	(3, 'Corte + Barba', 60, 400.00, 1, 'barba.jpg');
/*!40000 ALTER TABLE `servicio` ENABLE KEYS */;

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

-- Volcando datos para la tabla barber.visita: ~1 rows (aproximadamente)
/*!40000 ALTER TABLE `visita` DISABLE KEYS */;
INSERT INTO `visita` (`id_visita`, `fecha_hora`, `estado`, `id_cliente`, `id_barbero`, `id_servicio`, `created_at`) VALUES
	(1, '2025-12-09 16:30:00', 'reservado', 17, 1, 1, '2025-12-23 12:54:51'),
	(2, '2025-12-09 16:30:00', 'reservado', 18, 2, 1, '2025-12-23 21:39:31'),
	(3, '2025-12-25 12:30:00', 'reservado', 19, 1, 2, '2025-12-24 09:15:02');
/*!40000 ALTER TABLE `visita` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
