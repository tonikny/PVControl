<?php
include ("cabecera.inc");

// Establecer conexión a la base de datos
require('conexion.php');

// Procesar parámetros (tanto POST como GET para mantener los filtros)
$rango = isset($_REQUEST["rango"]) ? $_REQUEST["rango"] : "DAY";
$filtro_texto = isset($_REQUEST["filtro_texto"]) ? trim($_REQUEST["filtro_texto"]) : "";
$fecha_inicio = isset($_REQUEST["fecha_inicio"]) ? $_REQUEST["fecha_inicio"] : "";
$fecha_fin = isset($_REQUEST["fecha_fin"]) ? $_REQUEST["fecha_fin"] : "";
$pagina = isset($_REQUEST['pagina']) ? (int)$_REQUEST['pagina'] : 1;
$registros_por_pagina = 50;

// Construir consulta base
$sql_base = "SELECT Tiempo, log FROM log WHERE 1=1";
$sql_count = "SELECT COUNT(*) as total FROM log WHERE 1=1";

// Aplicar filtros
if($rango == "DAY") {
    $sql_base .= " AND DATE(Tiempo) = CURDATE()";
    $sql_count .= " AND DATE(Tiempo) = CURDATE()";
} elseif($rango == "WEEK") {
    $sql_base .= " AND WEEK(Tiempo,1) = WEEK(CURDATE(),1) AND log<>'Registro diario actualizado'";
    $sql_count .= " AND WEEK(Tiempo,1) = WEEK(CURDATE(),1) AND log<>'Registro diario actualizado'";
} elseif($rango == "MONTH") {
    $sql_base .= " AND MONTH(Tiempo) = MONTH(CURDATE()) AND YEAR(Tiempo) = YEAR(CURDATE()) AND log<>'Registro diario actualizado'";
    $sql_count .= " AND MONTH(Tiempo) = MONTH(CURDATE()) AND YEAR(Tiempo) = YEAR(CURDATE()) AND log<>'Registro diario actualizado'";
} elseif($rango == "CUSTOM" && !empty($fecha_inicio) && !empty($fecha_fin)) {
    $sql_base .= " AND DATE(Tiempo) BETWEEN '$fecha_inicio' AND '$fecha_fin'";
    $sql_count .= " AND DATE(Tiempo) BETWEEN '$fecha_inicio' AND '$fecha_fin'";
}

// Aplicar filtro de texto
if(!empty($filtro_texto)) {
    $sql_base .= " AND log LIKE '%" . mysqli_real_escape_string($link, $filtro_texto) . "%'";
    $sql_count .= " AND log LIKE '%" . mysqli_real_escape_string($link, $filtro_texto) . "%'";
}

// Ordenar resultados
$sql_base .= " ORDER BY Tiempo DESC";

// Obtener total de registros
$result_count = mysqli_query($link, $sql_count);
if($result_count) {
    $total_registros = mysqli_fetch_assoc($result_count)['total'];
    $total_paginas = ceil($total_registros / $registros_por_pagina);
    
    // Asegurar que la página actual sea válida
    if($pagina < 1) $pagina = 1;
    if($pagina > $total_paginas && $total_paginas > 0) $pagina = $total_paginas;
} else {
    $total_registros = 0;
    $total_paginas = 0;
    $pagina = 1;
}

// Calcular paginación
$offset = ($pagina - 1) * $registros_por_pagina;
$sql_base .= " LIMIT $offset, $registros_por_pagina";

// Obtener datos
$result = mysqli_query($link, $sql_base);
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Logs</title>
    <style>
        :root {
            --primary-color: #3498db;
            --secondary-color: #2980b9;
            --light-color: #ecf0f1;
            --dark-color: #2c3e50;
            --success-color: #27ae60;
            --danger-color: #e74c3c;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #ddd;
        }
        
        .header h1 {
            color: var(--dark-color);
            margin: 0;
        }
        
        .filters-container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .filter-group {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .filter-item {
            flex: 1;
            min-width: 200px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: var(--dark-color);
        }
        
        select, input[type="text"], input[type="date"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        
        .btn {
            padding: 10px 15px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        
        .btn:hover {
            background-color: var(--secondary-color);
        }
        
        .btn-secondary {
            background-color: #95a5a6;
        }
        
        .btn-secondary:hover {
            background-color: #7f8c8d;
        }
        
        .results-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-size: 14px;
            color: #555;
        }
        
        .table-container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background-color: var(--dark-color);
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }
        
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        tr:hover {
            background-color: #f1f7fd;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        
        .pagination a, .pagination span {
            margin: 0 5px;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            text-decoration: none;
            color: var(--primary-color);
        }
        
        .pagination a:hover {
            background-color: #f1f1f1;
        }
        
        .pagination .current {
            background-color: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }
        
        .no-results {
            text-align: center;
            padding: 40px;
            color: #777;
        }
        
        .export-buttons {
            display: flex;
            gap: 10px;
        }
        
        @media (max-width: 768px) {
            .filter-group {
                flex-direction: column;
            }
            
            .filter-item {
                min-width: 100%;
            }
            
            .header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .export-buttons {
                margin-top: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sistema de Logs</h1>
            <div class="export-buttons">
                <button class="btn" onclick="exportToCSV()">Exportar a CSV</button>
                <button class="btn btn-secondary" onclick="printLogs()">Imprimir</button>
            </div>
        </div>
        
        <div class="filters-container">
            <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST" id="filterForm">
                <input type="hidden" name="pagina" value="1">
                
                <div class="filter-group">
                    <div class="filter-item">
                        <label for="rango">Rango de tiempo:</label>
                        <select name="rango" id="rango" onchange="toggleCustomDates()">
                            <option value="DAY" <?php echo $rango == 'DAY' ? 'selected' : ''; ?>>Hoy</option>
                            <option value="WEEK" <?php echo $rango == 'WEEK' ? 'selected' : ''; ?>>Semana actual</option>
                            <option value="MONTH" <?php echo $rango == 'MONTH' ? 'selected' : ''; ?>>Mes actual</option>
                            <option value="CUSTOM" <?php echo $rango == 'CUSTOM' ? 'selected' : ''; ?>>Rango personalizado</option>
                        </select>
                    </div>
                    
                    <div class="filter-item" id="custom-dates" style="<?php echo $rango == 'CUSTOM' ? '' : 'display: none;' ?>">
                        <label for="fecha_inicio">Fecha inicio:</label>
                        <input type="date" name="fecha_inicio" id="fecha_inicio" value="<?php echo $fecha_inicio; ?>">
                    </div>
                    
                    <div class="filter-item" id="custom-dates-end" style="<?php echo $rango == 'CUSTOM' ? '' : 'display: none;' ?>">
                        <label for="fecha_fin">Fecha fin:</label>
                        <input type="date" name="fecha_fin" id="fecha_fin" value="<?php echo $fecha_fin; ?>">
                    </div>
                </div>
                
                <div class="filter-group">
                    <div class="filter-item">
                        <label for="filtro_texto">Filtrar por texto:</label>
                        <input type="text" name="filtro_texto" id="filtro_texto" placeholder="Buscar en los logs..." value="<?php echo htmlspecialchars($filtro_texto); ?>">
                    </div>
                    
                    <div class="filter-item" style="align-self: flex-end;">
                        <button type="submit" class="btn">Aplicar filtros</button>
                        <button type="button" class="btn btn-secondary" onclick="resetFilters()">Limpiar filtros</button>
                    </div>
                </div>
            </form>
        </div>
        
        <div class="results-info">
            <div>
                <?php if($total_registros > 0): ?>
                    Mostrando <?php echo min($registros_por_pagina, $total_registros - $offset); ?> de <?php echo $total_registros; ?> registros
                <?php else: ?>
                    No se encontraron registros
                <?php endif; ?>
            </div>
            <div>
                <?php if($total_paginas > 0): ?>
                    Página <?php echo $pagina; ?> de <?php echo $total_paginas; ?>
                <?php endif; ?>
            </div>
        </div>
        
        <div class="table-container">
            <?php if($result && mysqli_num_rows($result) > 0): ?>
                <table>
                    <thead>
                        <tr>
                            <th>Fecha y Hora</th>
                            <th>Mensaje de Log</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php while($row = mysqli_fetch_assoc($result)): ?>
                            <tr>
                                <td><?php echo date('d/m/Y H:i:s', strtotime($row['Tiempo'])); ?></td>
                                <td><?php echo htmlspecialchars($row['log']); ?></td>
                            </tr>
                        <?php endwhile; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <div class="no-results">
                    <p>No se encontraron registros con los filtros aplicados.</p>
                </div>
            <?php endif; ?>
        </div>
        
        <?php if($total_paginas > 1): ?>
            <div class="pagination">
                <?php if($pagina > 1): ?>
                    <a href="<?php echo buildPaginationLink($pagina - 1); ?>">&laquo; Anterior</a>
                <?php endif; ?>
                
                <?php 
                // Mostrar máximo 5 páginas alrededor de la actual
                $start_page = max(1, $pagina - 2);
                $end_page = min($total_paginas, $pagina + 2);
                
                if($start_page > 1): ?>
                    <a href="<?php echo buildPaginationLink(1); ?>">1</a>
                    <?php if($start_page > 2): ?>
                        <span>...</span>
                    <?php endif; ?>
                <?php endif; ?>
                
                <?php for($i = $start_page; $i <= $end_page; $i++): ?>
                    <?php if($i == $pagina): ?>
                        <span class="current"><?php echo $i; ?></span>
                    <?php else: ?>
                        <a href="<?php echo buildPaginationLink($i); ?>"><?php echo $i; ?></a>
                    <?php endif; ?>
                <?php endfor; ?>
                
                <?php if($end_page < $total_paginas): ?>
                    <?php if($end_page < $total_paginas - 1): ?>
                        <span>...</span>
                    <?php endif; ?>
                    <a href="<?php echo buildPaginationLink($total_paginas); ?>"><?php echo $total_paginas; ?></a>
                <?php endif; ?>
                
                <?php if($pagina < $total_paginas): ?>
                    <a href="<?php echo buildPaginationLink($pagina + 1); ?>">Siguiente &raquo;</a>
                <?php endif; ?>
            </div>
        <?php endif; ?>
    </div>
    
    <script>
        function toggleCustomDates() {
            const rango = document.getElementById('rango').value;
            const customDates = document.getElementById('custom-dates');
            const customDatesEnd = document.getElementById('custom-dates-end');
            
            if (rango === 'CUSTOM') {
                customDates.style.display = 'block';
                customDatesEnd.style.display = 'block';
            } else {
                customDates.style.display = 'none';
                customDatesEnd.style.display = 'none';
            }
        }
        
        function resetFilters() {
            document.getElementById('rango').value = 'DAY';
            document.getElementById('filtro_texto').value = '';
            document.getElementById('fecha_inicio').value = '';
            document.getElementById('fecha_fin').value = '';
            document.querySelector('input[name="pagina"]').value = '1';
            toggleCustomDates();
            document.getElementById('filterForm').submit();
        }
        
        function exportToCSV() {
            // Crear una copia del formulario para exportar
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '<?php echo $_SERVER['PHP_SELF']; ?>';
            
            // Agregar campos ocultos con los valores actuales
            const rango = document.createElement('input');
            rango.type = 'hidden';
            rango.name = 'rango';
            rango.value = document.getElementById('rango').value;
            form.appendChild(rango);
            
            const filtroTexto = document.createElement('input');
            filtroTexto.type = 'hidden';
            filtroTexto.name = 'filtro_texto';
            filtroTexto.value = document.getElementById('filtro_texto').value;
            form.appendChild(filtroTexto);
            
            const fechaInicio = document.createElement('input');
            fechaInicio.type = 'hidden';
            fechaInicio.name = 'fecha_inicio';
            fechaInicio.value = document.getElementById('fecha_inicio').value;
            form.appendChild(fechaInicio);
            
            const fechaFin = document.createElement('input');
            fechaFin.type = 'hidden';
            fechaFin.name = 'fecha_fin';
            fechaFin.value = document.getElementById('fecha_fin').value;
            form.appendChild(fechaFin);
            
            const exportar = document.createElement('input');
            exportar.type = 'hidden';
            exportar.name = 'exportar';
            exportar.value = 'csv';
            form.appendChild(exportar);
            
            document.body.appendChild(form);
            form.submit();
            document.body.removeChild(form);
        }
        
        function printLogs() {
            window.print();
        }
        
        // Inicializar el estado de los campos de fecha personalizada
        document.addEventListener('DOMContentLoaded', function() {
            toggleCustomDates();
        });
    </script>
</body>
</html>

<?php
// Función para construir enlaces de paginación manteniendo los filtros
function buildPaginationLink($pagina) {
    $params = array(
        'rango' => $GLOBALS['rango'],
        'filtro_texto' => $GLOBALS['filtro_texto'],
        'fecha_inicio' => $GLOBALS['fecha_inicio'],
        'fecha_fin' => $GLOBALS['fecha_fin'],
        'pagina' => $pagina
    );
    
    return $_SERVER['PHP_SELF'] . '?' . http_build_query($params);
}

// Procesar exportación a CSV
if(isset($_POST['exportar']) && $_POST['exportar'] == 'csv') {
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename=logs_' . date('Y-m-d') . '.csv');
    
    $output = fopen('php://output', 'w');
    fputcsv($output, array('Fecha y Hora', 'Mensaje de Log'), ';');
    
    // Reutilizar la consulta base sin LIMIT para obtener todos los registros
    $sql_export = str_replace("LIMIT $offset, $registros_por_pagina", "", $GLOBALS['sql_base']);
    $result_export = mysqli_query($GLOBALS['link'], $sql_export);
    
    if($result_export) {
        while($row = mysqli_fetch_assoc($result_export)) {
            fputcsv($output, array(
                date('d/m/Y H:i:s', strtotime($row['Tiempo'])),
                $row['log']
            ), ';');
        }
    }
    
    fclose($output);
    exit();
}

mysqli_close($link);
include ("pie.inc");
?>