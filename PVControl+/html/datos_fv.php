<?php

 $csvFile = file('/run/shm/datos_fv.csv');
 $data = [];
    foreach ($csvFile as $line) {
        $data[] = str_getcsv($line);
    }
 
 $temperatura = shell_exec('cat /sys/class/thermal/thermal_zone0/temp');
 $cpu=$temperatura/1000;
       
 $data[] = str_getcsv($cpu);
 
 
 header("Content-type: text/json");
 print json_encode($data, JSON_NUMERIC_CHECK);
    
?>
