<?php
$titulo="Historico Horas";
include ("cabecera.inc");

require('conexion.php');

if(( isset($_POST["fecha1"]) ) && (isset($_POST["fecha2"]) )) {
    $fecha1 = $_POST["fecha1"];
    $fecha2 = $_POST["fecha2"];

 }else{
    $fecha1= date("Y") . "-" . date("m") . "-" . date("d");
    $fecha2= date("Y") . "-" . date("m") . "-" . date("d");

 }


//Coger datos grafica
$sql = "SELECT  UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, SOC, Ibat, Iplaca, Vbat, Aux1, Vplaca,Wplaca,PWM,IPWM_P,IPWM_I,IPWM_D
        FROM datos_s WHERE DATE(Tiempo) >= '" . $fecha1 . "' and DATE(Tiempo) <= '" . $fecha2 . "'
        ORDER BY id lIMIT 80000";


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

mysqli_close($link);

//Adaptar el tiempo grafica historico general
//for($i=0;$i<count($rawdata);$i++){
//    $time = $rawdata[$i]["Tiempo"];
    //echo $rawdata[$i]["Tiempo"]." / ";
//    $date = new DateTime($time);
//    $rawdata[$i]["Tiempo"]=$date->getTimestamp()*1000;
    //$rawdata[$i]["Tiempo"]=$date->microtime(true)*1000;
    //echo $rawdata[$i]["Tiempo"]." --- ";
//}

?>


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
    <input type = "submit" value = "Ver" />

</form>



<!--
<div id="container12" style="width: auto; height: 600px; margin-left: 5;margin-right:5"></div>
-->
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
      text: 'SOC, Iplaca -Ibat - Vbat - Vplaca - Wplaca - PWM - IPWM_P/I/D'
      },
    subtitle: {
      //text: 'Permite Zoom XY'
      },
    credits: {
      enabled: false
      },
    yAxis: [
     {// ########## Valores eje Intensidad ######################
      opposite: false,     
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
        text: 'Ibat',
        rotation: 0,
        y: -10
        },
      plotLines: [{
        value: 0,
        width: 2,
        color: 'black',
        dashStyle: 'shortdash'
        }]
     },
     {// ########## Valores eje Vbat ######################
      opposite: false,
      min: Escala_Vbat_min,
      max: Escala_Vbat_max,
      tickInterval: 1,
      //gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Vbat',
        rotation: 0,
        y: -10
        },
      plotLines: [{

        // ########## Valores Linea Vabs #####################
        value: Vabs,
        width: 2,
        color: 'green',
        dashStyle: 'shortdash',
        label: {
          text: 'Vabs'
          }
       },{
        
       // ########## Valores Linea Vflot ######################
        value: Vflot,
        width: 2,
        color: 'red',
        dashStyle: 'shortdash',
        label: {
          text: 'Vflot'
          }
       }]
     },
     {// ########## Valores eje SOC ######################
      opposite: true,
      min: 20,
      max: 100 ,
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
        text: 'SOC',
        rotation: 0,
        y: -5
        },
      plotLines: [{
        value: 100,
        width: 2,
        color: 'green',
        dashStyle: 'shortdash',
        label: {
          text: '100%'
          }
       },{
        value: 80,
        width: 2,
        color: 'red',
        dashStyle: 'shortdash',
        label: {
          text: '80%'
          }
       }]
     },
     {// ########## Valores eje PWM ######################
      opposite: true,
      min: -50,
      max: Escala_PWM_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'PWM ',
        rotation: 0,
        y: -15
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

     },
     {// ########## Valores eje WPlaca ######################
      opposite: true,
      min: 0,
      max: Watios_placa_max ,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: -10,
        text: 'Wplaca',
        rotation: 0,
        y: -5
        },
      
     }
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
        count: 2,
        text: '2h'
       }, {
        type: 'hour',
        count: 4,
        text: '4hour'
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
     {name: 'SOC',
      visible: false,
      type: 'spline',
      yAxis: 2,
      color: Highcharts.getOptions().colors[1],
      tooltip: {
        valueSuffix: ' %',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          if(!isset($rawdata)) {$rawdata=[];}
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
              data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["SOC"];?>]);
              <?php } ?>
            return data;
        })()
     },
     {name: 'Vbat',
      type: 'spline',
      yAxis: 1,
      color: Highcharts.getOptions().colors[0],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vbat"];?>]);
            <?php } ?>
          return data;
        })()
     },
     {name: 'Ibat',
      type: 'spline',
      color: Highcharts.getOptions().colors[2],
      tooltip: {
        valueSuffix: ' A',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Ibat"];?>]);
            <?php } ?>
          return data;
        })()
     },
     {name: 'Iplaca',
      type: 'spline',
      color: Highcharts.getOptions().colors[3],
      tooltip: {
        valueSuffix: ' A',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Iplaca"];?>]);
            <?php } ?>
          return data;
        })()
     },
     {name: 'Vplaca',
      visible: false,
      type: 'spline',
      yAxis: 0, // poner 2 para escala del SOC
      color: Highcharts.getOptions().colors[20],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vplaca"];?>]);
          <?php } ?>
        return data;
        })()
     },
     {name: 'Aux1',
      visible: false,
      type: 'spline',
      yAxis: 0,
      color: Highcharts.getOptions().colors[4],
      tooltip: {
        valueSuffix: ' ',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Aux1"];?>]);
          <?php } ?>
        return data;
        })()
      },
     {name: 'PWM',
      visible: true,
      type: 'spline',
      yAxis: 3,
      color: Highcharts.getOptions().colors[5],
      tooltip: {
        valueSuffix: ' ',
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
      },
     {name: 'Wplaca',
      visible: true,
      type: 'spline',
      yAxis: 4,
      color: 'black', //Highcharts.getOptions().colors[7],
      tooltip: {
        valueSuffix: ' ',
        valueDecimals: 0,
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
     {name: 'IPWM_P',
      visible: true,
      type: 'spline',
      yAxis: 3,
      color: Highcharts.getOptions().colors[6],
      tooltip: {
        valueSuffix: ' ',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["IPWM_P"];?>]);
          <?php } ?>
        return data;
        })()  
      },
     {name: 'IPWM_I',
      visible: true,
      type: 'spline',
      yAxis: 3,
      color: Highcharts.getOptions().colors[7],
      tooltip: {
        valueSuffix: ' ',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["IPWM_I"];?>]);
          <?php } ?>
        return data;
        })()  
      },
     {name: 'IPWM_D',
      visible: true,
      type: 'spline',
      yAxis: 3,
      color: Highcharts.getOptions().colors[8],
      tooltip: {
        valueSuffix: ' ',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["IPWM_D"];?>]);
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
