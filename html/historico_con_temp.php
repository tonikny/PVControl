
<?php
$titulo="Historico con Temp";
include ("cabecera.inc");

require('conexion.php');

if(( isset($_POST["fecha1"]) ) && (isset($_POST["fecha2"]) )) {
   $fecha1 = $_POST["fecha1"];
   $fecha2 = $_POST["fecha2"];
   if ( $_POST["nseg_punto"] ) {
	   $nseg_punto=$_POST["nseg_punto"];   
   } else {
	   $nseg_punto=600;
   }
   
 }else{			
   	 $fecha1= date("Y") . "-" . date("m") . "-" . date("d");
     $fecha2= date("Y") . "-" . date("m") . "-" . date("d");
	 $nseg_punto=600;
    
 }
 
$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo1, AVG(SOC) as SOCavg, AVG(Ibat) as Ibatavg, AVG(Iplaca) as Iplacaavg, AVG(Vbat) as Vbatavg, AVG(Temp) as Vflotavg
        FROM datos_c WHERE DATE(Tiempo) >= '" . $fecha1 . "' and DATE(Tiempo) <= '" . $fecha2 . "'
        GROUP BY DATE(Tiempo),FLOOR(TIME_TO_SEC(TIME(Tiempo))/" . $nseg_punto . " ) ORDER BY Tiempo";

//echo " Desde: ",$fecha1,"   Hasta: ",$fecha2,"   -- Muestra cada ",$nseg_punto," seg   -- ";

if($result = mysqli_query($link, $sql)){
   $i=0;
   while($row = mysqli_fetch_assoc($result)) {
      $rawdata[$i] = $row;
      $i++;
   }
   //echo "  N_puntos=",$i;
 }else{
   echo "ERROR $sql. " . mysqli_error($link);
 }

mysqli_close($link);

?>


<!-- Importo el archivo Javascript de Highcharts directamente desde la RPi
<script src="js/jquery.js"></script>
<script src="js/stock/highstock.js"></script>
<script src="js/highcharts-more.js"></script>

<script src="js/themes/grid.js"></script>
-->

<!-- Importo el archivo Javascript directamente desde la web -->
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
				panning: true,
                panKey: 'shift'
            },

            title: {
                text: 'Promedio SOC, Iplaca/Ibat/ Vbat y Temp'
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
                //minorGridLineColor: 'transparent',
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
		            value: Vabs,
		            width: 2,
		            color: 'green',
		            dashStyle: 'shortdash',
		            label: {
			            text: 'Vabs'
		             }
		            }, {
		            value: Vflot,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: 'Vflot'
		              }
		            }]
	
             },
             {// SOC
                opposite: true,
				min: 5,
		        max: 100 ,
                gridLineColor: 'transparent',
                minorGridLineColor: 'transparent',
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    align: 'high',
                    offset: 0,
                    text: 'SOC <br/> Temp',//null
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
		            }, {
		            value: 80,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: '80%'
					       }
		              }, {
		            value: 30,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: '30ºC'
		                   }
		          }]
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
                    type: 'day',
                    count: 1,
                    text: '1día'
                }, {
                    type: 'day',
                    count: 3,
                    text: '3días'
                },	{
                    type: 'day',
                    count: 7,
                    text: '7días'
                }, {
                    type: 'day',
                    count: 15,
                    text: '15días'
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

            series: [
              { name: 'Avg SOC',
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
                   data.push([<?php echo $rawdata[$i]["Tiempo1"];?>,<?php echo $rawdata[$i]["SOCavg"];?>]);
                   <?php } ?>
                return data;
                     })()
              },
              { name: 'Avg Vbat',
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
                   data.push([<?php echo $rawdata[$i]["Tiempo1"];?>,<?php echo $rawdata[$i]["Vbatavg"];?>]);
                   <?php } ?>
                return data;
                     })()
              },
              { name: 'Avg Ibat',
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
                   data.push([<?php echo $rawdata[$i]["Tiempo1"];?>,<?php echo $rawdata[$i]["Ibatavg"];?>]);
                   <?php } ?>
                return data;
                     })()
              },
              { name: 'Avg Iplaca',
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
                   data.push([<?php echo $rawdata[$i]["Tiempo1"];?>,<?php echo $rawdata[$i]["Iplacaavg"];?>]);
                   <?php } ?>
                return data;
                     })()
              },
              { name: 'Avg Temp',
                type: 'spline',
				yAxis: 2,
                color: 'black', //color: Highcharts.getOptions().colors[4],
                tooltip: {
                    valueSuffix: ' ',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo1"];?>,<?php echo $rawdata[$i]["Vflotavg"];?>]);
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
