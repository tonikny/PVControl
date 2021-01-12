<?php
include ("cabecera.inc");

require('conexion.php');

date_default_timezone_set("UTC");

//Coger datos  grafica1
$sql = "SELECT Fecha, TRUNCATE(Whn_bat/Whp_bat*100,2) as Ratio
		FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY) and Whp_bat >= 1
		GROUP BY Fecha ORDER BY Fecha";

if($result = mysqli_query($link, $sql)){

        $i=0;
        while($row1 = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata1[$i] = $row1;
                $i++;
        }

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


//Coger datos grafica2

$sql = "SELECT FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 14)) AS Fecha, TRUNCATE(SUM(Whn_bat)/SUM(Whp_bat)*100,2) as Ratio
                        FROM diario
                        WHERE Fecha>= DATE_SUB(curdate(), INTERVAL (500 + DAYOFWEEK(curdate())) DAY)
                        GROUP BY FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 14))
						ORDER BY `Fecha`";
		
		
if($result = mysqli_query($link, $sql)){
        $i=0;
        while($row2 = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata2[$i] = $row2;
                $i++;
        }

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


//Coger datos grafica3
$sql = "SELECT FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 28)) AS Fecha, TRUNCATE(SUM(Whn_bat)/SUM(Whp_bat)*100,2) as Ratio
                        FROM diario
                        WHERE Fecha>= DATE_SUB(curdate(), INTERVAL (500 + DAYOFWEEK(curdate())) DAY)
                        GROUP BY FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 28))
						ORDER BY `Fecha`";
		
		
if($result = mysqli_query($link, $sql)){
        $i=0;
        while($row3 = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata3[$i] = $row3;
                $i++;
        }
} else{
        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

//Coger datos grafica4
$sql = "SELECT FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 90)) AS Fecha, TRUNCATE(SUM(Whn_bat)/SUM(Whp_bat)*100,2) as Ratio
                        FROM diario
                        WHERE Fecha>= DATE_SUB(curdate(), INTERVAL (500 + DAYOFWEEK(curdate())) DAY)
                        GROUP BY FROM_DAYS(TO_DAYS(Fecha) -MOD(TO_DAYS(Fecha) -2, 90))
						ORDER BY `Fecha`";
		
		
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


mysqli_close($link);


//Adaptar el tiempo grafica1
for($i=0;$i<count($rawdata1);$i++){
    $time = $rawdata1[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata1[$i]["Fecha"]=$date->getTimestamp()*1000;
}

//Adaptar el tiempo grafica2
for($i=0;$i<count($rawdata2);$i++){
    $time = $rawdata2[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata2[$i]["Fecha"]=$date->getTimestamp()*1000;
}

//Adaptar el tiempo grafica3
for($i=0;$i<count($rawdata3);$i++){
    $time = $rawdata3[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata3[$i]["Fecha"]=$date->getTimestamp()*1000;
}


//Adaptar el tiempo grafica4
for($i=0;$i<count($rawdata4);$i++){
    $time = $rawdata4[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata4[$i]["Fecha"]=$date->getTimestamp()*1000;
}

?>

<script src="https://code.jquery.com/jquery.js"></script>

<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="http://code.highcharts.com/themes/grid.js"></script>


<div id="container1"  style="width: 100%; height: 240px; margin-left:5; float: left"></div>
<div style="clear:both; height:10px;"/></div>
<div id="container2"  style="width: 100%; height: 240px; margin-left:5; float: left"></div>
<div style="clear:both; height:10px;"/></div>
<div id="container3"  style="width: 100%; height: 240px; margin-left:5; float: left"></div>
<div style="clear:both; height:10px;"/></div>
<div id="container4"  style="width: 100%; height: 240px; margin-left:5; float: left"></div>
<div style="clear:both; height:10px;"/></div>


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

    var char1 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container1',
                zoomType: 'xy'
            },

            title: {
                text: 'Eficiencia Carga/Descarga kWh'
            },
            subtitle: {
                text: 'Periodo 1 dia'
            },
            credits: {
                enabled: false
	    },
            xAxis: {
                dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'
                //categories: ['Mie','Jue','Vie','Sab','Dom']
            },

            yAxis: {
                title: {
                    text: null
                }
            },

            legend: {
                enabled: true,
                layout: 'vertical',
                backgroundColor: 'white',
                align: 'right',
                verticalAlign: 'top',
                y: 0,
                x: 0,
                borderWidth: 1,
                borderRadius: 0,
                floating: true
            },

            plotOptions: {
                  column: {
                    dataLabels: {
                        enabled: true,
                        crop: false,
                        overflow: 'none',
                    },
                    enableMouseTracking: false
                  }
            },

            series: [{
                name: '%',
                type: 'column',
        		pointWidth: 20,
                color: 'rgba(100,149,237,0.8)',
                //color: Highcharts.getOptions().colors[0],
                tooltip: {
                    valueSuffix: ' %',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata1);$i++){
                   ?>
                   data.push([<?php echo $rawdata1[$i]["Fecha"];?>,<?php echo $rawdata1[$i]["Ratio"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]

	});
		
	var char2 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container2',
                zoomType: 'xy'
            },

            title: {
                text: 'Eficiencia Carga/Descarga kWh'
            },
            subtitle: {
                text: 'Periodo 14 dias'
            },
            credits: {
                enabled: false
	    },
            xAxis: {
                dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'
                //categories: ['Mie','Jue','Vie','Sab','Dom']
            },

            yAxis: {
                title: {
                    text: null
                }
            },

            legend: {
                enabled: true,
                layout: 'vertical',
                backgroundColor: 'white',
                align: 'right',
                verticalAlign: 'top',
                y: 0,
                x: 0,
                borderWidth: 1,
                borderRadius: 0,
                floating: true
            },

            plotOptions: {
                  column: {
                    dataLabels: {
                        enabled: true,
                        crop: false,
                        overflow: 'none',
                    },
                    enableMouseTracking: false
                  }
            },

            series: [{
                name: '%',
                type: 'column',
				pointWidth: 20,
                color: 'rgba(100,149,237,0.8)',
                //color: Highcharts.getOptions().colors[0],
                tooltip: {
                    valueSuffix: ' %',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata2);$i++){
                   ?>
                   data.push([<?php echo $rawdata2[$i]["Fecha"];?>,<?php echo $rawdata2[$i]["Ratio"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]

	});

    var char3 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container3',
                zoomType: 'xy'
            },

            title: {
                text: 'Eficiencia Carga/Descarga kWh'
            },
            subtitle: {
                text: 'Periodo 28 dias'
            },
            credits: {
                enabled: false
	    },
            xAxis: {
                dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'
                //categories: ['Mie','Jue','Vie','Sab','Dom']
            },

            yAxis: {
                title: {
                    text: null
                }
            },

            legend: {
                enabled: true,
                layout: 'vertical',
                backgroundColor: 'white',
                align: 'right',
                verticalAlign: 'top',
                y: 0,
                x: 0,
                borderWidth: 1,
                borderRadius: 0,
                floating: true
            },

            plotOptions: {
                  column: {
                    dataLabels: {
                        enabled: true,
                        crop: false,
                        overflow: 'none',
                    },
                    enableMouseTracking: false
                  }
            },


            series: [{
                name: '%',
                type: 'column',
				pointWidth: 20,
                color: 'rgba(100,149,237,0.8)',
                //color: Highcharts.getOptions().colors[0],
                tooltip: {
                    valueSuffix: ' %',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata3);$i++){
                   ?>
                   data.push([<?php echo $rawdata3[$i]["Fecha"];?>,<?php echo $rawdata3[$i]["Ratio"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]

	});
		

    var char4 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container4',
                zoomType: 'xy'
            },

            title: {
                text: 'Eficiencia Carga/Descarga kWh'
            },
            subtitle: {
                text: 'Periodo 90 dias'
            },
            credits: {
                enabled: false
	    },
            xAxis: {
                dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'
                //categories: ['Mie','Jue','Vie','Sab','Dom']
            },

            yAxis: {
                title: {
                    text: null
                }
            },

            legend: {
                enabled: true,
                layout: 'vertical',
                backgroundColor: 'white',
                align: 'right',
                verticalAlign: 'top',
                y: 0,
                x: 0,
                borderWidth: 1,
                borderRadius: 0,
                floating: true
            },

            plotOptions: {
                  column: {
                    dataLabels: {
                        enabled: true,
                        crop: false,
                        overflow: 'none',
                    },
                    enableMouseTracking: false
                  }
            },


            series: [{
                name: '%',
                type: 'column',
				pointWidth: 20,
                color: 'rgba(100,149,237,0.8)',
                //color: Highcharts.getOptions().colors[0],
                tooltip: {
                    valueSuffix: ' %',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata4);$i++){
                   ?>
                   data.push([<?php echo $rawdata4[$i]["Fecha"];?>,<?php echo $rawdata4[$i]["Ratio"];?>]);
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
