<?php
$titulo="Historico 3 Dias";
include ("cabecera.inc");

require('conexion.php');

//Coger datos grafica historico general
$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, SOC as SOCavg, Ibat as Ibatavg, Iplaca as Iplacaavg, Vbat as Vbatavg, Aux1 as Aux1avg, Vplaca as Vplacaavg, PWM as PWMavg
        FROM datos_c WHERE Tiempo >= (NOW()- INTERVAL 3 DAY)
        ORDER BY Tiempo";

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
      text: 'SOC, Iplaca/Ibat - Vbat/Vplaca - PWM/Aux1 --- 3 DIAS'
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
        text: 'Vbat',//null
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
        text: 'SOC',//null
        rotation: 0,
        y: -10
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
      min: 0,
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
        text: 'PWM',//null
        rotation: 0,
        y: -10
        },
                  
     },
      
     {// ########## Valores eje Vplaca ######################
      opposite: false,
      min: 0,
      max: Escala_Vplaca_max,
      tickInterval: 20,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      title: {
        align: 'high',
        offset: 0,
        text: 'Vplaca',//null
        rotation: 0,
        y: -5
        },
      },
      
     {// ########## Valores eje Aux1 ######################
      opposite: true,
      min: Escala_Aux1_min,
      max: Escala_Aux1_max,
      tickInterval: 5,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      title: {
        align: 'high',
        offset: 0,
        text: 'Aux1',//null
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
        count: 12,
        text: '12h'
       }, {
        type: 'day',
        count: 1,
        text: '1dia'
       }, {
        type: 'day',
        count: 2,
        text: '2día'
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
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Ibatavg"];?>]);
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
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Iplacaavg"];?>]);
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
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vbatavg"];?>]);
            <?php } ?>
          return data;
        })()
     },
     {name: 'SOC',
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
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
              data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["SOCavg"];?>]);
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
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["PWMavg"];?>]);
          <?php } ?>
        return data;
        })()  
        
     },
     {name: 'Vplaca',
      visible: false,
      type: 'spline',
      yAxis: 4, // poner 2 para escala del SOC
      color: 'black', //Highcharts.getOptions().colors[20],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 0,
        },
      data: (function() {
        var data = [];
        <?php
        for($i = 0 ;$i<count($rawdata);$i++){
          ?>
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vplacaavg"];?>]);
          <?php } ?>
        return data;
        })()
     }, 
     
     {name: 'Aux1',
      visible: true,
      type: 'spline',
      yAxis: 5,
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
          data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Aux1avg"];?>]);
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
