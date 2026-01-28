<?php
// Definir el SQL y el título para este gráfico específico

$t_refresco = 0;

$titulo = "Histórico 1 días";

$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, SOC, Ibat, Iplaca, Vbat, Vplaca, PWM, Wplaca, Vred, Wred, Temp,
        Wplaca - Vbat*Ibat - Wred as Wconsumo,
        Wh_placa/1000 as Kwh_placa, (Whp_bat-Whn_bat)/1000 as Kwh_bat, (Whp_red-Whn_red)/1000 as Kwh_red,
        (Wh_placa - Whp_bat + Whn_bat - Whp_red + Whn_red)/1000 as Kwh_consumo,
        Mod_bat * 1 as Modo, Aux1, Aux2
        FROM datos WHERE Tiempo >= (NOW() - INTERVAL 25 HOUR)
        ORDER BY Tiempo";

$rangeSelectorOptions = [
    'buttons' => [
        ['type' => 'hour', 'count' => 1, 'text' => '1h'],
        ['type' => 'hour', 'count' => 8, 'text' => '8h'],
        ['type' => 'hour', 'count' => 16, 'text' => '16h'],
        ['type' => 'all', 'text' => 'Todo']
    ],
    'selected' => 1
];

// Incluir el archivo patrón que contiene la lógica común
include('historicoX_no_menu.php');
?>