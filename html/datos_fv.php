<?php

require('conexion.php');

$data = [];
$sql = "SELECT * FROM equipos WHERE id_equipo IN ('FV','RELES','TEMP')";

if($result = mysqli_query($link, $sql)){
    while ($row = mysqli_fetch_array($result)){
        $data[$row[0]]=json_decode($row[2], true);
        $data[$row[0]]["tiempo"]=$row[1];
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }


$sql = "SELECT * FROM equipos WHERE SUBSTRING(`id_equipo`, 1, 3) IN ('BMS') ORDER BY id_equipo";
/**/
if($result = mysqli_query($link, $sql)){
    while ($row = mysqli_fetch_array($result)){
        $data["BMS"][$row[0]]=json_decode($row[2], true);
        $data["BMS"][$row[0]]["tiempo"]=$row[1];
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
