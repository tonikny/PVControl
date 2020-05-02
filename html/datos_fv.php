<?php

$data = [];
$dat = file_get_contents('/run/shm/datos_fv.json');
$data[]= json_decode($dat, true);

$temperatura = shell_exec('cat /sys/class/thermal/thermal_zone0/temp');
$cpu=$temperatura/1000;
$data[] = str_getcsv($cpu);

$dat = file_get_contents('/run/shm/datos_reles.json');
$data[]= json_decode($dat, true);

 
header("Content-type: text/json");
#print $data;
print json_encode($data, JSON_NUMERIC_CHECK);
    
?>
