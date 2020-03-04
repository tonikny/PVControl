<?php

require('conexion.php');

$sql = "SELECT Ibat,Vbat,SOC,Iplaca,Vplaca,Wplaca,Temp,Aux1,Aux2,PWM FROM datos ORDER BY id DESC LIMIT 1";


$temperatura = shell_exec('cat /sys/class/thermal/thermal_zone0/temp');
$cpu=$temperatura/1000;

if($result = mysqli_query($link, $sql)){

        $row=mysqli_fetch_row($result);
        $row[10]=$cpu;
        header("Content-type: text/json");
        print json_encode($row, JSON_NUMERIC_CHECK);

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

mysqli_close($link);

?>

