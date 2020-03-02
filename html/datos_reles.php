<?php

$csvFile = file('/run/shm/datos_reles.csv');
 $data = [];
    foreach ($csvFile as $line) {
        $data[] = str_getcsv($line);
    }
  
 header("Content-type: text/json");
 print json_encode($data, JSON_NUMERIC_CHECK);
 

?>

