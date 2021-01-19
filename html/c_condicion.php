<?php

require('conexion.php');

$id_cond = mysqli_real_escape_string($link, $_POST['id_condicion']);

$ac = mysqli_real_escape_string($link, $_POST['activado']);
$ac = ($ac)?0:1; //cambiar valor

// attempt insert query execution

$sql = "UPDATE condiciones SET activado='$ac' WHERE id_condicion=$id_cond";

if(mysqli_query($link, $sql)){
	sleep(2);
	header("Location: reles.php");
//	echo "Records added successfully.";

} else{

	echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);

}

// close connection

mysqli_close($link);

?>


