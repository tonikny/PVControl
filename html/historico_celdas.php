<?php
$titulo="Historico Celdas";
include ("cabecera.inc");

require('conexion.php');

// Calculo numero de celdas en tabla
$sql = "SELECT * FROM datos_celdas LIMIT 1";
$resultado = mysqli_query($link,$sql);
$nceldas = mysqli_num_fields($resultado)-2;

if(( $_POST["fecha1"] ) && ($_POST["fecha2"] )) {
   $fecha1 = $_POST["fecha1"];
   $fecha2 = $_POST["fecha2"];
   //if ( $_POST["nseg_punto"] ) {
   //   $nseg_punto=$_POST["nseg_punto"];   
   //} else {
   //	   $nseg_punto=5;
   //}   
 }else{			
   	 $fecha1= date("Y") . "-" . date("m") . "-" . date("d");
     $fecha2= date("Y") . "-" . date("m") . "-" . date("d");
	 //$nseg_punto=5;
 }

//Coger datos grafica 

//$sql = "SELECT  * FROM datos_celdas 
//        WHERE DATE(Tiempo) >= '" . $fecha1 . "' and DATE(Tiempo) <= '" . $fecha2 . "'
//        GROUP BY DATE(Tiempo),FLOOR(TIME_TO_SEC(TIME(Tiempo))/" . $nseg_punto . " ) ORDER BY Tiempo";

$sql = "SELECT  *, UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo1 FROM datos_celdas 
        WHERE Tiempo BETWEEN '" . $fecha1 ." 00:00:00' and '".$fecha2 . " 23:59:59'";
        
if($result = mysqli_query($link, $sql)){
  $i=0;
  while($row = mysqli_fetch_assoc($result)) {
    //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
    $rawdata[$i] = $row;
    $i++;
  }
} else{
     echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

//Adaptar el tiempo grafica 
//for($i=0;$i<count($rawdata);$i++){
//   $time = $rawdata[$i]["Tiempo"];
//   $date = new DateTime($time);
//   $rawdata[$i]["Tiempo"]=$date->getTimestamp()*1000;
// }


//Coger datos grafica Ibat

//$sql = "SELECT  UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, Ibat FROM datos 
//        WHERE DATE(Tiempo) >= '" . $fecha1 . "' and DATE(Tiempo) <= '" . $fecha2 . "'
//        GROUP BY DATE(Tiempo),FLOOR(TIME_TO_SEC(TIME(Tiempo))/" . $nseg_punto . " ) ORDER BY Tiempo";

$sql = "SELECT  UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, Ibat FROM datos 
        WHERE Tiempo BETWEEN  '" . $fecha1 ." 00:00:00' and '".$fecha2 . " 23:59:59'";
       
if($result = mysqli_query($link, $sql)){
  $i=0;
  while($row = mysqli_fetch_assoc($result)) {
    //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
    $rawdata1[$i] = $row;
    $i++;
  }
} else{
     echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


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

  chart_vceldas = new Highcharts.StockChart ({
  
    chart: {
      renderTo: 'container1',
      zoomType: 'xy',
      alignTicks: false,
      panning: true,
      panKey: 'shift'
      },
    title: {
      text: 'Voltaje Celdas / Ibat'
      },
    subtitle: {
      //text: 'Permite Zoom XY'
      },
    credits: {
      enabled: false
      },
    yAxis: [
     {// ########## Valores eje Vceldas ######################
      opposite: false,
      min: Vcelda_min,
      max: Vcelda_max,
      tickInterval: 0.1,
      //gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Vcelda',//null
        rotation: 0,
        y: -10
        },
      plotBands: [{
        from: Vcelda_franja_min,
        to: Vcelda_franja_max,
        color: 'rgba(68, 170, 213, 0.2)',
        label: {
            text: ''
          }
        }],
      
     },
     {// ########## Valores eje Intensidad ######################
      opposite: true,
      min: Escala_intensidad_min,
      max: Escala_intensidad_max,
      tickInterval: 20,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Ibat',//null
        rotation: 0,
        y: -5
        },
      plotLines: [{
        value: 0,
        width: 2,
        color: 'black',
        dashStyle: 'shortdash'
        }]
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
      {name: 'Ibat',
      type: 'spline',
      yAxis: 1,
      color: Highcharts.getOptions().colors[2],
      tooltip: {
        valueSuffix: ' A',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata1);$i++){
            ?>
            data.push([<?php echo $rawdata1[$i]["Tiempo"];?>,<?php echo $rawdata1[$i]["Ibat"];?>]);
            <?php } ?>
          return data;
        })()
      },
     
      <?php 
       for($j = 1 ;$j<$nceldas+1 ;$j++)
       {
        $Cx = "C".$j;
        echo "{name: '".$Cx."'";
        echo ",type: 'spline', color: Highcharts.getOptions().colors[".$j."],";
        echo "tooltip: {valueSuffix: ' V',valueDecimals: 2,},";
        echo "data: (function() {var data = [];";
        for($i = 0 ;$i<count($rawdata);$i++)
         {
          echo "data.push([";
          echo $rawdata[$i]["Tiempo1"];
          echo ",";
          echo $rawdata[$i][$Cx];
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
