<?php

require('conexion.php');

//Coger datos soh
//$sql = "SELECT fecha, Ahn, AhCPn
//        FROM soh WHERE fecha>= SUBDATE(NOW(), INTERVAL 300 DAY)
//       ORDER BY fecha";

$sql = "SELECT fecha, Ahn, AhCPn
        FROM soh
        ORDER BY fecha";
		
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
    $time = $rawdata[$i]["fecha"];
    $date = new DateTime($time);
    $rawdata[$i]["fecha"]=$date->getTimestamp()*1000;
	//echo $rawdata[$i]["fecha"];
	//echo '-';
	//echo $rawdata[$i]["Ahn"];
	//echo '-';
	//echo $rawdata[$i]["AhCPn"];
	//echo '<br>';
	
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
				text: 'EVOLUCION CICLADO'
            },
            subtitle: {
                //text: 'Permite Zoom XY'
            },
            credits: {
                enabled: false
            },
            yAxis: [{
		        opposite: false, // Eje Ahn diario
				min: 0,
		        max: 2000,
				minorGridLineColor: 'transparent',
		        labels: {
                    //align: 'left',
                    y: 0
            	},
                title: {
                    text: null
                },
				plotLines: [{
					value: 200,
		            width: 2,
		            color: 'black',
		            dashStyle: 'shortdash',
					label: {
						text: '200Ah'
					}
		          }]
				
				
             },{
                opposite: false,
				min: 0,
		        max: 200000 ,
				minorGridLineColor: 'transparent',
		        labels: {
                    //align: 'left',
                    y: 0
            	},
                title: {
                    text: null
                },
				plotLines: [{
					value: 100000,
					width: 2,
					color: 'green',
					dashStyle: 'shortdash',
					label: {
						text: '100kAh',
						y:20,
						align: 'left'
					}
					}, {
					value: 200000,
					width: 2,
					color: 'red',
					dashStyle: 'shortdash',
					label: {
			            text: '200kAh',
						y:20
		              }
		          }]
	
             },{
                opposite: true,
				min: -100,
		        max: 100,
				tickInterval: 50,
				minorGridLineColor: 'transparent',
		        labels: {
                    //align: 'left',
                    y: 0
            	},
                title: {
                    text: null
                },
				plotLines: [{
		            value: 0,
		            width: 2,
		            color: 'green',
		            dashStyle: 'shortdash',
		            label: {
			            text: '0 ciclos',
						y:-5,
						align: 'left'
		             }
		            }, {
		            value: 50,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: '50 ciclos'
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
                    count: 7,
                    text: '7dias'
                }, {
                    type: 'day',
                    count: 30,
                    text: '30día'
                }, {
                    type: 'day',
                    count: 60,
                    text: '60días'
                }, {
                    type: 'all',
                    text: 'Todo'
                }],
                selected: 3
             },
            tooltip: {
                crosshairs: true,
                shared: true,
                valueDecimals: 2
             },

			navigator: {
					enabled: false
					},

			series: [{
                name: 'Ahn',
                type: 'column',
				yAxis: 0,
                color: Highcharts.getOptions().colors[1],
                tooltip: {
                    valueSuffix: ' Ah',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["fecha"];?>,<?php echo $rawdata[$i]["Ahn"];?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'AhCPn',
                type: 'column',
				yAxis: 0,
                color: Highcharts.getOptions().colors[0],
                tooltip: {
                    valueSuffix: ' AhCPn',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["fecha"];?>,<?php echo $rawdata[$i]["AhCPn"];?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'Ahn_Acum',
                type: 'spline',
				yAxis: 1,
                color: Highcharts.getOptions().colors[2],
                tooltip: {
                    valueSuffix: ' Ah',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       $Acu1=0;
					   for($i = 0 ;$i<count($rawdata);$i++){
						   $Acu1=$Acu1+$rawdata[$i]["Ahn"];
                   ?>
                   data.push([<?php echo $rawdata[$i]["fecha"];?>,<?php echo $Acu1;?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'AhCPn_Acum',
                type: 'spline',
				yAxis: 1,
                color: Highcharts.getOptions().colors[3],
                tooltip: {
                    valueSuffix: ' Ah',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
				       $Acu2=0;
                       for($i = 0 ;$i<count($rawdata);$i++){
						$Acu2=$Acu2+$rawdata[$i]["AhCPn"];   
                   ?>
                   data.push([<?php echo $rawdata[$i]["fecha"];?>,<?php echo $Acu2;?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'Nciclos Ah',
				visible: true,
                type: 'spline',
				yAxis: 2, // escala nciclos
                color: 'black', //Highcharts.getOptions().colors[20],
                tooltip: {
                    valueSuffix: ' ciclos',
                    valueDecimals: 1,
                },
                data: (function() {
                   var data = [];
                   <?php
				       $Acu3=0;
                       for($i = 0 ;$i<count($rawdata);$i++){
						 $Acu3=$Acu3+$rawdata[$i]["Ahn"]/1200;  
                   ?>
                   data.push([<?php echo $rawdata[$i]["fecha"];?>,<?php echo $Acu3;?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'Nciclos AhCP',
				visible: true,
                type: 'spline',
				yAxis: 2, // escala nciclos
                color: Highcharts.getOptions().colors[4],
                tooltip: {
                    valueSuffix: ' ciclos',
                    valueDecimals: 1,
                },
                data: (function() {
                   var data = [];
                   <?php
				       $Acu4=0;
                       for($i = 0 ;$i<count($rawdata);$i++){
						  $Acu4=$Acu4+$rawdata[$i]["AhCPn"]/1200;  
                   ?>
                   data.push([<?php echo $rawdata[$i]["fecha"];?>,<?php echo $Acu4;?>]);
                   <?php } ?>
                return data;
                     })()
            }]

        });

});
</script>
</html>
