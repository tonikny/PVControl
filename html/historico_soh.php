<?php
$titulo = "Histórico Ciclado Batería";
//include ("cabecera.inc");
require('conexion.php');

// Obtener parámetros - Cargar mes por defecto si no hay rango especificado
$range = isset($_GET['range']) ? $_GET['range'] : 'month';
$batteryAh = isset($_GET['batteryAh']) ? floatval($_GET['batteryAh']) : 1000;
$startDate = isset($_GET['startDate']) ? $_GET['startDate'] : '';
$endDate = isset($_GET['endDate']) ? $_GET['endDate'] : '';

// Calcular fechas según el rango
$endDateCalc = date('Y-m-d');
$startDateCalc = date('Y-m-d');

switch ($range) {
    case '7days':
        $startDateCalc = date('Y-m-d', strtotime('-7 days'));
        break;
    case 'month':
        $startDateCalc = date('Y-m-d', strtotime('-1 month'));
        break;
    case 'quarter':
        $startDateCalc = date('Y-m-d', strtotime('-3 months'));
        break;
    case 'year':
        // Año natural (desde 1 de enero)
        $startDateCalc = date('Y-01-01');
        break;
    case '365days':
        // Últimos 365 días exactos
        $startDateCalc = date('Y-m-d', strtotime('-365 days'));
        break;
    case 'custom':
        $startDateCalc = $startDate ?: '1970-01-01';
        $endDateCalc = $endDate ?: date('Y-m-d');
        break;
    case 'all':
        $startDateCalc = '1970-01-01';
        break;
}

// Consulta SQL para obtener datos y acumulados
$sql = "SELECT s.fecha, s.Ahn, s.Ahp,
        (SELECT SUM(Ahn) FROM soh WHERE fecha <= s.fecha AND fecha >= '$startDateCalc') AS Ahn_acumulado,
        (SELECT SUM(Ahp) FROM soh WHERE fecha <= s.fecha AND fecha >= '$startDateCalc') AS Ahp_acumulado,
        (CASE WHEN s.Ahp > 0 THEN ROUND((s.Ahn/s.Ahp)*100, 2) ELSE NULL END) AS eficiencia_diaria
        FROM soh s
        WHERE fecha BETWEEN '$startDateCalc' AND '$endDateCalc'
        ORDER BY fecha";

if($result = mysqli_query($link, $sql)){
    $i = 0;
    $totalAhn = 0;
    $totalAhp = 0;
    $rawdata = array();
    $eficienciaPromedio = 0;
    $contadorEficiencia = 0;
    
    while($row = mysqli_fetch_assoc($result)) {
        // Convertir fecha a timestamp
        $date = new DateTime($row["fecha"]);
        $row["fecha"] = $date->getTimestamp() * 1000;
        
        // Convertir valores a float
        $row["Ahn"] = (float)$row["Ahn"];
        $row["Ahp"] = (float)$row["Ahp"];
        $row["Ahn_acumulado"] = (float)$row["Ahn_acumulado"];
        $row["Ahp_acumulado"] = (float)$row["Ahp_acumulado"];
        $row["eficiencia_diaria"] = $row["eficiencia_diaria"] !== null ? (float)$row["eficiencia_diaria"] : null;
        
        
        // Guardar datos
        $rawdata[$i] = $row;
        
        // Calcular totales para ciclos
        $totalAhn = round($row['Ahn_acumulado'],2);
        $totalAhp = round($row['Ahp_acumulado'],2);
        
        $i++;
    }
    
    // Calcular número de ciclos
    $cycles = $batteryAh > 0 ? round($totalAhn / $batteryAh, 2) : 0;
    // Calcular eficiencia promedio
    //$eficienciaPromedio = $contadorEficiencia > 0 ? round($eficienciaPromedio / $contadorEficiencia, 2) : 0;
    $eficienciaPromedio = $totalAhp > 0 ? round($totalAhn / $totalAhp * 100 , 2) : 0;
    
    
} else {
    echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

mysqli_close($link);
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $titulo; ?></title>
    <link rel="stylesheet" href="css/menu_2025.css">
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <script src="https://code.highcharts.com/modules/exporting.js"></script>
    <script src="https://code.highcharts.com/modules/export-data.js"></script>
    <script src="https://code.highcharts.com/modules/accessibility.js"></script>
    <style>
        /* Estilos del menú se cargarán desde menu_2025.css */
        
        /* Estilos específicos para esta página */
        .content-wrapper {
            margin-top: 80px; /* Ajuste para el menú fijo */
            padding: 20px;
        }
        .controls {
            margin: 20px 0;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 5px;
        }
        .control-group {
            margin-bottom: 10px;
        }
        label {
            margin-right: 10px;
        }
        #chartContainer {
            width: 100%;
            height: 500px;
            margin-top: 20px;
        }
        .cycles-info {
            margin-top: 10px;
            padding: 10px;
            background: #e9f7ef;
            border-radius: 5px;
            font-weight: bold;
        }
        .highcharts-credits {
            display: none !important;
        }
        .chart-options {
            margin: 10px 0;
            text-align: center;
        }
        .chart-options button {
            margin: 0 5px;
            padding: 5px 15px;
            background: #e0e0e0;
            border: 1px solid #ccc;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .chart-options button:hover {
            background: #d0d0d0;
        }
        .chart-options button.active {
            background: #4CAF50;
            color: white;
            border-color: #3e8e41;
        }
        
        .efficiency-info {
            margin-top: 10px;
            padding: 10px;
            background: #e9f0f7;
            border-radius: 5px;
            font-weight: bold;
        }
        .efficiency-meter {
            display: inline-block;
            width: 100px;
            height: 20px;
            background: linear-gradient(to right, #ff0000, #ffff00, #00ff00);
            position: relative;
            vertical-align: middle;
            margin: 0 10px;
            border-radius: 3px;
        }
        .efficiency-pointer {
            position: absolute;
            top: -5px;
            left: calc(var(--eficiencia) * 1px);
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 10px solid #333;
            transform: translateX(-50%);
        }
    </style>
</head>
<body>
    <!-- Menú de navegación -->
    <div id="navbar"></div>
    
    <!-- Contenido principal -->
    <div class="content-wrapper">
        <h1><?php echo $titulo; ?></h1>
        
        <div class="controls">
            <div class="control-group">
                <label for="batteryAh">Capacidad de Batería (Ah):</label>
                <input type="number" id="batteryAh" value="<?php echo $batteryAh; ?>" min="1" step="1">
                
                <label for="rangeSelector">Rango temporal:</label>
                <select id="rangeSelector">
                    <option value="7days" <?php echo $range == '7days' ? 'selected' : ''; ?>>Últimos 7 días</option>
                    <option value="month" <?php echo $range == 'month' ? 'selected' : ''; ?>>Último mes</option>
                    <option value="quarter" <?php echo $range == 'quarter' ? 'selected' : ''; ?>>Último trimestre</option>
                    <option value="year" <?php echo $range == 'year' ? 'selected' : ''; ?>>Año actual (<?php echo date('Y'); ?>)</option>
                    <option value="365days" <?php echo $range == '365days' ? 'selected' : ''; ?>>Últimos 365 días</option>
                    <option value="all" <?php echo $range == 'all' ? 'selected' : ''; ?>>Todo el histórico</option>
                    <option value="custom" <?php echo $range == 'custom' ? 'selected' : ''; ?>>Personalizado</option>
                </select>
                
                <button id="updateChart">Actualizar Gráfica</button>
            </div>
            
            <div id="dateRangeControls" style="display: <?php echo $range == 'custom' ? 'block' : 'none'; ?>;">
                <label for="startDate">Desde:</label>
                <input type="date" id="startDate" value="<?php echo $startDate; ?>">
                
                <label for="endDate">Hasta:</label>
                <input type="date" id="endDate" value="<?php echo $endDate; ?>">
            </div>
            
            <div class="cycles-info">
                <strong>Resumen:</strong> <?php echo $cycles; ?> Ciclos -> <?php echo $totalAhp; ?> Ah cargados / <?php echo $totalAhn; ?> Ah descargados  ... <?php echo $batteryAh > 0 ? $batteryAh : '?'; ?> Ah batería)

            </div>
        </div>    
        
        <div class="efficiency-info">
            <strong>Eficiencia promedio:</strong> 
            <span id="eficienciaValor"><?php echo $eficienciaPromedio; ?>%</span>
            <div class="efficiency-meter">
                <div class="efficiency-pointer" style="--eficiencia: <?php echo $eficienciaPromedio; ?>"></div>
            </div>
            <span id="eficienciaTexto">
                <?php 
                if($eficienciaPromedio > 95) echo "Excelente";
                elseif($eficienciaPromedio > 90) echo "Buena";
                elseif($eficienciaPromedio > 85) echo "Aceptable";
                else echo "Mejorable";
                ?>
            </span>
        </div>

        
        
        <div class="chart-options">
            <button id="btnColumn" class="active">Columnas</button>
            <button id="btnArea">Áreas</button>
            <button id="btnLine">Líneas</button>
        </div>
        
        <div id="chartContainer"></div>
    </div>

    <!-- Scripts -->
    <script src="script/menu.js"></script>
    <script>
        // Datos para la gráfica
        const chartData = <?php echo isset($rawdata) ? json_encode($rawdata) : '[]'; ?>;
        const batteryAh = <?php echo $batteryAh; ?>;
        const cycles = <?php echo $cycles; ?>;
        
        // Variable global para el objeto chart
        let chart;
        
        // Función para guardar en localStorage
        function saveBatteryAh(value) {
            localStorage.setItem('batteryAh', value);
        }
        
        // Función para cargar de localStorage
        function loadBatteryAh() {
            const savedValue = localStorage.getItem('batteryAh');
            return savedValue ? parseFloat(savedValue) : <?php echo $batteryAh; ?>;
        }
        
        // Determinar el mejor tipo de gráfico inicial
        function getInitialChartType() {
            const dayCount = chartData.length;
            if (dayCount > 90) return 'line';
            return 'column';
        }
        
        // Crear gráfica con visualización optimizada
        function createChart1() {
            const initialType = getInitialChartType();
            const isLongRange = chartData.length > 30;
            
            // Configuración base
            const options = {
                chart: {
                    type: initialType,
                    zoomType: 'xy'
                },
                title: {
                    text: `Histórico de Ciclado de Batería - ${cycles} ciclos completos`
                },
                credits: {
                    enabled: false
                },
                xAxis: {
                    type: 'datetime',
                    title: {
                        text: 'Fecha'
                    },
                    crosshair: true,
                    dateTimeLabelFormats: {
                        day: '%e %b %Y',
                        month: '%b %Y',
                        year: '%Y'
                    }
                },
                yAxis: [{
                    title: {
                        text: 'Amperios hora (Ah)'
                    },
                    min: 0,
                    labels: {
                        format: '{value} Ah'
                    }
                }, {
                    title: {
                        text: 'Acumulado (Ah)'
                    },
                    opposite: true,
                    min: 0,
                    labels: {
                        format: '{value} Ah'
                    }
                }],
                tooltip: {
                    shared: true,
                    useHTML: true,
                    headerFormat: '<small>{point.key:%A, %e %b %Y}</small><table>',
                    pointFormat: '<tr><td style="color: {series.color}">{series.name}: </td>' +
                                '<td style="text-align: right"><b>{point.y:.2f} ' + 
                                '{series.options.tooltip.valueSuffix || "Ah"}</b></td></tr>',
                    footerFormat: '</table>',
                    valueDecimals: 2
                },
                plotOptions: {
                    column: {
                        pointPadding: isLongRange ? 0.05 : 0.1,
                        borderWidth: 0,
                        groupPadding: isLongRange ? 0.05 : 0.1,
                        pointWidth: isLongRange ? 5 : null
                    },
                    line: {
                        marker: {
                            radius: isLongRange ? 3 : 4
                        }
                    }
                },
                series: [{
                    name: 'Ah descargados (Ahn)',
                    type: initialType,
                    data: chartData.map(item => [item.fecha, item.Ahn]),
                    color: '#FF5733',
                    yAxis: 0,
                    tooltip: {
                        valueSuffix: ' Ah',
                        valueDecimals: 2
                    }
                }, {
                    name: 'Ah cargados (Ahp)',
                    type: initialType,
                    data: chartData.map(item => [item.fecha, item.Ahp]),
                    color: '#33FF57',
                    yAxis: 0,
                    tooltip: {
                        valueSuffix: ' Ah',
                        valueDecimals: 2
                    }
                }, {
                    name: 'Ahn acumulado',
                    type: 'spline',
                    data: chartData.map((item, index) => {
                        let acumulado = 0;
                        for(let i = 0; i <= index; i++) {
                            acumulado += chartData[i].Ahn;
                        }
                        return [item.fecha, acumulado];
                    }),
                    yAxis: 1,
                    color: '#FF0000',
                    dashStyle: 'shortdot',
                    tooltip: {
                        valueSuffix: ' Ah',
                        valueDecimals: 2
                    }
                }, {
                    name: 'Ahp acumulado',
                    type: 'spline',
                    data: chartData.map((item, index) => {
                        let acumulado = 0;
                        for(let i = 0; i <= index; i++) {
                            acumulado += chartData[i].Ahp;
                        }
                        return [item.fecha, acumulado];
                    }),
                    yAxis: 1,
                    color: '#00AA00',
                    dashStyle: 'shortdot',
                    tooltip: {
                        valueSuffix: ' Ah',
                        valueDecimals: 2
                    }
                }]
            };
            
            chart = Highcharts.chart('chartContainer', options);
        }

        function createChart() {
            const initialType = getInitialChartType();
            const isLongRange = chartData.length > 30;
            
            // Configuración base
            const options = {
                chart: {
                    type: initialType,
                    zoomType: 'xy'
                },
                title: {
                    text: `Histórico de Ciclado de Batería - ${cycles} ciclos completos`
                },
                credits: {
                    enabled: false
                },
                xAxis: {
                    type: 'datetime',
                    title: {
                        text: 'Fecha'
                    },
                    crosshair: true,
                    dateTimeLabelFormats: {
                        day: '%e %b %Y',
                        month: '%b %Y',
                        year: '%Y'
                    }
                },
                yAxis: [{
                    title: {
                        text: 'Amperios hora (Ah)'
                    },
                    min: 0,
                    labels: {
                        format: '{value} Ah'
                    }
                }, {
                    title: {
                        text: 'Acumulado (Ah)'
                    },
                    opposite: true,
                    min: 0,
                    labels: {
                        format: '{value} Ah'
                    }
                }, {
                    title: {
                        text: 'Eficiencia (%)'
                    },
                    opposite: false,
                    min: 0,
                    max: 200,
                    labels: {
                        format: '{value}%'
                    },
                    gridLineWidth: 0,
                    showEmpty: false

                }],
                tooltip: {
                    shared: true,
                    useHTML: true,
                    headerFormat: '<small>{point.key:%A, %e %b %Y}</small><table>',
//                    pointFormat: '<tr><td style="color: {series.color}">{series.name}: </td>' +
//                                '<td style="text-align: right"><b>{point.y:.2f} Ah</b></td></tr>',
                   

                    pointFormat: '<tr><td style="color: {series.color}">{series.name}: </td>' +
                                '<td style="text-align: right"><b>{point.y:.2f} </b></td></tr>',



                   footerFormat: '</table>'
                },
                plotOptions: {
                    column: {
                        pointPadding: isLongRange ? 0.05 : 0.1,
                        borderWidth: 0,
                        groupPadding: isLongRange ? 0.05 : 0.1,
                        pointWidth: isLongRange ? 5 : null
                    },
                    line: {
                        marker: {
                            radius: isLongRange ? 3 : 4
                        }
                    },
                    areaspline: {
                        fillOpacity: 0.4,
                        marker: {
                            enabled: false
                        }
                    }
                },
                series: [{
                    name: 'Ah descargados (Ahn)',
                    type: initialType,
                    data: chartData.map(item => [item.fecha, item.Ahn]),
                    color: '#FF5733',
                    yAxis: 0,
                    tooltip: {
                        valueDecimals: 2
                    }
                }, {
                    name: 'Ah cargados (Ahp)',
                    type: initialType,
                    data: chartData.map(item => [item.fecha, item.Ahp]),
                    color: '#33FF57',
                    yAxis: 0,
                    tooltip: {
                        valueDecimals: 2
                    }
                }, {
                    name: 'Ahn acumulado',
                    type: 'spline',
                    data: chartData.map(item => [item.fecha, item.Ahn_acumulado]),
                    yAxis: 1,
                    color: '#FF0000',
                    dashStyle: 'shortdot',
                    tooltip: {
                        valueDecimals: 2
                    }
                }, {
                    name: 'Ahp acumulado',
                    type: 'spline',
                    data: chartData.map(item => [item.fecha, item.Ahp_acumulado]),
                    yAxis: 1,
                    color: '#00AA00',
                    dashStyle: 'shortdot',
                    tooltip: {
                        valueDecimals: 2
                    }
                }, {
                    name: 'Eficiencia diaria',
                    type: 'line',
                    data: chartData.map(item => [item.fecha, item.eficiencia_diaria]),
                    yAxis: 2,
                    color: '#6633CC',
                    marker: {
                        symbol: 'circle',
                        radius: 3
                    },
                    tooltip: {
                        valueSuffix: '%'
                    }
                }]
            };
            
            // Ajustes específicos para áreas
            if (initialType === 'areaspline') {
                options.series[0].fillOpacity = 0.4;
                options.series[1].fillOpacity = 0.4;
            }
            
            chart = Highcharts.chart('chartContainer', options);
            
            // Configurar el botón activo inicial
            setActiveButton(initialType);
        }
        
        // Establecer el botón activo
        function setActiveButton(type) {
            // Mapeo de tipos a IDs de botón
            const buttonMap = {
                'column': 'btnColumn',
                'areaspline': 'btnArea',
                'line': 'btnLine'
            };
            
            // Remover activo de todos los botones
            document.querySelectorAll('.chart-options button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Activar el botón correspondiente
            const activeButton = document.getElementById(buttonMap[type]);
            if (activeButton) {
                activeButton.classList.add('active');
            }
        }
        
        // Cambiar tipo de gráfico
        function changeChartType(type) {
            // Actualizar el botón activo
            setActiveButton(type);
            
            // Actualizar series (solo las dos primeras)
            chart.series.forEach((serie, index) => {
                if (index < 2) {
                    const newOptions = {
                        type: type
                    };
                    
                    if (type === 'areaspline') {
                        newOptions.fillOpacity = 0.4;
                        newOptions.marker = { enabled: false };
                    }
                    
                    serie.update(newOptions, false);
                }
            });
            
            chart.redraw();
        }
        
        // Actualizar gráfica
        function updateChart() {
            const range = document.getElementById('rangeSelector').value;
            const batteryAh = parseFloat(document.getElementById('batteryAh').value) || 1000;
            let url = `historico_soh.php?range=${range}&batteryAh=${batteryAh}`;
            
            if (range === 'custom') {
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                if (startDate && endDate) {
                    url += `&startDate=${startDate}&endDate=${endDate}`;
                }
            }
            
            window.location.href = url;
        }
        
        // Inicialización
        document.addEventListener('DOMContentLoaded', function() {
            // Cargar valor guardado de la batería
            const savedBatteryAh = loadBatteryAh();
            if (savedBatteryAh && !<?php echo isset($_GET['batteryAh']) ? 'true' : 'false'; ?>) {
                document.getElementById('batteryAh').value = savedBatteryAh;
            }
            
            // Configurar fecha mínima/máxima para los datepickers
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('endDate').max = today;
            document.getElementById('startDate').max = today;
            
            // Verificar y mostrar datos
            if (chartData && chartData.length > 0) {
                createChart();
            } else {
                document.getElementById('chartContainer').innerHTML = '<p>No hay datos disponibles para el rango seleccionado.</p>';
            }
            
            // Controlador del selector de rango
            document.getElementById('rangeSelector').addEventListener('change', function() {
                const range = this.value;
                if (range === 'custom') {
                    document.getElementById('dateRangeControls').style.display = 'block';
                } else {
                    document.getElementById('dateRangeControls').style.display = 'none';
                }
            });
            
            // Controlador del botón actualizar
            document.getElementById('updateChart').addEventListener('click', function() {
                saveBatteryAh(document.getElementById('batteryAh').value);
                updateChart();
            });
            
            // Controladores para botones de tipo de gráfico
            document.getElementById('btnColumn').addEventListener('click', function() {
                changeChartType('column');
            });
            document.getElementById('btnArea').addEventListener('click', function() {
                changeChartType('areaspline');
            });
            document.getElementById('btnLine').addEventListener('click', function() {
                changeChartType('line');
            });
        });
    </script>
</body>
</html>