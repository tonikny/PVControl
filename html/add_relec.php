<?php

require('conexion.php');

$id_rele = mysqli_real_escape_string($link, $_POST['id_rele']);

$parametro = mysqli_real_escape_string($link, $_POST['parametro']);

$operacion = mysqli_real_escape_string($link, $_POST['operacion']);

$condicion = mysqli_real_escape_string($link, $_POST['condicion']);

$valor = mysqli_real_escape_string($link, $_POST['valor']);

// attempt insert query execution

$sql = "INSERT INTO reles_c (id_rele, parametro, operacion, condicion, valor) VALUES ('$id_rele', '$parametro', '$operacion', '$condicion', '$valor')";

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


