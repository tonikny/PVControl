<?php

require('conexion.php');

$sql = "SELECT Tiempo, Vbat, Iplaca, Vplaca, SoC, Estado, Temp0, Temp1
        FROM srne
        ORDER BY Tiempo DESC LIMIT 1";
if($result = mysqli_query($link, $sql)){
    if (! $data = mysqli_fetch_assoc($result)) {
        echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }
}
mysqli_close($link);
header("Content-type: text/json");
#print $data;
print json_encode($data, JSON_NUMERIC_CHECK);
    
?>
