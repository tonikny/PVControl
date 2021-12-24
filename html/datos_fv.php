<?php

require('conexion.php');

$data = [];
$sql = "SELECT * FROM equipos WHERE id_equipo IN ('FV','CELDAS','RELES','TEMP')";

if($result = mysqli_query($link, $sql)){
    while ($row = mysqli_fetch_array($result)){
        $data[$row[0]]=json_decode($row[2], true);
        $data[$row[0]]["tiempo"]=$row[1];
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }
    
mysqli_close($link); 
header("Content-type: text/json");
#print $data;
#var_dump($data);
print json_encode($data, JSON_NUMERIC_CHECK);
    
?>
