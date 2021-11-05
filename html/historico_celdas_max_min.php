<?php
$titulo="Resumen Celdas";
include ("cabecera.inc");

require('conexion.php');

$sql = "SELECT * FROM datos_celdas LIMIT 1";
$resultado = mysqli_query($link,$sql);

if (!$resultado) {
    echo 'No se pudo ejecutar la consulta: ' . mysqli_error($link);
    exit;
}
/* devuelve N campos */
$nceldas = mysqli_num_fields($resultado)-2;

$sql="SELECT UNIX_TIMESTAMP(CONCAT(YEAR(Tiempo),'-',MONTH(Tiempo),'-',DAY(Tiempo)))*1000 as Fecha,\n";
for ($i = 1; $i < $nceldas; $i++) {
    $sql = $sql."max(C".$i.") as 'Max_C".$i."',min(C".$i.") as 'Min_C".$i."',avg(C".$i.") as 'Med_C".$i."',\n";
}
$sql = $sql."max(C".$i.") as 'Max_C".$i."',min(C".$i.") as 'Min_C".$i."',avg(C".$i.") as 'Med_C".$i."'\n";
$sql = $sql."FROM datos_celdas WHERE Tiempo >= SUBDATE(NOW(), INTERVAL 15 DAY) GROUP BY DAY(Tiempo)";

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
for ($i = 1; $i < $nceldas; $i++) {
    $sql = $sql."max(C".$i.") as 'Max_C".$i."',min(C".$i.") as 'Min_C".$i."',\n";
}
$sql = $sql."max(C".$i.") as 'Max_C".$i."',min(C".$i.") as 'Min_C".$i."'\n";
$sql = $sql."FROM datos_celdas WHERE Tiempo >= SUBDATE(NOW(), INTERVAL 15 DAY)";

// Creo la variable $r con una lista de pareados [max,min] de cada celda
if($result = mysqli_query($link, $sql)){
    $row = mysqli_fetch_array($result,$resulttype = MYSQLI_NUM);
    $i=0;
    while ($i < $nceldas*2){
        $r = $r."[".$row[$i].",".$row[$i+1]."],";
        $i = $i+2;
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }

$cat="";// Nombres de las celdas para Eje X grafico
for ($i = 1; $i < $nceldas; $i++) {
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

<!--//<script src="https://code.highcharts.com/highcharts.js"></script>-->
<script src="https://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>
<script src="https://code.highcharts.com/modules/export-data.js"></script>
<script src="https://code.highcharts.com/modules/accessibility.js"></script>


<div id="container_C" style="width: 100%; height: 480px; margin-left: 0px; float: left"></div>
<?php 
  for($j = 1 ;$j<$nceldas+1 ;$j++)
    {
     $Cx = "C".$j;
     echo "<div id='container_".$Cx."' style='width: 25%; height: 240px; margin-left: 0px; float: left'></div>"."\n";
    }
?>

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
        description: 'Voltaje de cada celda de la bateria'
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
                //format: '{y} V'
                format: '{point.y:,.3f}'
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
 
  <?php
    for($j = 1 ;$j<$nceldas+1 ;$j++)
     {
      $Cx = "C".$j;
      echo "
       var Vcelda$j = new Highcharts.Chart ({
        chart: {
          renderTo: 'container_$Cx',
          backgroundColor: null,
          borderColor: null,
          shadow: false,
          zoomType: 'xy'
        },
        
        title: {
          text:'$Cx - Med, Máx y Mín'
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
      ";

      for($i = 0 ;$i<count($rawdata2);$i++){
        echo "data.push([".$rawdata2[$i]["Fecha"].",".$rawdata2[$i]["Med_$Cx"]."]);";
      }
      
      echo "
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
        ";         
      for($i = 0 ;$i<count($rawdata2);$i++){
        echo "data.push([".$rawdata2[$i]["Fecha"].",".$rawdata2[$i]["Max_$Cx"].",".$rawdata2[$i]["Min_$Cx"]."]);";
      }
            
      echo "
        return data;
           })()
         }
        ]

       });";

      
     }
  ?>   
               

  });
</script>

<?php
include ("pie.inc");
?>
