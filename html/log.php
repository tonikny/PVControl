<?php
include ("cabecera.inc");
?>


<form action = "<?php $_PHP_SELF ?>" method = "POST">
    <select name="rango">
        <option value="DAY" selected="selected">Hoy</option>
        <option value="WEEK">Semana actual</option>
        <option value="MONTH">Mes actual</option>
    </select>
    <input type = "submit" value = "Ver" />
</form>
<br>


<?php


require('conexion.php');

if (!isset($_POST["rango"])) {

    $rango = "DAY";

} else {

    $rango=$_POST["rango"];
}

if($rango=="DAY") {
		  echo "DIA";
          $sql = "SELECT Tiempo,log FROM log
                        WHERE DATE(Tiempo) = CURDATE()
                        ORDER BY Tiempo DESC";

} elseif($rango=="WEEK") {
		  echo "SEMANA";
          $sql = "SELECT Tiempo,log FROM log
                        WHERE WEEK(Tiempo,1) = WEEK(CURDATE(),1) and log<>'Registro diario actualizado'
                        ORDER BY Tiempo DESC";

} elseif($rango=="MONTH") {
	      echo "MES";
          $sql = "SELECT Tiempo,log FROM log
                        WHERE MONTH(Tiempo) = MONTH(CURDATE()) AND YEAR(Tiempo) = YEAR(CURDATE()) and log<>'Registro diario actualizado'
                        ORDER BY Tiempo DESC";
}


if($result = mysqli_query($link, $sql)){

	$rawdata=array();
	$i=0;

	while ($row = mysqli_fetch_array($result)){
		$rawdata[$i]=$row;
		$i++;
	}

	echo '<table width="56%" border="1" style="text-align:center;">';
	$columnas = (isset($rawdata[0])) ? count($rawdata[0])/2 : 0;
	$filas = count($rawdata);


	//Añadimos los titulos

	for($i=0;$i<$columnas;$i++){
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


include ("pie.inc");

?>

