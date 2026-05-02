-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         8.0.45 - MySQL Community Server - GPL
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
  `foto_url` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `descanso_inicio` varchar(10) DEFAULT NULL,
  `descanso_fin` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_barbero`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.barbero: ~2 rows (aproximadamente)
/*!40000 ALTER TABLE `barbero` DISABLE KEYS */;
INSERT INTO `barbero` (`id_barbero`, `nombre`, `created_at`, `foto_url`, `activo`, `descanso_inicio`, `descanso_fin`) VALUES
	(1, 'Nacho', '2026-01-04 21:35:34', 'barbero_1_1774571813.jpg', 1, '12:20', '13:20'),
	(3, 'Amilkar ', '2026-01-12 19:11:48', 'barbero_3_1774571810.jpg', 0, NULL, NULL);
/*!40000 ALTER TABLE `barbero` ENABLE KEYS */;

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

-- Volcando datos para la tabla barber.barberos: ~0 rows (aproximadamente)
/*!40000 ALTER TABLE `barberos` DISABLE KEYS */;
INSERT INTO `barberos` (`id`, `nombre`, `email`, `password_hash`, `role`, `is_active`, `barbero_id`) VALUES
	(1, 'Nacho', 'nacho@kingbarber.com', '$2b$12$WixmxQGqBKFCmK8REva6EuRLrP1QellMHs5PhU6e8KPd.QSmFg5Jm', 'admin', 1, 1);
/*!40000 ALTER TABLE `barberos` ENABLE KEYS */;

-- Volcando estructura para tabla barber.blacklist
CREATE TABLE IF NOT EXISTS `blacklist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `telefono` varchar(20) NOT NULL,
  `motivo` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `telefono_unico` (`telefono`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.blacklist: ~0 rows (aproximadamente)
/*!40000 ALTER TABLE `blacklist` DISABLE KEYS */;
INSERT INTO `blacklist` (`id`, `telefono`, `motivo`, `created_at`) VALUES
	(3, '099611465', 'Sin turno disponible ', '2026-03-16 02:37:58');
/*!40000 ALTER TABLE `blacklist` ENABLE KEYS */;

-- Volcando estructura para tabla barber.cliente
CREATE TABLE IF NOT EXISTS `cliente` (
  `id_cliente` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `uq_cliente_telefono` (`telefono`)
) ENGINE=InnoDB AUTO_INCREMENT=170 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.cliente: ~166 rows (aproximadamente)
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` (`id_cliente`, `nombre`, `apellido`, `telefono`, `email`, `created_at`) VALUES
	(1, 'Matias', 'MonTh', '095064060', 'csmatiperreng@gmail.com', '2026-01-12 19:09:39'),
	(2, 'Leandro', 'Estevez', '096636052', 'leandroestevez18@gmail.com', '2026-01-13 17:48:40'),
	(3, 'Ezequiel', 'Montero', '095541214', 'monte24ro@gmail.com', '2026-01-13 23:40:48'),
	(4, 'Agustín ', 'Calonge ', '092714524', 'agustincalonge8@gmail.com', '2026-01-13 23:50:56'),
	(5, 'Agustin', 'Mello', '097165801', 'agustinmello97@gmail.com', '2026-01-14 00:01:10'),
	(6, 'Diego ', 'Rodriguez', '094689077', 'diegomauricio1710@gmail.com', '2026-01-14 00:31:48'),
	(7, 'Sebastian', 'Olivera', '093703581', 'sebamanuo2710@gmail.com', '2026-01-14 01:17:24'),
	(8, 'franco ', 'king', '09999999', 'nicolasmedinab11@gmail.com', '2026-01-14 03:21:09'),
	(9, 'Gerard', 'Silva', '094728617', NULL, '2026-01-14 04:31:52'),
	(10, 'Dilan', 'Prado ', '094120793', 'dilanprado1104@gmail.com', '2026-01-14 05:44:29'),
	(11, 'Borrego', 'Mai', '098454871', NULL, '2026-01-14 06:15:49'),
	(12, 'nelson', 'nieves', '092937412', 'conejo4882@gmail.com', '2026-01-14 06:34:54'),
	(13, 'Danu', 'Santi ', '093920081', 'Santiagocardozo2000@icloud.com', '2026-01-14 06:54:50'),
	(14, 'Benjamín ', 'Peña', '095908606', 'santiagocardozo2000@icloud.com', '2026-01-14 06:56:53'),
	(15, 'Gaston', 'Martinez', '095934867', 'jenico1610@gmail.com', '2026-01-14 07:37:53'),
	(16, 'Ignacio ', 'González ', '095900995', 'ignacio.galmiron@gmail.com', '2026-01-14 07:54:54'),
	(17, 'lucas', 'arismendi', '093820358', 'arismendilucas2006@gmail.com', '2026-01-14 08:54:30'),
	(18, 'Ignacio Saravia ', 'Saravia', '099611465', 'ignaciosaravia1901@outlook.com', '2026-01-14 09:42:53'),
	(19, 'Marcel', 'Lordon', '098475158', 'marcellordon4700@hotmail.com', '2026-01-14 10:28:18'),
	(20, 'Franco', 'Estevez ', '096252500', 'estevezfranco12@gmail.com', '2026-01-14 12:39:49'),
	(21, 'Alexis', 'Villalba', '094023432', 'cabe-10@hotmail.com', '2026-01-14 20:55:08'),
	(22, 'Lucas ', 'Añon', '094122699', 'jonatahansanchez0@gmail.com', '2026-01-14 22:19:29'),
	(23, 'manu', 'vera', '094132749', 'manuvera1924@gmail.com', '2026-01-15 12:35:57'),
	(24, 'Alexis', 'Areosa', '099626627', 'aleareosa93@gmail.com', '2026-01-16 09:25:29'),
	(25, 'Carlos', 'Nieve', '094749449', NULL, '2026-01-16 19:37:11'),
	(26, 'Itan', 'Caceres', '093311302', NULL, '2026-01-16 22:04:52'),
	(28, 'nelson', 'nieves', '099589191', 'conejo2nieves@hotmail.com', '2026-01-18 07:35:03'),
	(29, 'Nicolas', 'Cruz', '095067544', 'nc07598@gmail.com', '2026-01-18 13:40:50'),
	(32, 'Ivan', 'Francia', '094388948', 'ivanfrancia2002@gmail.com', '2026-01-18 21:24:21'),
	(33, 'Nicolas', 'Cruz', '095067554', 'nc07598@gmail.com', '2026-01-20 00:39:00'),
	(34, 'Alfredo', 'Viera', '093705681', 'negrovieraa@gmail.com', '2026-01-20 09:54:46'),
	(35, 'Alex', 'olivera', '093350395', 'alexnahuelcolmanolivera@gmail.com', '2026-01-20 22:26:00'),
	(36, 'Bruno', 'Rosas', '092290441', 'brunorosas10@icloud.com', '2026-01-20 22:26:45'),
	(37, 'Carlito', 'Csr', '091696531', 'carlosmatias857@gmail.com', '2026-01-20 22:26:56'),
	(38, 'Santiago', 'García ', '093758964', 'garciasantiago2201@gmail.com', '2026-01-20 22:38:37'),
	(39, 'facundo', 'duarte', '095194808', 'facuduarte2006@gmail.com', '2026-01-20 22:42:01'),
	(40, 'Nicolás ', 'Medina', '091041010', 'nicolasmedinab11@gmail.com', '2026-01-20 22:59:35'),
	(41, 'Cristian ', 'Britos ', '098510368', 'cristian.britos20@gmail.com', '2026-01-20 23:01:20'),
	(42, 'Gino ', 'Marroche ', '094770894', 'gialessandro81@gmail.com', '2026-01-21 06:04:19'),
	(43, 'Fabrizio', 'De Dominicis', '094229162', 'linux3@hotmail.com.ar', '2026-01-21 08:53:55'),
	(44, 'Angel', 'Rodriguez ', '094656814', 'angel-_-gabelo@hotmail.com', '2026-01-21 09:35:17'),
	(45, 'Pablo', 'Mokarm', '097300739', 'pablomokarm@gmail.com', '2026-01-21 12:32:00'),
	(46, 'Thiago', 'Iglesias ', '093315166', 'thiagoiglesias2705@gmail.com', '2026-01-21 20:30:40'),
	(47, 'Santi', 'Ditchekenian ', '092225777', 'ditchekeniansantiago@gmail.com', '2026-01-21 22:52:29'),
	(48, 'Edinson ', 'Noble ', '094908127', 'edinsonnoble7@gmail.com', '2026-01-22 10:00:35'),
	(49, 'Lautaro ', 'Galeano', '098188340', 'galeano.facundo1922@icloud.com', '2026-01-22 13:54:15'),
	(50, 'Chino', 'Gutierrez', '099386984', 'chinower1922@icloud.com', '2026-01-22 15:10:03'),
	(51, 'Mathias', 'Alaniz', '091680511', 'bcfm.alaniz@gmail.com', '2026-01-22 19:16:06'),
	(52, 'Facundo ', 'Barbero', '094732581', 'facubar2368@gmail.com', '2026-01-23 12:46:35'),
	(53, 'Andrés ', 'Braga', '094185382', 'andresbraga2018@gmail.com', '2026-02-06 22:06:42'),
	(54, 'Christian ', 'Bethencourt', '091622999', 'christianbethencourt1919@gmail.com', '2026-02-06 22:08:20'),
	(55, 'Jbenjs ', 'S', '091279467', 'jonasouza276@gmail.com', '2026-02-06 22:26:55'),
	(56, 'Matías ', 'Pérez ', '094964008', 'matii4570@gmail.com', '2026-02-06 23:10:55'),
	(57, 'Marcos', 'Galván ', '098342852', NULL, '2026-02-07 18:06:17'),
	(58, 'Ivan', 'Aguirre', '094463097', 'ivanandres2332@gmail.com', '2026-02-09 00:40:35'),
	(59, 'Alejandro ', 'Velazquez ', '094702642', 'alenegocios_cerro@hotmail.com', '2026-02-09 14:57:19'),
	(60, 'Leandro ', 'Estevez ', '096636952', 'leandroestevez18@gmail.com', '2026-02-09 16:55:51'),
	(61, 'Martin', 'Guevara ', '095497528', 'martinguevara994@gmail.com', '2026-02-09 19:06:58'),
	(62, 'Gonzalo', 'Otero', '094762305', 'oterogonzalo73@gmail.com', '2026-02-10 10:03:24'),
	(63, 'Lautaro ', 'Taleano', '098188349', NULL, '2026-02-11 19:34:35'),
	(64, 'Marcos', 'Galvan', '098342952', 'marcosgalvan0816@gmail.com', '2026-02-11 19:50:33'),
	(65, 'Guille', 'Ventoso', '095717453', 'ventosog@gmail.com', '2026-02-12 16:40:28'),
	(66, 'Esteban ', 'Ortega ', '092298286', 'estebanortega1995810000@gmail.com', '2026-02-13 08:10:21'),
	(67, 'Santi', 'Jara', '093369253', 'jararamiro522@gmail.com', '2026-02-13 20:16:53'),
	(68, 'Ezequiel', 'Gomez', '092978644', 'monte34ro@gmail.com', '2026-02-15 21:37:56'),
	(69, 'Jonathan ', 'Gómez ', '099306084', 'Gigantee.23g@gmail.com', '2026-02-16 17:46:22'),
	(70, 'Rubén ', 'Saravia ', '099611467', 'ignaciosaravia1901@outlook.com', '2026-02-17 11:39:55'),
	(71, 'Héctor', 'Saravia', '092 961 927', 'hectorsaravia410@gmail.com', '2026-02-17 12:25:50'),
	(72, 'Leo', 'Trindade ', '099861148', 'leitotrindade@gmail.com', '2026-02-17 13:38:03'),
	(73, 'Benja ', 'Buen ', '098564729', NULL, '2026-02-17 16:57:58'),
	(74, 'Jordan ', 'Cortes', '092238680', 'jordancortescorrea@gmail.com', '2026-02-18 06:02:11'),
	(75, 'Franco', 'Ramírez', '094678260', 'franco1999siu@gmail.com', '2026-02-18 21:42:37'),
	(76, 'Fernando ', 'Giles ', '091860402', 'ffgiles81@gmail.com', '2026-02-19 06:56:37'),
	(77, 'Andrés ', 'Lefevre ', '095902749', 'andreslefevre9@gmail.com', '2026-02-19 09:53:17'),
	(78, 'Martin', 'Dos santos', '091 716 746', 'martindossantos@gmail.com', '2026-02-20 13:18:25'),
	(79, 'Martin', 'Dos santos ', '091716746', 'cdratwa5@gmail.com', '2026-02-20 14:05:40'),
	(80, 'Ignacio ', 'Saravia', '099611466', NULL, '2026-02-20 14:14:41'),
	(81, 'Ismael ', 'Luzardo ', '092453046', 'ismmael1111@gmail.com', '2026-02-20 17:33:21'),
	(82, 'Prueba', 'Barber', '093910963', 'matiperreng2019@gmail.com', '2026-02-20 20:17:30'),
	(83, 'Matias', 'MonTh', '095064061', 'matiperreng2019@gmail.com', '2026-02-20 20:48:13'),
	(84, 'Lucas', 'Morales', '094404221', 'lucasmoralesen@gmail.com', '2026-02-20 21:47:33'),
	(85, 'Ezequiel', 'Montero', '092802119', 'monte24ro@icloud.com', '2026-02-24 08:57:33'),
	(86, 'Joaco', 'Cerro', '094153688', 'joacoemma1922@gmail.com', '2026-02-24 09:25:08'),
	(87, 'Facundo ', 'Estevez', '096374628', 'facundoestevez13@gmail.com', '2026-02-24 09:57:44'),
	(88, 'Guillermo', 'Martinez', '095344765', 'guillemartinezavila0@gmail.com', '2026-02-24 10:38:24'),
	(89, 'Matias', 'Corajoria', '095570816', 'matiascorajoria@outlook.com', '2026-02-24 11:46:44'),
	(90, 'Agustin', 'Mello', '097165901', 'agustinmello97@gmail.com', '2026-02-25 00:13:33'),
	(91, 'Daniel', 'Michelli', '094176366', 'danielmichelli022@gmail.com', '2026-02-25 10:48:35'),
	(92, 'Benjamin', 'Quiroga', '092237859', 'bencap2015@gmail.com', '2026-02-25 11:44:51'),
	(93, 'Benjamin ', 'Romero', '093984626', 'romerosilvana438@gmail.com', '2026-02-25 12:54:35'),
	(94, 'Mati', 'perreng', '09623432', 'matiperreng2019@gmail.com', '2026-02-25 14:24:05'),
	(95, 'Ignacio ', 'Saravia ', '099611457', NULL, '2026-02-26 13:35:00'),
	(96, 'Juan', 'Franco', '093827125', 'juanfranco12281@gmail.com', '2026-02-26 15:50:02'),
	(97, 'Nahuel ', 'Anzalone ', '094679853', 'wahuelanzalone2004@gmail.com', '2026-02-27 10:08:36'),
	(98, 'manu', 'vera', '94132749', 'manuvera1924@gmail.com', '2026-02-27 10:33:39'),
	(99, 'Pepe', 'Prueba', '099888777', NULL, '2026-02-27 11:41:18'),
	(100, 'javier', 'mora', '097868290', 'javiermora23455@gmail.com', '2026-02-27 13:36:32'),
	(101, 'Fabio', 'Da silva', '091046616', 'dasilvafabio424@gmail.com', '2026-02-27 14:58:43'),
	(102, 'Gaston', 'Martinez', '654230974', 'jenico1610@gmail.com', '2026-02-27 18:03:03'),
	(103, 'Alexis', 'Morales', '098946869', 'alexis.morales90-@hotmail.com', '2026-02-28 14:19:23'),
	(104, 'Gonzalo ', 'Otero', '+59894762305', 'oterogonzalo73@gmail.com', '2026-02-28 22:06:54'),
	(105, 'Joaquin', 'Scaroni', '092388814', 'joaco23dfc@gmail.com', '2026-03-02 14:46:58'),
	(106, 'Ignacio ', 'Saravia', '099611469', 'ignaciosaravia1901@outlook.com', '2026-03-03 09:40:49'),
	(107, 'Mauri', 'Rodriguez ', '092211020', 'maurionce99@gmail.com', '2026-03-03 17:22:34'),
	(108, 'Gaston', 'Martinez', '095934869', 'jenico1610@gmail.com', '2026-03-04 10:46:50'),
	(109, 'Nano', 'Colman ', '095797765', 'alexnahuelcolmanolivera@gmail.com', '2026-03-04 17:13:50'),
	(110, 'Gonzalo ', 'Díaz ', '+59892714685', 'gonza94432756@gmail.com', '2026-03-04 23:15:27'),
	(111, 'Rubito', 'Rubito', '098130530', 'rubitosorroquueta@gmail.com', '2026-03-05 05:21:39'),
	(112, 'Rodrigo', 'Novas', '095168067', 'rodrigonovas4@gmail.com', '2026-03-07 08:28:13'),
	(113, 'César ', 'Carrasco Acosta ', '099686722', NULL, '2026-03-10 08:16:50'),
	(114, 'Maicol', 'Techera', '098425992', 'maicoltechera14@hotmail.com', '2026-03-10 08:17:59'),
	(115, 'Leo', 'Trindade', '099681148', 'leitotrindade@gmail.com', '2026-03-10 09:06:23'),
	(116, 'Ismael', 'Luzardo ', '092 453 046', 'ismmael1111@gmail.com', '2026-03-10 16:31:41'),
	(117, 'Gonchi ', 'Dutra', '092364840', 'dutragonchi@gmail.com', '2026-03-10 17:16:49'),
	(118, 'Ignacio ', 'Saravia ', '095238652', NULL, '2026-03-16 09:19:14'),
	(119, 'Nahuel ', 'Anzalone', '094008770', NULL, '2026-03-18 11:52:02'),
	(120, 'Daniel ', 'Michelli ', '094 176 366', 'danielmichelli022@gmail.com', '2026-03-19 18:17:40'),
	(121, 'Mathias ', 'Alaniz', '095131771', 'bcfm.alaniz@gmail.com', '2026-03-19 19:02:52'),
	(122, 'Agustín ', 'García ', '091063327', 'agusscar3@gmail.com', '2026-03-22 13:39:41'),
	(123, 'Ignacio ', 'Saravia', '099611463', NULL, '2026-03-23 21:18:07'),
	(124, 'Gaston ', 'Martinez ', '095 934 867', 'elrocho_de_lanoche@hotmail.com', '2026-03-23 23:21:58'),
	(125, 'Ignacio ', 'Saravia ', '099465532', NULL, '2026-03-25 10:29:53'),
	(126, 'Maximiliano', 'Fernandez', '095274651', 'jsjsha127@gmail.com', '2026-03-25 10:30:21'),
	(127, 'Ignacio Saravia ', 'Saravia ', '099611345', NULL, '2026-03-25 14:31:39'),
	(128, 'Ignacio ', 'Saravia ', '099611464', NULL, '2026-03-25 16:07:16'),
	(129, 'Seba ', 'Cáceres ', '098124851', NULL, '2026-03-26 08:34:06'),
	(130, 'Lucas', 'Rodríguez ', '096019327', 'oterogonzalo73@gmail.com', '2026-03-27 20:59:31'),
	(131, 'Itan ', 'Saravia ', '099420321', NULL, '2026-03-31 12:09:12'),
	(132, 'Ignacio', 'Saravia ', '095235652', NULL, '2026-03-31 12:09:19'),
	(133, 'Ignacio ', 'Saravia ', '099611453', NULL, '2026-03-31 12:09:39'),
	(134, 'Ignacio Saravia ', 'Saravia', '099611462', NULL, '2026-03-31 12:30:18'),
	(135, 'Santino ', 'Cuello', '094043292', 'echudezsandra@gmail.com', '2026-03-31 23:15:23'),
	(136, 'Ignacio ', 'Saravia ', '099652325', NULL, '2026-04-02 13:57:11'),
	(137, 'Ignacio ', 'Saravia ', '09356789', NULL, '2026-04-02 13:57:26'),
	(138, 'Nahuel', 'Velazquez ', '092 358 150', 'Nahuelvelazquez310@gmail.com', '2026-04-03 11:41:44'),
	(139, 'Corte a los del torque ', 'Club ', '099611473', NULL, '2026-04-06 21:26:20'),
	(140, 'Corte club torque ', 'Torque ', '095356282', NULL, '2026-04-06 21:26:59'),
	(141, 'lucas', 'arismendi', '093820368', 'arismendilucas2006@gmail.com', '2026-04-06 21:53:26'),
	(142, 'Katriel', 'Correa ', '099304184', NULL, '2026-04-07 09:42:39'),
	(143, 'Ignacio ', 'Saravia ', '099462327', NULL, '2026-04-07 09:46:47'),
	(144, 'Sebastian', 'Olivera', '003703581', 'sebamanuo2710@gmail.com', '2026-04-07 21:10:03'),
	(145, 'Agustin', 'Calonge', '002714524', NULL, '2026-04-07 21:12:27'),
	(146, 'Facundo', 'Rivero ', '099887993', 'yacyaragonzalez.08@gmail.com', '2026-04-07 21:22:33'),
	(147, 'Dylan', 'Dylan', '099278687', 'carlosmatias857@gmail.com', '2026-04-08 13:37:32'),
	(148, 'Ignacio', 'Saravia', '099543234', NULL, '2026-04-09 09:35:54'),
	(149, 'Ignacio', 'Mora', '096855184', 'elnachomora@gmail.com', '2026-04-09 12:48:07'),
	(150, 'Josse', 'Berrueta', '095963234', 'josseberrueta1@gmail.com', '2026-04-10 11:25:27'),
	(151, 'Nano', 'Colman', '091511202', 'nanocolman@gmail.com', '2026-04-13 01:50:09'),
	(152, 'Ignacio ', 'Arabia ', '099614545', NULL, '2026-04-13 09:26:07'),
	(153, 'Alexis', 'Jorge', '091060164', 'nunezalexis756@gmail.com', '2026-04-13 12:59:47'),
	(154, 'Ignacio ', 'Saravia ', '09853589', NULL, '2026-04-13 17:07:07'),
	(155, 'franco', 'nogueira', '095732118', 'francobaz87@gmail.com', '2026-04-13 18:02:37'),
	(156, 'Facundo', 'Botti', '098780056', 'facundobotti7@gmail.com', '2026-04-15 10:45:47'),
	(157, 'Cristian', 'Rissotto', '096499294', 'mathiasnahuelgimenohernandez@gmail.com', '2026-04-15 15:04:46'),
	(158, 'Ignacio Saravia ', 'Saravia', '099621543', NULL, '2026-04-16 09:18:20'),
	(159, 'Ignacio ', 'Saravia ', '099564354', NULL, '2026-04-16 09:19:55'),
	(160, 'Ignacio ', 'Saravia ', '099611456', NULL, '2026-04-16 10:53:24'),
	(161, 'Dylan ', 'Jordan ', '095252898', NULL, '2026-04-20 12:24:55'),
	(162, 'Ignacio ', 'Saravia', '096467899', NULL, '2026-04-22 09:42:07'),
	(163, 'Gonza ', 'Montes ', '9 3903 9358', NULL, '2026-04-22 13:25:24'),
	(164, 'Manu Vera cambio ', 'Cambio ', '096372889', NULL, '2026-04-23 13:41:27'),
	(165, '𝓑𝓻𝔂𝓪𝓷🥷🏻👑', 'Cuña', '096603414', 'cunabraian9@gmail.com', '2026-04-26 18:44:15'),
	(166, 'Miguel', 'Almeida ', '096679003', 'segovialuana72@gmail.com', '2026-04-27 17:43:56'),
	(167, 'Antonella', 'Echudez', '093627671', 'antoechudez12@gmail.com', '2026-04-28 18:46:25'),
	(168, 'Ignacio ', 'Saravia ', '098543578', NULL, '2026-04-29 09:44:01'),
	(169, 'Ignacio', 'Saravia', '095645678', NULL, '2026-04-29 09:44:39');
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
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.horario_barbero: ~8 rows (aproximadamente)
/*!40000 ALTER TABLE `horario_barbero` DISABLE KEYS */;
INSERT INTO `horario_barbero` (`id_horario`, `id_barbero`, `dia_semana`, `hora_desde`, `hora_hasta`, `fecha_desde`, `fecha_hasta`) VALUES
	(13, 1, 6, '15:00:00', '20:20:00', '2026-02-07', '2026-02-15'),
	(21, 1, 2, '10:30:00', '17:00:00', '2026-02-24', '2026-03-01'),
	(32, 1, 1, '10:00:00', '19:00:00', '2026-03-02', '2026-12-02'),
	(34, 1, 3, '10:00:00', '19:00:00', '2026-03-04', '2026-12-04'),
	(35, 1, 4, '10:00:00', '19:00:00', '2026-03-05', '2026-12-05'),
	(36, 1, 5, '10:00:00', '19:00:00', '2026-03-06', '2026-12-06'),
	(37, 1, 6, '10:00:00', '19:00:00', '2026-03-07', '2026-12-07'),
	(38, 1, 2, '10:00:00', '19:00:00', '2026-03-03', '2026-12-03');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.horario_excepcion: ~0 rows (aproximadamente)
/*!40000 ALTER TABLE `horario_excepcion` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.servicio: ~3 rows (aproximadamente)
/*!40000 ALTER TABLE `servicio` DISABLE KEYS */;
INSERT INTO `servicio` (`id_servicio`, `nombre`, `duracion_min`, `precio`, `activo`, `imagen`) VALUES
	(1, 'Corte y cejas gratis', 45, 350.00, 1, '0a646127-ed2b-4f25-9c4e-cfe4975c22f0.jpg'),
	(2, 'Mechas y corte', 90, 1500.00, 1, 'e7b8fc01-4ab0-443a-a116-98683d0d968b.jpeg'),
	(3, 'Corte + Barba', 45, 400.00, 1, '636eff8a-e9c7-4f02-b9d0-11db74483127.jpg');
/*!40000 ALTER TABLE `servicio` ENABLE KEYS */;

-- Volcando estructura para tabla barber.visita
CREATE TABLE IF NOT EXISTS `visita` (
  `id_visita` int unsigned NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL,
  `estado` enum('CONFIRMADO','CANCELADO','COMPLETADO','PENDIENTE_CONFIRMACION_MP') NOT NULL DEFAULT 'CONFIRMADO',
  `medio_pago` varchar(24) NOT NULL DEFAULT 'EFECTIVO',
  `mp_preference_id` varchar(255) DEFAULT NULL,
  `id_cliente` int unsigned NOT NULL,
  `id_barbero` int unsigned NOT NULL,
  `id_servicio` int unsigned NOT NULL,
  `precio_al_reservar` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `notificado_wsp` tinyint(1) NOT NULL DEFAULT '0',
  `mp_payment_id` varchar(255) DEFAULT NULL,
  `mp_status` varchar(64) DEFAULT NULL,
  `token_seguimiento` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id_visita`),
  UNIQUE KEY `uk_barbero_fecha` (`id_barbero`,`fecha_hora`),
  UNIQUE KEY `ux_visita_token_seguimiento` (`token_seguimiento`),
  KEY `fk_visita_cliente` (`id_cliente`),
  KEY `fk_visita_barbero` (`id_barbero`),
  KEY `fk_visita_servicio` (`id_servicio`),
  CONSTRAINT `fk_visita_barbero` FOREIGN KEY (`id_barbero`) REFERENCES `barbero` (`id_barbero`),
  CONSTRAINT `fk_visita_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`),
  CONSTRAINT `fk_visita_servicio` FOREIGN KEY (`id_servicio`) REFERENCES `servicio` (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla barber.visita: ~552 rows (aproximadamente)
/*!40000 ALTER TABLE `visita` DISABLE KEYS */;
INSERT INTO `visita` (`id_visita`, `fecha_hora`, `estado`, `medio_pago`, `mp_preference_id`, `id_cliente`, `id_barbero`, `id_servicio`, `precio_al_reservar`, `created_at`, `notificado_wsp`, `mp_payment_id`, `mp_status`, `token_seguimiento`) VALUES
	(1, '2026-05-09 18:15:00', 'CONFIRMADO', 'MERCADOPAGO', '3330219852-b51be38c-59f2-43b5-8117-4471442870d7', 1, 1, 1, 350.00, '2026-05-02 14:49:36', 0, '157406897212', 'approved', 'WjF9fbJo-OK45z6meXkNPwEb2c5d_9xS9qLWT2bY6jo');
/*!40000 ALTER TABLE `visita` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
