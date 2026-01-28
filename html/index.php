<?php

ini_set('error_reporting', E_ALL);

if (!include_once "version.inc") {
    echo "Error: Falta el archivo de configuración html/version.inc";
    exit(1);
}
if (!$version) {
    echo "Error: versión no definida en html/version.inc!";
}
if (!$archivo_inicio) {
    switch ($version) {
        case "CC":
            $i = "inicio_con_celdas.php";
            break;
        case "RD":
            $i = "inicio_red.php";
            break;
        default:
            $i = "inicio_sin_celdas.php";
            break;
    }
} else {
    $i = $archivo_inicio;
}
include_once $i;
