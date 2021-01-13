<?php

require('conexion.php');

$id_rele = mysqli_real_escape_string($link, $_POST['id_rele']);


// attempt insert query execution


$sql = "DELETE FROM reles_h WHERE id_rele=$id_rele";

if(mysqli_query($link, $sql)){
        sleep(2);
	header("Location: reles.php");
} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);

}

// close connection

mysqli_close($link);

?>


