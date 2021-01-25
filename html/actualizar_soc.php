<?php
$titulo="SOC";
include ("cabecera.inc");


require('conexion.php');

$sql = "SELECT SOC
        FROM datos
        ORDER BY Tiempo DESC LIMIT 1";
if($result = mysqli_query($link, $sql)){
    if (! $data = mysqli_fetch_assoc($result)) {
        echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }
}
mysqli_close($link);

$password = "3c77f4029be2e609c22bba665f13b101";
if ((!isset($_POST['password']) or (md5($_POST['password'])) != $password) && !isset($_SESSION['logged'])) {
?>
	<!--- <h3>Login</h3> ---->
	<form name="form" method="post" action="">
	<input type="password" name="password">
	<input type="submit" value="Modo edición"></form>
<?php
}else{
    $_SESSION['logged'] = "yes";
?>
	<form action="logout.php" method="post">
		<input type="hidden" name="origen" value="actualizar_soc.php" >
		<input type="submit" value="Salir modo edición"/>
	</form>
<?php
}
?>

<br /><br />
<h2>
SOC (%): <?php echo $data["SOC"]; ?>
</h2>

<?php
if (isset($_SESSION['logged'])){
?>
<br />

<form action="c_soc.php" method="post">
	<label for="SOC">Nuevo SOC %:</label>
	<input type="text" name="SOC" id="SOC">
    <input type="submit" value="Actualizar">
</form>

<?php
}
?>

<?php
include ("pie.inc");
?>
