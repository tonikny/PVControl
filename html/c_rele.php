<?php

require('conexion.php');

$id_rele = mysqli_real_escape_string($link, $_POST['id_rele']);

$modo = mysqli_real_escape_string($link, $_POST['modo']);


// attempt insert query execution

$sql = "UPDATE reles SET modo='$modo' WHERE id_rele=$id_rele";

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


