<?php
require_once __DIR__ . '/includes/conexion.php';

// Función para generar todas las categorías posibles para el eje X
function generarCategoriasEjeX($fechaInicio, $fechaFin, $agrupacion) {
    $categorias = [];
    $fechaInicio = new DateTime($fechaInicio);
    $fechaFin = new DateTime($fechaFin);
    
    // Generar todas las fechas posibles para el rango
    if ($agrupacion === 'dia') {
        $interval = new DateInterval('P1D');
        $fechaFin->modify('+1 day'); // Para incluir el último día
        
        // Primero generamos todos los días del rango
        $period = new DatePeriod($fechaInicio, $interval, $fechaFin);
        foreach ($period as $date) {
            $categorias[] = [
                'fechaGrupo' => $date->format('Y-m-d'),
                'display' => $date->format('d/m'),
                'timestamp' => $date->getTimestamp()
            ];
        }
        
        // Añadir 29 de febrero para años bisiestos en el rango aunque no estén en los datos
        $yearStart = (int)$fechaInicio->format('Y');
        $yearEnd = (int)$fechaFin->format('Y');
        
        for ($year = $yearStart; $year <= $yearEnd; $year++) {
            if (($year % 4 == 0 && $year % 100 != 0) || $year % 400 == 0) {
                $feb29 = new DateTime("$year-02-29");
                if ($feb29 >= $fechaInicio && $feb29 <= $fechaFin) {
                    $found = false;
                    foreach ($categorias as $cat) {
                        if ($cat['fechaGrupo'] === "$year-02-29") {
                            $found = true;
                            break;
                        }
                    }
                    if (!$found) {
                        $categorias[] = [
                            'fechaGrupo' => "$year-02-29",
                            'display' => '29/02',
                            'timestamp' => $feb29->getTimestamp()
                        ];
                    }
                }
            }
        }
        
        // Ordenar por timestamp para garantizar orden cronológico
        usort($categorias, function($a, $b) {
            return $a['timestamp'] - $b['timestamp'];
        });
    } else {
        // Para otras agrupaciones (semana, mes, trimestre, año)
        switch ($agrupacion) {
            case 'semana':
                $interval = new DateInterval('P1W');
                $format = 'Y-\WW';
                $displayFormat = 'W';
                break;
            case 'mes':
                $interval = new DateInterval('P1M');
                $format = 'Y-m';
                $displayFormat = 'm';
                break;
            case 'trimestre':
                $interval = new DateInterval('P3M'); // Intervalo de 3 meses
                $format = 'Y-\QQ'; // Formato: YYYY-Q1, YYYY-Q2, etc.
                $displayFormat = 'Q'; // Mostrar solo Q1, Q2, etc.
                
                // Ajustar fecha de inicio al inicio del trimestre
                $mesInicio = (int)$fechaInicio->format('n');
                $trimestreInicio = ceil($mesInicio / 3);
                $fechaInicio->setDate(
                    (int)$fechaInicio->format('Y'),
                    ($trimestreInicio - 1) * 3 + 1,
                    1
                );
                break;
            case 'ano':
                // Configuración específica para años
                $interval = new DateInterval('P1Y');
                // Ajustar fecha de inicio al inicio del año
                $fechaInicio->setDate((int)$fechaInicio->format('Y'), 1, 1);
                // Ajustar fecha fin al final del año
                $fechaFin->setDate((int)$fechaFin->format('Y'), 12, 31);
                
                $period = new DatePeriod($fechaInicio, $interval, $fechaFin);
                foreach ($period as $date) {
                    $year = $date->format('Y');
                    $categorias[] = [
                        'fechaGrupo' => $year,
                        'display' => $year,
                        'timestamp' => $date->getTimestamp()
                    ];
                }
                return $categorias; // Retornar aquí para evitar el DatePeriod general
                break;
        }
        
        $period = new DatePeriod($fechaInicio, $interval, $fechaFin);
        foreach ($period as $date) {
            if ($agrupacion === 'trimestre') {
                $trimestre = ceil($date->format('n') / 3);
                $categorias[] = [
                    'fechaGrupo' => $date->format('Y') . '-Q' . $trimestre,
                    'display' => 'Q' . $trimestre,
                    'timestamp' => $date->getTimestamp()
                ];
            } else {
                $categorias[] = [
                    'fechaGrupo' => $date->format($format),
                    'display' => $date->format($displayFormat),
                    'timestamp' => $date->getTimestamp()
                ];
            }
        }
    }
    
    return $categorias;
}
// 2. Función para obtener datos con depuración
function obtenerDatosGrafico($link, $fechaInicio, $fechaFin, $agrupacion = 'mes') {
    // Validación de fechas
    $fechaInicio = date('Y-m-d', strtotime($fechaInicio));
    $fechaFin = date('Y-m-d', strtotime($fechaFin));
    
    // Configuración de agrupación
    switch ($agrupacion) {
        case 'semana':
            $grupoSQL = "YEAR(Fecha), WEEK(Fecha, 3)";
            $formatoFecha = "CONCAT(YEAR(Fecha), '-W', LPAD(WEEK(Fecha, 3), 2, '0')) as fechaGrupo";
            break;
        case 'mes':
            $grupoSQL = "YEAR(Fecha), MONTH(Fecha)";
            $formatoFecha = "CONCAT(YEAR(Fecha), '-', LPAD(MONTH(Fecha), 2, '0')) as fechaGrupo";
            break;
        case 'trimestre':
            $grupoSQL = "YEAR(Fecha), QUARTER(Fecha)";
            $formatoFecha = "CONCAT(YEAR(Fecha), '-Q', QUARTER(Fecha)) as fechaGrupo";
            break;
        case 'ano':
            $grupoSQL = "YEAR(Fecha)";
            $formatoFecha = "YEAR(Fecha) as fechaGrupo";
            break;
        case 'dia':
        default:
            $grupoSQL = "DATE(Fecha)";
            $formatoFecha = "DATE(Fecha) as fechaGrupo";
            break;
    }
    
    // Consulta SQL COMPLETA (sin campos omitidos)
    $sql = "SELECT 
            $formatoFecha,
            MAX(maxVbat) as maxVbat,
            MIN(minVbat) as minVbat,
            AVG(avgVbat) as avgVbat,
            MAX(maxSOC) as maxSOC,
            MIN(minSOC) as minSOC,
            AVG(avgSOC) as avgSOC,
            MAX(maxIbat) as maxIbat,
            MIN(minIbat) as minIbat,
            AVG(avgIbat) as avgIbat,
            MAX(maxIplaca) as maxIplaca,
            AVG(avgIplaca) as avgIplaca,
            SUM(Wh_placa)/1000 as Kwh_placa,
            SUM(Whp_bat)/1000 as Kwhp_bat,
            SUM(Whn_bat)/1000 as Kwhn_bat,
            SUM(Wh_consumo)/1000 as Kwh_consumo,
            MAX(maxTemp) as maxTemp,
            MIN(minTemp) as minTemp,
            AVG(avgTemp) as avgTemp,
            SUM(Whn_red)/1000 as Kwhn_red,
            SUM(Whp_red)/1000 as Kwhp_red,
            MAX(maxWred) as maxWred,
            MIN(minWred) as minWred,
            AVG(avgWred) as avgWred,
            MAX(maxVred) as maxVred,
            MIN(minVred) as minVred,
            (SUM(Whp_bat)-SUM(Whn_bat))/1000 as Kwh_bat,
            (SUM(Whp_red)-SUM(Whn_red))/1000 as Kwh_red
        FROM diario
        WHERE Fecha BETWEEN ? AND ?
        GROUP BY $grupoSQL
        ORDER BY fechaGrupo";
    
    // Ejecución
    $stmt = $link->prepare($sql);
    if (!$stmt) {
        return ['error' => $link->error, 'data' => []];
    }
    
    $stmt->bind_param('ss', $fechaInicio, $fechaFin);
    $stmt->execute();
    $result = $stmt->get_result();
    
    $datos = [];
    while ($fila = $result->fetch_assoc()) {
        $datos[] = $fila;
    }
    
    // Generar categorías completas
    $categoriasCompletas = generarCategoriasEjeX($fechaInicio, $fechaFin, $agrupacion);
    
    // Rellenar huecos (versión completa)
    $variables = [
        'maxVbat', 'minVbat', 'avgVbat', 'maxSOC', 'minSOC', 'avgSOC',
        'maxIbat', 'minIbat', 'avgIbat', 'maxIplaca', 'avgIplaca',
        'Kwh_placa', 'Kwhp_bat', 'Kwhn_bat', 'Kwh_consumo', 'maxTemp',
        'minTemp', 'avgTemp', 'Kwhn_red', 'Kwhp_red', 'maxWred',
        'minWred', 'avgWred', 'maxVred', 'minVred', 'Kwh_bat', 'Kwh_red'
    ];
    
    $datosCompletos = [];
    foreach ($categoriasCompletas as $categoria) {
        $encontrado = false;
        foreach ($datos as $dato) {
            if ($dato['fechaGrupo'] == $categoria['fechaGrupo']) {
                $datosCompletos[] = $dato;
                $encontrado = true;
                break;
            }
        }
        
        if (!$encontrado) {
            $registroVacio = ['fechaGrupo' => $categoria['fechaGrupo']];
            foreach ($variables as $var) {
                $registroVacio[$var] = 0;
            }
            $datosCompletos[] = $registroVacio;
        }
    }
    
    return ['data' => $datosCompletos];
}

// 3. Procesar solicitud AJAX
if (isset($_GET['ajax'])) {
    header('Content-Type: application/json');
    try {
        // Por defecto: rango completo del año actual (1/Ene a 31/Dic)
        $year = date('Y');
        $fechaInicio = $_GET['inicio'] ?? $year . '-01-01';
        $fechaFin = $_GET['fin'] ?? $year . '-12-31';
        
        // Agrupación por defecto: mes
        $agrupacion = $_GET['agrupacion'] ?? 'mes';
        
        $resultado = obtenerDatosGrafico($link, $fechaInicio, $fechaFin, $agrupacion);
        echo json_encode($resultado);
    } catch (Exception $e) {
        http_response_code(400);
        echo json_encode(['error' => $e->getMessage()]);
    }
    exit;
}

// 4. HTML y JavaScript
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <link rel="icon" href="/img/favicon.ico" type="image/x-icon">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($tituloPagina); ?></title>

    <title>Datos del Sistema Fotovoltaico</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <link rel="stylesheet" href="css/menu_2025.css">
    <script src="script/menu.js"></script>
    
    <style>
        #graficoContainer { height: 600px; min-width: 310px; margin: 20px 0; }
        .contenido-principal { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .data-columns { display: flex; gap: 20px; margin-top: 20px; }
        .data-column { flex: 1; border: 1px solid #ddd; border-radius: 5px; padding: 15px; }
        .data-column h5 { text-align: center; margin-bottom: 15px; }
        .table-responsive { max-height: 480px; overflow-y: auto; }
    </style>

</head>
<body>
    <!-- Menú principal -->
    
    <div id="navbar"></div>

    <!-- Contenido -->
    
    <main class="contenido-principal">
        <!--  
        <h2 class="my-4">Datos tabla diario</h2>
        -->
        <!-- Controles -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Configuración del Gráfico</h5>
            </div>
            <div class="card-body">
                <form id="configForm" onsubmit="actualizarGraficos(); return false;">
                    <div class="row">
                        <!-- Rangos temporales -->
                        <div class="col-md-3">
                            <h6>Rangos Temporales</h6>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="rangoPrincipalInicio" class="form-label">Inicio</label>
                                    <input type="date" id="rangoPrincipalInicio" class="form-control" value="<?php echo date('Y').'-01-01'; ?>">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="rangoPrincipalFin" class="form-label">Fin</label>
                                    <input type="date" id="rangoPrincipalFin" class="form-control" value="<?php echo date('Y').'-12-31'; ?>">
                                </div>
                            </div>
                            <div class="form-check form-switch mb-2">
                                <input class="form-check-input" type="checkbox" id="habilitarRango2" checked>
                                <label class="form-check-label" for="habilitarRango2">Incluir año anterior</label>
                            </div>
                            <div class="form-check form-switch mb-2">
                                <input class="form-check-input" type="checkbox" id="habilitarRango3" checked>
                                <label class="form-check-label" for="habilitarRango3">Incluir hace 2 años</label>
                            </div>
                            
                            <div class="mb-3">
                                <label for="agrupacion" class="form-label">Agrupación</label>
                                <select id="agrupacion" class="form-select">
                                    <option value="dia">Día</option>
                                    <option value="semana">Semana</option>
                                    <option value="mes" selected>Mes</option>
                                    <option value="trimestre">Trimestre</option>
                                    <option value="ano">Año</option>
                                </select>
                            </div>
                        </div>
                        
                        <!-- Variables a mostrar - 5 columnas -->
                        <div class="col-md-9">
                            <h6>Variables a Mostrar</h6>
                            <div class="row">
                                <!-- Columna 1: Voltajes -->
                                <div class="col-md">
                                    <div class="fw-bold mb-2">Voltajes</div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_maxVbat" value="maxVbat">
                                        <label class="form-check-label" for="v_maxVbat">Batería (máx)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_minVbat" value="minVbat">
                                        <label class="form-check-label" for="v_minVbat">Batería (mín)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_avgVbat" value="avgVbat">
                                        <label class="form-check-label" for="v_avgVbat">Batería (avg)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_maxVred" value="maxVred">
                                        <label class="form-check-label" for="v_maxVred">Red (máx)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_minVred" value="minVred">
                                        <label class="form-check-label" for="v_minVred">Red (mín)</label>
                                    </div>
                                </div>
                                
                                <!-- Columna 2: Corrientes -->
                                <div class="col-md">
                                    <div class="fw-bold mb-2">Corrientes</div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_maxIbat" value="maxIbat">
                                        <label class="form-check-label" for="v_maxIbat">Batería (máx)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_minIbat" value="minIbat">
                                        <label class="form-check-label" for="v_minIbat">Batería (mín)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_avgIbat" value="avgIbat">
                                        <label class="form-check-label" for="v_avgIbat">Batería (avg)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_maxIplaca" value="maxIplaca">
                                        <label class="form-check-label" for="v_maxIplaca">Placa (máx)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_avgIplaca" value="avgIplaca">
                                        <label class="form-check-label" for="v_avgIplaca">Placa (avg)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_maxWred" value="maxWred">
                                        <label class="form-check-label" for="v_maxWred">Red (máx)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_minWred" value="minWred">
                                        <label class="form-check-label" for="v_minWred">Red (mín)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_avgWred" value="avgWred">
                                        <label class="form-check-label" for="v_avgWred">Red (avg)</label>
                                    </div>
                                </div>
                                
                                <!-- Columna 3: Estado y Temperatura -->
                                <div class="col-md">
                                    <div class="fw-bold mb-2">Estado y Temp.</div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_maxSOC" value="maxSOC">
                                        <label class="form-check-label" for="v_maxSOC">SOC (máx)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_minSOC" value="minSOC">
                                        <label class="form-check-label" for="v_minSOC">SOC (mín)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_avgSOC" value="avgSOC">
                                        <label class="form-check-label" for="v_avgSOC">SOC (avg)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_maxTemp" value="maxTemp">
                                        <label class="form-check-label" for="v_maxTemp">Temp (máx)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_minTemp" value="minTemp">
                                        <label class="form-check-label" for="v_minTemp">Temp (mín)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_avgTemp" value="avgTemp">
                                        <label class="form-check-label" for="v_avgTemp">Temp (avg)</label>
                                    </div>
                                </div>
                                
                                <!-- Columna 4: Energía Solar -->
                                <div class="col-md">
                                    <div class="fw-bold mb-2">Energía Solar</div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_Kwh_placa" value="Kwh_placa" checked>
                                        <label class="form-check-label" for="v_Kwh_placa">Placa (Kwh)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_Kwhp_bat" value="Kwhp_bat">
                                        <label class="form-check-label" for="v_Kwhp_bat">A Batería (Kwh)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_Kwhn_bat" value="Kwhn_bat">
                                        <label class="form-check-label" for="v_Kwhn_bat">De Batería (Kwh)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_Kwh_bat" value="Kwh_bat">
                                        <label class="form-check-label" for="v_Kwh_bat">Neta Batería (Kwh)</label>
                                    </div>
                                </div>
                                
                                <!-- Columna 5: Red y Consumo -->
                                <div class="col-md">
                                    <div class="fw-bold mb-2">Red y Consumo</div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_Kwn_red" value="Kwhn_red">
                                        <label class="form-check-label" for="v_Kwhn_red">De Red (Kwh)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_Kwhp_red" value="Kwhp_red">
                                        <label class="form-check-label" for="v_Kwhp_red">A Red (Kwh)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_Kwh_red" value="Kwh_red">
                                        <label class="form-check-label" for="v_Kwh_red">Neta Red (Kwh)</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input variable-check" type="checkbox" id="v_Kwh_consumo" value="Kwh_consumo">
                                        <label class="form-check-label" for="v_Kwh_consumo">Consumo (Kwh)</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="text-end mt-3">
                        <button type="submit" class="btn btn-primary">Actualizar Gráfico</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Gráfico -->
        <div id="graficoContainer"></div>
    
        <!-- sección para mostrar depuración -->
        <div class="card mt-4">
            <div class="card-header">
                <h5>Información Registros</h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                      
                    <div id="dataColumnsContainer" class="data-columns">
                        <!-- Columnas se llenarán dinámicamente -->
                    </div>
                </div>
                
                <!-- Debug -->
                <div class="mb-3" hidden>
                    <label class="form-label">Consulta SQL Ejecutada:</label>
                    <pre id="sqlDebug" class="bg-light p-3"></pre>
                </div>
                <div class="mb-3" hidden>
                    <label class="form-label">Parámetros:</label>
                    <pre id="paramsDebug" class="bg-light p-3"></pre>
                </div>
            </div>
        </div>
    </main>

    <script>
    // Configuración inicial al cargar la página
    document.addEventListener('DOMContentLoaded', function() {
        // Configuración inicial
        const year = new Date().getFullYear();
        
        // Establecer rango anual completo (1/Ene - 31/Dic)
        document.getElementById('rangoPrincipalInicio').value = `${year}-01-01`;
        document.getElementById('rangoPrincipalFin').value = `${year}-12-31`;
        
        // Agrupación por defecto: mes
        document.getElementById('agrupacion').value = 'mes';
        
        // Cargar gráfico inicial
        actualizarGraficos();
    });

    //Función procesarDatosParaSerie modificada y corregida
    function procesarDatosParaSerie(data, variables, series, nombreRango = 'Principal') {
        console.group(`Procesando serie para rango: ${nombreRango}`);
                
        // Paleta de colores base por año
        const coloresBase = {
            'Principal': '#4CAF50',  // Verde 
            'Hace 1 año': '#2196F3', // Azul 
            'Hace 2 años': '#FF9800' // Naranja 
        };

        // Función para convertir HEX a HSL
        function hexToHSL(hex) {
            // Convertir HEX a RGB
            let r = parseInt(hex.substring(1,3), 16)/255;
            let g = parseInt(hex.substring(3,5), 16)/255;
            let b = parseInt(hex.substring(5,7), 16)/255;
            
            // Encontrar mínimo y máximo
            let max = Math.max(r, g, b), min = Math.min(r, g, b);
            let h, s, l = (max + min) / 2;

            if(max === min) {
                h = s = 0; // Achromatic
            } else {
                let d = max - min;
                s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
                switch(max) {
                    case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                    case g: h = (b - r) / d + 2; break;
                    case b: h = (r - g) / d + 4; break;
                }
                h /= 6;
            }

            return [h * 360, s * 100, l * 100];
        }

        // Función para convertir HSL a HEX
        function hslToHex(h, s, l) {
            l /= 100;
            const a = s * Math.min(l, 1 - l) / 100;
            const f = n => {
                const k = (n + h/30) % 12;
                const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
                return Math.round(255 * color).toString(16).padStart(2, '0');
            };
            return `#${f(0)}${f(8)}${f(4)}`;
        }

        // Función para variar colores
        const variarColor = (hex, index, total) => {
            const [h, s, l] = hexToHSL(hex);
            const factor = index / Math.max(1, total - 1); // Evitar división por cero
            
            // Ajustar luminosidad (50% a 80%)
            const nuevaL = 50 + (30 * factor);
            // Mantener saturación alta pero variarla ligeramente
            const nuevaS = 80 - (20 * factor);
            
            return hslToHex(h, nuevaS, nuevaL);
        };
        
        // Procesar cada variable
        variables.forEach((variable, index) => {
            const colorBase = coloresBase[nombreRango] || coloresBase['Principal'];
            const colorVariable = variarColor(colorBase, index, variables.length);
            
            console.log(`Variable ${index+1}/${variables.length}: ${variable}`, {
                colorBase,
                colorVariable,
                variacion: `${Math.round((index/Math.max(1, variables.length-1))*100)}%`
            });
                
            // Procesar datos
            const serieData = data.map(item => {
                let fecha;                
                if (item.fechaGrupo && typeof item.fechaGrupo === 'string') {
                    if (item.fechaGrupo.includes('W')) {
                        const [year, week] = item.fechaGrupo.split('-W');
                        fecha = new Date(year, 0, 1 + (parseInt(week) - 1) * 7);
                    } else if (item.fechaGrupo.includes('Q')) {
                        const [year, quarter] = item.fechaGrupo.split('-Q');
                        fecha = new Date(year, (parseInt(quarter) - 1) * 3, 1);
                    } else if (/^\d{4}-\d{2}$/.test(item.fechaGrupo)) {
                        const [year, month] = item.fechaGrupo.split('-');
                        fecha = new Date(year, parseInt(month) - 1, 1);
                    } else if (/^\d{4}$/.test(item.fechaGrupo)) {
                        fecha = new Date(item.fechaGrupo, 0, 1);
                    } else {
                        fecha = new Date(item.fechaGrupo);
                    }
                } else {
                    fecha = new Date();
                }
                
                return {
                    x: new Date(item.fechaGrupo).getTime(),
                    y: parseFloat(item[variable]) || 0,
                    fechaOriginal: item.fechaGrupo,
                    variable: variable
                };
            });
            
            // Crear la serie con patrón único
            series.push({
                name: `${variable} (${nombreRango})`,
                data: serieData,
                type: 'column',
                color: colorVariable, // Color para cada variable
                borderColor: '#333', // Color de borde fijo para mejor contraste
                borderWidth: 1,
                groupPadding: nombreRango.includes('Actual') ? 0.1 : 0.3,
                pointPadding: 0.05,
                pointPlacement: 0,
                pointWidth: 15,
                states: {
                    hover: {
                        brightness: 0.1,
                        borderWidth: 2
                    }
                },
                dataLabels: {
                    enabled: false,
                    format: variable.replace('max', 'Mx')
                                  .replace('min', 'Mn')
                                  .replace('avg', 'Av')
                                  .replace('Wh_', ''),
                    style: {
                        color: '#333333',
                        textOutline: 'none',
                        fontSize: '10px',
                        fontWeight: 'bold'
                    },
                    filter: {
                        property: 'y',
                        operator: '>',
                        value: 0
                    }
                },
                tooltip: {
                    pointFormat: '<span style="color:{point.color}">●</span> {series.name}: <b>{point.y:.2f}</b><br>'
                }
            });
        });
            
        console.groupEnd();
    }

    // Función renderizarGrafico
    function renderizarGrafico(series, agrupacion) {
        try {
            // 1. Procesar todas las categorías
            const categoriasMap = new Map();
            
            series.forEach(serie => {
                serie.data.forEach(punto => {
                    if (!punto.fechaOriginal) return;
                    
                    let clave, display, orden;
                    
                    switch (agrupacion) {
                        case 'dia':
                            const [y, m, d] = punto.fechaOriginal.split('-');
                            clave = `${m}-${d}`;
                            display = `${parseInt(d)}/${parseInt(m)}`;
                            orden = new Date(2000, parseInt(m)-1, parseInt(d)).getTime();
                            break;
                            
                        case 'semana':
                            const [yw, week] = punto.fechaOriginal.split('-W');
                            clave = week;
                            display = `S${week}`;
                            orden = parseInt(week);
                            break;
                            
                        case 'mes':
                            const [ym, month] = punto.fechaOriginal.split('-');
                            clave = month;
                            display = `M${parseInt(month)}`;
                            orden = parseInt(month);
                            break;
                            
                        case 'trimestre':
                            const [yq, quarter] = punto.fechaOriginal.split('-Q');
                            clave = `Q${quarter}`;
                            display = `T${quarter}`;
                            orden = parseInt(quarter);
                            break;
                            
                        case 'ano':
                            clave = punto.fechaOriginal;
                            display = punto.fechaOriginal;
                            orden = parseInt(punto.fechaOriginal);
                            break;
                    }
                    
                    if (!categoriasMap.has(clave)) {
                        categoriasMap.set(clave, {
                            display: display,
                            orden: orden,
                            clave: clave,
                            fechaOriginal: punto.fechaOriginal
                        });
                    }
                });
            });

            // 2. Ordenar categorías
            const categoriasOrdenadas = Array.from(categoriasMap.values())
                .sort((a, b) => a.orden - b.orden);
            
            // 3. Preparar series para Highcharts
            const seriesConfig = series.map(serie => {
                const data = categoriasOrdenadas.map(cat => {
                    const punto = serie.data.find(p => {
                        switch (agrupacion) {
                            case 'dia':
                                const [y, m, d] = p.fechaOriginal.split('-');
                                return `${m}-${d}` === cat.clave;
                            case 'semana':
                                const [yw, week] = p.fechaOriginal.split('-W');
                                return week === cat.clave;
                            case 'mes':
                                const [ym, month] = p.fechaOriginal.split('-');
                                return month === cat.clave;
                            case 'trimestre':
                                const q = p.fechaOriginal.split('-')[1].replace('Q', '');
                                return `Q${q}` === cat.clave;
                            case 'ano':
                                return p.fechaOriginal === cat.clave;
                        }
                    });
                    return punto ? punto.y : null;
                });
                
                return {
                    name: serie.name,
                    data: data,
                    type: 'column',
                    color: serie.color,
                    groupPadding: agrupacion === 'ano' ? 0.3 : 0.15,
                    pointPadding: agrupacion === 'ano' ? 0.2 : 0.1,
                    pointWidth: agrupacion === 'ano' ? 20 : null,
                    
                    tooltip: {
                        pointFormatter: function() {
                            const cat = categoriasOrdenadas[this.x];
                            let info = `${cat.display} (${this.series.name})`;
                            
                            if (agrupacion === 'trimestre') {
                                const year = cat.fechaOriginal.split('-')[0];
                                info = `T${cat.clave.replace('Q', '')} ${year} (${this.series.name})`;
                            }
                            
                            return `<span style="color:${this.color}">●</span> ${info}: <b>${this.y?.toFixed(2) || '0'}</b><br>`;
                        }
                    }
                };
            });

            // 4. Configuración completa de Highcharts
            Highcharts.chart('graficoContainer', {
                chart: {
                    type: 'column',
                    zoomType: 'x'
                },
             	credits: {
                    enabled: false
                },

                title: {
                    text: 'Datos Resumen Diario'
                },
                xAxis: {
                    categories: categoriasOrdenadas.map(c => c.display),
                    title: { text: getAxisTitle(agrupacion) },
                    labels: {
                        rotation: agrupacion === 'ano' ? 0 : -45,
                        style: { fontSize: '11px' }
                    }
                },
                yAxis: {
                    title: { text: 'Valores' },
                    labels: {
                        formatter: function() {
                            return this.value.toLocaleString('es-ES', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                        }
                    }
                },
                tooltip: {
                    useHTML: true,
                    headerFormat: '<b>{point.key}</b><br>',
                    shared: true
                },
                plotOptions: {
                    column: {
                        //grouping: agrupacion !== 'ano', // No agrupar columnas para años
                        grouping: true, 
 
                        //pointWidth: agrupacion === 'ano' ? 30 : null, // Ancho fijo para años
                        groupPadding: 0.15,
                        pointPadding: 0.1,
                        borderWidth: 1,
                        borderColor: 'black'
                    }
                },
                series: seriesConfig
            });

        } catch (e) {
            console.error('Error al renderizar gráfico:', e);
            document.getElementById('graficoContainer').innerHTML = `
                <div class="alert alert-danger">
                    Error: ${e.message}
                    <small>${e.stack}</small>
                </div>
            `;
        }
    }

    // Función para obtener el título del eje X según la agrupación
    function getAxisTitle(agrupacion) {
        switch (agrupacion) {
            case 'semana': return 'Semanas';
            case 'mes': return 'Meses';
            case 'trimestre': return 'Trimestres';
            case 'ano': return 'Años';
            default: return 'Días';
        }
    }
    
    // Función principal para actualizar los gráficos
    async function actualizarGraficos() {
        // Obtener parámetros del formulario
        const fechaInicio = document.getElementById('rangoPrincipalInicio').value;
        const fechaFin = document.getElementById('rangoPrincipalFin').value;
        const agrupacion = document.getElementById('agrupacion').value;
        const habilitarRango2 = document.getElementById('habilitarRango2').checked;
        const habilitarRango3 = document.getElementById('habilitarRango3').checked;
        
        // Obtener variables seleccionadas
        const variables = [];
        document.querySelectorAll('.variable-check:checked').forEach(checkbox => {
            variables.push(checkbox.value);
        });

        // Mostrar carga
        const container = document.getElementById('graficoContainer');
        container.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>';

        try {
            // Obtener datos del rango principal
            const response = await fetch(`?ajax=1&inicio=${fechaInicio}&fin=${fechaFin}&agrupacion=${agrupacion}`);
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            const resultado = await response.json();
            
            // Mostrar información de depuración
            document.getElementById('paramsDebug').textContent = JSON.stringify({
                fechaInicio: fechaInicio,
                fechaFin: fechaFin,
                agrupacion: agrupacion,
                variables: variables
            }, null, 2);

            // Variables para almacenar datos de los diferentes rangos
            let dataAnoPasado = null;
            let data2Anos = null;
            
            // Si hay rangos adicionales, obtener sus datos
            if (habilitarRango2 || habilitarRango3) {
                const promesas = [];
                
                if (habilitarRango2) {
                    const fechaInicioAnoPasado = new Date(fechaInicio);
                    fechaInicioAnoPasado.setFullYear(fechaInicioAnoPasado.getFullYear() - 1);
                    const fechaFinAnoPasado = new Date(fechaFin);
                    fechaFinAnoPasado.setFullYear(fechaFinAnoPasado.getFullYear() - 1);
                    
                    promesas.push(
                        fetch(`?ajax=1&inicio=${formatDate(fechaInicioAnoPasado)}&fin=${formatDate(fechaFinAnoPasado)}&agrupacion=${agrupacion}`)
                            .then(res => res.json())
                            .then(data => {
                                dataAnoPasado = data.data;
                                return data;
                            })
                    );
                }
                
                if (habilitarRango3) {
                    const fechaInicio2Anos = new Date(fechaInicio);
                    fechaInicio2Anos.setFullYear(fechaInicio2Anos.getFullYear() - 2);
                    const fechaFin2Anos = new Date(fechaFin);
                    fechaFin2Anos.setFullYear(fechaFin2Anos.getFullYear() - 2);
                    
                    promesas.push(
                        fetch(`?ajax=1&inicio=${formatDate(fechaInicio2Anos)}&fin=${formatDate(fechaFin2Anos)}&agrupacion=${agrupacion}`)
                            .then(res => res.json())
                            .then(data => {
                                data2Anos = data.data;
                                return data;
                            })
                    );
                }
                
                await Promise.all(promesas);
            }
            
            // Mostrar datos en la tabla con las 3 columnas
            mostrarDatosEnTabla(resultado.data, dataAnoPasado, data2Anos, variables);

            // Procesar datos para el gráfico
            const series = [];
            procesarDatosParaSerie(resultado.data, variables, series, 'Actual');
            
            if (dataAnoPasado) {
                procesarDatosParaSerie(dataAnoPasado, variables, series, 'Hace 1 año');
            }
            
            if (data2Anos) {
                procesarDatosParaSerie(data2Anos, variables, series, 'Hace 2 años');
            }
            
            renderizarGrafico(series, agrupacion);
        } catch (error) {
            console.error('Error:', error);
            container.innerHTML = '<div class="alert alert-danger">Error al cargar los datos: ' + error.message + '</div>';
            
            // Mostrar error en la sección de depuración
            document.getElementById('sqlDebug').textContent = 'Error al ejecutar la consulta';
            document.getElementById('paramsDebug').textContent = error.message;
            document.getElementById('dataColumnsContainer').innerHTML = '<div class="alert alert-danger col-12">Error al obtener datos</div>';
        }
    }

    // Función para obtener datos del servidor
    async function obtenerDatos(fechaInicio, fechaFin, agrupacion) {
        const response = await fetch(`?ajax=1&inicio=${fechaInicio}&fin=${fechaFin}&agrupacion=${agrupacion}`);
        if (!response.ok) throw new Error('Error en la respuesta del servidor');
        return await response.json();
    }

    // Función auxiliar para formatear fechas
    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    // Función para mostrar datos en tabla
    function mostrarDatosEnTabla(dataActual, dataAnoPasado = null, data2Anos = null, variablesSeleccionadas = []) {
        const container = document.getElementById('dataColumnsContainer');
        container.innerHTML = '';

        // Añadir estilos CSS específicos para el contenedor y tablas
        const style = document.createElement('style');
        style.textContent = `
            .data-columns-container {
                width: 100%;
                overflow-x: auto;
                display: flex;
                gap: 20px;
                padding-bottom: 10px; /* Espacio para el scroll */
            }
            .data-column {
                min-width: 300px; /* Ancho mínimo para cada columna */
                flex: 1;
            }
            .table-container {
                width: 100%;
                overflow-x: auto;
            }
            .data-table {
                min-width: 100%;
                white-space: nowrap;
            }
            .text-right { text-align: right !important; font-family: monospace; }
            .text-left { text-align: left !important; }
            .table td, .table th { padding: 0.3rem 0.75rem; }
            /* Estilo personalizado para la barra de scroll */
            .data-columns-container::-webkit-scrollbar {
                height: 8px;
            }
            .data-columns-container::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            .data-columns-container::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 4px;
            }
            .data-columns-container::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        `;
        document.head.appendChild(style);
        
        // Columnas a mostrar siempre
        const columnasBase = ['fechaGrupo'];
        // Añadir variables seleccionadas
        const columnasAMostrar = [...columnasBase, ...variablesSeleccionadas];
        
        const formatNumber = (value) => {
            // Verificación extra para asegurar que es un número
            const num = Number(value);
            if (isNaN(num)) return value;

            return new Intl.NumberFormat('es-ES', {
                style: 'decimal',
                minimumFractionDigits: 1,  // Mostrar al menos 1 decimal
                maximumFractionDigits: 1,  // Mostrar máximo 1 decimal
                useGrouping: true          // Separadores de miles
            }).format(num);
        };

        // Función para formatear valores
        const formatValue = (key, value) => {
            if (value === null || value === undefined || value === 'NULL') {
                return 'NULL';
            }

            // Manejar campo fechaGrupo de forma especial
            if (key === 'fechaGrupo') {
                if (!value) return 'NULL';
                
                // Intentar formatear según los diferentes formatos posibles
                try {
                    // Formato de año (YYYY)
                    if (/^\d{4}$/.test(value)) return value;
                    
                    // Formato de mes (YYYY-MM)
                    if (/^\d{4}-\d{2}$/.test(value)) {
                        const [year, month] = value.split('-');
                        return `${year}-${parseInt(month)}`; // Elimina ceros iniciales
                    }
                    
                    // Formato de trimestre (YYYY-QX)
                    if (/^\d{4}-Q\d$/.test(value)) return value;
                    
                    // Formato de semana (YYYY-WXX)
                    if (/^\d{4}-W\d{2}$/.test(value)) return value;
                    
                    // Formato de fecha (YYYY-MM-DD)
                    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
                        const [year, month, day] = value.split('-');
                        return `${parseInt(day)}/${parseInt(month)}/${year}`;
                    }
                    
                    return value; // Devolver el valor original si no coincide con ningún formato
                } catch (e) {
                    return value; // Si hay error, devolver el valor original
                }
            }
          
            // Formatear cualquier valor numérico
            if (!isNaN(value)) {
                return formatNumber(value);
            }
                        
            return value;
        };

        // Función para crear una columna de datos
        const crearColumnaDatos = (data, titulo) => {
            if (!data || data.length === 0) {
                return `
                    <div class="data-column">
                        <h5>${titulo}</h5>
                        <div class="alert alert-info">No hay datos disponibles</div>
                    </div>
                `;
            }
            
            // Crear encabezados
            let headHtml = '<tr>';
            columnasAMostrar.forEach(h => headHtml += `<th class="${h === 'fechaGrupo' ? 'text-left' : 'text-right'}">${h}</th>`);
            headHtml += '</tr>';
            
            // Crear filas
            let bodyHtml = '';
            data.forEach(row => {
                bodyHtml += '<tr>';
                columnasAMostrar.forEach(h => {
                    const value = row[h];
                    const cellClass = h === 'fechaGrupo' ? 'text-left' : 'text-right';
                    bodyHtml += `<td class="${cellClass}">${formatValue(h, value)}</td>`;
                });
                bodyHtml += '</tr>';
            });
            
            return `
                <div class="data-column">
                    <h5>${titulo}</h5>
                    <div class="table-responsive">
                        <table class="table table-striped table-sm">
                            <thead>${headHtml}</thead>
                            <tbody>${bodyHtml}</tbody>
                        </table>
                    </div>
                </div>
            `;
        };
    
        // Contenedor principal con scroll horizontal
        container.innerHTML = `
            <div class="data-columns-container">
                ${crearColumnaDatos(dataActual, 'Año Actual')}
                ${dataAnoPasado ? crearColumnaDatos(dataAnoPasado, 'Hace 1 Año') : crearColumnaDatos([], 'Hace 1 Año')}
                ${data2Anos ? crearColumnaDatos(data2Anos, 'Hace 2 Años') : crearColumnaDatos([], 'Hace 2 Años')}
            </div>
        `;
    }
    
    </script>
</body>
</html>