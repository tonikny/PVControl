<?php

require('conexion.php');

$id_rele = mysqli_real_escape_string($link, $_POST['id_rele']);
$modo = mysqli_real_escape_string($link, $_POST['modo']);
$prio = mysqli_real_escape_string($link, $_POST['prioridad']);
$nueva_prio = mysqli_real_escape_string($link, $_POST['nueva_prio']);

if ($modo=="ON" or $modo=="OFF" or $modo=="PRG") {
	$sql = "UPDATE reles SET modo='$modo' WHERE id_rele=$id_rele";

} elseif ($modo=="M_ON") {
	$sql = "UPDATE reles SET modo='MAN', estado=100 WHERE id_rele=$id_rele";
	
} elseif ($modo=="M_OFF") {
	$sql = "UPDATE reles SET modo='MAN', estado=0 WHERE id_rele=$id_rele";

} elseif ($nueva_prio=="+1" or ($nueva_prio=="-1" and $prio>0)) {	
	$sql = "UPDATE reles SET prioridad=$prio$nueva_prio WHERE id_rele=$id_rele";
	//print ($sql);
	
} else {
	header("Location: reles.php");
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


