-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 13-03-2020 a las 18:26:39
-- Versión del servidor: 10.3.22-MariaDB-0+deb10u1
-- Versión de PHP: 7.2.9-1+b2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Base de datos: `control_solar`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `srne`
--

CREATE TABLE IF NOT EXISTS `srne` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Tiempo` datetime NOT NULL,
  `Iplaca` float NOT NULL DEFAULT 0,
  `Vplaca` float NOT NULL DEFAULT 0,
  `Vbat` float NOT NULL DEFAULT 0,
  `Estado` enum('DEACTIVATED','ACTIVATED','BULK','EQUALIZE','ABSORTION','FLOAT','LIMITING') COLLATE latin1_spanish_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
COMMIT;
