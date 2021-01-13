<?php

require('conexion.php');

$id_rele = mysqli_real_escape_string($link, $_POST['id_rele']);

$parametro_h = mysqli_real_escape_string($link, $_POST['parametro_h']);

$valor_h_ON = mysqli_real_escape_string($link, $_POST['valor_h_ON']);

$valor_h_OFF = mysqli_real_escape_string($link, $_POST['valor_h_OFF']);

// attempt insert query execution

$sql = "INSERT INTO reles_h (id_rele, parametro_h, valor_h_ON, valor_h_OFF) VALUES ('$id_rele', '$parametro_h', '$valor_h_ON', '$valor_h_OFF')";

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


