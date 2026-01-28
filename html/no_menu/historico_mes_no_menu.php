<?php
// Definir el SQL y el título para este gráfico específico

$t_refresco = 300000;

$titulo = "Histórico 30 días";

$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, SOC, Ibat, Iplaca, Vbat, Vplaca, PWM, Wplaca, Vred, Wred, Temp,
        Wplaca - Vbat*Ibat - Wred as Wconsumo,
        Wh_placa/1000 as Kwh_placa, (Whp_bat-Whn_bat)/1000 as Kwh_bat, (Whp_red-Whn_red)/1000 as Kwh_red,
        (Wh_placa - Whp_bat + Whn_bat - Whp_red + Whn_red)/1000 as Kwh_consumo,
        Mod_bat * 1 as Modo, Aux1, Aux2
        FROM datos_c WHERE Tiempo >= (NOW() - INTERVAL 30 DAY)
        ORDER BY Tiempo";

$rangeSelectorOptions = [
    'buttons' => [
        ['type' => 'day', 'count' => 1, 'text' => '1d'],
        ['type' => 'day', 'count' => 7, 'text' => '7d'],
        ['type' => 'day', 'count' => 15, 'text' => '15d'],
        ['type' => 'all', 'text' => 'Todo']
    ],
    'selected' => 1
];

// Incluir el archivo patrón que contiene la lógica común
include('historicoX_no_menu.php');
?>