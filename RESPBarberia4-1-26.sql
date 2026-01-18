-- --------------------------------------------------------
-- Host:                         kingbarber.webhop.net
-- Versión del servidor:         8.0.44-0ubuntu0.22.04.2 - (Ubuntu)
-- SO del servidor:              Linux
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
  `descanso_inicio` varchar(10) DEFAULT NULL,
  `descanso_fin` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_barbero`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.barbero: ~2 rows (aproximadamente)
INSERT INTO `barbero` (`id_barbero`, `nombre`, `created_at`, `foto_url`, `activo`, `descanso_inicio`, `descanso_fin`) VALUES
	(1, 'Nacho', '2026-01-05 00:35:34', 'barbero_1_1768436468.jpg', 1, '14:00', '15:00'),
	(3, 'Amilkar ', '2026-01-12 22:11:48', 'barbero_3_1768437946.jpg', 0, NULL, NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.barberos: ~1 rows (aproximadamente)
INSERT INTO `barberos` (`id`, `nombre`, `email`, `password_hash`, `role`, `is_active`, `barbero_id`) VALUES
	(1, 'Nacho', 'nacho@kingbarber.com', '$2b$12$WixmxQGqBKFCmK8REva6EuRLrP1QellMHs5PhU6e8KPd.QSmFg5Jm', 'admin', 1, 1);

-- Volcando estructura para tabla barber.cliente
CREATE TABLE IF NOT EXISTS `cliente` (
  `id_cliente` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `uq_cliente_telefono` (`telefono`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.cliente: ~28 rows (aproximadamente)
INSERT INTO `cliente` (`id_cliente`, `nombre`, `apellido`, `telefono`, `email`, `created_at`) VALUES
	(1, 'Matias', 'Perreng', '095064060', 'csmatiperreng@gmail.com', '2026-01-12 22:09:39'),
	(2, 'Leandro ', 'Estevez ', '096636052', 'leandroestevez18@gmail.com', '2026-01-13 20:48:40'),
	(3, 'Ezequiel', 'Montero', '095541214', 'monte24ro@gmail.com', '2026-01-14 02:40:48'),
	(4, 'Agustín ', '.', '092714524', 'agustincalonge8@gmail.com', '2026-01-14 02:50:56'),
	(5, 'Agustin', 'Mello', '097165801', 'agustinmello97@gmail.com', '2026-01-14 03:01:10'),
	(6, 'Diego ', 'Rodríguez ', '094689077', 'diegomauricio1710@gmail.com', '2026-01-14 03:31:48'),
	(7, 'Sebastián ', 'Olivera ', '093703581', NULL, '2026-01-14 04:17:24'),
	(8, 'Nahuel ', 'Anzalone ', NULL, 'wahuelanzalone2004@gmail.com', '2026-01-14 06:21:09'),
	(9, 'Gerard', 'Silva', '094728617', NULL, '2026-01-14 07:31:52'),
	(10, 'Dilan ', 'Prado ', '094120793', 'Dilanprado1104@gmail.com', '2026-01-14 08:44:29'),
	(11, 'Borrego', 'Cerro', '098454871', NULL, '2026-01-14 09:15:49'),
	(12, 'Luciano', 'nieves', '092937412', 'conejo2nieves@hotmail.com', '2026-01-14 09:34:54'),
	(13, 'Benjamín ', 'Peña', '093920081', 'santiagocardozo2000@icloud.com', '2026-01-14 09:54:50'),
	(14, 'Benjamín ', 'Peña', '095908606', 'santiagocardozo2000@icloud.com', '2026-01-14 09:56:53'),
	(15, 'Gaston', 'Martinez ', '095934867', NULL, '2026-01-14 10:37:53'),
	(16, 'Nacho ', 'González ', '095900995', 'ignacio.galmiron@gmail.com', '2026-01-14 10:54:54'),
	(17, 'lucas', 'arismendi', '093820358', 'arismendilucas2006@gmail.com', '2026-01-14 11:54:30'),
	(18, 'Ignacio ', 'Saravia ', '099611465', 'ignaciosaravia1901@outlook.com', '2026-01-14 12:42:53'),
	(19, 'Marcel', 'Lordon', '098475158', 'marcellordon4700@hotmail.com', '2026-01-14 13:28:18'),
	(20, 'Franco ', 'Estevez ', '096252500', 'estevezfranco12@gmail.com', '2026-01-14 15:39:49'),
	(21, 'Alexis', 'Villalba', '094023432', 'cabe-10@hotmail.com', '2026-01-14 23:55:08'),
	(22, 'Lucas ', 'Añon', '094122699', 'jonatahansanchez0@gmail.com', '2026-01-15 01:19:29'),
	(23, 'Manuel', 'Vera', '094132749', 'Manuvera1924@gmail.com', '2026-01-15 15:35:57'),
	(24, 'Alexis', 'Areosa', '099626627', 'aleareosa93@gmail.com', '2026-01-16 12:25:29'),
	(25, 'Carlos', 'Nieve', '094749449', NULL, '2026-01-16 22:37:11'),
	(26, 'Itan', 'Caceres', '093311302', NULL, '2026-01-17 01:04:52'),
	(28, 'nelson', 'nieves', '099589191', 'conejo2nieves@hotmail.com', '2026-01-18 10:35:03'),
	(29, 'Nicolas', 'Cruz', '095067544', 'nc07598@gmail.com', '2026-01-18 16:40:50');

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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.horario_barbero: ~6 rows (aproximadamente)
INSERT INTO `horario_barbero` (`id_horario`, `id_barbero`, `dia_semana`, `hora_desde`, `hora_hasta`, `fecha_desde`, `fecha_hasta`) VALUES
	(1, 1, 1, '10:00:00', '19:00:00', '2026-01-05', '2026-09-28'),
	(2, 1, 2, '10:00:00', '19:00:00', '2026-01-06', '2026-09-29'),
	(3, 1, 3, '10:00:00', '19:00:00', '2026-01-07', '2026-09-30'),
	(4, 1, 4, '10:00:00', '19:00:00', '2026-01-08', '2026-10-01'),
	(5, 1, 5, '10:00:00', '19:00:00', '2026-01-09', '2026-10-02'),
	(6, 1, 6, '10:00:00', '19:00:00', '2026-01-10', '2026-10-03');

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
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.servicio: ~3 rows (aproximadamente)
INSERT INTO `servicio` (`id_servicio`, `nombre`, `duracion_min`, `precio`, `activo`, `imagen`) VALUES
	(1, 'Corte y cejas gratis', 45, 350.00, 1, '0a646127-ed2b-4f25-9c4e-cfe4975c22f0.jpg'),
	(2, 'Mechas y corte', 90, 1500.00, 1, 'e7b8fc01-4ab0-443a-a116-98683d0d968b.jpeg'),
	(3, 'Corte + Barba', 45, 400.00, 1, '636eff8a-e9c7-4f02-b9d0-11db74483127.jpg');

-- Volcando estructura para tabla barber.visita
CREATE TABLE IF NOT EXISTS `visita` (
  `id_visita` int unsigned NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL,
  `estado` enum('CONFIRMADO','CANCELADO','COMPLETADO') NOT NULL,
  `id_cliente` int unsigned NOT NULL,
  `id_barbero` int unsigned NOT NULL,
  `id_servicio` int unsigned NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `notificado_wsp` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_visita`),
  KEY `fk_visita_cliente` (`id_cliente`),
  KEY `fk_visita_barbero` (`id_barbero`),
  KEY `fk_visita_servicio` (`id_servicio`),
  CONSTRAINT `fk_visita_barbero` FOREIGN KEY (`id_barbero`) REFERENCES `barbero` (`id_barbero`),
  CONSTRAINT `fk_visita_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`),
  CONSTRAINT `fk_visita_servicio` FOREIGN KEY (`id_servicio`) REFERENCES `servicio` (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.visita: ~34 rows (aproximadamente)
INSERT INTO `visita` (`id_visita`, `fecha_hora`, `estado`, `id_cliente`, `id_barbero`, `id_servicio`, `created_at`, `notificado_wsp`) VALUES
	(1, '2026-01-15 18:00:00', 'COMPLETADO', 2, 1, 1, '2026-01-13 20:48:40', 0),
	(2, '2026-01-17 10:00:00', 'COMPLETADO', 3, 1, 1, '2026-01-14 02:40:48', 0),
	(3, '2026-01-16 15:20:00', 'COMPLETADO', 4, 1, 1, '2026-01-14 02:50:56', 0),
	(4, '2026-01-14 11:30:00', 'COMPLETADO', 5, 1, 1, '2026-01-14 03:01:10', 0),
	(5, '2026-01-15 10:45:00', 'COMPLETADO', 6, 1, 1, '2026-01-14 03:31:49', 0),
	(6, '2026-01-14 13:00:00', 'COMPLETADO', 7, 1, 1, '2026-01-14 04:17:24', 0),
	(7, '2026-01-14 10:45:00', 'COMPLETADO', 8, 1, 3, '2026-01-14 06:21:09', 0),
	(8, '2026-01-16 10:45:00', 'COMPLETADO', 9, 1, 3, '2026-01-14 07:31:52', 0),
	(9, '2026-01-15 13:45:00', 'COMPLETADO', 10, 1, 3, '2026-01-14 08:44:29', 0),
	(10, '2026-01-16 17:30:00', 'COMPLETADO', 11, 1, 1, '2026-01-14 09:15:49', 0),
	(11, '2026-01-16 10:00:00', 'COMPLETADO', 12, 1, 1, '2026-01-14 09:34:54', 0),
	(12, '2026-01-14 12:15:00', 'COMPLETADO', 13, 1, 1, '2026-01-14 09:54:50', 0),
	(13, '2026-01-14 13:45:00', 'COMPLETADO', 14, 1, 1, '2026-01-14 09:56:54', 0),
	(14, '2026-01-16 16:45:00', 'COMPLETADO', 15, 1, 3, '2026-01-14 10:37:53', 0),
	(15, '2026-01-17 15:15:00', 'COMPLETADO', 16, 1, 1, '2026-01-14 10:54:54', 0),
	(16, '2026-01-15 10:00:00', 'COMPLETADO', 17, 1, 1, '2026-01-14 11:54:30', 0),
	(17, '2026-01-14 10:00:00', 'COMPLETADO', 18, 1, 1, '2026-01-14 12:42:53', 0),
	(18, '2026-01-14 17:30:00', 'COMPLETADO', 19, 1, 1, '2026-01-14 13:28:18', 0),
	(19, '2026-01-14 18:15:00', 'COMPLETADO', 2, 1, 1, '2026-01-14 14:39:16', 0),
	(20, '2026-01-15 11:30:00', 'COMPLETADO', 9, 1, 1, '2026-01-14 14:47:34', 0),
	(21, '2026-01-14 16:45:00', 'COMPLETADO', 20, 1, 1, '2026-01-14 15:39:49', 0),
	(23, '2026-01-16 18:15:00', 'COMPLETADO', 21, 1, 3, '2026-01-14 23:55:08', 0),
	(28, '2026-01-15 16:45:00', 'COMPLETADO', 22, 1, 3, '2026-01-15 01:19:29', 0),
	(31, '2026-01-15 16:00:00', 'COMPLETADO', 23, 1, 1, '2026-01-15 15:35:57', 0),
	(32, '2026-01-16 13:00:00', 'COMPLETADO', 24, 1, 3, '2026-01-16 12:25:29', 0),
	(33, '2026-01-17 12:15:00', 'COMPLETADO', 12, 1, 1, '2026-01-16 12:29:17', 0),
	(34, '2026-01-17 13:00:00', 'COMPLETADO', 12, 1, 1, '2026-01-16 12:29:35', 0),
	(35, '2026-01-19 10:00:00', 'CONFIRMADO', 25, 1, 1, '2026-01-16 22:37:11', 0),
	(36, '2026-01-19 12:15:00', 'CONFIRMADO', 12, 1, 1, '2026-01-16 23:03:20', 0),
	(37, '2026-01-19 13:00:00', 'CONFIRMADO', 12, 1, 1, '2026-01-16 23:03:47', 0),
	(38, '2026-01-17 16:00:00', 'COMPLETADO', 26, 1, 1, '2026-01-17 01:04:52', 0),
	(41, '2026-01-19 10:45:00', 'CONFIRMADO', 28, 1, 1, '2026-01-18 10:35:03', 0),
	(42, '2026-01-19 11:30:00', 'CONFIRMADO', 28, 1, 1, '2026-01-18 10:35:45', 0),
	(43, '2026-01-20 15:15:00', 'CONFIRMADO', 29, 1, 1, '2026-01-18 16:40:51', 0);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
