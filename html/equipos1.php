<?php
require('conexion.php');

$sql = "SELECT * FROM equipos ORDER BY CASE  WHEN id_equipo = '_PVControl+' THEN 1 ELSE 2 END, id_equipo";

if ($result = mysqli_query($link, $sql)) {
    $rawdata = [];
    while ($row = mysqli_fetch_assoc($result)) {
        $rawdata[] = $row;
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
}
mysqli_close($link);

// Establecer la zona horaria local (opcional, si es necesario)
date_default_timezone_set('Europe/Madrid'); // Cambia esto según tu zona horaria

/**
 * Función recursiva para formatear los datos de los sensores.
 * @param array $data Los datos a formatear.
 * @param int $depth La profundidad actual del diccionario.
 * @return string Los datos formateados.
 */
function formatSensors($data, $depth = 0) {
    $output = "";
    foreach ($data as $key => $value) {
        $output .= "<span class='red'>$key</span>: ";
        if (is_array($value)) {
            $output .= "{" . formatSensors($value, $depth + 1) . "}\n\n";
        } else {
            $output .= "<span class='blue'>" . htmlspecialchars($value) . "</span>, ";
        }
    }
    return $output;
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tabla de Equipos</title>
    <link rel="stylesheet" href="css/menu_2025.css">
    <script src="script/menu.js"></script>

    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
        .collapsed {
            display: none;
        }
        .red {
            color: red;
        }
        .blue {
            color: blue;
        }
        .yellow {
            background-color: yellow;
        }
        .red-bg {
            background-color: #ffcccc; /* Rojo claro para mejor visibilidad */
        }
        .toggle-button {
            cursor: pointer;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-right: 8px;
        }
        .toggle-button:hover {
            background-color: #0056b3;
        }
        pre {
            margin: 0; /* Eliminar margen predeterminado del <pre> */
            white-space: pre-wrap; /* Mantener el formato pero permitir saltos de línea si es necesario */
        }
        .summary {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 700px; /* Ajusta según el ancho deseado */
        }
        .expanded-row {
            background-color: #f0f8ff; /* Fondo azul claro para la zona expandida */
        }
        .id-equipo {
            font-weight: bold; /* Texto en negrita */
            font-size: 1.1em; /* Tamaño de letra más grande */
            display: flex;
            align-items: center;
        }
        .even-row {
            background-color: #ffffff; /* Fondo blanco para filas pares */
        }
        .odd-row {
            background-color: #e0e0e0; /* Fondo gris claro (30%) para filas impares */
        }
    </style>
    <script>
        // Función para ajustar el margen superior de la tabla
        function adjustTableMargin() {
            var navbar = document.getElementById('navbar');
            var table = document.querySelector('table');
            if (navbar && table) {
                var navbarHeight = navbar.offsetHeight; // Obtener la altura del menú
                table.style.marginTop = navbarHeight + 'px'; // Aplicar el margen superior
            }
        }

        // Función para colapsar/expandir una fila
        function toggleRow(rowId, button) {
            var row = document.getElementById(rowId);
            if (row.classList.contains('collapsed')) {
                row.classList.remove('collapsed');
                row.classList.add('expanded-row'); // Añadir fondo azul claro
                button.textContent = '-'; // Cambiar el botón a "-"
                localStorage.setItem(rowId, 'expanded'); // Guardar estado en localStorage
            } else {
                row.classList.add('collapsed');
                row.classList.remove('expanded-row'); // Quitar fondo azul claro
                button.textContent = '+'; // Cambiar el botón a "+"
                localStorage.setItem(rowId, 'collapsed'); // Guardar estado en localStorage
            }
        }

        // Función para restaurar el estado de las filas al cargar la página
        function restoreRowStates() {
            document.querySelectorAll('.collapsible-row').forEach(function(row) {
                var rowId = row.id;
                var state = localStorage.getItem(rowId);
                var button = document.querySelector(`button[data-row='${rowId}']`);
                if (state === 'expanded') {
                    row.classList.remove('collapsed');
                    row.classList.add('expanded-row'); // Añadir fondo azul claro
                    if (button) button.textContent = '-'; // Cambiar el botón a "-"
                } else {
                    row.classList.add('collapsed');
                    if (button) button.textContent = '+'; // Cambiar el botón a "+"
                }
            });
        }

        // Actualizar la tabla cada 15 segundos
        function updateTable() {
            // Guardar la altura del menú en sessionStorage antes de recargar
            var navbar = document.getElementById('navbar');
            if (navbar) {
                sessionStorage.setItem('navbarHeight', navbar.offsetHeight);
            }
            location.reload();
        }

        // Restaurar estados y ajustar el margen al cargar la página
        window.addEventListener('load', function() {
            // Recuperar la altura del menú desde sessionStorage
            var navbarHeight = sessionStorage.getItem('navbarHeight');
            if (navbarHeight) {
                var table = document.querySelector('table');
                if (table) {
                    table.style.marginTop = navbarHeight + 'px'; // Aplicar el margen superior
                }
                sessionStorage.removeItem('navbarHeight'); // Limpiar sessionStorage
            } else {
                adjustTableMargin(); // Ajustar el margen si no hay altura guardada
            }

            restoreRowStates(); // Restaurar el estado de las filas
            setInterval(updateTable, 15000); // Actualizar cada 15 segundos
        });

        // Ajustar el margen si la ventana cambia de tamaño
        window.addEventListener('resize', adjustTableMargin);
    </script>
</head>
<body>
    <div id="navbar"></div>

    <table>
        <thead>
            <tr>
                <th>ID Equipo</th>
                <th>Última Actualización</th>
                <th>Sensores</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($rawdata as $index => $row): ?>
                <?php
                // Calcular el tiempo transcurrido desde la última actualización
                $now = new DateTime(); // Usa la hora local
                $lastUpdate = new DateTime($row['tiempo']); // Asume que la hora en la BD está en hora local
                $interval = $now->diff($lastUpdate);
                $minutes = ($interval->days * 1440) + ($interval->h * 60) + $interval->i;

                // Determinar el color de fondo según el tiempo transcurrido
                $rowClass = '';
                if ($minutes > 10) {
                    $rowClass = 'red-bg';
                } elseif ($minutes > 5) {
                    $rowClass = 'yellow';
                } else {
                    // Alternar entre fondo blanco y gris claro
                    $rowClass = ($index % 2 === 0) ? 'even-row' : 'odd-row';
                }
                ?>
                <tr class="<?php echo $rowClass; ?>">
                    <td class="id-equipo">
                        <button class="toggle-button" data-row="row<?php echo $index; ?>" onclick="toggleRow('row<?php echo $index; ?>', this)">+</button>
                        <?php echo htmlspecialchars($row['id_equipo']); ?>
                    </td>
                    <td><?php echo htmlspecialchars($row['tiempo']); ?></td>
                    <td>
                        <?php
                        // Decodificar los datos de sensores
                        $sensores = json_decode($row['sensores'], true);
                        if (json_last_error() === JSON_ERROR_NONE) {
                            if (is_array($sensores)) {
                                echo "<pre class='summary'>";
                                echo htmlspecialchars(substr($row['sensores'], 0, 200)) . "..."; // Resumen de los sensores
                                echo "</pre>";
                                echo "<pre class='full-content' style='display: none;'>";
                                echo formatSensors($sensores); // Usar la función recursiva
                                echo "</pre>";
                            }
                        } else {
                            echo "Error al decodificar los sensores.";
                        }
                        ?>
                    </td>
                </tr>
                <tr id="row<?php echo $index; ?>" class="collapsible-row collapsed">
                    <td colspan="3">
                        <pre><?php
                        if (is_array($sensores)) {
                            echo formatSensors($sensores); // Usar la función recursiva
                        }
                        ?></pre>
                    </td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</body>
</html>