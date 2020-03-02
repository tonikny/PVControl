<?php

$handle = fopen("/run/shm/datos_fv.csv", "r");
for ($i = 0; $row = fgetcsv($handle ); ++$i) {
    // Do something will $row array
}
fclose($handle);

echo $row

header("Content-type: text/json");
print json_encode($row, JSON_NUMERIC_CHECK);
        
 ?>
