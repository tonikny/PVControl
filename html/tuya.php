<?php
// Incluir archivo de conexión
require 'conexion.php';

// Obtener la fecha actual
$fecha_actual = date("Y-m-d");

// Obtener el rango de fechas del formulario (o usar el día actual por defecto)
$fecha_inicio = $_POST['fecha_inicio'] ?? $fecha_actual;
$fecha_fin = $_POST['fecha_fin'] ?? $fecha_actual;

// Obtener los reles disponibles en el rango de fechas con sus nombres
$query_reles = "
    SELECT DISTINCT h.id_rele, d.nombre 
    FROM TUYA_HISTORICO h
    JOIN TUYA_DISPOSITIVOS d ON h.id_rele = d.id_rele
    WHERE h.tiempo BETWEEN '$fecha_inicio 00:00:00' AND '$fecha_fin 23:59:59'
    ORDER BY h.tiempo
";
$resultado_reles = $link->query($query_reles);

// Obtener los reles seleccionados (si los hay, o seleccionar todos por defecto)
$reles_seleccionados = $_POST['reles'] ?? [];
if (empty($reles_seleccionados)) {
    // Seleccionar todos los reles por defecto
    while ($rele = $resultado_reles->fetch_assoc()) {
        $reles_seleccionados[] = $rele['id_rele'];
    }
    // Reiniciar el puntero del resultado para usarlo nuevamente en el formulario
    $resultado_reles->data_seek(0);
}

// Obtener los tipos de datos seleccionados (si los hay, o seleccionar "Estado" por defecto)
$tipos_datos_seleccionados = $_POST['tipos_datos'] ?? ['estado']; // "Estado" activado por defecto

// Obtener los datos de los sensores seleccionados
$datos_grafico = [];
if (!empty($reles_seleccionados)) {
    $lista_reles = implode("','", $reles_seleccionados);
    $query_datos = "
        SELECT id_rele, tiempo, estado, wac, vac, wh 
        FROM TUYA_HISTORICO 
        WHERE id_rele IN ('$lista_reles') 
        AND tiempo BETWEEN '$fecha_inicio 00:00:00' AND '$fecha_fin 23:59:59'
        ORDER BY tiempo
    ";
    $resultado_datos = $link->query($query_datos);

    while ($fila = $resultado_datos->fetch_assoc()) {
        $tiempo = strtotime($fila['tiempo']) * 1000; // Convertir a milisegundos para Highcharts
        $datos_grafico[$fila['id_rele']][] = [
            'tiempo' => $tiempo,
            'estado' => $fila['estado'],
            'wac' => $fila['wac'],
            'vac' => $fila['vac'],
            'wh' => $fila['wh']
        ];
    }
}

// Obtener los datos de la tabla TUYA_DIARIO para los últimos 15 días
$fecha_15_dias_atras = date("Y-m-d", strtotime("-15 days"));
$query_diario = "
    SELECT Fecha, id_rele, Wh, T_on 
    FROM TUYA_DIARIO 
    WHERE Fecha BETWEEN '$fecha_15_dias_atras' AND '$fecha_actual'
    AND id_rele IN ('$lista_reles')
    ORDER BY Fecha
";
$resultado_diario = $link->query($query_diario);

$datos_diario = [];
while ($fila = $resultado_diario->fetch_assoc()) {
    $datos_diario[$fila['id_rele']][] = [
        'Fecha' => $fila['Fecha'],
        'Wh' => $fila['Wh'],
        'T_on' => $fila['T_on']
    ];
}
// Aplanar el array $datos_diario
$datos_planos = [];
foreach ($datos_diario as $rele => $datos) {
    $datos_planos = array_merge($datos_planos, $datos);
}

// Extraer las fechas únicas y ordenadas
$fechas_unicas = array_unique(array_column($datos_planos, 'Fecha'));
sort($fechas_unicas); // Ordenar las fechas de menor a mayor

// Reestructurar los datos para que estén en el orden correcto
$datos_ordenados = [];
foreach ($datos_diario as $id_rele => $datos) {
    $datos_por_fecha = array_column($datos, null, 'Fecha'); // Indexar por fecha
    $datos_ordenados[$id_rele] = array_map(function ($fecha) use ($datos_por_fecha) {
        return $datos_por_fecha[$fecha] ?? ['Wh' => null, 'T_on' => null]; // Si no hay datos, usar null
    }, $fechas_unicas);
}


// Ordenar los datos por id_rele (alfabéticamente)
ksort($datos_ordenados);

//echo "<pre>";
//print_r($datos_diario);
//echo "</pre>";

//echo "<pre>";
//print_r($fechas_unicas);
//echo "</pre>";

//echo "<pre>";
//print_r($datos_ordenados);
//echo "</pre>";

//sleep(30);
//die();
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RELES TUYA</title>
    <link rel="stylesheet" href="css/menu_2025.css">
    <script src="script/menu.js"></script>
    
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <script src="https://code.highcharts.com/modules/exporting.js"></script>
    <script src="https://code.highcharts.com/modules/export-data.js"></script>
    <script src="https://code.highcharts.com/modules/accessibility.js"></script>
    <style>
        /* Contenedor flexible para los formularios */
        .form-container {
            display: flex;
            flex-wrap: wrap; /* Permite que los elementos se envuelvan si no hay espacio */
            gap: 20px; /* Espacio entre los elementos */
            margin-bottom: 20px;
        }

        /* Estilo para cada grupo de controles (fechas, sensores, tipos de datos) */
        .form-group {
            flex: 1; /* Cada grupo ocupa el mismo espacio */
            min-width: 200px; /* Ancho mínimo para evitar que se compriman demasiado */
        }

        /* Estilo para los checkboxes y labels */
        .form-group label {
            display: block;
            margin: 0px 0;
        }

        /* Estilo para el botón */
        .form-container button {
            align-self: flex-end; /* Alinea el botón al final */
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
        }

        .form-container button:hover {
            background-color: #0056b3;
        }

        /* Estilo responsivo para pantallas pequeñas */
        @media (max-width: 768px) {
            .form-container {
                flex-direction: column; /* Apila los elementos verticalmente */
            }
        }
    </style>
</head>
<body>
    <div id="navbar"></div>
    
    <h1>RELES TUYA</h1>

    <!-- Formulario para seleccionar fechas, sensores y tipos de datos -->
    <form method="POST">
        <div class="form-container">
            <!-- Grupo para las fechas -->
            <div class="form-group">
                <label for="fecha_inicio">Fecha de inicio:</label>
                <input type="date" id="fecha_inicio" name="fecha_inicio" value="<?php echo $fecha_inicio; ?>" required>

                <label for="fecha_fin">Fecha de fin:</label>
                <input type="date" id="fecha_fin" name="fecha_fin" value="<?php echo $fecha_fin; ?>" required>
            </div>

            <!-- Grupo para los reles -->
            <div class="form-group">
                <h3>Seleccionar reles:</h3>
                <?php
                while ($rele = $resultado_reles->fetch_assoc()) {
                    $id_rele = $rele['id_rele'];
                    $nombre_rele = $rele['nombre'];
                    $checked = in_array($id_rele, $reles_seleccionados) ? 'checked' : '';
                    echo "<label>
                             <input type='checkbox' name='reles[]' value='$id_rele' $checked>
                             $id_rele - $nombre_rele
                          </label><br>";
                }
                ?>
            </div>
            
            <!-- Grupo para los tipos de datos -->
            <div class="form-group">
                <h3>Seleccionar tipos de datos:</h3>
                <label><input type="checkbox" name="tipos_datos[]" value="estado" <?php echo in_array('estado', $tipos_datos_seleccionados) ? 'checked' : ''; ?>> Estado</label><br>
                <label><input type="checkbox" name="tipos_datos[]" value="wac" <?php echo in_array('wac', $tipos_datos_seleccionados) ? 'checked' : ''; ?>> Wac</label><br>
                <label><input type="checkbox" name="tipos_datos[]" value="vac" <?php echo in_array('vac', $tipos_datos_seleccionados) ? 'checked' : ''; ?>> Vac</label><br>
                <label><input type="checkbox" name="tipos_datos[]" value="wh" <?php echo in_array('wh', $tipos_datos_seleccionados) ? 'checked' : ''; ?>> Wh</label><br>
            </div>
            
            <!-- Botón de enviar -->
            <button type="submit">Generar gráfico</button>
        </div>
    </form>

    <!-- Contenedor para el gráfico -->
    <div id="grafico" style="width: 100%; height: 500px; margin-top: 20px;"></div>

    <!-- Contenedor para el gráfico de Wh -->
    <div id="grafico-wh" style="width: 100%; height: 500px; margin-top: 20px;"></div>

    <!-- Contenedor para el gráfico de T_on -->
    <div id="grafico-ton" style="width: 100%; height: 500px; margin-top: 20px;"></div>

    <!-- Script para generar los gráficos con Highcharts -->
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            // Gráfico principal (líneas)
            Highcharts.chart('grafico', {
                chart: {
                    type: 'line',
                    zoomType: 'xy',
                    panning: true,
                    panKey: 'shift'
                },
                credits: {
                  enabled: false
                },
                title: {
                    text: ''
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
                tooltip: {
                  split: true,
                  distance: 30,
                  padding: 1,
                  outside: true,
                  shared: true,
                  valueDecimals: 2
                  },
                plotOptions: {
                    series: {
                        grouping: true, // Habilitar agrupación de series
                        groupPadding: 0.5 // Espaciado entre grupos
                    }
                },  
                navigator: {
                  enabled: true // false
                  },
                series: [
                    <?php
                    foreach ($datos_grafico as $id_rele => $datos) {
                        if (in_array('estado', $tipos_datos_seleccionados)) {
                            echo "{
                                name: '$id_rele - Estado',
                                data: [" . implode(",", array_map(function ($dato) {
                                    return "[{$dato['tiempo']}, {$dato['estado']}]";
                                }, $datos)) . "]
                            },";
                        }
                        if (in_array('wac', $tipos_datos_seleccionados)) {
                            echo "{
                                name: '$id_rele - Wac',
                                data: [" . implode(",", array_map(function ($dato) {
                                    return "[{$dato['tiempo']}, " . ($dato['wac'] ?? 'null') . "]";
                                }, $datos)) . "]
                            },";
                        }
                        if (in_array('vac', $tipos_datos_seleccionados)) {
                            echo "{
                                name: '$id_rele - Vac',
                                data: [" . implode(",", array_map(function ($dato) {
                                    return "[{$dato['tiempo']}, " . ($dato['vac'] ?? 'null') . "]";
                                }, $datos)) . "]
                            },";
                        }
                        if (in_array('wh', $tipos_datos_seleccionados)) {
                            echo "{
                                name: '$id_rele - Wh',
                                data: [" . implode(",", array_map(function ($dato) {
                                    return "[{$dato['tiempo']}, " . ($dato['wh'] ?? 'null') . "]";
                                }, $datos)) . "]
                            },";
                        }
                    }
                    ?>
                ]
            });

            // Gráfico de Wh (columnas)
            Highcharts.chart('grafico-wh', {
                chart: {
                    type: 'column'
                },
                credits: {
                  enabled: false
                },
                title: {
                    text: 'Consumo de energía (Wh) por día'
                },
                xAxis: {
                    categories: <?php echo json_encode($fechas_unicas); ?>,
                    title: {
                        text: 'Fecha'
                    }
                },
                yAxis: {
                    title: {
                        text: 'Wh'
                    }
                },
                tooltip: {
                    shared: true,
                    formatter: function () {
                        let tooltipText = `<b>${this.x}</b><br>`;
                        this.points.forEach(point => {
                            tooltipText += `${point.series.name}: ${Highcharts.numberFormat(point.y, 1)} Wh<br>`;
                        });
                        return tooltipText;
                    }
                },
                plotOptions: {
                    column: {
                        dataLabels: {
                            enabled: true,
                            crop: false,
                            overflow: 'none',
                            formatter: function () {
                                return Highcharts.numberFormat(this.y, 1); // Formato con 1 decimal
                            }
                        },
                        enableMouseTracking: false
                    }
                },


                
                series: [
                    <?php
                    foreach ($datos_ordenados as $id_rele => $datos) {
                        echo "{
                            name: '$id_rele - Wh',
                            data: [" . implode(",", array_map(function ($dato) {
                                return $dato['Wh'] ?? 0; // Usar 0 si no hay datos
                            }, $datos)) . "]
                        },";
                    }
                    ?>
                ]
            });

            
            // Gráfico de T_on (columnas)
            Highcharts.chart('grafico-ton', {
                chart: {
                    type: 'column'
                },
                credits: {
                  enabled: false
                },
                title: {
                    text: 'Minutos encendido (T_on) por día'
                },
                xAxis: {
                    categories: <?php echo json_encode($fechas_unicas); ?>,
                    title: {
                        text: 'Fecha'
                    }
                },
                yAxis: {
                    title: {
                        text: 'T_on (minutos)'
                    }
                },
                tooltip: {
                    shared: true,
                    formatter: function () {
                        let tooltipText = `<b>${this.x}</b><br>`;
                        this.points.forEach(point => {
                            tooltipText += `${point.series.name}: ${Highcharts.numberFormat(point.y / 60, 1)} minutos<br>`;
                        });
                        return tooltipText;
                    }
                },
                plotOptions: {
                    column: {
                        dataLabels: {
                            enabled: true,
                            crop: false,
                            overflow: 'none',
                            formatter: function () {
                                return Highcharts.numberFormat(this.y / 60, 1); // Convertir a minutos con 1 decimal
                            }
                        },
                        enableMouseTracking: false
                    }
                },
                    
                series: [
                    <?php
                    foreach ($datos_ordenados as $id_rele => $datos) {
                        echo "{
                            name: '$id_rele - T_on',
                            data: [" . implode(",", array_map(function ($dato) {
                                return $dato['T_on'] ?? 0; // Usar 0 si no hay datos
                            }, $datos)) . "]
                        },";
                    }
                    ?>
                ]
            });
            
        });
    </script>
</body>
</html>