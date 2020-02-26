<?php

require('conexion.php');

$sql = "SELECT nombre,estado FROM reles ORDER BY id_rele";

if($result = mysqli_query($link, $sql)){

        $i=0;
        while($row = mysqli_fetch_row($result)) {
                $rele[$i]= $row;
                $i++;
        }
        header("Content-type: text/json");
        echo json_encode($rele, JSON_NUMERIC_CHECK);


} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}




mysqli_close($link);

?>

