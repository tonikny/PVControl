<?php

require('conexion.php');

//Coger datos grafica historico general
$sql = "SELECT Tiempo,   Wplaca,Vbat*Ibat as Excedentes, Wplaca-Vbat*Ibat as Consumo
        FROM datos WHERE Tiempo >= (NOW()- INTERVAL 25 HOUR)
        ORDER BY Tiempo";

//$sql = "SELECT Tiempo, SOC as SOCavg, Ibat as Ibatavg, Iplaca as Iplacaavg, Vbat as Vbatavg, Vflot*10 as Vflotavg, Vplaca as Vplacaavg
//        FROM datos WHERE DATE(Tiempo) >= SUBDATE(NOW(), INTERVAL 3 DAY)
//        ORDER BY Tiempo";
//$sql = "SELECT Tiempo, AVG(SOC) as SOCavg, AVG(Ibat) as Ibatavg, AVG(Iplaca) as Iplacaavg, AVG(Vbat) as Vbatavg, AVG(Vflot)*10 as Vflotavg
//        FROM datos WHERE DATE(Tiempo) >= SUBDATE(NOW(), INTERVAL 7 DAY)
//        GROUP BY DAY(Tiempo),((60/1)*HOUR(TIME(Tiempo))+FLOOR(MINUTE(TIME(Tiempo))/1)) ORDER BY Tiempo";

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
for($i=0;$i<count($rawdata);$i++){
    $time = $rawdata[$i]["Tiempo"];
    $date = new DateTime($time);
    $rawdata[$i]["Tiempo"]=$date->getTimestamp()*1000;
}

?>


<HTML>

<body>

<meta charset="utf-8">


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

</body>

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
      text: ' GRÁFICA POTENCIA SOLAR -  EXCEDENTES  - CONSUMO '
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
	  min: 0,
      max: 6000,
	  tickInterval: 250,
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
      max: 6000 ,
      tickInterval: 250,
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        format:  '{value} W',
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
    series: [{
      name: 'Energia Solar',
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
     }, {
      name: 'Excedentes',
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
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Excedentes"];?>]);
            <?php } ?>
          return data;
        })()
     }, {
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
     
        
     }]

    });

  });
</script>
</html>
