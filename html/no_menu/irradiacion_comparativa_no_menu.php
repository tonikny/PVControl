<?php
// Definir el SQL y el título para este gráfico específico
$titulo = "Predicción de Irradiación Solar - Comparativa Fuentes";

// Obtener el número de días desde el parámetro GET o usar 15 por defecto
$dias = isset($_GET['dias']) ? intval($_GET['dias']) : 15;

// Obtener nombres de tablas desde parámetros GET o usar valores por defecto
$tabla1 = isset($_GET['tabla1']) ? $_GET['tabla1'] : 'TABLA_IRRADIACION';
$tabla2 = isset($_GET['tabla2']) ? $_GET['tabla2'] : 'TABLA_IRRADIACION1';

// Procesar el formulario si se envió
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $tabla1 = $_POST['tabla1'];
    $tabla2 = $_POST['tabla2'];
    
    // Redirigir con los nuevos parámetros
    header("Location: ?dias=$dias&tabla1=" . urlencode($tabla1) . "&tabla2=" . urlencode($tabla2));
    exit;
}

// Consulta para obtener datos reales de la tabla datos_c incluyendo SOC
$sql_real = "SELECT 
                UNIX_TIMESTAMP(DATE_FORMAT(Tiempo, '%Y-%m-%d %H:00:00'))*1000 as Tiempo_hora,
                AVG(Wplaca) / 1000 as Kwh_placa_horario,
                AVG(SOC) as SOC_medio
            FROM datos_c 
            WHERE Tiempo >= (NOW() - INTERVAL $dias DAY)
            GROUP BY DATE_FORMAT(Tiempo, '%Y-%m-%d %H:00:00')
            ORDER BY Tiempo_hora";

// Consultas originales para las tablas de predicción (sin Kwh_placa)
$sql1 = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, Wirradiacion
        FROM $tabla1 WHERE Tiempo >= (NOW() - INTERVAL $dias DAY)
        ORDER BY Tiempo";

$sql2 = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, Wirradiacion
        FROM $tabla2 WHERE Tiempo >= (NOW() - INTERVAL $dias DAY)
        ORDER BY Tiempo";

$rangeSelectorOptions = [
    'buttons' => [
        ['type' => 'day', 'count' => 3, 'text' => '3d'],
        ['type' => 'day', 'count' => 10, 'text' => '10d'],
        ['type' => 'day', 'count' => 15, 'text' => '15d'],
        ['type' => 'all', 'text' => 'Todo']
    ],
    'selected' => 1, // Por defecto seleccionado 10 días
    'inputEnabled' => false
];

// Conexión a la base de datos
require('../conexion.php');

// Variables que se deben definir en el archivo específico
if (!isset($sql1) || !isset($sql2) || !isset($titulo)) {
    die("Debe definir las consultas SQL y el título.");
}

// Primero obtener los datos reales de datos_c y crear arrays asociativos por timestamp
$result_real = $link->query($sql_real);
$datos_reales_kwh = [];
$datos_reales_soc = [];

if ($result_real->num_rows > 0) {
    while ($row = $result_real->fetch_assoc()) {
        $timestamp = (int)$row['Tiempo_hora'];
        $datos_reales_kwh[$timestamp] = round((float)$row['Kwh_placa_horario'], 1);
        $datos_reales_soc[$timestamp] = round((float)$row['SOC_medio'], 1);
    }
}

// Obtener datos de la primera tabla y combinar con datos reales
$result1 = $link->query($sql1);
$campos = ['Tiempo', 'Wirradiacion', 'Kwh_placa'];
$d1_ = array_fill_keys($campos, []);

if ($result1->num_rows > 0) {
    while ($row = $result1->fetch_assoc()) {
        $timestamp = (int)$row['Tiempo'];
        
        // Agregar tiempo y Wirradiacion
        $d1_['Tiempo'][] = $timestamp;
        $d1_['Wirradiacion'][] = (float)$row['Wirradiacion'];
        
        // Agregar Kwh_placa desde datos_c si existe, sino 0
        if (isset($datos_reales_kwh[$timestamp])) {
            $d1_['Kwh_placa'][] = $datos_reales_kwh[$timestamp];
        } else {
            $d1_['Kwh_placa'][] = 0;
        }
    }
} else {
    echo "0 resultados en $tabla1<br>";
}

// Obtener datos de la segunda tabla y combinar con datos reales
$result2 = $link->query($sql2);
$d2_ = array_fill_keys($campos, []);

if ($result2->num_rows > 0) {
    while ($row = $result2->fetch_assoc()) {
        $timestamp = (int)$row['Tiempo'];
        
        // Agregar tiempo y Wirradiacion
        $d2_['Tiempo'][] = $timestamp;
        $d2_['Wirradiacion'][] = (float)$row['Wirradiacion'];
        
        // Agregar Kwh_placa desde datos_c si existe, sino 0
        if (isset($datos_reales_kwh[$timestamp])) {
            $d2_['Kwh_placa'][] = $datos_reales_kwh[$timestamp];
        } else {
            $d2_['Kwh_placa'][] = 0;
        }
    }
} else {
    echo "0 resultados en $tabla2<br>";
}

// Preparar datos del SOC para el gráfico
$soc_data = [];
foreach ($datos_reales_soc as $timestamp => $soc) {
    $soc_data[] = [$timestamp, $soc];
}

$link->close();
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title><?php echo $titulo; ?></title>
	
	<script src="/Parametros_Web_DIST.js"></script>
    <script src="/Parametros_Web.js"></script>
	
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://code.highcharts.com/stock/highstock.js"></script>
    <script src="https://code.highcharts.com/highcharts.js"></script>
	<script src="https://code.highcharts.com/themes/grid.js"></script>
    
    <style>
        .header-panel {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header-panel h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }
        .header-panel .subtitle {
            margin: 5px 0 0 0;
            font-size: 16px;
            opacity: 0.9;
        }
        .control-panel {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .control-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .control-group label {
            font-weight: bold;
            color: #495057;
            margin: 0;
        }
        .control-group select, .control-group input {
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background: white;
            font-size: 14px;
        }
        .control-group input {
            min-width: 150px;
        }
        .buttons-group {
            display: flex;
            gap: 10px;
        }
        .help-button, .home-button, .config-button {
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.3s ease;
        }
        .help-button {
            background: #6c757d;
            color: white;
        }
        .help-button:hover {
            background: #5a6268;
            transform: translateY(-1px);
        }
        .home-button {
            background: #28a745;
            color: white;
        }
        .home-button:hover {
            background: #218838;
            transform: translateY(-1px);
        }
        .config-button {
            background: #ffc107;
            color: #212529;
        }
        .config-button:hover {
            background: #e0a800;
            transform: translateY(-1px);
        }
        .stats-panel {
            background: #e9ecef;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 14px;
            border-left: 4px solid #007bff;
        }
        .chart-container {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Modal styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 0;
            border-radius: 10px;
            width: 90%;
            max-width: 700px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            animation: modalSlideIn 0.3s ease-out;
        }
        @keyframes modalSlideIn {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .modal-header h2 {
            margin: 0;
            font-size: 24px;
        }
        .close-button {
            background: none;
            border: none;
            color: white;
            font-size: 28px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .close-button:hover {
            opacity: 0.8;
        }
        .modal-body {
            padding: 25px;
            max-height: 60vh;
            overflow-y: auto;
        }
        .info-section {
            margin-bottom: 25px;
        }
        .info-section h3 {
            color: #495057;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
            margin-bottom: 15px;
            font-size: 18px;
        }
        .info-section ul {
            padding-left: 20px;
            margin: 0;
        }
        .info-section li {
            margin-bottom: 8px;
            line-height: 1.5;
        }
        .unit-note {
            background: #fff3cd;
            padding: 12px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }
        .source-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 8px;
        }
        .badge-real { background: #2c3e50; color: white; }
        .badge-tutiempo { background: #e74c3c; color: white; }
        .badge-openmeteo { background: #3498db; color: white; }
        .badge-soc { background: #ff6b6b; color: white; }
        
        /* Form styles */
        .config-form {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #495057;
        }
        .form-group input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
        }
        .form-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 20px;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background: #007bff;
            color: white;
        }
        .btn-primary:hover {
            background: #0056b3;
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #545b62;
        }
    </style>
</head>
<body>

<!-- Panel de cabecera con título -->
<div class="header-panel">
    <h1>🌞 Predicción de Irradiación Solar</h1>
    <div class="subtitle">Comparativa entre Tutiempo.net y OpenMeteo vs Producción Real + SOC Baterías</div>
</div>

<!-- Panel de control compacto -->
<div class="control-panel">
    <div class="control-group">
        <label for="diasConsulta">Período de análisis:</label>
        <select id="diasConsulta" onchange="cambiarDias()">
            <option value="7" <?php echo $dias == 7 ? 'selected' : ''; ?>>7 días</option>
            <option value="15" <?php echo $dias == 15 ? 'selected' : ''; ?>>15 días</option>
            <option value="30" <?php echo $dias == 30 ? 'selected' : ''; ?>>30 días</option>
            <option value="60" <?php echo $dias == 60 ? 'selected' : ''; ?>>60 días</option>
        </select>
    </div>
    <div class="buttons-group">
        <button class="config-button" onclick="abrirConfiguracion()">
            ⚙️ Configurar Tablas
        </button>
        <button class="home-button" onclick="irAInicio()">
            🏠 Inicio
        </button>
        <button class="help-button" onclick="abrirAyuda()">
            ? Ayuda
        </button>
    </div>
</div>

<!-- Modal de configuración de tablas -->
<div id="modalConfiguracion" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>⚙️ Configurar Nombres de Tablas</h2>
            <button class="close-button" onclick="cerrarConfiguracion()">&times;</button>
        </div>
        <div class="modal-body">
            <form method="POST" class="config-form">
                <div class="form-group">
                    <label for="tabla1">Nombre de la Tabla 1 (Predicción tutiempo.net):</label>
                    <input type="text" id="tabla1" name="tabla1" value="<?php echo htmlspecialchars($tabla1); ?>" required>
                    <small>Tabla que contiene los datos de predicción de tutiempo.net</small>
                </div>
                <div class="form-group">
                    <label for="tabla2">Nombre de la Tabla 2 (Predicción openmeteo):</label>
                    <input type="text" id="tabla2" name="tabla2" value="<?php echo htmlspecialchars($tabla2); ?>" required>
                    <small>Tabla que contiene los datos de predicción de openmeteo</small>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="cerrarConfiguracion()">Cancelar</button>
                    <button type="submit" class="btn btn-primary">Aplicar Cambios</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Modal de ayuda -->
<div id="modalAyuda" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>📊 Información del Análisis</h2>
            <button class="close-button" onclick="cerrarAyuda()">&times;</button>
        </div>
        <div class="modal-body">
            <div class="info-section">
                <h3>Configuración de Tablas</h3>
                <ul>
                    <li><strong>Tabla 1:</strong> Contiene los datos de predicción tutiempo.net</li>
                    <li><strong>Tabla 2:</strong> Contiene los datos de predicción openmeteo</li>
                    <li><strong>Formato:</strong> Ambas tablas deben tener la misma estructura de columnas</li>
                </ul>
            </div>
            <div class="info-section">
                <h3>Fuentes de Datos</h3>
                <ul>
                    <li>
                        <span class="source-badge badge-real">Producción Real</span>
                        <strong>Datos medidos:</strong> Generación real (tabla 'datos_c')
                    </li>
                    <li>
                        <span class="source-badge badge-soc">SOC Baterías</span>
                        <strong>Estado de carga:</strong> Porcentaje de carga de las baterías (0-100%)
                    </li>
                    <li>
                        <span class="source-badge badge-tutiempo">Tutiempo.net</span>
                        <strong>Predicción meteorológica:</strong> w/m2 * factor definido en Parametros_FV.py
                    </li>
                    <li>
                        <span class="source-badge badge-openmeteo">OpenMeteo</span>
                        <strong>Predicción meteorológica:</strong> Descarga segun definido en Parametros_FV.py
                    </li>
                </ul>
            </div>

            <div class="info-section">
                <h3>Unidades de Medida</h3>
                <div class="unit-note">
                    <strong>⚡ Conversión de unidades para comparación correcta:</strong><br>
                    • <strong>Gráfico principal:</strong> Todas las series en Watios (W)<br>
                    • <strong>Producción real:</strong> Convertida de KWh a W (KWh × 1000 = W)<br>
                    • <strong>SOC Baterías:</strong> Porcentaje (0-100%) en eje secundario<br>
                    • <strong>Gráfico diario:</strong> Totales en KWh para mejor legibilidad
                </div>
                <ul>
                    <li><strong>Watios (W):</strong> Potencia instantánea - ideal para comparación horaria</li>
                    <li><strong>KiloWatios-hora (KWh):</strong> Energía total - ideal para resúmenes diarios</li>
                    <li><strong>SOC (%):</strong> Estado de carga de las baterías - ayuda a identificar limitaciones</li>
                </ul>
            </div>

            <div class="info-section">
                <h3>Funcionalidades</h3>
                <ul>
                    <li><strong>Zoom:</strong> Haz clic y arrastra en los gráficos para ampliar</li>
                    <li><strong>Navegador:</strong> Usa la barra inferior para navegar en el tiempo</li>
                    <li><strong>Leyenda:</strong> Haz clic en los nombres para mostrar/ocultar series</li>
                    <li><strong>Tooltips:</strong> Pasa el cursor sobre los datos para ver valores exactos</li>
                    <li><strong>SOC:</strong> Ayuda a identificar cuando la producción se limita por baterías llenas</li>
                </ul>
            </div>

            <div class="info-section">
                <h3>Estadísticas de Precisión</h3>
                <ul>
                    <li><strong>Error medio absoluto:</strong> Diferencia promedio en Watios entre predicción y realidad</li>
                    <li><strong>Error porcentual:</strong> Porcentaje de error respecto a la producción real</li>
                    <li><strong>Objetivo:</strong> Identificar qué fuente ofrece predicciones más precisas</li>
                    <li><strong>SOC:</strong> Analizar impacto del estado de baterías en la producción real</li>
                </ul>
            </div>
        </div>
    </div>
</div>

<!-- Gráfico principal de series temporales -->
<div class="chart-container">
    <div id="container" style="width:100%; height:500px;"></div>
</div>

<!-- Gráfico de columnas diarias -->
<div class="chart-container">
    <div id="container-daily" style="width:100%; height:450px;"></div>
</div>

<div id="statsPanel" class="stats-panel">
    <!-- Aquí se mostrarán las estadísticas -->
</div>

<script>
// Datos del servidor en formato JSON
const campos = <?php echo json_encode($campos); ?>;
const d1_ = <?php echo json_encode($d1_); ?>; // Datos de Tabla 1
const d2_ = <?php echo json_encode($d2_); ?>; // Datos de Tabla 2
const soc_data = <?php echo json_encode($soc_data); ?>; // Datos SOC

// Variables globales
let graficaPrincipal, graficaDiaria;

// Función para ir a la página principal
function irAInicio() {
    window.location.href = '/';
}

// Funciones para el modal de configuración
function abrirConfiguracion() {
    document.getElementById('modalConfiguracion').style.display = 'block';
}

function cerrarConfiguracion() {
    document.getElementById('modalConfiguracion').style.display = 'none';
}

// Funciones para el modal de ayuda
function abrirAyuda() {
    document.getElementById('modalAyuda').style.display = 'block';
}

function cerrarAyuda() {
    document.getElementById('modalAyuda').style.display = 'none';
}

// Cerrar modales al hacer clic fuera del contenido
window.onclick = function(event) {
    const modalConfig = document.getElementById('modalConfiguracion');
    const modalAyuda = document.getElementById('modalAyuda');
    
    if (event.target === modalConfig) {
        cerrarConfiguracion();
    }
    if (event.target === modalAyuda) {
        cerrarAyuda();
    }
}

// Cerrar modales con tecla ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        cerrarConfiguracion();
        cerrarAyuda();
    }
});

// Función para cambiar el número de días y recargar la página
function cambiarDias() {
    const dias = document.getElementById('diasConsulta').value;
    const url = new URL(window.location.href);
    url.searchParams.set('dias', dias);
    window.location.href = url.toString();
}

// Función para convertir KWh a W (asumiendo datos horarios)
function convertirKwhAW(kwh) {
    return kwh * 1000; // 1 KWh = 1000 W para datos horarios
}

// Función para calcular totales diarios en KWh
function calcularTotalesDiarios(tiempos, valoresWatios) {
    const datosPorDia = {};
    
    // Sumar los valores horarios para obtener el total diario en Wh, luego convertir a KWh
    tiempos.forEach((tiempo, index) => {
        const fecha = new Date(tiempo);
        const dia = new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate()).getTime();
        const valorWh = valoresWatios[index]; // Ya está en W, que equivale a Wh para datos horarios
        
        if (!datosPorDia[dia]) {
            datosPorDia[dia] = 0;
        }
        
        datosPorDia[dia] += valorWh;
    });
    
    // Convertir a array y a KWh (de Wh a KWh)
    return Object.keys(datosPorDia).map(dia => {
        return {
            tiempo: parseInt(dia),
            valor: datosPorDia[dia] / 1000 // Convertir Wh a KWh
        };
    }).sort((a, b) => a.tiempo - b.tiempo);
}

// Función para crear las series del gráfico principal (todo en W)
function crearSeriesPrincipal() {
    return [
        // Producción real convertida a W
        {
            name: 'Producción Real (W)',
            type: 'spline',
            yAxis: 0,
            visible: true,
            color: '#2c3e50',
            lineWidth: 3,
            marker: { enabled: false },
            tooltip: {
                valueSuffix: ' W',
                valueDecimals: 0,
            },
            data: d1_['Kwh_placa'].map((value, i) => [d1_['Tiempo'][i], convertirKwhAW(value)]),
            zIndex: 5
        },
        
        // Previsión Tutiempo.net en W
        {
            name: 'Tutiempo.net - Predicción (W)',
            type: 'spline',
            yAxis: 0,
            visible: true,
            color: '#e74c3c',
            dashStyle: 'dash',
            tooltip: {
                valueSuffix: ' W',
                valueDecimals: 0,
            },
            data: d1_['Wirradiacion'].map((value, i) => [d1_['Tiempo'][i], value]),
        },
        
        // Previsión Openmeteo en W
        {
            name: 'Openmeteo - Predicción (W)',
            type: 'spline',
            yAxis: 0,
            visible: true,
            color: '#3498db',
            dashStyle: 'dash',
            tooltip: {
                valueSuffix: ' W',
                valueDecimals: 0,
            },
            data: d2_['Wirradiacion'].map((value, i) => [d2_['Tiempo'][i], value]),
        },
        
        // SOC Baterías en eje secundario
        {
            name: 'SOC Baterías (%)',
            type: 'line',
            yAxis: 1,
            visible: true,
            color: '#FF6B6B',
            lineWidth: 2,
            marker: { enabled: false },
            tooltip: {
                valueSuffix: ' %',
                valueDecimals: 1,
            },
            data: soc_data,
            zIndex: 1
        }
    ];
}

// Función para crear series del gráfico diario (en KWh para mejor legibilidad)
function crearSeriesDiarias() {
    // Calcular totales diarios en KWh
    const realDiario = calcularTotalesDiarios(d1_['Tiempo'], d1_['Kwh_placa'].map(kwh => convertirKwhAW(kwh)));
    const tabla1Diario = calcularTotalesDiarios(d1_['Tiempo'], d1_['Wirradiacion']);
    const tabla2Diario = calcularTotalesDiarios(d2_['Tiempo'], d2_['Wirradiacion']);
    
    return [
        {
            name: 'Producción Real',
            type: 'column',
            color: 'rgba(44, 62, 80, 0.9)',
            borderColor: '#2c3e50',
            borderWidth: 1,
            data: realDiario.map(item => [item.tiempo, item.valor]),
            tooltip: {
                valueSuffix: ' KWh',
                valueDecimals: 1
            },
            dataLabels: {
                enabled: true,
                formatter: function() {
                    return this.y > 0.1 ? this.y.toFixed(1) : '';
                },
                style: {
                    fontSize: '10px',
                    fontWeight: 'bold',
                    color: '#2c3e50',
                    textOutline: '1px white'
                },
                verticalAlign: 'top',
                y: -5
            },
            pointPadding: 0.15,
            groupPadding: 0.1,
            pointWidth: 15
        },
        {
            name: 'tutiempo.net - Predicción',
            type: 'column',
            color: 'rgba(231, 76, 60, 0.7)',
            borderColor: '#e74c3c',
            borderWidth: 1,
            data: tabla1Diario.map(item => [item.tiempo, item.valor]),
            tooltip: {
                valueSuffix: ' KWh',
                valueDecimals: 1
            },
            dataLabels: {
                enabled: true,
                formatter: function() {
                    return this.y > 0.1 ? this.y.toFixed(1) : '';
                },
                style: {
                    fontSize: '10px',
                    fontWeight: 'bold',
                    color: '#e74c3c',
                    textOutline: '1px white'
                },
                verticalAlign: 'bottom',
                y: 5
            },
            pointPadding: 0.3,
            groupPadding: 0.2,
            pointWidth: 15
        },
        {
            name: 'openmeteo - Predicción',
            type: 'column',
            color: 'rgba(52, 152, 219, 0.7)',
            borderColor: '#3498db',
            borderWidth: 1,
            data: tabla2Diario.map(item => [item.tiempo, item.valor]),
            tooltip: {
                valueSuffix: ' KWh',
                valueDecimals: 1
            },
            dataLabels: {
                enabled: true,
                formatter: function() {
                    return this.y > 0.1 ? this.y.toFixed(1) : '';
                },
                style: {
                    fontSize: '10px',
                    fontWeight: 'bold',
                    color: '#3498db',
                    textOutline: '1px white'
                },
                verticalAlign: 'top',
                y: -20
            },
            pointPadding: 0.45,
            groupPadding: 0.3,
            pointWidth: 15
        }
    ];
}

// Función para calcular y mostrar estadísticas (todo en W)
function calcularEstadisticas() {
    let diffTabla1 = [];
    let diffTabla2 = [];
    let diffTabla1Rel = [];
    let diffTabla2Rel = [];
    
    // Calcular diferencias absolutas en W
    d1_['Wirradiacion'].forEach((value, i) => {
        const produccionW = convertirKwhAW(d1_['Kwh_placa'][i]);
        if (produccionW > 0) {
            diffTabla1.push(Math.abs(value - produccionW));
            diffTabla1Rel.push(Math.abs((value - produccionW) / produccionW * 100));
        }
    });
    
    d2_['Wirradiacion'].forEach((value, i) => {
        const tiempo = d2_['Tiempo'][i];
        const index = d1_['Tiempo'].indexOf(tiempo);
        if (index !== -1) {
            const produccionW = convertirKwhAW(d1_['Kwh_placa'][index]);
            if (produccionW > 0) {
                diffTabla2.push(Math.abs(value - produccionW));
                diffTabla2Rel.push(Math.abs((value - produccionW) / produccionW * 100));
            }
        }
    });
    
    const mediaTabla1 = diffTabla1.reduce((a, b) => a + b, 0) / diffTabla1.length;
    const mediaTabla2 = diffTabla2.reduce((a, b) => a + b, 0) / diffTabla2.length;
    const mediaRelTabla1 = diffTabla1Rel.reduce((a, b) => a + b, 0) / diffTabla1Rel.length;
    const mediaRelTabla2 = diffTabla2Rel.reduce((a, b) => a + b, 0) / diffTabla2Rel.length;
    
    // Mostrar estadísticas en el panel
    const statsPanel = document.getElementById('statsPanel');
    statsPanel.innerHTML = `
        <strong>📈 Estadísticas de Precisión (en Watios):</strong><br>
        <strong>Tabla 1 (<?php echo $tabla1; ?>):</strong> Error medio: ${mediaTabla1.toFixed(0)}W (${mediaRelTabla1.toFixed(1)}%)<br>
        <strong>Tabla 2 (<?php echo $tabla2; ?>):</strong> Error medio: ${mediaTabla2.toFixed(0)}W (${mediaRelTabla2.toFixed(1)}%)<br>
        <em>Nota: El SOC de baterías ayuda a identificar cuando la producción real se limita por baterías llenas</em>
    `;
    
    return { mediaTabla1, mediaTabla2, mediaRelTabla1, mediaRelTabla2 };
}

// Función para calcular el rango inicial (desde anteayer hasta 7 días después)
function calcularRangoInicial() {
    const ahora = new Date().getTime();
    const dia =  24 * 60 * 60 * 1000; // 1 dia
    const dosDiasMs = 2 * 24 * 60 * 60 * 1000; // 2 días en milisegundos (anteayer)
    const sieteDiasMs = 7 * 24 * 60 * 60 * 1000; // 7 días en milisegundos
    const extremoInicial = ahora - 4 * dia; //dosDiasMs;
    const extremoFinal = ahora + 5 * dia; // sieteDiasMs;
    
    return { extremoInicial, extremoFinal };
}

// Función para inicializar el gráfico principal con ventana centrada
function inicializarGraficoPrincipal() {
    const series = crearSeriesPrincipal();
    const { extremoInicial, extremoFinal } = calcularRangoInicial();
    const dia =  24 * 60 * 60 * 1000; // 1 dia
    
    Highcharts.setOptions({
        global: {
          useUTC: false
        },
        time: {
            timezone: zona_horaria
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

    graficaPrincipal = Highcharts.stockChart('container', {
        chart: {
            zoomType: 'xy',
            alignTicks: false,
            panning: true,
            panKey: 'shift'
        },
        
        title: {
            text: 'Comparativa en Tiempo Real - Predicción vs Producción Real + SOC Baterías'
        },
        
        credits: {
            enabled: false
        },
        
        yAxis: [
            {   // Eje principal para Watios
                title: {
                    text: 'Watios (W)',
                    style: { color: '#2c3e50' }
                },
                opposite: true,
                min: 0,
                labels: { style: { color: '#2c3e50' } },
                gridLineWidth: 0
            },
            {   // Eje secundario para SOC
                title: {
                    text: 'SOC Baterías (%)',
                    style: { color: '#FF6B6B' }
                },
                opposite: false,
                min: 0,
                max: 100,
                labels: { style: { color: '#FF6B6B' } },
                gridLineWidth: 0
            }
        ],

        xAxis: {
            dateTimeLabelFormats: { day: '%e %b' },
            type: 'datetime',
            min: extremoInicial + dia,
            max: extremoFinal + dia
        },
        
        legend: {
            enabled: true,
            align: 'center',
            verticalAlign: 'top',
            layout: 'horizontal'
        },

        rangeSelector: <?php echo json_encode($rangeSelectorOptions); ?>,

        tooltip: {
            split: true,
            distance: 30,
            padding: 1,
            outside: true,
            shared: true,
            valueDecimals: 0,
            crosshairs: true
        },
        
        navigator: {
            enabled: true,
            height: 40
        },

        series: series
    });
}

// Función para inicializar el gráfico diario con la misma ventana inicial
function inicializarGraficoDiario() {
    const series = crearSeriesDiarias();
    const { extremoInicial, extremoFinal } = calcularRangoInicial();

    graficaDiaria = Highcharts.chart('container-daily', {
        chart: {
            type: 'column',
            zoomType: 'x'
        },
        
        title: {
            text: 'Resumen Diario - Producción Real vs Predicciones (KiloWatios-hora)'
        },
        
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                day: '%e %b',
                week: '%e %b',
                month: '%b %Y'
            },
            crosshair: true,
            min: extremoInicial,
            max: extremoFinal
        },
        
        yAxis: {
            title: {
                text: 'KiloWatios-hora (KWh)'
            },
            min: 0
        },
        
        tooltip: {
            shared: true,
            valueSuffix: ' KWh',
            valueDecimals: 1
        },
        
        plotOptions: {
            column: {
                grouping: true,
                shadow: false,
                borderWidth: 1,
                pointWidth: 15,
                states: {
                    hover: {
                        brightness: 0.1
                    }
                }
            }
        },
        
        legend: {
            enabled: true
        },

        rangeSelector: <?php echo json_encode($rangeSelectorOptions); ?>,

        credits: {
            enabled: false
        },

        exporting: {
            buttons: {
                contextButton: {
                    menuItems: ['viewFullscreen', 'printChart', 'separator', 'downloadPNG', 'downloadJPEG', 'downloadPDF', 'downloadSVG', 'separator', 'resetZoom']
                }
            }
        },

        zooming: {
            type: 'x'
        },

        navigator: {
            enabled: true,
            height: 40
        },

        series: series
    });
}

// Inicializar los gráficos cuando la página cargue
document.addEventListener('DOMContentLoaded', function() {
    inicializarGraficoPrincipal();
    inicializarGraficoDiario();
    calcularEstadisticas();
});

</script>
</body>
</html>