<?php

//$link = mysqli_connect("localhost", "fv", "fv", "fv");


//if($link === false){
//	die("ERROR: Could not connect. " . mysqli_connect_error());
//}

require('conexion.php');

$id_rele = mysqli_real_escape_string($link, $_POST['id_rele']);

$nombre = mysqli_real_escape_string($link, $_POST['nombre']);

$modo = mysqli_real_escape_string($link, $_POST['modo']);

$grabacion = mysqli_real_escape_string($link, $_POST['grabacion']);


// attempt insert query execution

$sql = "INSERT INTO reles (id_rele, nombre, modo, grabacion) VALUES ('$id_rele', '$nombre', '$modo', '$grabacion')";

if(mysqli_query($link, $sql)){
        sleep(2);
	header("Location: index.php?pagina=boton5");
//	echo "Records added successfully.";

} else{

	echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);

}

// close connection

mysqli_close($link);

?>


