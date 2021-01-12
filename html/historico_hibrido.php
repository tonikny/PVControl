<?php
include ("cabecera.inc");

require('conexion.php');

if(( $_POST["fecha1"] ) && ($_POST["fecha2"] )) {
   $fecha1 = $_POST["fecha1"];
   $fecha2 = $_POST["fecha2"];
   if ( $_POST["nseg_punto"] ) {
	   $nseg_punto=$_POST["nseg_punto"];   
   } else {
	   $nseg_punto=60;
   }
   
 }else{			
   	 $fecha1= date("Y") . "-" . date("m") . "-" . date("d");
     $fecha2= date("Y") . "-" . date("m") . "-" . date("d");
	 $nseg_punto=60;
    
 }
 
$sql = "SELECT Tiempo, AVG(Vbus) as Vbus,(AVG(Vbus)/Avg(Vbat))*30 as Vbus_Vbat, (AVG(Ibatp)-AVG(Ibatn)) as Ibat,
                       AVG(Iplaca) as Iplaca, AVG(Vbat) as Vbat, AVG(Temp) as Temp, AVG(PACW) as PACW, AVG(Flot)*50 as Flot
        FROM hibrido WHERE DATE(Tiempo) >= '" . $fecha1 . "' and DATE(Tiempo) <= '" . $fecha2 . "'
        GROUP BY DAY(Tiempo),FLOOR(TIME_TO_SEC(TIME(Tiempo))/" . $nseg_punto . " ) ORDER BY Tiempo";

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

//Adaptar el tiempo grafica historico general
for($i=0;$i<count($rawdata);$i++){
   $time = $rawdata[$i]["Tiempo"];
   $date = new DateTime($time);
   $rawdata[$i]["Tiempo"]=$date->getTimestamp()*1000;
 }

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
	Muestra cada:<input type="number" size="5" name="nseg_punto" min="4" max="3600" step="4" value= <?php echo $nseg_punto ?> > seg__
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
                text: 'HIBRIDO -  Vbus, Iplaca/Ibat/Vbat/PACW/Flot y Temp Disipador'
            },
            subtitle: {
                //text: 'Permite Zoom XY'
            },
            credits: {
                enabled: false
            },
            yAxis: [{
		        opposite: false,
				min: -80,
		        max: 80 ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                }
             },{
                opposite: false,
				min: 24,
		        max: 36 ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                },
				plotLines: [{
		            value: 29,
		            width: 2,
		            color: 'green',
		            dashStyle: 'shortdash',
		            label: {
			            text: 'Vabs'
		             }
		            }, {
		            value: 27.2,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: 'Vflot'
		              }
		          }]
	
             },{
                opposite: true,
				min: 0,
		        max: 500 ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                },
				plotLines: [{
		            value: 480,
		            width: 2,
		            color: 'green',
		            dashStyle: 'shortdash',
		            label: {
			            text: '480= Ratio 16*30'
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
		       },{
                opposite: true,
				min: 0,
		        max: 5000 ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                },
				plotLines: [{
		            value: 4000,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: '4000w'
		                   }
		          }]
		
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

            series: [{
                name: 'Vbus',
                type: 'spline',
				yAxis: 2,
                color: Highcharts.getOptions().colors[1],
                tooltip: {
                    valueSuffix: ' V',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vbus"];?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'Vbat',
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
              }, {
                name: 'Ibat',
                type: 'spline',
                color: Highcharts.getOptions().colors[2],
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 0,
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
              }, {
                name: 'Iplaca',
                type: 'spline',
                color: Highcharts.getOptions().colors[3],
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 0,
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
              }, {
                name: 'Temp Disipador',
                type: 'spline',
				yAxis: 2,
                color: 'black', //color: Highcharts.getOptions().colors[4],
                tooltip: {
                    valueSuffix: ' ºC',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Temp"];?>]);
                   <?php } ?>
                return data;
                     })()
					 
			   }, {
                name: 'Ratio Vbus/Vbat*30',
                type: 'spline',
				yAxis: 2,
                color: 'black', //color: Highcharts.getOptions().colors[4],
                tooltip: {
                    valueSuffix: '',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vbus_Vbat"];?>]);
                   <?php } ?>
                return data;
                     })()
					 		 
			   }, {
                name: 'Consumo AC ',
                type: 'spline',
				yAxis: 3,
				//color: '#F000FF', //Highcharts.getOptions().colors[7],
                color: 'brown',
                tooltip: {
                    valueSuffix: 'W',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["PACW"];?>]);
                   <?php } ?>
                return data;
                     })()
					
               }, {
                name: 'Flot',
                type: 'spline',
				yAxis: 2,
				//color: '#F000FF', 
                color: 'green',
                tooltip: {
                    valueSuffix: ' ',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Flot"];?>]);
                   <?php } ?>
                return data;
                     })()

					
            }]

        });

});
</script>

<?php
include ("pie.inc");
?>
