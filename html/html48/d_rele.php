<?php

require('conexion.php');

$id_rele = mysqli_real_escape_string($link, $_POST['id_rele']);


// attempt insert query execution

$sql = "DELETE FROM reles WHERE id_rele=$id_rele";

mysqli_query($link, $sql);

$sql1 = "DELETE FROM reles_c WHERE id_rele=$id_rele";

mysqli_query($link, $sql1);

$sql2 = "DELETE FROM reles_h WHERE id_rele=$id_rele";

mysqli_query($link, $sql2);

header("Location: index.php?pagina=boton5");

// close connection

mysqli_close($link);

?>


