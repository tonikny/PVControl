<?php

require('conexion.php');

$sql = "SELECT estado FROM reles ORDER BY id_rele";


if($result = mysqli_query($link, $sql)){

	$rows = array();
	$i=0;
	while($row = mysqli_fetch_row($result)) {
		$rows[$i]= $row;
		$i++;
	}

	header("Content-type: text/json");
	print json_encode($rows, JSON_NUMERIC_CHECK);

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

mysqli_close($link);

?>
