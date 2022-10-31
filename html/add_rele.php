<?php


require('conexion.php');

$nuevo = mysqli_real_escape_string($link, $_POST['nuevo']);
$id_rele = mysqli_real_escape_string($link, $_POST['id_rele']);
$nombre = mysqli_real_escape_string($link, $_POST['nombre']);
$modo = mysqli_real_escape_string($link, $_POST['modo']);
$grabacion = mysqli_real_escape_string($link, $_POST['grabacion']);
$salto = mysqli_real_escape_string($link, $_POST['salto']);
$pot = mysqli_real_escape_string($link, $_POST['potencia']);
$ret = mysqli_real_escape_string($link, $_POST['retardo']);
$prioridad = mysqli_real_escape_string($link, $_POST['prioridad']);

if ($nuevo=="true") {
	$sql = "INSERT INTO reles (id_rele, salto, potencia, retardo, prioridad, nombre, modo, grabacion) VALUES ('$id_rele','$salto','$pot','$ret','$prioridad','$nombre', '$modo', '$grabacion')";
} else {
	$sql = "UPDATE reles SET salto='$salto', potencia='$pot', retardo='$ret', prioridad='$prioridad', nombre='$nombre', modo='$modo', grabacion='$grabacion' WHERE id_rele='$id_rele'";
}

if(mysqli_query($link, $sql)){
  sleep(2);
	header("Location: reles.php");
} else{
	echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

// close connection
mysqli_close($link);

?>


