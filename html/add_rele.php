<?php


require('conexion.php');

$id_rele = mysqli_real_escape_string($link, $_POST['id_rele']);

$nombre = mysqli_real_escape_string($link, $_POST['nombre']);

$modo = mysqli_real_escape_string($link, $_POST['modo']);

$grabacion = mysqli_real_escape_string($link, $_POST['grabacion']);

$salto = mysqli_real_escape_string($link, $_POST['salto']);

$prioridad = mysqli_real_escape_string($link, $_POST['prioridad']);


// attempt insert query execution

$sql = "INSERT INTO reles (id_rele, salto, prioridad, nombre, modo, grabacion) VALUES ('$id_rele','$salto','$prioridad','$nombre', '$modo', '$grabacion')";

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


