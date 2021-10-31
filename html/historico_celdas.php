<?php
$titulo="Historico Celdas";
include ("cabecera.inc");

require('conexion.php');

if(( $_POST["fecha1"] ) && ($_POST["fecha2"] )) {
   $fecha1 = $_POST["fecha1"];
   $fecha2 = $_POST["fecha2"];
   if ( $_POST["nseg_punto"] ) {
	   $nseg_punto=$_POST["nseg_punto"];   
   } else {
	   $nseg_punto=10;
   }
   
 }else{			
   	 $fecha1= date("Y") . "-" . date("m") . "-" . date("d");
     $fecha2= date("Y") . "-" . date("m") . "-" . date("d");
	 $nseg_punto=10;
    
 }



//Coger datos grafica 
//$sql = "SELECT  UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, C0,C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15
//        FROM datos_celdas WHERE DATE(Tiempo) >= '" . $fecha1 . "' and DATE(Tiempo) <= '" . $fecha2 . "'
//        GROUP BY DATE(Tiempo),FLOOR(TIME_TO_SEC(TIME(Tiempo))/" . $nseg_punto . " ) ORDER BY Tiempo";

$sql = "SELECT  *
        FROM datos_celdas WHERE DATE(Tiempo) >= '" . $fecha1 . "' and DATE(Tiempo) <= '" . $fecha2 . "'
        GROUP BY DATE(Tiempo),FLOOR(TIME_TO_SEC(TIME(Tiempo))/" . $nseg_punto . " ) ORDER BY Tiempo";


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
for($i=0;$i<count($rawdata);$i++){
   $time = $rawdata[$i]["Tiempo"];
   $date = new DateTime($time);
   $rawdata[$i]["Tiempo"]=$date->getTimestamp()*1000;
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
	Muestra cada:<input type="number" size="5" name="nseg_punto" min="5" max="3600" step="5" value= <?php echo $nseg_punto ?> > seg__
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
      text: 'Voltaje Celdas'
      },
    subtitle: {
      //text: 'Permite Zoom XY'
      },
    credits: {
      enabled: false
      },
    yAxis: [
     {// ########## Valores eje Vbat ######################
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
        text: 'Vbat',//null
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
      /*
      plotLines: [{
        // ########## Valores Linea 2V #####################
        value: 2,
        width: 2,
        color: 'green',
        dashStyle: 'shortdash',
        label: {
          text: 'Vabs'
          }
       },{
        
        // ########## Valores Linea 2.5 ######################
        value: 2.5,
        width: 2,
        color: 'red',
        dashStyle: 'shortdash',
        label: {
          text: 'Vflot'
          }
       }]
       */
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
        count: 7,
        text: '7h'
       }, {
        type: 'hour',
        count: 12,
        text: '12h'
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
     {name: 'C1',
      type: 'spline',
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
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C0"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C2',
      type: 'spline',
      color: Highcharts.getOptions().colors[1],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C1"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C3',
      type: 'spline',
      color: Highcharts.getOptions().colors[2],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C2"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C4',
      type: 'spline',
      color: Highcharts.getOptions().colors[3],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C3"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C5',
      type: 'spline',
      color: Highcharts.getOptions().colors[4],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C4"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C6',
      type: 'spline',
      color: Highcharts.getOptions().colors[5],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C5"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C7',
      type: 'spline',
      color: Highcharts.getOptions().colors[6],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C6"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C8',
      type: 'spline',
      color: Highcharts.getOptions().colors[7],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C7"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C9',
      type: 'spline',
      color: Highcharts.getOptions().colors[8],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C8"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C10',
      type: 'spline',
      color: Highcharts.getOptions().colors[9],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C9"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C11',
      type: 'spline',
      color: Highcharts.getOptions().colors[10],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C10"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C12',
      type: 'spline',
      color: Highcharts.getOptions().colors[11],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C11"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C13',
      type: 'spline',
      color: Highcharts.getOptions().colors[12],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C12"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C14',
      type: 'spline',
      color: Highcharts.getOptions().colors[13],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C13"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C15',
      type: 'spline',
      color: Highcharts.getOptions().colors[14],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C14"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     {name: 'C16',
      type: 'spline',
      color: Highcharts.getOptions().colors[15],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: (function() {
        var data = [];
        
        <?php
          for($i = 0 ;$i<count($rawdata);$i++){
            ?>
            data.push([<?php echo $rawdata[$i]["Tiempo"];?>,
                       <?php echo $rawdata[$i]["C15"];?>]);
            <?php } ?>
          return data;
        })()      
     },
     
     ]

    });


  });
</script>

<?php
include ("pie.inc");
?>
