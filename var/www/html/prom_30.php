<?php

require('conexion.php');

date_default_timezone_set("UTC");

//Coger datos grafica 4
$sql = "SELECT Fecha, maxIbat, minIbat, avgIbat
		FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY)
		GROUP BY Fecha ORDER BY Fecha";

if($result = mysqli_query($link, $sql)){

	$i=0;
	while($row4 = mysqli_fetch_assoc($result)) {
		//guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
		$rawdata4[$i] = $row4;
		$i++;
	}

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


//Coger datos grafica 5
$sql = "SELECT Fecha, maxVbat, minVbat, avgVbat
		FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY)
		GROUP BY Fecha ORDER BY Fecha";

if($result = mysqli_query($link, $sql)){

        $i=0;
        while($row5 = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata5[$i] = $row5;
                $i++;
        }

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


//Coger datos grafica 6
$sql = "SELECT Fecha, maxSOC, minSOC, avgSOC
		FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY)
		GROUP BY Fecha ORDER BY Fecha";

if($result = mysqli_query($link, $sql)){

        $i=0;
        while($row6 = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata6[$i] = $row6;
                $i++;
        }

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


//Coger datos grafica 7
$sql = "SELECT Fecha, maxIplaca, avgIplaca
		FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY)
		GROUP BY Fecha ORDER BY Fecha";

if($result = mysqli_query($link, $sql)){

        $i=0;
        while($row7 = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata7[$i] = $row7;
                $i++;
        }

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}



//Coger datos grafica 8
$sql = "SELECT Fecha, maxTemp, minTemp, avgTemp
                FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY)
                GROUP BY Fecha ORDER BY Fecha";

if($result = mysqli_query($link, $sql)){

        $i=0;
        while($row8 = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata8[$i] = $row8;
                $i++;
        }

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}



mysqli_close($link);


//Adaptar el tiempo grafica4
for($i=0;$i<count($rawdata4);$i++){
    $time = $rawdata4[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata4[$i]["Fecha"]=$date->getTimestamp()*1000;
}


//Adaptar el tiempo grafica5
for($i=0;$i<count($rawdata5);$i++){
    $time = $rawdata5[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata5[$i]["Fecha"]=$date->getTimestamp()*1000;
}


//Adaptar el tiempo grafica6
for($i=0;$i<count($rawdata6);$i++){
    $time = $rawdata6[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata6[$i]["Fecha"]=$date->getTimestamp()*1000;
}


//Adaptar el tiempo grafica7
for($i=0;$i<count($rawdata7);$i++){
    $time = $rawdata7[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata7[$i]["Fecha"]=$date->getTimestamp()*1000;
}


//Adaptar el tiempo grafica8
for($i=0;$i<count($rawdata8);$i++){
    $time = $rawdata8[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata8[$i]["Fecha"]=$date->getTimestamp()*1000;
}



?>

<HTML>

<body>

<meta charset="utf-8">

<script src="https://code.jquery.com/jquery.js"></script>

<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="http://code.highcharts.com/themes/grid.js"></script>


<div id="container4" style="width: 48%; height: 240px; margin-left: 20px; float: left"></div>
<div id="container5" style="width: 48%; height: 240px; margin-left: 10px; float: left"></div>
<div style="clear:both; height:10px;"/></div>
<div id="container7" style="width: 48%; height: 240px; margin-left: 20px; float: left"></div>
<div id="container6" style="width: 48%; height: 240px; margin-left: 10px; float: left"></div>
<div style="clear:both; height:10px;"/></div>
<div id="container8" style="width: 48%; height: 240px; margin-left: 20px; float: left"></div>
<div id="container9" style="width: 48%; height: 240px; margin-left: 10px; float: left"></div>
<div style="clear:both; height:10px;"/></div>


</body>

<script>
$(function () {

	Highcharts.setOptions({
            global: {
                useUTC: true
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

        var char4 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container4',
                zoomType: 'xy'
            },

            title: {
                text: 'Ibat - AVG, Máx y Mín'
            },
            subtitle: {
                //text: 'Permite Zoom XY'
            },
            credits: {
                enabled: false
            },
	    xAxis: {
		type: 'datetime',
                dateTimeLabelFormats: { day: '%e %b' }
	    },
	    yAxis: {
		title: {
		    text: null
		}
	    },
	    tooltip: {
		crosshairs: true,
		shared: true,
		valueSuffix: 'A'
	    },
	    legend: {
		enabled: false
	    },

            series: [{
                name: 'AVG',
		zIndex: 1,
		color: Highcharts.getOptions().colors[2],
            	marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[2]
                },
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata4);$i++){
                   ?>
                   data.push([<?php echo $rawdata4[$i]["Fecha"];?>,<?php echo $rawdata4[$i]["avgIbat"];?>]);
                   <?php } ?>
                return data;
                     })()
            }, {
                name: 'Máx-Mín',
                type: 'arearange',
		lineWidth: 0,
		linkedTo: ':previous',
                color: Highcharts.getOptions().colors[2],
		fillOpacity: 0.3,
		zIndex: 0,
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata4);$i++){
                   ?>
                   data.push([<?php echo $rawdata4[$i]["Fecha"];?>,<?php echo $rawdata4[$i]["maxIbat"];?>,<?php echo $rawdata4[$i]["minIbat"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]


        });

        var char5 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container5',
                zoomType: 'xy'
            },

            title: {
                text: 'Vbat - AVG, Máx y Mín'
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
            series: [{
                name: 'AVG',
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
                       for($i = 0 ;$i<count($rawdata5);$i++){
                   ?>
                   data.push([<?php echo $rawdata5[$i]["Fecha"];?>,<?php echo $rawdata5[$i]["avgVbat"];?>]);
                   <?php } ?>
                return data;
                     })()
            }, {
                name: 'Máx-Mín',
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
                       for($i = 0 ;$i<count($rawdata5);$i++){
                   ?>
                   data.push([<?php echo $rawdata5[$i]["Fecha"];?>,<?php echo $rawdata5[$i]["maxVbat"];?>,<?php echo $rawdata5[$i]["minVbat"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]


        });

        var char6 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container6',
                zoomType: 'xy'
            },

            title: {
                text: 'SOC - AVG, Máx y Mín'
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
                title: {
                    text: null
                }
            },
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: ' %'
            },
            legend: {
                enabled: false
            },
            series: [{
                name: 'AVG',
                zIndex: 1,
                color: Highcharts.getOptions().colors[1],
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[1]
                },
                tooltip: {
                    valueSuffix: ' %',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata6);$i++){
                   ?>
                   data.push([<?php echo $rawdata6[$i]["Fecha"];?>,<?php echo $rawdata6[$i]["avgSOC"];?>]);
                   <?php } ?>
                return data;
                     })()
            }, {
                name: 'Máx-Mín',
                type: 'arearange',
                lineWidth: 0,
                linkedTo: ':previous',
                color: Highcharts.getOptions().colors[1],
                fillOpacity: 0.3,
                zIndex: 0,
                tooltip: {
                    valueSuffix: ' %',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata6);$i++){
                   ?>
                   data.push([<?php echo $rawdata6[$i]["Fecha"];?>,<?php echo $rawdata6[$i]["maxSOC"];?>,<?php echo $rawdata6[$i]["minSOC"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]


        });

        var char7 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container7',
                zoomType: 'xy'
            },

            title: {
                text: 'Iplaca - AVG, Máx y Mín'
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
                title: {
                    text: null
                }
            },
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: ' %'
            },
            legend: {
                enabled: false
            },
            series: [{
                name: 'AVG',
                zIndex: 1,
                color: Highcharts.getOptions().colors[3],
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[3]
                },
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata7);$i++){
                   ?>
                   data.push([<?php echo $rawdata7[$i]["Fecha"];?>,<?php echo $rawdata7[$i]["avgIplaca"];?>]);
                   <?php } ?>
                return data;
                     })()
            }, {
                name: 'Máx-Mín',
                type: 'arearange',
                lineWidth: 0,
                linkedTo: ':previous',
                color: Highcharts.getOptions().colors[3],
                fillOpacity: 0.3,
                zIndex: 0,
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata7);$i++){
                   ?>
                   data.push([<?php echo $rawdata7[$i]["Fecha"];?>,<?php echo $rawdata7[$i]["maxIplaca"];?>,<?php echo 0;?>]);
                   <?php } ?>
                return data;
                     })()
            }]
        });

        var char8 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container8',
                zoomType: 'xy'
            },

            title: {
                text: 'Temp - AVG, Máx y Mín'
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
                title: {
                    text: null
                }
            },
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: ' %'
            },
            legend: {
                enabled: false
            },
            series: [{
                name: 'AVG',
                zIndex: 1,
                color: Highcharts.getOptions().colors[8],
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[8]
                },
                tooltip: {
                    valueSuffix: ' ºC',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata8);$i++){
                   ?>
                   data.push([<?php echo $rawdata8[$i]["Fecha"];?>,<?php echo $rawdata8[$i]["avgTemp"];?>]);
                   <?php } ?>
                return data;
                     })()
            }, {
                name: 'Máx-Mín',
                type: 'arearange',
                lineWidth: 0,
                linkedTo: ':previous',
                color: Highcharts.getOptions().colors[8],
                fillOpacity: 0.3,
                zIndex: 0,
                tooltip: {
                    valueSuffix: ' ºC',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata8);$i++){
                   ?>
                   data.push([<?php echo $rawdata8[$i]["Fecha"];?>,<?php echo $rawdata8[$i]["maxTemp"];?>,<?php echo $rawdata8[$i]["minTemp"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]
        });


});
</script>
</html>
