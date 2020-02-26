<html>
<head>
<style>
#div1 {font-size-adjust:0.41;}
table {width:100%;}
</style>
</head>
<body>


<div id="div1">
<table>

<?php

require('conexion.php');

$sql = "SELECT Fecha as ___Fecha___,maxVbat,minVbat,avgVbat,maxSOC,minSOC,avgSOC,maxIbat,minIbat,avgIbat,maxIplaca,avgIplaca,
                round(Wh_placa/1000,2) as kWh_placa,round(Whp_bat/1000,2) as kWhp_bat,
		round(Whn_bat/1000,2) as kWhn_bat,round(Wh_consumo/1000,2) as kWh_con,
		maxTemp,minTemp,avgTemp
		FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY) GROUP BY Fecha ORDER BY Fecha DESC";

if($result = mysqli_query($link, $sql)){

	$rawdata=array();
	$i=0;

	while ($row = mysqli_fetch_array($result)){
		$rawdata[$i]=$row;

		$rele[$i]=$row;  //Pasar contenido a rele[$i]

		$i++;
	}

	echo '<table width="56%" border="1" style="text-align:center;">';
	$columnas = count($rawdata[0])/2;
	$filas = count($rawdata);


	//Añadimos los titulos

	for($i=1;$i<count($rawdata[0]);$i=$i+2){
		next($rawdata[0]);
		echo "<th><b>".key($rawdata[0])."</b></th>";
		next($rawdata[0]);
	}

	for($i=0;$i<$filas;$i++){

		echo "<tr>";
		for($j=0;$j<$columnas;$j++){
			echo "<td>".$rawdata[$i][$j]."</td>";
		}
		echo "</tr>";
	}

	echo '</table>';

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


mysqli_close($link);

echo "<br \>";


?>
</table>
</div>

</body>
</html>
