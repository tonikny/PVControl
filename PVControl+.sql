-- phpMyAdmin SQL Dump
-- version 5.1.2
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 02-02-2022 a las 18:14:16
-- Versión del servidor: 10.5.12-MariaDB-0+deb11u1
-- Versión de PHP: 8.1.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `control_solar`
--
CREATE DATABASE IF NOT EXISTS `control_solar` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `control_solar`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bmv`
--

CREATE TABLE `bmv` (
  `id` int(11) NOT NULL,
  `Tiempo` datetime NOT NULL COMMENT 'Fecha captura',
  `SOC` float NOT NULL DEFAULT 0 COMMENT 'SOC bateria',
  `Vbat` float NOT NULL DEFAULT 0 COMMENT 'Voltaje Bateria',
  `Vm` float NOT NULL DEFAULT 0 COMMENT 'Valor Medio Bateria',
  `Temp` float NOT NULL DEFAULT 0 COMMENT 'Temperatura',
  `Ibat` float NOT NULL DEFAULT 0 COMMENT 'Intensidad Bateria'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `condiciones`
--

CREATE TABLE `condiciones` (
  `activado` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1 para activar la condicion',
  `condicion1` text COLLATE latin1_spanish_ci NOT NULL COMMENT 'expresión a evaluar 1 ',
  `condicion2` text COLLATE latin1_spanish_ci NOT NULL COMMENT 'expresion a evaluar 2 (se realiza un "AND" con la condicion 1',
  `accion` text COLLATE latin1_spanish_ci NOT NULL COMMENT 'Expresion en Python que se ejecuta si se cumple la condicion1 y la condicion2',
  `descripcion` text COLLATE latin1_spanish_ci NOT NULL,
  `id_condicion` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

--
-- Volcado de datos para la tabla `condiciones`
--

INSERT INTO `condiciones` (`activado`, `condicion1`, `condicion2`, `accion`, `descripcion`, `id_condicion`) VALUES
(0, '', '', 'PWM = 72', 'Simula Excedentes a un valor', 105);

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
  `PWM` float NOT NULL DEFAULT 0 COMMENT 'PWM total para excedentes',
  `Mod_bat` enum('OFF','BULK','FLOT','ABS','EQU','INYECT','CONS') COLLATE latin1_spanish_ci NOT NULL DEFAULT 'BULK',
  `Vred` float NOT NULL DEFAULT 0 COMMENT 'V red AC',
  `Wred` float NOT NULL DEFAULT 0 COMMENT 'W inyectados o consumidos de red',
  `Whn_red` float NOT NULL DEFAULT 0 COMMENT 'Wh consumidos de red',
  `Whp_red` float NOT NULL DEFAULT 0 COMMENT 'Wh inyectados a red'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos_c`
--

CREATE TABLE `datos_c` (
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
  `Whp_red` float NOT NULL DEFAULT 0 COMMENT 'Wh inyectados a red'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos_celdas`
--

CREATE TABLE `datos_celdas` (
  `id_celda` int(11) NOT NULL,
  `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
  `C1` float NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos_s`
--

CREATE TABLE `datos_s` (
  `id` int(10) UNSIGNED NOT NULL COMMENT 'Indentificador Captura',
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
  `Whp_red` float NOT NULL DEFAULT 0 COMMENT 'Wh inyectados a red'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `diario`
--

CREATE TABLE `diario` (
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
  `minVred` float NOT NULL DEFAULT 0 COMMENT 'minima Vred'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `equipos`
--

CREATE TABLE `equipos` (
  `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
  `tiempo` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha Actualizacion',
  `sensores` varchar(5000) COLLATE latin1_spanish_ci NOT NULL
) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `hibrido`
--

CREATE TABLE `hibrido` (
  `id` int(11) NOT NULL,
  `Tiempo` datetime NOT NULL,
  `Vgen` float NOT NULL DEFAULT 0,
  `Fgen` float NOT NULL DEFAULT 0,
  `Iplaca` float NOT NULL DEFAULT 0,
  `Vplaca` float NOT NULL DEFAULT 0,
  `Wplaca` smallint(5) NOT NULL DEFAULT 0,
  `Vbat` float NOT NULL DEFAULT 0,
  `Vbus` smallint(3) NOT NULL DEFAULT 0,
  `Ibatp` float NOT NULL DEFAULT 0,
  `Ibatn` float NOT NULL DEFAULT 0,
  `temp` float NOT NULL DEFAULT 0,
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
  `id_parametros` tinyint(4) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

--
-- Volcado de datos para la tabla `parametros`
--

INSERT INTO `parametros` (`grabar_datos`, `grabar_reles`, `t_muestra`, `n_muestras_grab`, `nuevo_soc`, `objetivo_PID`, `sensor_PID`, `Kp`, `Ki`, `Kd`, `Mod_bat`, `Vflot`, `Vabs`, `Tabs`, `Vequ`, `Tequ`, `Icola`, `coef_temp`, `id_parametros`) VALUES
('S', 'S', 5, 1, 0, 28.8, 'Vbat', 10, 0, 10, 'BULK', 27.2, 28.8, 3600, 29.6, 3600, 4, 0, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `parametros1`
--

CREATE TABLE `parametros1` (
  `id_parametro` int(11) NOT NULL,
  `nombre` varchar(100) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
  `valor` varchar(100) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reles`
--

CREATE TABLE `reles` (
  `id_rele` int(3) NOT NULL DEFAULT 0,
  `nombre` text COLLATE latin1_spanish_ci DEFAULT NULL,
  `modo` varchar(3) COLLATE latin1_spanish_ci DEFAULT 'PRG',
  `estado` float DEFAULT 0,
  `grabacion` varchar(1) COLLATE latin1_spanish_ci DEFAULT 'N',
  `salto` float DEFAULT 100,
  `prioridad` int(2) DEFAULT 0 COMMENT 'Define la prioridad en la asignacion de excedentes \r\n - 0 no se utiliza en la asignacion de excedentes)\r\n\r\n - 1 Primera prioridad\r\n\r\n - 2 - Segunda prioridad\r\n\r\n - Etc',
  `potencia` int(11) DEFAULT 0 COMMENT 'Watios potencia maxima que controla el rele',
  `retardo` int(11) DEFAULT 0 COMMENT 'Segundos a esperar entre dos cambios de estado del rele',
  `calibracion` varchar(500) COLLATE latin1_spanish_ci NOT NULL DEFAULT '' COMMENT 'Calibracion respuesta SSR [%Potencia, Duty PWM]'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

--
-- Volcado de datos para la tabla `reles`
--

INSERT INTO `reles` (`id_rele`, `nombre`, `modo`, `estado`, `grabacion`, `salto`, `prioridad`, `potencia`, `retardo`, `calibracion`) VALUES
(511, 'Rele TASMOTA', 'PRG', 0, 'N', 100, 1, 1000, 0, '');

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
-- Estructura de tabla para la tabla `sma`
--

CREATE TABLE `sma` (
  `id` int(11) NOT NULL,
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
  `IP22` float NOT NULL DEFAULT 0
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
-- Estructura de tabla para la tabla `srne`
--

CREATE TABLE `srne` (
  `id` int(11) NOT NULL,
  `Tiempo` datetime NOT NULL,
  `Iplaca` float NOT NULL DEFAULT 0,
  `Vplaca` float NOT NULL DEFAULT 0,
  `Vbat` float NOT NULL DEFAULT 0,
  `Estado` enum('DEACTIVATED','ACTIVATED','BULK','EQUALIZE','ABSORTION','FLOAT','LIMITING') COLLATE latin1_spanish_ci NOT NULL,
  `SoC` int(11) DEFAULT 0,
  `Temp0` int(11) DEFAULT NULL COMMENT 'Temp Bat',
  `Temp1` int(11) DEFAULT NULL COMMENT 'Temp Reg'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `victron`
--

CREATE TABLE `victron` (
  `id` int(11) NOT NULL,
  `Tiempo` datetime NOT NULL,
  `Iplaca` float NOT NULL DEFAULT 0,
  `Vplaca` float NOT NULL DEFAULT 0,
  `Vbat` float NOT NULL DEFAULT 0,
  `Estado` enum('OFF','FAULT','BULK','ABSORTION','FLOAT') COLLATE latin1_spanish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura para la vista `reles_activos_hoy`
--
DROP TABLE IF EXISTS `reles_activos_hoy`;

CREATE ALGORITHM=UNDEFINED DEFINER=`rpi`@`localhost` SQL SECURITY DEFINER VIEW `reles_activos_hoy`  AS SELECT `reles_segundos_on`.`id_rele` AS `id_rele`, `reles_segundos_on`.`fecha` AS `fecha`, `reles_segundos_on`.`segundos_on` AS `segundos_on`, `reles_segundos_on`.`nconmutaciones` AS `nconmutaciones`, `reles_segundos_on`.`id_reles_segundos_on` AS `id_reles_segundos_on` FROM `reles_segundos_on` WHERE `reles_segundos_on`.`fecha` = curdate()  ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `bmv`
--
ALTER TABLE `bmv`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Tiempo` (`Tiempo`);

--
-- Indices de la tabla `condiciones`
--
ALTER TABLE `condiciones`
  ADD PRIMARY KEY (`id_condicion`);

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
-- Indices de la tabla `datos_celdas`
--
ALTER TABLE `datos_celdas`
  ADD PRIMARY KEY (`id_celda`),
  ADD KEY `Tiempo` (`Tiempo`);

--
-- Indices de la tabla `datos_s`
--
ALTER TABLE `datos_s`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Tiempo` (`Tiempo`);

--
-- Indices de la tabla `diario`
--
ALTER TABLE `diario`
  ADD PRIMARY KEY (`Fecha`);

--
-- Indices de la tabla `equipos`
--
ALTER TABLE `equipos`
  ADD PRIMARY KEY (`id_equipo`);

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
-- Indices de la tabla `parametros1`
--
ALTER TABLE `parametros1`
  ADD PRIMARY KEY (`id_parametro`);

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
  ADD PRIMARY KEY (`id_reles_segundos_on`),
  ADD UNIQUE KEY `id_rele_dia` (`id_rele`,`fecha`);

--
-- Indices de la tabla `sma`
--
ALTER TABLE `sma`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Tiempo` (`Tiempo`);

--
-- Indices de la tabla `soh`
--
ALTER TABLE `soh`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `srne`
--
ALTER TABLE `srne`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Tiempo` (`Tiempo`);

--
-- Indices de la tabla `victron`
--
ALTER TABLE `victron`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Tiempo` (`Tiempo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `bmv`
--
ALTER TABLE `bmv`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `condiciones`
--
ALTER TABLE `condiciones`
  MODIFY `id_condicion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=106;

--
-- AUTO_INCREMENT de la tabla `datos`
--
ALTER TABLE `datos`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Identificador captura';

--
-- AUTO_INCREMENT de la tabla `datos_celdas`
--
ALTER TABLE `datos_celdas`
  MODIFY `id_celda` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `datos_s`
--
ALTER TABLE `datos_s`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Indentificador Captura';

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
-- AUTO_INCREMENT de la tabla `sma`
--
ALTER TABLE `sma`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `soh`
--
ALTER TABLE `soh`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `srne`
--
ALTER TABLE `srne`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `victron`
--
ALTER TABLE `victron`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
