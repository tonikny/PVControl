<?php

require('conexion.php');

// Obtener las fechas del formulario (si se envió)
$fecha_inicio = isset($_GET['fecha_inicio']) ? $_GET['fecha_inicio'] : date('Y-m-d 00:00:00');
$fecha_fin = isset($_GET['fecha_fin']) ? $_GET['fecha_fin'] : date('Y-m-d 23:59:59');

// Consulta SQL para obtener los datos filtrados por rango de fechas
$query = "SELECT tiempo, datos FROM TUYA WHERE tiempo BETWEEN '$fecha_inicio' AND '$fecha_fin'";
$resultado = $link->query($query);

$datos_grafico = [];

if ($resultado->num_rows > 0) {
    while ($fila = $resultado->fetch_assoc()) {
        $tiempo = strtotime($fila['tiempo']) * 1000; // Convertir a milisegundos para Highcharts
        $datos = json_decode($fila['datos'], true);

        foreach ($datos as $clave => $valores) {
            if (!isset($datos_grafico[$clave])) {
                $datos_grafico[$clave] = [
                    'Estado' => [],
                    'Wac' => [],
                    'Wh' => [],
                    'Vac' => []
                ];
            }
            $datos_grafico[$clave]['Estado'][] = [$tiempo, $valores['Estado']];
            $datos_grafico[$clave]['Wac'][] = [$tiempo, $valores['Wac']];
            $datos_grafico[$clave]['Wh'][] = [$tiempo, $valores['Wh']];
            $datos_grafico[$clave]['Vac'][] = [$tiempo, $valores['Vac']];
        }
    }
}

$link->close();


?>


<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">

    <title>Gráficos TUYA</title>
    
<!--    
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <script src="https://code.highcharts.com/modules/exporting.js"></script>
    <script src="https://code.highcharts.com/modules/export-data.js"></script>
    
    <script src="https://code.highcharts.com/themes/grid.js"></script>
    
-->

    <script src="https://code.jquery.com/jquery.js"></script>
    <script src="https://code.highcharts.com/stock/highstock.js"></script>
    <script src="https://code.highcharts.com/highcharts-more.js"></script>

    <script src="https://code.highcharts.com/themes/grid.js"></script>




    <style>
        .form-container {
            margin-bottom: 20px;
        }
        .form-container label {
            margin-right: 10px;
        }
        .form-container input {
            margin-right: 20px;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <form method="GET" action="">
            <label for="fecha_inicio">Fecha de inicio:</label>
            <input type="datetime-local" id="fecha_inicio" name="fecha_inicio" value="<?php echo date('Y-m-d\TH:i', strtotime($fecha_inicio)); ?>">
            
            <label for="fecha_fin">Fecha de fin:</label>
            <input type="datetime-local" id="fecha_fin" name="fecha_fin" value="<?php echo date('Y-m-d\TH:i', strtotime($fecha_fin)); ?>">
            
            <button type="submit">Filtrar</button>
        </form>
    </div>

    <div id="container" style="min-width: 310px; height: 400px; margin: 0 auto"></div>

    <script type="text/javascript">
    
    
    document.addEventListener('DOMContentLoaded', function () {
    var datos_grafico = <?php echo json_encode($datos_grafico); ?>;
    var series = [];
    var grupos = {};

    // Organizar las series por concepto
    for (var clave in datos_grafico) {
        for (var concepto in datos_grafico[clave]) {
            if (!grupos[concepto]) {
                grupos[concepto] = {
                    name: concepto,
                    series: []
                };
            }
            grupos[concepto].series.push({
                name: clave + ' - ' + concepto,
                data: datos_grafico[clave][concepto],
                visible: concepto === 'Wac' // Activar solo las series de "Estado"

            });
        }
    }

    // Crear las series agrupadas
    for (var grupo in grupos) {
        series.push({
            name: grupos[grupo].name,
            data: [], // No se usan datos aquí, es solo para la leyenda
            linkedTo: ':previous',
            showInLegend: true,
            events: {
                legendItemClick: function () {
                    var grupo = this.name;
                    var todasLasSeries = this.chart.series;

                    // Activar/desactivar todas las series del grupo
                    todasLasSeries.forEach(function (serie) {
                        if (serie.name.includes(grupo)) {
                            if (serie.visible) {
                                serie.hide();
                            } else {
                                serie.show();
                            }
                        }
                    });
                    return false; // Evitar que Highcharts maneje el evento por defecto
                }
            }
        });

        // Agregar las series individuales
        grupos[grupo].series.forEach(function (serie) {
            series.push(serie);
        });
    }

    // Crear el gráfico
    Highcharts.chart('container', {
  
        chart: {
            type: 'line',
            zoomType: 'xy',
            panning: true,
            panKey: 'shift'
        },
        title: {
            text: 'Reles TUYA'
        },
        credits: {
          enabled: false
          },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Tiempo'
            }
        },
        yAxis: {
            title: {
                text: 'Valores'
            }
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
            count: 12,
            text: '12h'
           }, {
            type: 'day',
            count: 1,
            text: '1día'
           }, {
            type: 'all',
            text: 'Todo'
           }],
          selected: 1
          },
        
        
        tooltip: {
          split: true,
          distance: 30,
          padding: 1,
          outside: true,
          shared: true,
          valueDecimals: 2
          },
        navigator: {
          enabled: true // false
          },
        
        plotOptions: {
            series: {
                grouping: true, // Habilitar agrupación de series
                groupPadding: 0.5 // Espaciado entre grupos
            }
        },
        series: series
    });
});
        
    

    </script>
</body>
</html>
