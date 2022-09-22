<?php
$titulo="Historico Personalizado";
include ("cabecera.inc");

require('conexion.php');

// Calculo numero de campos en tabla datos_aux
//$sql = "SELECT * FROM datos_aux LIMIT 1";
//$resultado = mysqli_query($link,$sql);
//$ncampos = mysqli_num_fields($resultado)-2;

if(( $_POST["fecha1"] ) && ($_POST["fecha2"] )) {
   $fecha1 = $_POST["fecha1"];
   $fecha2 = $_POST["fecha2"];
      
 }else{			
   	 $fecha1= date("Y") . "-" . date("m") . "-" . date("d");
     $fecha2= date("Y") . "-" . date("m") . "-" . date("d");
	 
 }


$sql = "SELECT  *, UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo1 FROM datos_aux 
        WHERE Tiempo BETWEEN '" . $fecha1 ." 00:00:00' and '".$fecha2 . " 23:59:59'";
        
if($result = mysqli_query($link, $sql)){
  $i=0;
  while($row = mysqli_fetch_assoc($result)) {
    //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
    $rawdata1[$i] = $row;
    $datos[$i] = explode(",", $rawdata1[$i]["datos"]); 
    
    $i++;
  }
} else{
     echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

$ncampos= count($datos[$i-1]);
//print_r($datos);
//echo $ncampos;

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
<script src="http://code.highcharts.com/stock/highstock.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>


<form action = "<?php $_PHP_SELF ?>" method = "POST">
    Periodo Desde: <input type="date" name="fecha1" value=<?php echo $fecha1 ?> />
    A: <input type="date" name="fecha2" value=<?php echo $fecha2 ?> />
    <!--
    Muestra cada:<input type="number" size="5" name="nseg_punto" min="5" max="3600" step="5" value= <?php echo $nseg_punto ?> > seg__
    -->
    <input type = "submit" value = "Ver" />
		
</form>

<p></p>


<div id="container1" style="width: 100%; height: 80vh; margin-left: 5; float: left"></div>

<br>


<script>
$(function () 
  {
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

  chart_grafica_auxiliar = new Highcharts.StockChart ({
  
    chart: {
      renderTo: 'container1',
      zoomType: 'xy',
      fillOpacity: 0.2,
      backgroundColor: null,
      alignTicks: false,
      panning: true,
      panKey: 'shift'
      },
    title: {
      text: G_titulo //'Grafica Auxilar'
      },
    subtitle: {
      text: G_subtitulo //'Permite Zoom XY'
      },
    credits: {
      enabled: false
      },
    yAxis: [
     {// ########## Valores Eje1 ######################
      visible: Eje1_visible,
      opposite: Eje1_opposite,
      min: Eje1_min,
      max: Eje1_max,
      tickInterval: Eje1_tickInterval,
      minorGridLineColor: 'transparent',
      labels: {
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: Eje1_titulo,
        rotation: 0,
        y: -10
        },
     },
     
     {// ########## Valores Eje2 ######################
      visible: Eje2_visible,
      opposite: Eje2_opposite,
      min: Eje2_min,
      max: Eje2_max,
      tickInterval: Eje2_tickInterval,
      minorGridLineColor: 'transparent',
      labels: {
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: Eje2_titulo,
        rotation: 0,
        y: -10
        },
     },
     
     ],
     
     
    xAxis: {
      dateTimeLabelFormats: { day: '%e %b' },
      type: 'datetime'
      },
    legend: {
      enabled: true
      },
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
      selected: 2
      },
    tooltip: {
      valueSuffix: 'C1',
      split: true,
      distance: 30,
      padding: 2,
      outside: true,
      crosshairs: true,
      //shared: true,
      valueDecimals: 2
      },
    navigator: {
      enabled: true // false
      },
      
    series: [
    
       <?php 
       for($j = 1 ;$j<$ncampos+1 ;$j++)
       {
        echo "\n";
        echo "{name: G".$j."_nombre,";
        echo "type: G".$j."_tipo_grafico,";
        echo "yAxis: G".$j."_yAxis-1,";
        echo "visible: G".$j."_visible,";
        echo "color: G".$j."_color,";
        
        echo "tooltip: {valueSuffix: G".$j."_unidades, valueDecimals: G".$j."_decimales},";
        
        echo "data: (function() {var data = [];";
        for($i = 0 ;$i<count($rawdata1);$i++)
         {
          echo "data.push([";
          echo $rawdata1[$i]["Tiempo1"];
          echo ",";
          echo $datos[$i][$j-1];
          echo"]);";
         }
        echo "return data;";
        echo "})()";
        echo "},";
       }
     ?> 
    
     ]
     
    });
  });
</script>

<?php
include ("pie.inc");
?>
