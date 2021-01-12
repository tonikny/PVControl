<?php
session_start([
    'cookie_lifetime' => 0,
]);
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="es-ES" lang="es-ES">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link href="img/favicon.ico" rel="shortcut icon" type="image/x-icon" />
    <link href="css/index.css" rel="stylesheet" type="text/css" media="screen" />
    <link href="css/inicio.css" rel="stylesheet" type="text/css" media="screen" />
    <style type="text/css">
        body {
            #color: purple;
            background: linear-gradient(to bottom, white, #fafafa);}
    </style>
    <title>PVControl+:Control sistema fotovoltaico</title>
</head>

<body>

    <div id="contenedor">
        <div id="cabecera">
            <a id="logo-header" href="index.php">
                <span class="site-name"><img src="img/fvcontrol.png" alt="logo" style="width:200px;height:60px;" /></span>
                
            </a> 
            <?php
            $recibe_pagina=$_GET['pagina'];
             ?>

            <nav>
                <ul>
                    <!-- Inicio -->
                    <li><a href="/" 
                        title="Inicio"><img src="img/Home.png" width="20" height="20"> Inicio</a>
                    </li>
                    
                    <!-- Utilidades -->
                    <li><a href="#" 
                        title="Utilidades"><img src="img/util.jpg" width="20" height="20"> Utilidades</a>
                        <ul>
                            <li><a href="meteogram.php"
                                title="Gráficas Prevision Meteorologica">Meteorologia</a>
                            </li>
                            <li><a href="log.php"
                                title="Logs del sistema">Log</a>
                            </li>
                            
                        </ul>
                    </li>

                    <!-- Graficas -->
                    <li><a href="#"
                        title="Gráficas"><img src="img/Graph.png" width="20" height="20"> Gráficas</a>
                        <ul>
                            <li><a href="wh.php"
                                title="KWh Batería, Producción y Consumo">KWh</a>
                            </li>
                            <li><a href="prom_30.php"
                                title="Promedios 30 días">Promedios</a>
                            </li>
                            <li><a href="historico_con_temp.php"
                                title="Histórico temp">Hist_Temp</a>
                            </li>
                            <li><a href="historico_horas.php"
                                title="Histórico 8 horas">Hist_8h</a>
                            </li>
                            <li><a href="historico1.php"
                                title="Histórico 1 días">Hist_1</a>
                            </li>
                            <li><a href="historico3c.php"
                                title="Histórico 3 días">Hist_3</a>
                            </li>
                            <li><a href="historico_mes.php"
                                title="Histórico Mes">Hist_Mes</a>
                            </li>
                            <li><a href="historico_soh.php"
                                title="Histórico Ciclado">Hist_Ciclado</a>
                            </li>
                            <li><a href="grafica_elige.php"
                                title="Gráficas Producción y Consumo">Extra</a>
                            </li>
                            
                            <li><a href="diario.php"
                                title="Tabla resumen diario">Diario</a>
                            </li>
                            <li><a href="wh_2.php"
                                title="Eficiencia Carga/Descarga Bateria">Carga/Descaga</a>
                            </li>
                            
                        </ul>
                    </li>

                    <!-- Equipos -->
                    <li><a href="#" 
                        title="Equipos"><img src="img/inverter.png" width="20" height="20"> Equipos</a>
                        <ul>
                            <li><a href="historico_hibrido.php"
                                title="Hist_Hibrido">Hibrido</a>
                            </li>
                            <li><a href="#"
                                title="Fronius">Fronius</a>
                            </li>
                            <li><a href="#"
                                title="Huawei">Huawei</a>
                            </li>
                            <li><a href="#"
                                title="SMA">SMA</a>
                            </li>
                            <li><a href="#"
                                title="BMV">BMV</a>
                            </li>
                            <li><a href="srne.php"
                                title="SRNE">SRNE</a>
                            </li>
                        </ul>
                    </li>
                    
                   <!-- Reles -->
                    <li><a href="#"
                        title="Relés"><img src="img/Target.png" width="20" height="20"> Relés</a>
                        <ul>
                            <li><a href="reles.php"
                                title="Tabla relés">T.Relés</a>
                            </li>
                            <li><a href="horas_reles.php"
                                title="Horas funcionamiento">H.Relés</a>
                            </li>
                        </ul>
                    </li>  
                    
                    <!-- Celdas 
                    <li><a href="#"
                        title="Celdas"><img src="img/bateria.png" width="20" height="20"> Celdas</a>
                        <ul>
                            <li><a href="index.php?pagina=celda1"
                                title="Grafica diaria">Dia</a>
                            </li>
                            <li><a href="index.php?pagina=celda2"
                                title="Graficas resumen">Resumen</a>
                            </li>
                        </ul>
                    </li>
                    -->
                </ul>
            </nav>
        </div> 
        <script src="Parametros_Web.js"></script>
        
        <div id="contenido">
            <br>

