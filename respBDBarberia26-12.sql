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
  PRIMARY KEY (`id_barbero`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla barber.barberos
CREATE TABLE IF NOT EXISTS `barberos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla barber.cliente
CREATE TABLE IF NOT EXISTS `cliente` (
  `id_cliente` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

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

-- La exportación de datos fue deseleccionada.

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

-- La exportación de datos fue deseleccionada.

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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
