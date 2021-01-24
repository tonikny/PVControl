<?php

//error_reporting(E_ALL ^ E_NOTICE);
// Lo mismo que error_reporting(E_ALL);
ini_set('error_reporting', E_ALL);

include_once("version.inc");
switch ($version) {
    case "CC":  $i = "inicio_con_celdas.php";
                break;
    case "RD":  $i = "inicio_red.php";
                break;
    default:    $i = "inicio_sin_celdas.php";
                break;
}
include ($i);
?>
