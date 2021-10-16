<?php
$titulo="Resumen Celdas";
include ("cabecera.inc");

require('conexion.php');

$sql = "SELECT * FROM datos_mux LIMIT 1";
$resultado = mysqli_query($link,$sql);

if (!$resultado) {
    echo 'No se pudo ejecutar la consulta: ' . mysqli_error($link);
    exit;
}
/* devuelve N campos */
$ncampos =mysqli_num_fields($resultado)-2;

$sql="SELECT UNIX_TIMESTAMP(CONCAT(YEAR(Tiempo),'-',MONTH(Tiempo),'-',DAY(Tiempo)))*1000 as Fecha,\n";
for ($i = 0; $i < $ncampos-1; $i++) {
    $sql = $sql."max(C".$i.") as 'Max_C".$i."',min(C".$i.") as 'Min_C".$i."',avg(C".$i.") as 'Med_C".$i."',\n";
}
$sql = $sql."max(C".$i.") as 'Max_C".$i."',min(C".$i.") as 'Min_C".$i."',avg(C".$i.") as 'Med_C".$i."'\n";
$sql = $sql."FROM datos_mux WHERE Tiempo >= SUBDATE(NOW(), INTERVAL 15 DAY) GROUP BY DAY(Tiempo)";

if($result = mysqli_query($link, $sql)){
    $i=0;
    while ($row = mysqli_fetch_array($result)){
        $rawdata2[$i]=$row;
        $i++;
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }

//Creacion SQL Max-Min de cada Celda..salida en una unica fila
$sql="SELECT ";
for ($i = 0; $i < $ncampos-1; $i++) {
    $sql = $sql."max(C".$i.") as 'Max_C".$i."',min(C".$i.") as 'Min_C".$i."',\n";
}
$sql = $sql."max(C".$i.") as 'Max_C".$i."',min(C".$i.") as 'Min_C".$i."'\n";
$sql = $sql."FROM datos_mux WHERE Tiempo >= SUBDATE(NOW(), INTERVAL 15 DAY)";

// Creo la variable $r con una lista de pareados [max,min] de cada celda
if($result = mysqli_query($link, $sql)){
    $row = mysqli_fetch_array($result,$resulttype = MYSQLI_NUM);
    $i=0;
    while ($i < $ncampos*2){
        $r = $r."[".$row[$i].",".$row[$i+1]."],";
        $i = $i+2;
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }

$cat="";// Nombres de las celdas para Eje X grafico
for ($i = 1; $i < $ncampos; $i++) {
    $cat = $cat."'C".$i."', ";
}
$cat = $cat."'C".$i."'";

//echo $cat;

mysqli_close($link);

?>


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
        categories: [<?php echo $cat;?>]
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
        data: [<?php echo $r;?>]
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

<?php
include ("pie.inc");
?>
