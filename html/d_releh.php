<?php

require('conexion.php');

$id_reles_h = mysqli_real_escape_string($link, $_POST['id_reles_h']);


// attempt insert query execution


$sql = "DELETE FROM reles_h WHERE id_reles_h=$id_reles_h";

if(mysqli_query($link, $sql)){
        sleep(2);
	header("Location: reles.php");
} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);

}

// close connection

mysqli_close($link);

?>


