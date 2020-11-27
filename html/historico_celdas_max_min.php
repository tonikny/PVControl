<?php

require('conexion.php');

$sql = "SELECT UNIX_TIMESTAMP(CONCAT(YEAR(Tiempo),'-',MONTH(Tiempo),'-',DAY(Tiempo)))*1000 as Fecha,
        max(C0) as 'Max_C0',min(C0) as 'Min_C0',avg(C0) as 'Med_C0',
        max(C1) as 'Max_C1',min(C1) as 'Min_C1',avg(C1) as 'Med_C1',
        max(C2) as 'Max_C2',min(C2) as 'Min_C2',avg(C2) as 'Med_C2',
        max(C3) as 'Max_C3',min(C3) as 'Min_C3',avg(C3) as 'Med_C3',
        max(C4) as 'Max_C4',min(C4) as 'Min_C4',avg(C4) as 'Med_C4',
        max(C5) as 'Max_C5',min(C5) as 'Min_C5',avg(C5) as 'Med_C5',
        max(C6) as 'Max_C6',min(C6) as 'Min_C6',avg(C6) as 'Med_C6',
        max(C7) as 'Max_C7',min(C7) as 'Min_C7',avg(C7) as 'Med_C7',
        max(C8) as 'Max_C8',min(C8) as 'Min_C8',avg(C8) as 'Med_C8',
        max(C9) as 'Max_C9',min(C9) as 'Min_C9',avg(C9) as 'Med_C9',
        max(C10) as 'Max_C10',min(C10) as 'Min_C10',avg(C10) as 'Med_C10',
        max(C11) as 'Max_C11',min(C11) as 'Min_C11',avg(C11) as 'Med_C11',
        max(C12) as 'Max_C12',min(C12) as 'Min_C12',avg(C12) as 'Med_C12',
        max(C13) as 'Max_C13',min(C13) as 'Min_C13',avg(C13) as 'Med_C13',
        max(C14) as 'Max_C14',min(C14) as 'Min_C14',avg(C14) as 'Med_C14',
        max(C15) as 'Max_C15',min(C15) as 'Min_C15',avg(C15) as 'Med_C15'
        FROM datos_mux_1 WHERE Tiempo >= SUBDATE(NOW(), INTERVAL 15 DAY) 
        GROUP BY DAY(Tiempo)";

if($result = mysqli_query($link, $sql)){
    $i=0;
    while ($row = mysqli_fetch_array($result)){
        $rawdata2[$i]=$row;
        $i++;
        
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }

$sql = "SELECT  max(C0) as 'Max_C0',min(C0) as 'Min_C0',
        max(C1) as 'Max_C1',min(C1) as 'Min_C1',
        max(C2) as 'Max_C2',min(C2) as 'Min_C2',
        max(C3) as 'Max_C3',min(C3) as 'Min_C3',
        max(C4) as 'Max_C4',min(C4) as 'Min_C4',
        max(C5) as 'Max_C5',min(C5) as 'Min_C5',
        max(C6) as 'Max_C6',min(C6) as 'Min_C6',
        max(C7) as 'Max_C7',min(C7) as 'Min_C7',
        max(C8) as 'Max_C8',min(C8) as 'Min_C8',
        max(C9) as 'Max_C9',min(C9) as 'Min_C9',
        max(C10) as 'Max_C10',min(C10) as 'Min_C10',
        max(C11) as 'Max_C11',min(C11) as 'Min_C11',
        max(C12) as 'Max_C12',min(C12) as 'Min_C12',
        max(C13) as 'Max_C13',min(C13) as 'Min_C13',
        max(C14) as 'Max_C14',min(C14) as 'Min_C14',
        max(C15) as 'Max_C15',min(C15) as 'Min_C15'
        FROM datos_mux_1 WHERE Tiempo >= SUBDATE(NOW(), INTERVAL 15 DAY)";

if($result = mysqli_query($link, $sql)){
    $i=0;
    while ($row = mysqli_fetch_array($result)){
        $rawdata3[$i]=$row;
        $i++;
        
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }
mysqli_close($link);


?>


<HTML>

<body>

<meta charset="utf-8">

<script src="Parametros_Web.js"></script>



<!-- Importo el archivo Javascript directamente desde la webr -->


<script src="https://code.jquery.com/jquery.js"></script>
<script src="http://code.highcharts.com/stock/highstock.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>

<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>
<script src="https://code.highcharts.com/modules/export-data.js"></script>
<script src="https://code.highcharts.com/modules/accessibility.js"></script>


<div id="container_C" style="width: 100%; height: 480px; margin-left: 0px; float: left"></div>

<div id="container_C0" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C1" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C2" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C3" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C4" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C5" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C6" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C7" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C8" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C9" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C10" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C11" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C12" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C13" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C14" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>
<div id="container_C15" style="width: 25%; height: 240px; margin-left: 0px; float: left"></div>


<br>

</body>

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
  
  var Vceldas = new Highcharts.chart({

    chart: {
        renderTo: 'container_C',
        type: 'columnrange',
        //backgroundColor: null,
        borderColor: null,
        shadow: false,
        inverted: false
    },

    accessibility: {
        description: 'Voltaje de cad celda de la bateria'
    },

    title: {
        text: 'Variacion Max-Min Vceldas (15 dias)'
    },

    subtitle: {
        text: 'PVControl+'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        categories: ['C1', 'C2', 'C3', 'C4', 'C5','C6', 'C7', 'C8', 'C9', 'C10','C11','C12', 'C13', 'C14','C15','C16']
    },

    yAxis: {
        title: {
            text: 'Voltaje Celda'
        },
        plotBands: [{
          from: Vcelda_franja_min,
          to: Vcelda_franja_max,
          color: 'rgba(68, 170, 213, 0.2)',
          label: {
              text: ''
          }
         }]
    },

    tooltip: {
        valueSuffix: ' V'
    },

    plotOptions: {
        columnrange: {
            dataLabels: {
                enabled: true,
                format: '{y} V'
            }
        }
    },

    legend: {
        enabled: false
    },

    series: [{
        name: 'Vceldas',
        data: [
            [<?php echo $rawdata3[0]["Min_C0"];?>,<?php echo $rawdata3[0]["Max_C0"];?>],
            [<?php echo $rawdata3[0]["Min_C1"];?>,<?php echo $rawdata3[0]["Max_C1"];?>],
            [<?php echo $rawdata3[0]["Min_C2"];?>,<?php echo $rawdata3[0]["Max_C2"];?>],
            [<?php echo $rawdata3[0]["Min_C3"];?>,<?php echo $rawdata3[0]["Max_C3"];?>],
            [<?php echo $rawdata3[0]["Min_C4"];?>,<?php echo $rawdata3[0]["Max_C4"];?>],
            [<?php echo $rawdata3[0]["Min_C5"];?>,<?php echo $rawdata3[0]["Max_C5"];?>],
            [<?php echo $rawdata3[0]["Min_C6"];?>,<?php echo $rawdata3[0]["Max_C6"];?>],
            [<?php echo $rawdata3[0]["Min_C7"];?>,<?php echo $rawdata3[0]["Max_C7"];?>],
            [<?php echo $rawdata3[0]["Min_C8"];?>,<?php echo $rawdata3[0]["Max_C8"];?>],
            [<?php echo $rawdata3[0]["Min_C9"];?>,<?php echo $rawdata3[0]["Max_C9"];?>],
            [<?php echo $rawdata3[0]["Min_C10"];?>,<?php echo $rawdata3[0]["Max_C10"];?>],
            [<?php echo $rawdata3[0]["Min_C11"];?>,<?php echo $rawdata3[0]["Max_C11"];?>],
            [<?php echo $rawdata3[0]["Min_C12"];?>,<?php echo $rawdata3[0]["Max_C12"];?>],
            [<?php echo $rawdata3[0]["Min_C13"];?>,<?php echo $rawdata3[0]["Max_C13"];?>],
            [<?php echo $rawdata3[0]["Min_C14"];?>,<?php echo $rawdata3[0]["Max_C14"];?>],
            [<?php echo $rawdata3[0]["Min_C15"];?>,<?php echo $rawdata3[0]["Max_C15"];?>]
        ]
    }]

});
  
  
  var Vcelda0 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C0',
        backgroundColor: null,
        borderColor: null,
        shadow: false,
        zoomType: 'xy'
    },

    title: {
        text: 'C1 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C0"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C0"];?>,<?php echo $rawdata2[$i]["Min_C0"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda1 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C1',
        backgroundColor: null,
        borderColor: null,
        shadow: false,
        zoomType: 'xy'
    },

    title: {
        text: 'C2 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C1"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C1"];?>,<?php echo $rawdata2[$i]["Min_C1"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda2 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C2',
        backgroundColor: null,
        borderColor: null,
        shadow: false,
        zoomType: 'xy'
    },

    title: {
        text: 'C3 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C2"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C2"];?>,<?php echo $rawdata2[$i]["Min_C2"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda3 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C3',
        backgroundColor: null,
        borderColor: null,
        shadow: false,
        zoomType: 'xy'
    },

    title: {
        text: 'C4 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C3"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C3"];?>,<?php echo $rawdata2[$i]["Min_C3"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda4 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C4',
        zoomType: 'xy'
    },

    title: {
        text: 'C5 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C4"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C4"];?>,<?php echo $rawdata2[$i]["Min_C4"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda5 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C5',
        zoomType: 'xy'
    },

    title: {
        text: 'C6 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C5"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C5"];?>,<?php echo $rawdata2[$i]["Min_C5"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda6 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C6',
        zoomType: 'xy'
    },

    title: {
        text: 'C7 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C6"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C6"];?>,<?php echo $rawdata2[$i]["Min_C6"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda7 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C7',
        zoomType: 'xy'
    },

    title: {
        text: 'C8 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C7"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C7"];?>,<?php echo $rawdata2[$i]["Min_C7"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda8 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C8',
        zoomType: 'xy'
    },

    title: {
        text: 'C9 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C8"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C8"];?>,<?php echo $rawdata2[$i]["Min_C8"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda9 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C9',
        zoomType: 'xy'
    },

    title: {
        text: 'C10 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C9"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C9"];?>,<?php echo $rawdata2[$i]["Min_C9"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda10 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C10',
        zoomType: 'xy'
    },

    title: {
        text: 'C11 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C10"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C10"];?>,<?php echo $rawdata2[$i]["Min_C10"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  var Vcelda11 = new Highcharts.Chart ({
    chart: {
        renderTo: 'container_C11',
        zoomType: 'xy'
    },

    title: {
        text: 'C12 - Med, Máx y Mín'
    },
    subtitle: {
        //text: 'Permite Zoom XY'
    },
    credits: {
        enabled: false
    },
    xAxis: {
        dateTimeLabelFormats: { day: '%e %b' },
        type: 'datetime'
    },
    yAxis: {
        min: Vcelda_min,
        max: Vcelda_max,
        title: {
            text: null
        }
    },
    tooltip: {
        crosshairs: true,
        shared: true,
        valueSuffix: 'V'
    },
    legend: {
        enabled: false
    },
    series: [
      {name: 'AVG',
      zIndex: 1,
      color: Highcharts.getOptions().colors[0],
      marker: {
          fillColor: 'white',
          lineWidth: 2,
          lineColor: Highcharts.getOptions().colors[0]
      },
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Med_C11"];?>]);
         <?php } ?>
      return data;
           })()
      },
      {name: 'Máx-Mín',
      type: 'arearange',
      lineWidth: 0,
      linkedTo: ':previous',
      color: Highcharts.getOptions().colors[0],
      fillOpacity: 0.3,
      zIndex: 0,
      tooltip: {
          valueSuffix: ' V',
          valueDecimals: 2,
      },
      data: (function() {
         var data = [];
         <?php
             for($i = 0 ;$i<count($rawdata2);$i++){
         ?>
         data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Max_C11"];?>,<?php echo $rawdata2[$i]["Min_C11"];?>]);
         <?php } ?>
      return data;
           })()
      }
    ]


  });

  });
</script>
</html>
