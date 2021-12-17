<?php
$titulo="Reles";
include ("cabecera.inc");
?>
<!-- Latest compiled and minified JavaScript -->
<script src="https://code.jquery.com/jquery.js"></script>

<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/highcharts-3d.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>
<script src="https://code.highcharts.com/modules/solid-gauge.js"></script>


<!-- TimePicker -->
<link rel="stylesheet" media="all" type="text/css" href="http://code.jquery.com/ui/1.11.0/themes/smoothness/jquery-ui.css"/> 
<link rel="stylesheet" media="all" type="text/css" 
              href="https://cdnjs.cloudflare.com/ajax/libs/jquery-ui-timepicker-addon/1.6.3/jquery-ui-timepicker-addon.min.css" />
<script type="text/javascript" src="http://code.jquery.com/ui/1.11.0/jquery-ui.min.js"></script> 
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery-ui-timepicker-addon/1.6.3/jquery-ui-timepicker-addon.min.js"> </script> 
<script type="text/javascript"> 
    $(function () { 
	$(".dateTimePicker").timepicker({ 
	    timeFormat: "H:mm", 
	    addSliderAccess: true, 
	    sliderAccessArgs: { touchonly: true },
	    currentText: "Ahora",
	    closeText: "Ok",
	    timeOnlyTitle: "Elige hora",
	    hourText: "Hora",
	    minuteText: "Minuto",
	    showTime: false,
	}); 
    }); 
</script> 

<?php
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
		<input type="hidden" name="origen" value="reles.php" >
		<input type="submit" value="Salir modo edición"/>
	</form>
<?php
}
?>

<div id="container_reles" style="width: 80%; height: 160px; margin-left: 1%;"></div>
<script>
$(function () {
	recibirDatosFV(); 
    
	Highcharts.setOptions({

	global: {
	   useUTC: false
	   },
	lang: {
	    months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
	    weekdays: ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'],
	    shortMonths: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
	    rangeSelectorFrom: "Desde",
	    rangeSelectorTo: "A",
	    printChart: "Imprimir gráfico",
	    loading: "Cargando..."
	    } 
	});

	chart_reles =new Highcharts.Chart({
	chart: {
	    renderTo: 'container_reles',
	    backgroundColor: null,//'#ffffff',//'#f2f2f2',
	    borderColor: null,
	    type: 'column',
	    shadow: false,
	    options3d: {
		enabled: true,
		alpha: 0,
		beta: 10,
		depth: 100,
		viewDistance: 25,
	    //backgroundColor: null,//'#ffffff',//'#f2f2f2',
	    //borderColor: null,
	   
	    },
	},

	plotOptions: {
	  column: {
	    dataLabels: {
		enabled: true,
		inside: true, //valor de la columna en el interior
		crop: false,
		overflow: 'none',
		//borderWidth: null,
		//borderColor: 'red',
	    },
	    enableMouseTracking: false
	  }
	},

	credits: {
	     enabled: false
	     },
	title: {
	      y:20,
	      text: 'SITUACION RELES'
	     },
	subtitle: {
	      text: null
	     },
	xAxis: {
	     categories: [] //Nombre_Reles()
	       },
	yAxis: {
	      gridLineWidth: 0,
	      minorGridLineWidth: 0,
	      gridLineColor: 'transparent',
	      min: 0,
	      max: 100,
	      //minPadding:0,
	      //maxPadding:0,
	      tickInterval: 10,
	      allowDecimals: false,
	      visible: true, //desactivar grid i resta
	      labels: {
		    enabled: true
	       },
	      title: {
		    enabled: false
	       }
	     },

	series: [{
		name: 'Estado Relés',
		colorByPoint: false,//Color aleatorio para cada columna de un rele
		color : '#2b5dc7',
		borderColor: '#303030',
		data: [],
		
		dataLabels: {
		    enabled: true, 
		    formatter: function() {
			return Highcharts.numberFormat(this.y,0) + " %"
		    }
		}
		}],

	navigation: {
	      buttonOptions: {
		enabled: false
	       }
	     },
	legend: {
	      enabled: false,
	      layout: 'vertical',
	      floating: true,
	      align: 'center',
	      verticalAlign: 'center',
	      //x: -100,
	      y: 30,
	      borderWidth: 0
	     },
	tooltip: {
	      formatter: function () {
		return '<b>' + this.series.name + '</b><br/>' +
		    this.point.y + ' ' + this.point.name.toLowerCase();
	       }
	     }

	});

	function recibirDatosFV() {
	$.ajax({
	url: 'datos_fv.php',
	success: function(data) {
	  try {             
	    // tiempo_sg, "%d-%B-%Y -- %H:%M:%S"
	    fecha = data['FV']['tiempo'];
            
	    chart_reles.setTitle({
              text: 'SITUACION RELES  - '+ fecha
                });
            
	    // Actualizacion Reles     
	    var t_Datos_Reles = [];
            
            for (var i in data['RELES']) {
                n= data['RELES'][i]['nombre']+'</br>'+data['RELES'][i]['modo']+'-P'+ data['RELES'][i]['prioridad']+'-'+
                  data['RELES'][i]['potencia']+'w-'+data['RELES'][i]['retardo']+'sg';
                t_Datos_Reles.push([n,data['RELES'][i]['estado']]);
            }
            t_Datos_Reles.pop(); // quito el ultimo elemento dado que es la fecha
            
            chart_reles.series[0].setData(t_Datos_Reles);
            
            var tCategories = []; // se cambian los nombres en funcion de los datos recibidos
            for (i = 0; i < chart_reles.series[0].data.length; i++) {
                tCategories.push(chart_reles.series[0].data[i].name); 
            }
            chart_reles.xAxis[0].setCategories(tCategories);
            
	  }
	   
	  catch (e) {
	    var d = new Date();
	    s = d.getSeconds()
	    t = d.getHours() + ':' + d.getMinutes() + ':' + s;
		
	    grafica_t_real.setTitle({
		text: 'SIN RESPUESTA - Hora=' + t,
		 });      
	    }       
	  },
	  
	// código a ejecutar sin importar si la petición falló o no
	complete : function(xhr, status) {
	    setTimeout(recibirDatosFV, 3000);
	   },
	  
	cache: false
	});
	}

	function round(value, precision) {
		var multiplier = Math.pow(10, precision || 0);
		return Math.round(value * multiplier) / multiplier;
	}
});
</script>
<style>
.block {
  display: block;
  width: 100%;
  padding-top: 100%;
  border: none;
  background-color: #4CAF50;
  color: white;
  padding: 1px 1px;
  font-size: 14px;
  font-family: monospace;
  cursor: pointer;
  text-align: right;
}

.block:hover {
  background-color: #ddd;
  color: black;
}
</style>

<?php
// --------------------- TABLA RELES -----------------------------------------------
echo '<strong>RELES</strong>';

require('conexion.php');

$sql = "SELECT id_rele,nombre,modo,grabacion,salto,potencia,retardo,prioridad
		FROM reles
		ORDER BY id_rele ASC";

if($result = mysqli_query($link, $sql)){

	$rawdata=array();
	$i=0;

	while ($row = mysqli_fetch_array($result)){
		$rawdata[$i]=$row;

		$rele[$i]=$row;  //Pasar contenido a rele[$i]

		$i++;
	}

	echo '<table width="80%" border="1" style="text-align:center;">';
	$columnas = (isset($rawdata[0])) ? count($rawdata[0])/2 : 0;
	$filas = count($rawdata);

	//Añadimos los titulos
	echo "<tr>";
	for($i=0;$i<$columnas;$i++){
		next($rawdata[0]);
		echo "<th><b>".key($rawdata[0])."</b></th>";
		next($rawdata[0]);
	}
	echo "</tr>";

	for($i=0;$i<$filas;$i++){

		echo "<tr>";
		for($j=0;$j<$columnas-1;$j++){
			echo "<td>".$rawdata[$i][$j]."</td>";
		}
	?>
	<td><span style="display: inline-block;"><?=$rele[$i][$columnas-1]; ?></span>
		<?php if (isset($_SESSION['logged'])){ ?>
		<span style="display: inline-block;float: right;padding-right: 1em;"><form action="c_rele.php" method="post">
			<input type="hidden" name="id_rele" value="<?php echo $rele[$i][0]; ?>" >
			<input type="hidden" name="prioridad" value="<?php echo $rele[$i][$columnas-1]; ?>" >
			<span style="display: inline-block;"><button type="submit" name="nueva_prio" value="+1" class="block">+</button></span>
			<span style="display: inline-block;"><button type="submit" name="nueva_prio" value="-1" class="block">-</button></span>
		</form>
		<?php }?>
	</span></td>
		<?php if (isset($_SESSION['logged'])){ ?>						
	<td><form action="c_rele.php" method="post">
        	<input type="hidden" name="id_rele" value="<?php echo $rele[$i][0]; ?>" >
		<button type="submit" name="modo" value="PRG" style="border: 0; background: transparent">
			<img src="img/pulazult.png" width="30" alt="submit" />
		</button>
        	<button type="submit" name="modo" value="ON" style="border: 0; background: transparent">
			<img src="img/pulverdet.png" width="30" alt="submit" />
		</button>
        	<button type="submit" name="modo" value="OFF" style="border: 0; background: transparent">
			<img src="img/pulrojot.png" width="30" alt="submit" />
		</button>
	</form></td>
	
	<td width="10px"><form action="d_rele.php" method="post">
        	<input type="hidden" name="id_rele" value="<?php echo $rele[$i][0]; ?>" >

		<button type="submit" style="border: 0; background: transparent" title="Eliminar Relé" onclick="return confirm('Estás seguro de eliminar relé de todas las tablas?')">
			<img src="img/delete.png" width="30" alt="submit" />
		</button>
	</form></td>
<?php	
		}
		echo "</tr>\n";
	}
	echo "</table>\n\n";

} else{
        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

if (isset($_SESSION['logged'])){
?>
Añadir relé
<div style="border:1px solid; width:80%">
<form action="add_rele.php" method="post">
    <table style="border-spacing:5px;">
	<tr>
	<th><label for="id_rele">id_rele</label></th>
	<th><label for="nombre">Nombre</label></th>
	<th><label for="modo">Modo</label></th>
	<th><label for="grabacion" title="Relés normales = 0, Relés PWM = 1,2,...">Grabación</label></th>
	<th><label for="salto" title="Relés normales = 100, Relés PWM = % de salto">Salto</label></th>
	<th><label for="prioridad">Prioridad</label></th>
	<th></th>
	</tr><tr>
        <td><input type="text" name="id_rele" id="id_rele" size="15"></td>
        <td><input type="text" name="nombre" id="nombre"></td>
        <td><select name="modo">
                <option value="PRG" selected="selected">PRG</option>
                <option value="ON">ON</option>
                <option value="OFF">OFF</option>
	</select></td>
        <td><select name="grabacion">
                <option value="N" selected="selected">No</option>
                <option value="S">Sí</option>
        </select></td>
        <td><input type="text" name="salto" id="salto" size="15" title="Relés normales = 100, Relés PWM = % de salto"></td>
        <td><input type="text" name="prioridad" id="prioridad" size="15" title="Relés normales = 0, Relés PWM = 1,2,..."></td>
	<td><input type="submit" value="Añadir"></td>
	</tr>
    </table>
</form>
</div>
<br />


<?php
}

echo '<br>';
echo '<strong>CONDICIONES FOTOVOLTAICAS</strong>';
// --------------------- TABLA CONDICIONES FV -----------------------------------------

$sql = "SELECT reles.id_rele,reles.nombre,reles.modo,reles_c.parametro,reles_c.operacion,reles_c.condicion,reles_c.valor,reles_c.id_reles_c
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
	$columnas = (isset($rawdata[0])) ? count($rawdata[0])/2 : 0;
	$filas = count($rawdata);

	//Añadimos los titulos
	echo "<tr>";
	for($i=0;$i<$columnas-1;$i++){
		next($rawdata[0]);
		echo "<th><b>".key($rawdata[0])."</b></th>";
		next($rawdata[0]);
	}
	echo "</tr>";
	for($i=0;$i<$filas;$i++){

		echo "<tr>";
		for($j=0;$j<$columnas-1;$j++){
			echo "<td>".htmlentities($rawdata[$i][$j])."</td>";
		}
		if (isset($_SESSION['logged'])){
?>			
	<td width="10px"><form action="d_relec.php" method="post">
        	<input type="hidden" name="id_reles_c" value="<?php echo $rawdata[$i]["id_reles_c"]; ?>" >

		<button type="submit" style="border: 0; background: transparent" title="Eliminar Condición (<?php echo $rawdata[$i]["id_reles_c"]; ?>)" onclick="return confirm('Estás seguro de eliminar la condición?')">
			<img src="img/delete.png" width="30" alt="submit" />
		</button>
	</form></td>
<?php	
		}
		echo "</tr>\n";
	}

	echo "</table>\n\n";

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}
if (isset($_SESSION['logged'])){
?>
Añadir condiciones FV para relé
<div style="border:1px solid; width:80%;">
<form action="add_relec.php" method="post">
    <table style="border-spacing:5px;">
	<tr>
	<th><label for="id_rele">id_rele</label></th>
        <th><label for="parametro">Parámetro</label></th>
	<th><label for="operacion">Operación</label></th>
        <th><label for="condicion">Condición</label></th>
        <th><label for="valor">Valor</label></th>
	<th></th>
	</tr><tr>
        <td><select name="id_rele">
                <option value="" selected="selected"> </option>
<?php
	foreach ($rele as $r) {
		print("<option value=".$r["0"].">".$r["id_rele"]."</option>");
	}
?>
	</select></td>
        <td><select name="parametro">
                <option value="SOC" selected="selected">SOC</option>
                <option value="Vbat">Vbat</option>
                <option value="Ibat">Ibat</option>
                <option value="Iplaca">Iplaca</option>
                <option value="Vplaca">Vplaca</option>
                <option value="Wplaca">Wplaca</option>
                <option value="PWM">PWM</option>
                <option value="Temp">Temp</option>
                <option value="Wconsumo">Wconsumo</option>
                <option value="Whn_bat">Whn_bat</option>
                <option value="Whp_bat">Whp_bat</option>
                <option value="Wh_bat">Wh_bat</option>
                <option value="Wbat">Wbat</option>
                <option value="Vred">Vred</option>
                <option value="Ired">Ired</option>
                <option value="EFF">EFF</option>
                <option value="Whn_red">Whn_red</option>
                <option value="Whp_red">Whp_red</option>
                <option value="Wh_red">Wh_red</option>
                <option value="Wred">Wred</option>
                <option value="Aux1">Aux1</option>
                <option value="Aux2">Aux2</option>
        </select></td>
        <td><select name="operacion">
                <option value="ON" selected="selected">ON</option>
                <option value="OFF">OFF</option>
	</select></td>
        <td><select name="condicion">
                <option value=">" selected="selected">&gt;</option>
                <option value="<">&lt;</option>
        </select></td>
        <td><input type="text" name="valor" id="valor"></td>
	<td><input type="submit" value="Añadir"></td>
	</tr>
    </table>
</form>
</div>
<br />

<?php
}

echo '<br>';
echo '<strong>CONDICIONES HORARIAS</strong>';
// --------------------- TABLA CONDICIONES HORARIO -----------------------------------------


$sql = "SELECT reles.id_rele,reles.nombre,reles.modo,reles_h.parametro_h,reles_h.valor_h_ON,reles_h.valor_h_OFF,reles_h.id_reles_h
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
	$columnas = (isset($rawdata[0])) ? count($rawdata[0])/2 : 0;
	$filas = count($rawdata);
	//Añadimos los titulos
	echo "<tr>";
	for($i=0;$i<$columnas-1;$i++){
		next($rawdata[0]);
		echo "<th><b>".key($rawdata[0])."</b></th>";
		next($rawdata[0]);
	}
	echo "</tr>";

	for($i=0;$i<$filas;$i++){
		echo "<tr>";
		for($j=0;$j<$columnas-1;$j++){
			echo "<td>".$rawdata[$i][$j]."</td>";
		}
		if (isset($_SESSION['logged'])){
?>			
	<td width="10px"><form action="d_releh.php" method="post">
        	<input type="hidden" name="id_reles_h" value="<?php echo $rawdata[$i]["id_reles_h"]; ?>" >

		<button type="submit" style="border: 0; background: transparent" title="Eliminar Condición <?php echo $rawdata[$i]["id_reles_h"]; ?>" onclick="return confirm('Estás seguro de eliminar la condición?')">
			<img src="img/delete.png" width="30" alt="submit" />
		</button>
	</form></td>
<?php	
		}
		echo "</tr>\n";
	}

	echo "</table>\n\n";

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

if (isset($_SESSION['logged'])){
?>

Añadir horario para relé
<div style="border:1px solid; width:80%">
<form action="add_releh.php" method="post">
    <table style="border-spacing:5px;">
	<tr>
	<th><label for="id_rele">id_rele</label></th>
        <th><label for="parametro_h">Parámetro_h</label></th>
        <th><label for="valor_h_ON">Valor_h_ON</label></th>
        <th><label for="valor_h_OFF">Valor_h_OFF</label></th>
	<th></th>
	</tr><tr>
        <td><select name="id_rele">
                <option value="" selected="selected"> </option>
<?php
	foreach ($rele as $r) {
		print("<option value=".$r["0"].">".$r["id_rele"]."</option>");
	}
?>
	</select></td>
        <td><select name="parametro_h">
                <option value="T" selected="T">Todos</option>
                <option value="L">Lunes</option>
                <option value="M">Martes</option>
                <option value="X">Miércoles</option>
                <option value="J">Jueves</option>
                <option value="V">Viernes</option>
                <option value="S">Sábado</option>
                <option value="D">Domingo</option>
        </select></td>
        <td><input type="text" name="valor_h_ON" id="valor_h_ON" class="dateTimePicker"></td>
        <td><input type="text" name="valor_h_OFF" id="valor_h_OFF" class="dateTimePicker"></td>
	<td><input type="submit" value="Añadir"></td>
	</tr>
    </table>
</form>
</div>


<?php
}

echo '<br><br>';
echo '<strong>CONDICIONES AVANZADAS</strong>';
// --------------------- TABLA CONDICIONES -----------------------------------------


$sql = "SELECT id_condicion,activado,condicion1,condicion2,accion,descripcion
		FROM condiciones
		ORDER BY id_condicion ASC";

if($result = mysqli_query($link, $sql)){

        $rawdata=array();
        $i=0;

        while ($row = mysqli_fetch_array($result)){
                $rawdata[$i]=$row;
                $i++;
        }

	echo "<br \>";

	echo '<table width="80%" border="1" style="text-align:center;">';
	$columnas = (isset($rawdata[0])) ? count($rawdata[0])/2 : 0;
	$filas = count($rawdata);

	//Añadimos los titulos
	echo "<tr>";
	for($i=0;$i<$columnas;$i++){
		next($rawdata[0]);
		echo "<th><b>".key($rawdata[0])."</b></th>";
		next($rawdata[0]);
	}
	echo "</tr>";

	for($i=0;$i<$filas;$i++){

		echo "<tr>";
		for($j=0;$j<$columnas;$j++){
			echo "<td>".htmlentities($rawdata[$i][$j])."</td>";
		}
		if (isset($_SESSION['logged'])){
?>			
	<td width="10px"><form action="c_condicion.php" method="post">
        	<input type="hidden" name="id_condicion" value="<?php echo $rawdata[$i]["id_condicion"]; ?>" >
        	<input type="hidden" name="activado" value="<?php echo $rawdata[$i]["activado"]; ?>" >
		<button type="submit" style="border: 0; background: transparent" title="<?php echo ($rawdata[$i]["activado"])?'Desactivar':'Activar'; ?> Condición">
			<img src="<?php echo ($rawdata[$i]["activado"])?'img/pause.png':'img/play.png'; ?>" width="30" alt="submit" />
		</button>
	</form></td>
<?php	
		}
		echo "</tr>\n";
	}

	echo "</table>\n\n";

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}



mysqli_close($link);

echo "<br \>";
?>


<?php
include ("pie.inc");
?>
