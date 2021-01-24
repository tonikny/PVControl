<?php

require('conexion.php');

$soc = mysqli_real_escape_string($link, $_POST['SOC']);


// attempt insert query execution

$sql = "UPDATE parametros SET nuevo_soc='$soc'";

if(mysqli_query($link, $sql)){
	header("Location: actualizar_soc.php");
//	echo "Records added successfully.";

} else{

	echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);

}

// close connection

mysqli_close($link);

?>

