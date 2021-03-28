-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 28-03-2021 a las 15:59:12
-- Versión del servidor: 10.3.25-MariaDB-0+deb10u1
-- Versión de PHP: 7.2.9-1+b2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `control_solar`
--
CREATE DATABASE IF NOT EXISTS `control_solar` DEFAULT CHARACTER SET latin1 COLLATE latin1_spanish_ci;
USE `control_solar`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bmv`
--

DROP TABLE IF EXISTS `bmv`;
CREATE TABLE IF NOT EXISTS `bmv` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Tiempo` datetime NOT NULL COMMENT 'Fecha captura',
  `SOC` float NOT NULL DEFAULT 0 COMMENT 'SOC bateria',
  `Vbat` float NOT NULL DEFAULT 0 COMMENT 'Voltaje Bateria',
  `Vm` float NOT NULL DEFAULT 0 COMMENT 'Valor Medio Bateria',
  `Temp` float NOT NULL DEFAULT 0 COMMENT 'Temperatura',
  `Ibat` float NOT NULL DEFAULT 0 COMMENT 'Intensidad Bateria',
  PRIMARY KEY (`id`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `condiciones`
--

DROP TABLE IF EXISTS `condiciones`;
CREATE TABLE IF NOT EXISTS `condiciones` (
  `activado` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1 para activar la condicion',
  `condicion1` text COLLATE latin1_spanish_ci NOT NULL COMMENT 'expresión a evaluar 1 ',
  `condicion2` text COLLATE latin1_spanish_ci NOT NULL COMMENT 'expresion a evaluar 2 (se realiza un "AND" con la condicion 1',
  `accion` text COLLATE latin1_spanish_ci NOT NULL COMMENT 'Expresion en Python que se ejecuta si se cumple la condicion1 y la condicion2',
  `descripcion` text COLLATE latin1_spanish_ci NOT NULL,
  `id_condicion` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id_condicion`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

--
-- Volcado de datos para la tabla `condiciones`
--

INSERT INTO `condiciones` (`activado`, `condicion1`, `condicion2`, `accion`, `descripcion`, `id_condicion`) VALUES
(0, 'hora > \'18:00:00\'', 'Rele_Tiempo[411] < 1000', 'PWM = 80', 'Ejemplo1\r\nSi la hora es mayor de las 18:00 y el rele 411 lleva encendido en el dia menos de 1000sg pone el PWM a 80', 1),
(0, '', 'PWM > 200', 'Rele[201] = 100', 'Ejemplo2\r\nEnciende el rele 201 si el PWM es mayor de 200', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos`
--

DROP TABLE IF EXISTS `datos`;
CREATE TABLE IF NOT EXISTS `datos` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Identificador captura',
  `Tiempo` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha/hora de la captura',
  `Ibat` float NOT NULL DEFAULT 0 COMMENT 'Intensidad que entra a bateria (positiva) o sale (negativa)',
  `Vbat` float NOT NULL DEFAULT 0 COMMENT 'Voltaje bateria',
  `SOC` float NOT NULL DEFAULT 0 COMMENT 'DS /Capacidad nominal bateria en %',
  `DS` float NOT NULL DEFAULT 0 COMMENT 'Valor actual en Ah de la bateria',
  `Aux1` float NOT NULL DEFAULT 0 COMMENT 'Valor Auxiliar 1...salida Aux regulador, Hz, Iplaca2, etc',
  `Aux2` float NOT NULL DEFAULT 0 COMMENT 'Valor Auxiliar2',
  `Whp_bat` float NOT NULL DEFAULT 0 COMMENT 'Watios hora cargados a bateria',
  `Whn_bat` float NOT NULL DEFAULT 0 COMMENT 'Watios hora descargados de bateria',
  `Iplaca` float NOT NULL DEFAULT 0 COMMENT 'Salida tras el regulador',
  `Vplaca` float NOT NULL DEFAULT 0 COMMENT 'Voltaje de placas',
  `Wplaca` float NOT NULL DEFAULT 0 COMMENT 'Potencia total generada por las Placas',
  `Wh_placa` float NOT NULL DEFAULT 0 COMMENT 'Watios hora generados por la placas',
  `Temp` float NOT NULL DEFAULT 0 COMMENT 'Temperatura baterias',
  `PWM` float NOT NULL DEFAULT 0 COMMENT 'PWM total para excedentes',
  `Mod_bat` enum('OFF','BULK','FLOT','ABS','EQU','INYECT','CONS') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'BULK',
  `Vred` float NOT NULL DEFAULT 0 COMMENT 'V red AC',
  `Wred` float NOT NULL DEFAULT 0 COMMENT 'W inyectados o consumidos de red',
  `Whn_red` float NOT NULL DEFAULT 0 COMMENT 'Wh consumidos de red',
  `Whp_red` float NOT NULL DEFAULT 0 COMMENT 'Wh inyectados a red',
  PRIMARY KEY (`id`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos_c`
--

DROP TABLE IF EXISTS `datos_c`;
CREATE TABLE IF NOT EXISTS `datos_c` (
  `id` int(10) UNSIGNED NOT NULL,
  `Tiempo` datetime DEFAULT NULL,
  `Ibat` float DEFAULT NULL,
  `Vbat` float DEFAULT NULL,
  `SOC` float DEFAULT NULL,
  `DS` float DEFAULT NULL,
  `Aux1` float DEFAULT NULL,
  `Aux2` float DEFAULT NULL,
  `Whp_bat` float DEFAULT NULL,
  `Whn_bat` float DEFAULT NULL,
  `Iplaca` float DEFAULT NULL,
  `Vplaca` float DEFAULT NULL,
  `Wplaca` float DEFAULT NULL,
  `Wh_placa` float DEFAULT NULL,
  `Temp` float DEFAULT NULL,
  `PWM` float DEFAULT NULL,
  `Mod_bat` enum('OFF','BULK','FLOT','ABS','EQU','INYECT','CONS') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'BULK',
  `Vred` float NOT NULL DEFAULT 0 COMMENT 'V red AC',
  `Wred` float NOT NULL DEFAULT 0 COMMENT 'W inyectados o consumidos de red',
  `Whn_red` float NOT NULL DEFAULT 0 COMMENT 'Wh consumidos de red',
  `Whp_red` float NOT NULL DEFAULT 0 COMMENT 'Wh inyectados a red',
  PRIMARY KEY (`id`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos_mux_1`
--

DROP TABLE IF EXISTS `datos_mux_1`;
CREATE TABLE IF NOT EXISTS `datos_mux_1` (
  `id_mux_1` int(11) NOT NULL AUTO_INCREMENT,
  `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
  `C0` float NOT NULL DEFAULT 0,
  `C1` float NOT NULL DEFAULT 0,
  `C2` float NOT NULL DEFAULT 0,
  `C3` float NOT NULL DEFAULT 0,
  `C4` float NOT NULL DEFAULT 0,
  `C5` float NOT NULL DEFAULT 0,
  `C6` float NOT NULL DEFAULT 0,
  `C7` float NOT NULL DEFAULT 0,
  `C8` float NOT NULL DEFAULT 0,
  `C9` float NOT NULL DEFAULT 0,
  `C10` float NOT NULL DEFAULT 0,
  `C11` float NOT NULL DEFAULT 0,
  `C12` float NOT NULL DEFAULT 0,
  `C13` float NOT NULL DEFAULT 0,
  `C14` float NOT NULL DEFAULT 0,
  `C15` float NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_mux_1`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos_s`
--

DROP TABLE IF EXISTS `datos_s`;
CREATE TABLE IF NOT EXISTS `datos_s` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Indentificador Captura',
  `Tiempo` datetime(1) DEFAULT NULL COMMENT 'Fecha/Hora Captura',
  `Ibat` float DEFAULT NULL,
  `Vbat` float DEFAULT NULL,
  `SOC` float DEFAULT NULL,
  `DS` float DEFAULT 0,
  `Aux1` float DEFAULT 0,
  `Aux2` float NOT NULL DEFAULT 0,
  `Whp_bat` float DEFAULT 0,
  `Whn_bat` float DEFAULT 0,
  `Iplaca` float DEFAULT 0,
  `Vplaca` float NOT NULL DEFAULT 0,
  `Wplaca` float NOT NULL DEFAULT 0,
  `Wh_placa` float DEFAULT 0,
  `Temp` float NOT NULL DEFAULT 0,
  `PWM` float DEFAULT 0,
  `IPWM_P` float(5,2) NOT NULL DEFAULT 0.00,
  `IPWM_I` float(5,2) NOT NULL DEFAULT 0.00,
  `IPWM_D` float(5,2) NOT NULL DEFAULT 0.00,
  `Kp` float NOT NULL DEFAULT 0,
  `Ki` float NOT NULL DEFAULT 0,
  `Kd` float NOT NULL DEFAULT 0,
  `Vred` float NOT NULL DEFAULT 0 COMMENT 'V red AC',
  `Wred` float NOT NULL DEFAULT 0 COMMENT 'W inyectados o consumidos de red',
  `Whn_red` float NOT NULL DEFAULT 0 COMMENT 'Wh consumidos de red',
  `Whp_red` float NOT NULL DEFAULT 0 COMMENT 'Wh inyectados a red',
  PRIMARY KEY (`id`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `diario`
--

DROP TABLE IF EXISTS `diario`;
CREATE TABLE IF NOT EXISTS `diario` (
  `Fecha` date NOT NULL DEFAULT current_timestamp(),
  `maxVbat` float NOT NULL DEFAULT 0,
  `minVbat` float NOT NULL DEFAULT 0,
  `avgVbat` float NOT NULL DEFAULT 0,
  `maxSOC` float NOT NULL DEFAULT 0,
  `minSOC` float NOT NULL DEFAULT 0,
  `avgSOC` float NOT NULL DEFAULT 0,
  `maxIbat` float NOT NULL DEFAULT 0,
  `minIbat` float NOT NULL DEFAULT 0,
  `avgIbat` float NOT NULL DEFAULT 0,
  `maxIplaca` float NOT NULL DEFAULT 0,
  `avgIplaca` float NOT NULL DEFAULT 0,
  `Wh_placa` float NOT NULL DEFAULT 0,
  `Whp_bat` float NOT NULL DEFAULT 0,
  `Whn_bat` float NOT NULL DEFAULT 0,
  `Wh_consumo` float NOT NULL DEFAULT 0,
  `maxTemp` float NOT NULL DEFAULT 0,
  `minTemp` float NOT NULL DEFAULT 0,
  `avgTemp` float NOT NULL DEFAULT 0,
  `Whn_red` float NOT NULL DEFAULT 0 COMMENT 'Wh consumidos de red',
  `Whp_red` float NOT NULL DEFAULT 0 COMMENT 'Wh inyectados a red',
  `maxWred` float NOT NULL DEFAULT 0 COMMENT 'maximo W inyectados a red',
  `minWred` float NOT NULL DEFAULT 0 COMMENT 'minimo W consumidos de red',
  `avgWred` float NOT NULL DEFAULT 0 COMMENT 'media W de red',
  `maxVred` float NOT NULL DEFAULT 0 COMMENT 'maxima Vred',
  `minVred` float NOT NULL DEFAULT 0 COMMENT 'minima Vred',
  PRIMARY KEY (`Fecha`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `equipos`
--

DROP TABLE IF EXISTS `equipos`;
CREATE TABLE IF NOT EXISTS `equipos` (
  `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
  `sensores` varchar(500) COLLATE latin1_spanish_ci NOT NULL,
  PRIMARY KEY (`id_equipo`)
) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `hibrido`
--

DROP TABLE IF EXISTS `hibrido`;
CREATE TABLE IF NOT EXISTS `hibrido` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Tiempo` datetime NOT NULL,
  `Vgen` float NOT NULL DEFAULT 0,
  `Fgen` float NOT NULL DEFAULT 0,
  `Iplaca` smallint(3) NOT NULL DEFAULT 0,
  `Vplaca` float NOT NULL DEFAULT 0,
  `Wplaca` smallint(5) NOT NULL DEFAULT 0,
  `Vbat` float NOT NULL DEFAULT 0,
  `Vbus` smallint(3) NOT NULL DEFAULT 0,
  `Ibatp` smallint(3) NOT NULL DEFAULT 0,
  `Ibatn` smallint(3) NOT NULL DEFAULT 0,
  `temp` tinyint(3) NOT NULL DEFAULT 0,
  `PACW` smallint(5) NOT NULL DEFAULT 0,
  `PACVA` smallint(5) NOT NULL DEFAULT 0,
  `Flot` tinyint(1) NOT NULL DEFAULT 0,
  `OnOff` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `log`
--

DROP TABLE IF EXISTS `log`;
CREATE TABLE IF NOT EXISTS `log` (
  `id_log` int(11) NOT NULL AUTO_INCREMENT,
  `Tiempo` datetime NOT NULL,
  `log` varchar(50) CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`id_log`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `parametros`
--

DROP TABLE IF EXISTS `parametros`;
CREATE TABLE IF NOT EXISTS `parametros` (
  `grabar_datos` set('S','N') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'S',
  `grabar_reles` set('S','N') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'N',
  `t_muestra` float NOT NULL,
  `n_muestras_grab` int(3) NOT NULL,
  `nuevo_soc` float NOT NULL DEFAULT 0 COMMENT 'valor distinto de 0 actualiza',
  `objetivo_PID` float NOT NULL COMMENT 'Valor objetivo a conseguir por el control PID',
  `sensor_PID` set('Aux1','Aux2','Vplaca','Iplaca','Wplaca','Vbat','Ibat','Wbat','SOC','Hz','Vred','Ired','Wred') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'Vbat' COMMENT 'Variable de control PID',
  `Kp` float NOT NULL DEFAULT 10 COMMENT 'Constante proporcional PID',
  `Ki` float NOT NULL DEFAULT 0 COMMENT 'Constante Integral PID',
  `Kd` float NOT NULL DEFAULT 0 COMMENT 'Constante derivativa PID',
  `Mod_bat` set('BULK','FLOT','ABS','EQU') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'BULK',
  `Vflot` float NOT NULL DEFAULT 27.2 COMMENT 'Valor de flotacion',
  `Vabs` float NOT NULL DEFAULT 28.8 COMMENT 'Valor de absorcion',
  `Tabs` int(11) NOT NULL DEFAULT 3600 COMMENT 'Tiempo de absorcion en segundos',
  `Vequ` float NOT NULL DEFAULT 29.6 COMMENT 'Valor de ecualizacion',
  `Tequ` int(11) NOT NULL DEFAULT 3600 COMMENT 'Tiempo de ecualizacion en segundos',
  `Icola` float NOT NULL DEFAULT 4 COMMENT 'Intensidad de cola para corte de Absorcion',
  `coef_temp` float NOT NULL DEFAULT 0 COMMENT 'Coeficiente Compesancion Temperatura para Vflot y Vabs',
  `id_parametros` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_parametros`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

--
-- Volcado de datos para la tabla `parametros`
--

INSERT INTO `parametros` (`grabar_datos`, `grabar_reles`, `t_muestra`, `n_muestras_grab`, `nuevo_soc`, `objetivo_PID`, `sensor_PID`, `Kp`, `Ki`, `Kd`, `Mod_bat`, `Vflot`, `Vabs`, `Tabs`, `Vequ`, `Tequ`, `Icola`, `coef_temp`, `id_parametros`) VALUES
('S', 'S', 5, 1, 0, 28.8, 'Vbat', 10, 0, 0, 'BULK', 27.2, 28.8, 3600, 29.6, 3600, 4, 0, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles`
--

DROP TABLE IF EXISTS `reles`;
CREATE TABLE IF NOT EXISTS `reles` (
  `id_rele` int(3) NOT NULL DEFAULT 0,
  `nombre` text CHARACTER SET latin1 DEFAULT NULL,
  `modo` varchar(3) CHARACTER SET latin1 DEFAULT 'PRG',
  `estado` tinyint(3) DEFAULT 0,
  `grabacion` varchar(1) CHARACTER SET latin1 DEFAULT 'N',
  `salto` tinyint(3) NOT NULL DEFAULT 100,
  `prioridad` tinyint(2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_rele`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

--
-- Volcado de datos para la tabla `reles`
--

INSERT INTO `reles` (`id_rele`, `nombre`, `modo`, `estado`, `grabacion`, `salto`, `prioridad`) VALUES
(201, 'Rele WIFI', 'PRG', 0, 'N', 100, 0),
(411, 'Rele GPIO 411', 'PRG', 0, 'N', 5, 1);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `reles_activos_hoy`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `reles_activos_hoy`;
CREATE TABLE IF NOT EXISTS `reles_activos_hoy` (
`id_rele` int(3)
,`fecha` date
,`segundos_on` float
,`nconmutaciones` float
,`id_reles_segundos_on` int(11)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles_c`
--

DROP TABLE IF EXISTS `reles_c`;
CREATE TABLE IF NOT EXISTS `reles_c` (
  `id_rele` int(3) DEFAULT NULL,
  `operacion` text CHARACTER SET latin1 DEFAULT NULL,
  `parametro` text CHARACTER SET latin1 DEFAULT NULL,
  `condicion` text CHARACTER SET latin1 DEFAULT NULL,
  `valor` float DEFAULT NULL,
  `id_reles_c` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id_reles_c`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles_grab`
--

DROP TABLE IF EXISTS `reles_grab`;
CREATE TABLE IF NOT EXISTS `reles_grab` (
  `Tiempo` datetime DEFAULT NULL,
  `id_rele` int(3) DEFAULT NULL,
  `valor_rele` int(1) DEFAULT NULL,
  `id_reles_grab` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id_reles_grab`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles_h`
--

DROP TABLE IF EXISTS `reles_h`;
CREATE TABLE IF NOT EXISTS `reles_h` (
  `id_rele` int(3) DEFAULT NULL,
  `parametro_h` varchar(10) COLLATE latin1_spanish_ci DEFAULT 'T',
  `valor_h_ON` time DEFAULT NULL,
  `valor_h_OFF` time DEFAULT NULL,
  `id_reles_h` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id_reles_h`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles_segundos_on`
--

DROP TABLE IF EXISTS `reles_segundos_on`;
CREATE TABLE IF NOT EXISTS `reles_segundos_on` (
  `id_rele` int(3) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `segundos_on` float DEFAULT NULL,
  `nconmutaciones` float DEFAULT 0,
  `id_reles_segundos_on` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id_reles_segundos_on`),
  UNIQUE KEY `id_rele_dia` (`id_rele`,`fecha`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sma`
--

DROP TABLE IF EXISTS `sma`;
CREATE TABLE IF NOT EXISTS `sma` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Tiempo` datetime NOT NULL,
  `Vbat` float NOT NULL DEFAULT 0,
  `Ibat` float NOT NULL DEFAULT 0,
  `SOC_si` float NOT NULL DEFAULT 0,
  `t_to_abs` int(10) NOT NULL DEFAULT 0,
  `VP11` float NOT NULL DEFAULT 0,
  `VP12` float NOT NULL DEFAULT 0,
  `VP21` float NOT NULL DEFAULT 0,
  `VP22` float NOT NULL DEFAULT 0,
  `IP11` float NOT NULL DEFAULT 0,
  `IP12` float NOT NULL DEFAULT 0,
  `IP21` float NOT NULL DEFAULT 0,
  `IP22` float NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `soh`
--

DROP TABLE IF EXISTS `soh`;
CREATE TABLE IF NOT EXISTS `soh` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `Ahn` float NOT NULL,
  `Ahp` float NOT NULL,
  `AhCPn` float NOT NULL,
  `AhCPp` float NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `srne`
--

DROP TABLE IF EXISTS `srne`;
CREATE TABLE IF NOT EXISTS `srne` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Tiempo` datetime NOT NULL,
  `Iplaca` float NOT NULL DEFAULT 0,
  `Vplaca` float NOT NULL DEFAULT 0,
  `Vbat` float NOT NULL DEFAULT 0,
  `Estado` enum('DEACTIVATED','ACTIVATED','BULK','EQUALIZE','ABSORTION','FLOAT','LIMITING') COLLATE latin1_spanish_ci NOT NULL,
  `SoC` int(11) DEFAULT 0,
  `Temp0` int(11) DEFAULT NULL COMMENT 'Temp Bat',
  `Temp1` int(11) DEFAULT NULL COMMENT 'Temp Reg',
  PRIMARY KEY (`id`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `victron`
--

DROP TABLE IF EXISTS `victron`;
CREATE TABLE IF NOT EXISTS `victron` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Tiempo` datetime NOT NULL,
  `Iplaca` float NOT NULL DEFAULT 0,
  `Vplaca` float NOT NULL DEFAULT 0,
  `Vbat` float NOT NULL DEFAULT 0,
  `Estado` enum('OFF','FAULT','BULK','ABSORTION','FLOAT') COLLATE latin1_spanish_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Tiempo` (`Tiempo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura para la vista `reles_activos_hoy`
--
DROP TABLE IF EXISTS `reles_activos_hoy`;

CREATE ALGORITHM=UNDEFINED DEFINER=`rpi`@`localhost` SQL SECURITY DEFINER VIEW `reles_activos_hoy`  AS  select `reles_segundos_on`.`id_rele` AS `id_rele`,`reles_segundos_on`.`fecha` AS `fecha`,`reles_segundos_on`.`segundos_on` AS `segundos_on`,`reles_segundos_on`.`nconmutaciones` AS `nconmutaciones`,`reles_segundos_on`.`id_reles_segundos_on` AS `id_reles_segundos_on` from `reles_segundos_on` where `reles_segundos_on`.`fecha` = curdate() ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
