<?php
$titulo="Historico Auxiliar";
include ("cabecera.inc");

require('conexion.php');


if(( $_POST["fecha1"] ) && ($_POST["fecha2"] )) {
   $fecha1 = $_POST["fecha1"];
   $fecha2 = $_POST["fecha2"];
   if ( $_POST["nseg_punto"] ) {
	   $nseg_punto=$_POST["nseg_punto"];   
   } else {
	   $nseg_punto=300;
   }   
 }else{			
   	 $fecha1= date("Y") . "-" . date("m") . "-" . date("d");
     $fecha2= date("Y") . "-" . date("m") . "-" . date("d");
	 $nseg_punto=300;
 }


//Capturar datos de graficos ...maximo 10
$rawdata=[];
$tablas = []; // Nombre de las tablas
$ngraficos = 0;
$ncampos = []; // Nombres de los campos de cada tabla
$n = 0;
$tgrafico=[];  // tipo de grafico ..... tiempo o dia

if($result = mysqli_query($link, 'SHOW TABLES LIKE "TABLA_%"')){
    while($tabla = mysqli_fetch_array($result)){
        
		$tablas[$n] = $tabla[0]; // nombre de la tabla
        //echo $tablas[$n]. " -- ";
		
		// Calculo numero de campos en tabla
		$sql = "DESCRIBE $tabla[0]";
		$resultado = mysqli_query($link,$sql);

		if ($resultado->num_rows > 0) {
			// Mostrar los nombres de los campos
			$ncampo = 0;
			while($row = $resultado->fetch_assoc()) {
				//var_dump($row) . "<br>";
				$campos[$n][$ncampo] = $row["Field"];
				$ncampo++;
				//echo $row["Field"] . "<br>";
			}
		} else {
			echo "La tabla no tiene campos.";
		}
		
        if  (substr($tabla[0], 6, 3) == 'DIA'){ 
		    $tgrafico[$n] = 3;
			$sql = "SELECT  *, UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo1
                  FROM ".$tabla[0]." WHERE Tiempo >= (NOW()- INTERVAL 31 DAY)";
		}else{
			$tgrafico[$n] = 2;
			$sql = "SELECT  *, UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo1
                   FROM ".$tabla[0]." WHERE Tiempo BETWEEN '" . $fecha1 ." 00:00:00' and '".$fecha2 . " 23:59:59'
				   GROUP BY UNIX_TIMESTAMP(Tiempo) DIV ($nseg_punto)
				   ";
		}
        
        if($result1 = mysqli_query($link, $sql)){
              
           $j=0;
           
           while($row = mysqli_fetch_assoc($result1)) {
              $rawdata[$n][$j] = $row;
              $j++;
           }
           
         }else{
           echo "ERROR $sql. " . mysqli_error($link);
         }
         
         
         if ($j > 0) {
            $n++;
            $ngraficos++;
            //echo "Nuevo grafico valido... numero=$n<br />";
        
         }else{
            //echo "tabla sin datos<br />";
         }
           
         
    }

    //var_dump($campos) . "<br>";
	
}
/*
echo "---------------<br />";
echo "RESUMEN<br />";
echo "N Graficos=$ngraficos<br />";
for($n = 0 ;$n<$ngraficos ;$n++){
  echo "filas $tablas[$n]: ". count($rawdata[$n]). "  campos:". count($campos[$n])."<br />";
}
*/

mysqli_close($link);

?>

<script src="Parametros_Web.js"></script>

<!-- Importo el archivo Javascript de Highcharts directamente desde la RPi 
<script src="js/jquery.js"></script>
<script src="js/stock/highstock.js"></script>
<script src="js/highcharts-more.js"></script>

<script src="js/themes/grid.js"></script>
-->


<!-- Importo el archivo Javascript directamente desde la webr -->
<!---->

<script src="https://code.jquery.com/jquery.js"></script>
<script src="https://code.highcharts.com/stock/highstock.js"></script>
<script src="https://code.highcharts.com/highcharts-more.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>

<form action = "<?php $_PHP_SELF ?>" method = "POST">
    Periodo Desde: <input type="date" name="fecha1" value=<?php echo $fecha1 ?> />
    A: <input type="date" name="fecha2" value=<?php echo $fecha2 ?> />
    
    Muestra cada:<input type="number" size="5" name="nseg_punto" min="1" max="36000" step="1" value= <?php echo $nseg_punto ?> > seg__
    
    <input type = "submit" value = "Ver" />
		
</form>

<p></p>

<?php 
  // Se crean tantos div como graficos existan
  for($n = 0 ;$n<$ngraficos ;$n++)
    {
     //echo '<h3 style="color: #5e9ca0;" align="center">TABLA <span style="color: #2b2301;">'.$tablas[$n]."</span> Registros=".count($rawdata[$n])."</h3>";
     echo "<div id='container_".$n."' style='width: 100%; height: 80vh; margin-botton: 5px; float: left'></div>";
     echo "<p>&nbsp;</p>";
     //echo "<div id='sep_".$n."' style='width: 100%; height: 10px; float: left'></div>"; // separador
     
    }
    
?>


<script>
$(function () 
  {

  //recorrerDiccionario(Grafica_Aux);  
  
  Highcharts.setOptions({
    global: {
      useUTC: false
      },

    time: {
        timezone: zona_horaria
    },

    lang: {
      months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
      weekdays: ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'],
      shortMonths: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
      rangeSelectorFrom: "Desde",
      rangeSelectorTo: "A",
      printChart: "Imprimir gráfico",
      loading: "Cargando..."
      },
	  colors: ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9', '#f15c80', '#e4d354', '#2b908f', '#f45b5b', '#91e8e1','#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9', '#f15c80', '#e4d354', '#2b908f', '#f45b5b', '#91e8e1'],
    });

  <?php
  
  for($n = 0 ;$n<$ngraficos ;$n++)
    {   $T = (0 == $n) ? '' : $n;
      echo "var subtitulo = (Grafica_Aux['".$tablas[$n]."'] && Grafica_Aux['".$tablas[$n]."']['Subtitulo']) ? Grafica_Aux['".$tablas[$n]."']['Subtitulo'] : '';";
	  
	  echo "var ejes = (Grafica_Aux['".$tablas[$n]."'] && Grafica_Aux['".$tablas[$n]."']['Ejes']) ? Grafica_Aux['".$tablas[$n]."']['Ejes'] : '';
	  //console.log('ejes:....',ejes);
	  ";
				
	
     
	 //echo "var char = new Highcharts.StockChart ({
      echo "var chartOptions = {";

    	echo "chart: {
		    	renderTo: 'container_".$n."',
			    zoomType: 'xy',
			    alignTicks: false,
			    panning: true,
			    panKey: 'shift'
			  },
		      title: { text: 'TABLA : ".$tablas[$n]."... Nº Registros:".count($rawdata[$n])."' },
              subtitle: {text: subtitulo},
              credits: {enabled: false},
			  
			 ";
		
		echo "yAxis: ejes,
		     ";
		
	    echo "xAxis: {
                //dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'},
			 ";
		
		echo "legend: {enabled: true},
              rangeSelector: {
				buttons: [{
				  type: 'hour',
				  count: 1,
				  text: '1h'
				 }, {
				  type: 'hour',
				  count: 8,
				  text: '8h'
				 }, {
				  type: 'hour',
				  count: 24,
				  text: '24h'
				 }, {
				  type: 'all',
				  text: 'Todo'
				 }],
				selected: ".$tgrafico[$n]."
    		  },
			  tooltip: {
				valueSuffix: '',
				split: true,
				distance: 30,
				padding: 2,
				outside: true,
				crosshairs: true,
				//shared: true,
				valueDecimals: 2
				},
              navigator: {enabled: true},
			 ";
		
		echo "series:[";
				 
              
				//  #### series de cada tabla####

				for($j = 1 ;$j<count($campos[$n]) ;$j++)
				{
					$Cx = $campos[$n][$j];

					echo "\n" . "{name: '".$Cx."',";

             		echo "\n" . "type: function() {
							    var salida_e = 'spline';
								try {
								   var salida = Grafica_Aux['".$tablas[$n]."']['Series']['".$Cx."']['tipo'];
								} catch (error) {
									var salida = salida_e;
								} finally {
									salida = (typeof salida !== 'undefined') ? salida : salida_e;
									//console.log('" .$Cx. " tipo:--->>',salida);
								}
							return salida;}(),";

					
					echo "\n" . "visible: function() {
							    var salida_e = true;
								try {
								   var salida = Grafica_Aux['".$tablas[$n]."']['Series']['".$Cx."']['visible'];
								} catch (error) {
									var salida = salida_e;
								} finally {
									salida = (typeof salida !== 'undefined') ? salida : salida_e;
									//console.log('" .$Cx. " visible:--->>',salida);
								}
							return salida;}(),";

             		echo "\n" . "yAxis: function() {
							    var salida_e = 0;
								try {
								   var salida = Grafica_Aux['".$tablas[$n]."']['Series']['".$Cx."']['eje'];
								} catch (error) {
									var salida = salida_e;
								} finally {
									salida = (typeof salida !== 'undefined') ? salida : salida_e;
									//console.log('" .$Cx. " yAxis:--->>',salida);
								}
							return salida;}(),";
					
					echo "\n" . "color: function() {
							    var salida_e = Highcharts.getOptions().colors[".$j."];
								try {
								   var salida = Grafica_Aux['".$tablas[$n]."']['Series']['".$Cx."']['color'];
								} catch (error) {
								   salida : salida_e
								} finally {
									salida = (typeof salida !== 'undefined') ? salida : salida_e;
									//console.log('" .$Cx. " color:--->>',salida);
									
								}
							return salida;}(),";
					
					echo "\n" . "tooltip: function() {
							    var salida_e = {};
								try {
								   var salida = Grafica_Aux['".$tablas[$n]."']['Series']['".$Cx."']['tooltip'];
								} catch (error) {
									var salida = salida_e;
								} finally {
									salida = (typeof salida !== 'undefined') ? salida : salida_e;
									//console.log('" .$Cx. " tipo:--->>',salida);
								}
							return salida;}(),";

					
					//echo "tooltip: {valueSuffix: ' V',valueDecimals: 3,},";
					
					echo "data: (function() {var data = [];";
					for($i = 0 ;$i<count($rawdata[$n]);$i++)
						{
						  echo "data.push([";
						  echo $rawdata[$n][$i]["Tiempo1"];
						  echo ",";
						  echo $rawdata[$n][$i][$Cx];
						  echo"]);";
						}
					echo "return data;";
					echo "})()";
					echo "},";
				}

				echo"]";
    
    echo "};";

    echo "\n" . "var chart = new Highcharts.StockChart(chartOptions);". "\n";
 
}
 
echo "}); </script>"; 


include ("pie.inc");
?>
