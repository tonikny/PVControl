<?php
$titulo="Historico 3 Dias";
include ("cabecera.inc");


require('conexion.php');

//Coger datos grafica historico general
$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, Wplaca,Wred, Wplaca-Wred as Consumo, PWM
        FROM datos_c WHERE Tiempo >= (NOW()- INTERVAL 3 DAY)
        ORDER BY Tiempo";

if($result = mysqli_query($link, $sql)){
  $i=0;
  while($row = mysqli_fetch_assoc($result)) {
        //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
        $rawdata[$i] = $row;
        $i++;
    }
  }
else{
  echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
  }

mysqli_close($link);

?>

<script src="Parametros_Web.js"></script>

<script src="https://code.jquery.com/jquery.js"></script>
<script src="http://code.highcharts.com/stock/highstock.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>


<div id="container12" style="width: 100%; height: 80vh; margin-left: 5; float: left"></div>

<br>


<script>
$(function () {

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

  var char = new Highcharts.StockChart ({
    chart: {
      renderTo: 'container12',
      zoomType: 'xy',
      alignTicks: false,
      panning: true,
      panKey: 'shift'
      },
    title: {
      text: ' GRÁFICA POTENCIA SOLAR -  POTENCIA RED  - CONSUMO '
      },
    subtitle: {
      //text: 'Permite Zoom XY'
      },
    credits: {
      enabled: false
      },
    yAxis: [{
      opposite: false,
      
	  // ########## Valores POTENCIA ######################
      min: Escala_Wred_min,
      max: Escala_Wred_max,
      tickInterval: 500,
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        format:  '{value} W',
        y: 5
        },
      title: {
        text: null
        },
      plotLines: []
     }, {
      opposite: true,
      
	  // ########## Valores eje PWM ######################
      min: 0,
      max: Escala_PWM_max ,
      tickInterval: 50,
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        format:  '{value}',
        y: 5
        },
      title: {
        text: null
        },
	  	  
	  /*
      plotLines: [{
        value: 100,
        width: 2,
        color: 'green',
        dashStyle: 'shortdash',
        label: {
          text: 'Rele1'
          }
       },{
        value: 200,
        width: 2,
        color: 'red',
        dashStyle: 'shortdash',
        label: {
          text: 'Rele2'
          }	
       }]
	  */
	   
     }],
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
        count: 6,
        text: '6h'
       }, {
        type: 'hour',
        count: 12,
        text: '12h'
       }, {
        type: 'day',
        count: 1,
        text: '1día'
       }, {
        type: 'all',
        text: 'Todo'
       }],
      selected: 1
      },
    tooltip: {
      crosshairs: true,
      shared: true,
      valueDecimals: 2
      },
    navigator: {
      enabled: true // false
      },
    series: [
      {//Wplaca
      name: 'Wplaca',
      type: 'spline',
      yAxis: 0,
      
      color: Highcharts.getOptions().colors[0],
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Wplaca"];?>]);
            <?php } ?>
          return data;
        })()
      },
      {//Wred
      name: 'Wred',
      type: 'spline',
      yAxis: 0,
      color: Highcharts.getOptions().colors[2],
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Wred"];?>]);
            <?php } ?>
          return data;
        })()
      },
      {//Wconsumo
      name: 'Consumo',
      type: 'spline',
      yAxis: 0,
      color: Highcharts.getOptions().colors[3],
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Consumo"];?>]);
            <?php } ?>
          return data;
        })()
      },
      {//PWM
      name: 'PWM',
      type: 'spline',
      yAxis: 1,
      color: Highcharts.getOptions().colors[4],
      tooltip: {
        valueSuffix: ' %',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["PWM"];?>]);
            <?php } ?>
          return data;
        })()
      }
     ]

    });

  });
</script>

<?php
include ("pie.inc");
?>
