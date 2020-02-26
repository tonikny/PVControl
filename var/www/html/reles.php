<html>
<body>

<?php

echo 'RELÉS';
// --------------------- TABLA RELES -----------------------------------------------

require('conexion.php');

$sql = "SELECT reles.id_rele,reles.nombre,reles.modo,reles.estado,reles.grabacion,reles.salto,reles.prioridad
		FROM reles
		ORDER BY reles.id_rele ASC";

if($result = mysqli_query($link, $sql)){

	$rawdata=array();
	$i=0;

	while ($row = mysqli_fetch_array($result)){
		$rawdata[$i]=$row;

		$rele[$i]=$row;  //Pasar contenido a rele[$i]

		$i++;
	}

	echo '<table width="56%" border="1" style="text-align:center;">';
	$columnas = count($rawdata[0])/2;
	$filas = count($rawdata);


	$numreles = count($rawdata);    //Contar numero de reles para filas de LEDS

	//Añadimos los titulos

	for($i=1;$i<count($rawdata[0]);$i=$i+2){
		next($rawdata[0]);
		echo "<th><b>".key($rawdata[0])."</b></th>";
		next($rawdata[0]);
	}

	for($i=0;$i<$filas;$i++){

		echo "<tr>";
		for($j=0;$j<$columnas;$j++){
			echo "<td>".$rawdata[$i][$j]."</td>";
		}
		echo "</tr>";
	}

	echo '</table>';

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

echo '<br>';
echo 'CONDICIONES FOTOVOLTAICAS';
// --------------------- TABLA CONDICIONES FV -----------------------------------------


$sql = "SELECT reles.id_rele,reles.nombre,reles.modo,reles_c.parametro,reles_c.operacion,reles_c.condicion,reles_c.valor
		FROM reles INNER JOIN reles_c ON reles.id_rele = reles_c.id_rele
		ORDER BY reles.id_rele,reles_c.parametro,reles_c.operacion DESC";

if($result = mysqli_query($link, $sql)){

        $rawdata=array();
        $i=0;

        while ($row = mysqli_fetch_array($result)){
                $rawdata[$i]=$row;
                $i++;
        }

	echo "<br \>";

	echo '<table width="80%" border="1" style="text-align:center;">';
	$columnas = count($rawdata[0])/2;
	$filas = count($rawdata);

	//Añadimos los titulos

	for($i=1;$i<count($rawdata[0]);$i=$i+2){
		next($rawdata[0]);
		echo "<th><b>".key($rawdata[0])."</b></th>";
		next($rawdata[0]);
	}

	for($i=0;$i<$filas;$i++){

		echo "<tr>";
		for($j=0;$j<$columnas;$j++){
			echo "<td>".$rawdata[$i][$j]."</td>";
		}
		echo "</tr>";
	}

	echo '</table>';

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

echo '<br>';
echo 'CONDICIONES HORARIAS';
// --------------------- TABLA CONDICIONES HORARIO -----------------------------------------


$sql = "SELECT reles.id_rele,reles.nombre,reles.modo,reles_h.parametro_h,reles_h.valor_h_ON,reles_h.valor_h_OFF
		FROM reles INNER JOIN reles_h ON reles.id_rele = reles_h.id_rele
		ORDER BY reles.id_rele,reles_h.parametro_h DESC";

if($result = mysqli_query($link, $sql)){

        $rawdata=array();
        $i=0;

        while ($row = mysqli_fetch_array($result)){
                $rawdata[$i]=$row;
                $i++;
        }


	echo "<br \>";

	echo '<table width="80%" border="1" style="text-align:center;">';
	$columnas = count($rawdata[0])/2;
	$filas = count($rawdata);

	//Añadimos los titulos

	for($i=1;$i<count($rawdata[0]);$i=$i+2){
		next($rawdata[0]);
		echo "<th><b>".key($rawdata[0])."</b></th>";
		next($rawdata[0]);
	}

	for($i=0;$i<$filas;$i++){

		echo "<tr>";
		for($j=0;$j<$columnas;$j++){
			echo "<td>".$rawdata[$i][$j]."</td>";
		}
		echo "</tr>";
	}

	echo '</table>';

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

mysqli_close($link);

echo "<br \>";

?>


<?php
$password = "3c77f4029be2e609c22bba665f13b101";
if (md5($_POST['password']) != $password) {
?>
<!--- <h3>Login</h3> ---->
<form name="form" method="post" action="">
<input type="password" name="password">
<input type="submit" value="Entrar"></form>
<?php
}else{
?>



<?php
for($i=0;$i<$numreles;$i=$i+1) {
?>
	<p></p>
	Cambiar estado relé <?php echo $rele[$i][1]; ?>

	<form action="c_rele.php" method="post">
        	<input type="hidden" name="id_rele" value="<?php echo $rele[$i][0]; ?>" >

		<button type="submit" name="modo" value="PRG" style="border: 0; background: transparent">
			<img src="img/pulazult.png" width="40" alt="submit" />
		</button>
        	<button type="submit" name="modo" value="ON" style="border: 0; background: transparent">
			<img src="img/pulverdet.png" width="40" alt="submit" />
		</button>
        	<button type="submit" name="modo" value="OFF" style="border: 0; background: transparent">
			<img src="img/pulrojot.png" width="40" alt="submit" />
		</button>

	</form>

<?php
}
?>


<p></p>

Actualizar SOC (%):

<form action="c_soc.php" method="post">
	<label for="SOC">SOC %:</label>
	<input type="text" name="SOC" id="SOC">
    <input type="submit" value="Actualizar">
</form>


<p></p>
Cambiar modo relé:

<form action="c_rele.php" method="post">
        <label for="id_rele">id_rele:</label>
        <input type="text" name="id_rele" id="id_rele">
        <label for="modo">modo:</label>
	<select name="modo">
		<option value="PRG" selected="selected">PRG</option>
		<option value="ON">ON</option>
		<option value="OFF">OFF</option>
	</select>
    <input type="submit" value="Cambiar">
</form>

<p></p>
Añadir relé (Salto = Relés normales = 100, Relés PWM = % de salto. Ej.: 5,10,20,25,50)(Prioridad: sólo para relés PWM):

<form action="add_rele.php" method="post">
        <label for="id_rele">id_rele:</label>
        <input type="text" name="id_rele" id="id_rele">
        <label for="nombre">nombre:</label>
        <input type="text" name="nombre" id="nombre">
        <label for="modo">modo:</label>
        <select name="modo">
                <option value="PRG" selected="selected">PRG</option>
                <option value="ON">ON</option>
                <option value="OFF">OFF</option>
	</select>
        <label for="grabacion">Grabación:</label>
        <select name="grabacion">
                <option value="N" selected="selected">No</option>
                <option value="S">Sí</option>
        </select>
        <label for="salto">Salto:</label>
        <input type="text" name="salto" id="salto">
        <label for="prioridad">Prioridad:</label>
        <input type="text" name="prioridad" id="prioridad">
    <input type="submit" value="Añadir">
</form>

<p></p>
Añadir condiciones FV para relé (siempre añadir relé primero):

<form action="add_relec.php" method="post">
        <label for="id_rele">id_rele:</label>
        <input type="text" name="id_rele" id="id_rele">
        <label for="parametro">parámetro:</label>
        <select name="parametro">
                <option value="SOC" selected="selected">SOC</option>
                <option value="Vbat">Vbat</option>
                <option value="Ibat">Ibat</option>
                <option value="Iplaca">Iplaca</option>
                <option value="Vflot">Vflot</option>
                <option value="Temp">Temp</option>
                <option value="Diver">Diver</option>
        </select>
	<label for="operacion">operación:</label>
        <select name="operacion">
                <option value="ON" selected="selected">ON</option>
                <option value="OFF">OFF</option>
	</select>
        <label for="condicion">condición:</label>
        <select name="condicion">
                <option value=">" selected="selected">></option>
                <option value="<"><</option>
        </select>
        <label for="valor">valor:</label>
        <input type="text" name="valor" id="valor">
    <input type="submit" value="Añadir">
</form>

<p></p>
Añadir horario para relé (siempre añadir relé primero):

<form action="add_releh.php" method="post">
        <label for="id_rele">id_rele:</label>
        <input type="text" name="id_rele" id="id_rele">
        <label for="parametro_h">parámetro_h:</label>
        <select name="parametro_h">
                <option value="T" selected="T">Todos</option>
                <option value="L">Lunes</option>
                <option value="M">Martes</option>
                <option value="X">Miércoles</option>
                <option value="J">Jueves</option>
                <option value="V">Viernes</option>
                <option value="S">Sábado</option>
                <option value="D">Domingo</option>
        </select>
        <label for="valor_h_ON">valor_h_ON:</label>
        <input type="text" name="valor_h_ON" id="valor_h_ON">
        <label for="valor_h_OFF">valor_h_OFF:</label>
        <input type="text" name="valor_h_OFF" id="valor_h_OFF">

    <input type="submit" value="Añadir">
</form>

<p></p>
Eliminar relé de todas las tablas

<form action="d_rele.php" method="post">
        <label for="id_rele">id_rele:</label>
        <input type="text" name="id_rele" id="id_rele">
    <input type="submit" value="Eliminar">
</form>

<p></p>
Eliminar relé tabla condiciones FV

<form action="d_relec.php" method="post">
        <label for="id_rele">id_rele:</label>
        <input type="text" name="id_rele" id="id_rele">
    <input type="submit" value="Eliminar">
</form>

<p></p>
Eliminar relé tabla horarios

<form action="d_releh.php" method="post">
        <label for="id_rele">id_rele:</label>
        <input type="text" name="id_rele" id="id_rele">
    <input type="submit" value="Eliminar">
</form>


<?php
}
?>



</body>
</html>
