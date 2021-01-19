<?php
$titulo="Promedios 30 dias";
include("cabecera.inc");

require('conexion.php');

date_default_timezone_set("UTC");

$sql = "SELECT UNIX_TIMESTAMP(Fecha)*1000 as Fecha,Fecha as ___Dia___,
                maxVbat as 'Max Vbat',minVbat as 'Min Vbat',avgVbat as 'Med Vbat',
                maxSOC as 'Max SOC',minSOC as 'Min SOC',avgSOC as 'Med SOC',
                maxIbat as 'Max Ibat',minIbat as 'Min Ibat',avgIbat as 'Med Ibat',
                maxIplaca as 'Max Iplaca',avgIplaca as 'Med Iplaca',
                round(Wh_placa/1000,2) as 'kWh Placa',round(Whp_bat/1000,2) as 'kWhp Bat',
                round(Whn_bat/1000,2) as 'kWhn Bat',round(Wh_consumo/1000,2) as 'kWh Con',
                maxTemp as 'Max Temp',minTemp as 'Min Temp',avgTemp as 'Med Temp',
                round(Whp_red/1000,2) as 'kWhp red',round(Whn_red/1000,2) as 'kWhn red',
                round((Whp_red - Whn_red)/1000,2) as 'kWh red',
                maxWred as 'Max Wred',minWred as 'Min Wred',avgWred as 'Med Wred',
                maxVred as 'Max Vred',minVred as 'Min Vred'
        FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY) 
        GROUP BY Fecha ORDER BY Fecha";


if($result = mysqli_query($link, $sql)){
    $i=0;
    while ($row = mysqli_fetch_array($result)){
        $rawdata[$i]=$row;
        $i++;
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }
mysqli_close($link);

$columnas = count($rawdata[0])/2;
$filas = count($rawdata);

?>

<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css" media="screen" />

<script src="https://code.jquery.com/jquery.js"></script>

<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="http://code.highcharts.com/themes/grid.js"></script>

<script src="https://code.jquery.com/jquery-3.3.1.js"></script>
<script src="https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js"></script>


<div id="container_Ibat" style="width: 32%; height: 240px; margin-left: 10px; float: left"></div>
<div id="container_Vbat" style="width: 32%; height: 240px; margin-left: 10px; float: left"></div>
<div id="container_Iplaca" style="width: 32%; height: 240px; margin-left: 10px; float: left"></div>

<div id="container_Wred" style="width: 32%; height: 240px; margin-left: 10px; float: left"></div>
<div id="container_Vred" style="width: 32%; height: 240px; margin-left: 10px; float: left"></div>
<div id="container_kWhred" style="width: 32%; height: 240px; margin-left: 10px; float: left"></div>


<div style="clear:both; height:10px;"/></div>
<div id="container_SOC" style="width: 48%; height: 240px; margin-left: 10px; float: left"></div>
<div id="container_Temp" style="width: 48%; height: 240px; margin-left: 10px; float: left"></div>

<div style="clear:both; height:10px;"/></div>
<!--
<div id="container9" style="width: 48%; height: 240px; margin-left: 10px; float: left"></div>
-->
<div style="clear:both; height:10px;"/></div>


<div id="div1">

<table id="example" class="display compact" style="width:100%">
        <thead>
            <tr>
             <?php
                //Añadimos los titulos
                next($rawdata[0]);
                next($rawdata[0]);
                for($i=3;$i<count($rawdata[0]);$i=$i+2){
                    next($rawdata[0]);
                    echo "<th><b>".key($rawdata[0])."</b></th>";
                    next($rawdata[0]);
                }
               ?>                
            </tr>
        </thead>
        <tbody>
            <?php
               	for($i=0;$i<$filas;$i++){
                    echo "<tr>";
                    for($j=1;$j<$columnas;$j++){
                        echo "<td>".$rawdata[$i][$j]."</td>";
                    }
                    echo "</tr>";
                }
             ?> 
            
        </tbody>
        <tfoot>
            <?php
                //Añadimos los pies
                for($i=3;$i<count($rawdata[0]);$i=$i+2){
                    next($rawdata[0]);
                    echo "<th><b>".key($rawdata[0])."</b></th>";
                    next($rawdata[0]);
                }
               ?>                
        </tfoot>

</table>

</div>



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

        var Ibat = new Highcharts.Chart ({
            chart: {
                renderTo: 'container_Ibat',
                zoomType: 'xy'
            },

            title: {
                text: 'Ibat - Med, Máx y Mín'
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Med Ibat"];?>]);
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Max Ibat"];?>,<?php echo $rawdata[$i]["Min Ibat"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]


        });

        var Vbat = new Highcharts.Chart ({
            chart: {
                renderTo: 'container_Vbat',
                zoomType: 'xy'
            },

            title: {
                text: 'Vbat - Med, Máx y Mín'
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Med Vbat"];?>]);
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Max Vbat"];?>,<?php echo $rawdata[$i]["Min Vbat"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]


        });

        var Iplaca = new Highcharts.Chart ({
            chart: {
                renderTo: 'container_Iplaca',
                zoomType: 'xy'
            },

            title: {
                text: 'Iplaca - Med, Máx y Mín'
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Med Iplaca"];?>]);
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Max Iplaca"];?>,<?php echo 0;?>]);
                   <?php } ?>
                return data;
                     })()
            }]
        });


        var Wred = new Highcharts.Chart ({
            chart: {
                renderTo: 'container_Wred',
                zoomType: 'xy'
            },

            title: {
                text: 'Wred - Med, Máx y Mín'
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Med Wred"];?>]);
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
                    valueSuffix: ' W',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Max Wred"];?>,<?php echo $rawdata[$i]["Min Wred"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]
        });


        var Vred = new Highcharts.Chart ({
            chart: {
                renderTo: 'container_Vred',
                zoomType: 'xy'
            },

            title: {
                text: 'Vred - Máx y Mín'
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
                min: 180,
                max: 260,
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
                name: 'Máx-Mín',
                type: 'arearange',
                lineWidth: 0,
                linkedTo: ':previous',
                color: Highcharts.getOptions().colors[3],
                fillOpacity: 0.3,
                zIndex: 0,
                tooltip: {
                    valueSuffix: ' V',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Max Vred"];?>,<?php echo $rawdata[$i]["Min Vred"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]
        });


        var kWhred = new Highcharts.Chart ({
            chart: {
                renderTo: 'container_kWhred',
                zoomType: 'xy'
            },

            title: {
                text: 'kWh AC - Neto, Inyecc y Consumo'
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
                tickInterval: 1,
                title: {
                    text: null
                }
             },
            tooltip: {
                crosshairs: true,
                shared: true,
                valueSuffix: 'kWh'
             },
            legend: {
                enabled: false
             },

            series: [{
                name: 'Neto',
                type: 'column',
                zIndex: 1,
                color: Highcharts.getOptions().colors[1],
                marker: {
                    fillColor: 'white',
                    lineWidth: 2,
                    lineColor: Highcharts.getOptions().colors[2]
                },
                tooltip: {
                    valueSuffix: ' kWh',
                    valueDecimals: 1,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["kWh red"];?>]);
                   <?php } ?>
                  return data;
                     })()
                }, {
                name: 'Inyecc-Consumo',
                type: 'arearange',
                lineWidth: 0,
                linkedTo: ':previous',
                color: Highcharts.getOptions().colors[2],
                fillOpacity: 0.3,
                zIndex: 0,
                tooltip: {
                    valueSuffix: ' kWh',
                    valueDecimals: 1,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["kWhp red"];?>,<?php echo -$rawdata[$i]["kWhn red"];?>]);
                   <?php } ?>
                 return data;
                     })()
            }]
        });




        var SOC = new Highcharts.Chart ({
            chart: {
                renderTo: 'container_SOC',
                zoomType: 'xy'
            },

            title: {
                text: 'SOC - Med, Máx y Mín'
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Med SOC"];?>]);
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Max SOC"];?>,<?php echo $rawdata[$i]["Min SOC"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]


        });

        var Temp = new Highcharts.Chart ({
            chart: {
                renderTo: 'container_Temp',
                zoomType: 'xy'
            },

            title: {
                text: 'Temp - Med, Máx y Mín'
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Med Temp"];?>]);
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
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Fecha"];?>,<?php echo $rawdata[$i]["Max Temp"];?>,<?php echo $rawdata[$i]["Min Temp"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]
        });


});

$(document).ready(function() {
    $('#example').DataTable({
        "order": [[ 0, "desc" ]],
        "scrollY":  "400px",
        "scrollCollapse": true,
        "scrollX": true,
        "info":    false,
        "paging":  false
        
    } );
} );



</script>
<?php
include ("pie.inc");
?>
