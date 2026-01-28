<?php
session_start([
    'cookie_lifetime' => 0,
]);
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="es-ES" lang="es-ES">

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="cache-control" content="no-cache" />
    <meta http-equiv="expires" content="0" />
    <link href="/img/favicon.ico" rel="shortcut icon" type="image/x-icon" />
    <link href="/css/index.css" rel="stylesheet" type="text/css" media="screen" />
    <link href="/css/inicio.css" rel="stylesheet" type="text/css" media="screen" />
    <link href="/css/menu.css" rel="stylesheet" type="text/css" media="screen" />
    <title>
        <?php echo $titulo; ?>:PVControl+:Control sistema fotovoltaico
    </title>

</head>

<body>
    <script src="/Parametros_Web_DIST.js"></script>
    <script src="/Parametros_Web.js"></script>
    <?php
    include_once "version.inc";
    if ($version != "SC" && $version != "CC" && $version != "RD") {
        echo "<div>Error: Falta el archivo de configuración html/version.inc o la versión no está definida</div>";
        exit(1);
    }
    $menu_inicio["Inicio"] = ["Inicio", "/"];

    $menu["Utilidades"]["Meteo"] = ["Meteorología", "/meteogram.php"];
    ($version == "RD") ?: $menu["Utilidades"]["SOC"] = ["SOC", "/actualizar_soc.php"];
    $menu["Utilidades"]["Log"] = ["Log", "/log.php"];
    $menu["Utilidades"]["Parametros"] = ["Parametros", "/parametros.php"];
    $menu["Utilidades"]["Servicios"] = ["Servicios", "/servicios.php"];

    $menu["Gráficas"]["KWh"] = ($version != "RD") ? ["KWh Batería, Producción y Consumo", "/wh.php"] : ["KWh Red, Producción y Consumo", "wh_red.php"];
    $menu["Gráficas"]["Promedios"] = ["Promedios 30 días", "/prom_30.php"];
    $menu["Gráficas"]["Hist_Fechas"] = ["Histórico Fechas", "/historico_fechas.php"];
    $menu["Gráficas"]["Hist_8h"] = ["Histórico 8 horas", "/historico_horas.php"];
    $menu["Gráficas"]["Hist_1"] = ["Histórico 1 Día", "/historico1.php"];
    $menu["Gráficas"]["Hist_3"] = ["Histórico 3 Días", "/historico3c.php"];
    $menu["Gráficas"]["Hist_Mes"] = ["Histórico Mes", "/historico_mes.php"];
    $menu["Gráficas"]["Hist_Personal"] = ["Histórico Personal", "/historico_aux.php"];

    ($version == "RD") ?: $menu["Gráficas"]["Hist_Ciclado"] = ["Histórico Ciclado", "/historico_soh.php"];
    $menu["Gráficas"]["Extra"] = ["Gráficas Producción y Consumo", "/grafica_elige.php"];
    $menu["Gráficas"]["Diario"] = ($version != "RD") ? ["Tabla resumen diario", "/diario.php"] : ["Tabla resumen diario", "diario_red.php"];
    ($version == "RD") ?: $menu["Gráficas"]["Carga/Desc"] = ["Eficiencia Carga/Descarga Batería", "/wh_2.php"];

    $menu["Equipos"]["Equipos"] = ["Tabla equipamiento en uso", "/equipos.php"];
    $menu["Equipos"]["Hibrido"] = ["Histórico Hibrido", "/historico_hibrido.php"];
    // $menu["Equipos"]["Fronius"] = ["Fronius", ".php"];
    // $menu["Equipos"]["Huawei"] = ["Huawei", ".php"];
    // $menu["Equipos"]["SMA"] = ["SMA", ".php"];
    // $menu["Equipos"]["BMV"] = ["BMV", ".php"];
    $menu["Equipos"]["SRNE"] = ["SRNE", "/srne.php"];

    $menu["Relés"]["T.Relés"] = ["Gestión Relés", "/reles.php"];
    $menu["Relés"]["H.Relés"] = ["Horas Funcionamiento Relés", "/horas_reles.php"];

    ($version != "CC") ?: $menu["Celdas"]["Día"] = ["Gráfica diaria", "/historico_celdas.php"];
    ($version != "CC") ?: $menu["Celdas"]["Resumen"] = ["Gráficas resumen", "/historico_celdas_max_min.php"];

    $menu_ayuda["Ayuda"] = ["Ayuda", "/ayuda.php"];

    $icono["Inicio"] = "/img/Home.png";
    $icono["Utilidades"] = "/img/util.jpg";
    $icono["Gráficas"] = "/img/Graph.png";
    $icono["Equipos"] = "/img/inverter.png";
    $icono["Relés"] = "/img/Target.png";
    $icono["Celdas"] = "/img/bateria.png";
    $icono["Ayuda"] = "/img/help.png";
    ?>

    <div id="contenedor">
        <div id="cabecera">
            <!-- capçalera original -->
            <a id="logo-header" href="<?= $menu_inicio["Inicio"][1]; ?>">
                <img src="/img/fvcontrol.png" alt="Control Placas Solares" style="width:200px;height:60px;" />
            </a>

            <nav id="menu"> <input id="responsive-menu" type="checkbox"><label></label>
                <ul>
                    <!-- Inici -->
                    <li>
                        <a href="<?= $menu_inicio["Inicio"][1]; ?>" title="Inicio">
                            <img src="<?= $icono["Inicio"]; ?>" width="20" height="20" alt="">
                            Inicio
                        </a>
                    </li>
                    <!-- Menus -->
                    <?php
                    foreach (array_keys($menu) as $grupo) { ?>
                        <li>
                            <a class="dropdown-arrow" href="#" title="<?= $grupo; ?>">
                                <img src="<?= $icono[$grupo]; ?>" width="20" height="20" alt="">
                                <?= $grupo; ?>
                            </a>
                            <ul class="sub-menus">
                                <?php
                                foreach (array_keys($menu[$grupo]) as $entrada) { ?>
                                    <li>
                                        <a href="<?= $menu[$grupo][$entrada][1]; ?>" title="<?= $menu[$grupo][$entrada][0]; ?>">
                                            <?= $entrada; ?>
                                        </a>
                                    </li>
                                <?php } ?>
                            </ul>
                        </li>
                    <?php } ?>
                    <li>
                        <a href="<?= $menu_ayuda["Ayuda"][1]; ?>">
                            <img src="<?= $icono["Ayuda"]; ?>" width="20" height="20" alt="">Ayuda
                        </a>
                    </li>
                </ul>
            </nav>
        </div>

        <div id="contenido">
            <br>
