-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 16-12-2019 a las 19:50:11
-- Versión del servidor: 10.3.17-MariaDB-0+deb10u1
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
CREATE DATABASE IF NOT EXISTS `control_solar_2` DEFAULT CHARACTER SET latin1 COLLATE latin1_spanish_ci;
USE `control_solar_2`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos`
--

CREATE TABLE `datos` (
  `id` int(10) UNSIGNED NOT NULL COMMENT 'Identificador captura',
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
  `PWM` int(4) NOT NULL DEFAULT 0 COMMENT 'PWM total para excedentes'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos_c`
--

CREATE TABLE `datos_c` (
  `id` int(10) UNSIGNED NOT NULL,
  `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
  `Ibat` float NOT NULL DEFAULT 0,
  `Vbat` float NOT NULL DEFAULT 0,
  `SOC` float NOT NULL DEFAULT 0,
  `DS` float NOT NULL DEFAULT 0,
  `Aux1` float NOT NULL DEFAULT 0,
  `Aux2` float NOT NULL DEFAULT 0,
  `Whp_bat` float NOT NULL DEFAULT 0,
  `Whn_bat` float NOT NULL DEFAULT 0,
  `Iplaca` float NOT NULL DEFAULT 0,
  `Vplaca` float NOT NULL DEFAULT 0,
  `Wplaca` float NOT NULL DEFAULT 0,
  `Wh_placa` float NOT NULL DEFAULT 0,
  `Temp` float NOT NULL DEFAULT 0,
  `PWM` int(4) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos_mux_1`
--

CREATE TABLE `datos_mux_1` (
  `id_mux_1` int(11) NOT NULL,
  `Tiempo` datetime NOT NULL,
  `C0` float NOT NULL,
  `C1` float NOT NULL,
  `C2` float NOT NULL,
  `C3` float NOT NULL,
  `C4` float NOT NULL,
  `C5` float NOT NULL,
  `C6` float NOT NULL,
  `C7` float NOT NULL,
  `C8` float NOT NULL,
  `C9` float NOT NULL,
  `C10` float NOT NULL,
  `C11` float NOT NULL,
  `C12` float NOT NULL,
  `C13` float NOT NULL,
  `C14` float NOT NULL,
  `C15` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `diario`
--

CREATE TABLE `diario` (
  `Fecha` date NOT NULL,
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
  `avgTemp` float NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `hibrido`
--

CREATE TABLE `hibrido` (
  `id` int(11) NOT NULL,
  `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
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
  `OnOff` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `log`
--

CREATE TABLE `log` (
  `id_log` int(11) NOT NULL,
  `Tiempo` datetime NOT NULL,
  `log` varchar(50) CHARACTER SET latin1 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `parametros`
--

CREATE TABLE `parametros` (
  `grabar_datos` set('S','N') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'S',
  `grabar_reles` set('S','N') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'N',
  `t_muestra` float NOT NULL,
  `n_muestras_grab` int(3) NOT NULL,
  `nuevo_soc` float NOT NULL DEFAULT 0 COMMENT 'valor distinto de 0 actualiza',
  `objetivo_diver` float NOT NULL COMMENT 'Valor objetivo a conseguir por el control PID',
  `sensor_diver` set('Aux1','Aux2','Vplaca','Vbat','Hz','Vplaca_Vbat','Ibat') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'Aux1' COMMENT 'Variable de control PID',
  `Kp` float NOT NULL DEFAULT 10 COMMENT 'Constante proporcional PID',
  `Ki` float NOT NULL DEFAULT 0 COMMENT 'Constante Integral PID',
  `Kd` float NOT NULL DEFAULT 0 COMMENT 'Constante derivativa PID',
  `id_parametros` tinyint(4) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles`
--

CREATE TABLE `reles` (
  `id_rele` int(3) NOT NULL DEFAULT 0,
  `nombre` text CHARACTER SET latin1 DEFAULT NULL,
  `modo` varchar(3) CHARACTER SET latin1 DEFAULT 'PRG',
  `estado` int(1) DEFAULT 0,
  `grabacion` varchar(1) CHARACTER SET latin1 DEFAULT 'N',
  `salto` int(3) NOT NULL DEFAULT 100,
  `prioridad` int(2) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `reles_activos_hoy`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `reles_activos_hoy` (
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

CREATE TABLE `reles_c` (
  `id_rele` int(3) DEFAULT NULL,
  `operacion` text CHARACTER SET latin1 DEFAULT NULL,
  `parametro` text CHARACTER SET latin1 DEFAULT NULL,
  `condicion` text CHARACTER SET latin1 DEFAULT NULL,
  `valor` float DEFAULT NULL,
  `id_reles_c` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles_grab`
--

CREATE TABLE `reles_grab` (
  `Tiempo` datetime DEFAULT NULL,
  `id_rele` int(3) DEFAULT NULL,
  `valor_rele` int(1) DEFAULT NULL,
  `id_reles_grab` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles_h`
--

CREATE TABLE `reles_h` (
  `id_rele` int(3) DEFAULT NULL,
  `parametro_h` varchar(1) CHARACTER SET latin1 DEFAULT 'T',
  `valor_h_ON` time DEFAULT NULL,
  `valor_h_OFF` time DEFAULT NULL,
  `id_reles_h` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles_segundos_on`
--

CREATE TABLE `reles_segundos_on` (
  `id_rele` int(3) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `segundos_on` float DEFAULT NULL,
  `nconmutaciones` float DEFAULT 0,
  `id_reles_segundos_on` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `soh`
--

CREATE TABLE `soh` (
  `id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `Ahn` float NOT NULL,
  `Ahp` float NOT NULL,
  `AhCPn` float NOT NULL,
  `AhCPp` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura para la vista `reles_activos_hoy`
--
DROP TABLE IF EXISTS `reles_activos_hoy`;

CREATE ALGORITHM=UNDEFINED DEFINER=`rpi`@`localhost` SQL SECURITY DEFINER VIEW `reles_activos_hoy`  AS  select `reles_segundos_on`.`id_rele` AS `id_rele`,`reles_segundos_on`.`fecha` AS `fecha`,`reles_segundos_on`.`segundos_on` AS `segundos_on`,`reles_segundos_on`.`nconmutaciones` AS `nconmutaciones`,`reles_segundos_on`.`id_reles_segundos_on` AS `id_reles_segundos_on` from `reles_segundos_on` where `reles_segundos_on`.`fecha` = curdate() ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `datos`
--
ALTER TABLE `datos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Tiempo` (`Tiempo`);

--
-- Indices de la tabla `datos_c`
--
ALTER TABLE `datos_c`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Tiempo` (`Tiempo`);

--
-- Indices de la tabla `datos_mux_1`
--
ALTER TABLE `datos_mux_1`
  ADD PRIMARY KEY (`id_mux_1`);

--
-- Indices de la tabla `diario`
--
ALTER TABLE `diario`
  ADD PRIMARY KEY (`Fecha`);

--
-- Indices de la tabla `hibrido`
--
ALTER TABLE `hibrido`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Tiempo` (`Tiempo`);

--
-- Indices de la tabla `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`id_log`);

--
-- Indices de la tabla `parametros`
--
ALTER TABLE `parametros`
  ADD PRIMARY KEY (`id_parametros`);

--
-- Indices de la tabla `reles`
--
ALTER TABLE `reles`
  ADD PRIMARY KEY (`id_rele`);

--
-- Indices de la tabla `reles_c`
--
ALTER TABLE `reles_c`
  ADD PRIMARY KEY (`id_reles_c`);

--
-- Indices de la tabla `reles_grab`
--
ALTER TABLE `reles_grab`
  ADD PRIMARY KEY (`id_reles_grab`);

--
-- Indices de la tabla `reles_h`
--
ALTER TABLE `reles_h`
  ADD PRIMARY KEY (`id_reles_h`);

--
-- Indices de la tabla `reles_segundos_on`
--
ALTER TABLE `reles_segundos_on`
  ADD PRIMARY KEY (`id_reles_segundos_on`);

--
-- Indices de la tabla `soh`
--
ALTER TABLE `soh`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `datos`
--
ALTER TABLE `datos`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Identificador captura';

--
-- AUTO_INCREMENT de la tabla `hibrido`
--
ALTER TABLE `hibrido`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `log`
--
ALTER TABLE `log`
  MODIFY `id_log` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reles_c`
--
ALTER TABLE `reles_c`
  MODIFY `id_reles_c` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reles_grab`
--
ALTER TABLE `reles_grab`
  MODIFY `id_reles_grab` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reles_h`
--
ALTER TABLE `reles_h`
  MODIFY `id_reles_h` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reles_segundos_on`
--
ALTER TABLE `reles_segundos_on`
  MODIFY `id_reles_segundos_on` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `soh`
--
ALTER TABLE `soh`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
