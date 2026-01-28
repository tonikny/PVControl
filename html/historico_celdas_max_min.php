<?php
$titulo = "Resumen Celdas";
include("cabecera.inc");

require('conexion.php');

// Obtener todas las tablas que comienzan con "datos_celdas_"
$sql = "SHOW TABLES LIKE 'datos_celdas%'";
$resultado = mysqli_query($link, $sql);

if (!$resultado) {
    die('No se pudo ejecutar la consulta: ' . mysqli_error($link));
}

$tablas = [];
while ($row = mysqli_fetch_array($resultado)) {
    $tablas[] = $row[0];
}

// Si no hay tablas, mostrar un mensaje de error y detener la ejecución
if (empty($tablas)) {
    die("No se encontraron tablas que comiencen con 'datos_celdas_'.");
}

// Obtener la tabla seleccionada (por defecto, la primera tabla encontrada)
$tabla_seleccionada = $_POST['tabla'] ?? $tablas[0];
$dias = $_POST['dias'] ?? 15;

// Mostrar el formulario para seleccionar la tabla y el número de días
echo '<form method="POST" action="">
        <label for="tabla">Seleccione la tabla:</label>
        <select name="tabla" id="tabla">';
foreach ($tablas as $tabla) {
    $selected = $tabla === $tabla_seleccionada ? 'selected' : '';
    echo "<option value='$tabla' $selected>$tabla</option>";
}
echo '</select>
      <label for="dias">Número de días:</label>
      <input type="number" name="dias" id="dias" value="' . $dias . '" min="1">
      <input type="submit" value="Actualizar">
      </form>';

// Consulta para obtener los datos de la tabla seleccionada
$sql = "SELECT * FROM $tabla_seleccionada LIMIT 1";
$resultado = mysqli_query($link, $sql);

if (!$resultado) {
    die('No se pudo ejecutar la consulta: ' . mysqli_error($link));
}

// Calcular el número de campos que empiezan por "C"
$nceldas = 0;
$num_fields = mysqli_num_fields($resultado);
for ($i = 0; $i < $num_fields; $i++) {
    $field_info = mysqli_fetch_field_direct($resultado, $i);
    if (strpos($field_info->name, 'C') === 0) {
        $nceldas++;
    }
}

// Construir la consulta SQL dinámicamente
$sql = "SELECT UNIX_TIMESTAMP(DATE(Tiempo))*1000 as Fecha, ";
$sql .= implode(", ", array_map(function($i) {
    return "max(C$i) as 'Max_C$i', min(C$i) as 'Min_C$i', avg(C$i) as 'Med_C$i'";
}, range(1, $nceldas)));
$sql .= " FROM $tabla_seleccionada WHERE Tiempo >= SUBDATE(NOW(), INTERVAL $dias DAY) GROUP BY DATE(Tiempo)";


if ($result = mysqli_query($link, $sql)) {
    $rawdata2 = mysqli_fetch_all($result, MYSQLI_ASSOC);
} else {
    die("ERROR: No se puede ejecutar $sql. " . mysqli_error($link));
}

// Creacion SQL Max-Min de cada Celda..salida en una unica fila

$sql = "SELECT " . implode(", ", array_map(function($i) {
    return "max(C$i) as 'Max_C$i', min(C$i) as 'Min_C$i'";
}, range(1, $nceldas))) . " FROM $tabla_seleccionada WHERE Tiempo >= SUBDATE(NOW(), INTERVAL $dias DAY)";

if ($result = mysqli_query($link, $sql)) {
    $row = mysqli_fetch_array($result, MYSQLI_NUM);
    $r = implode(",", array_map(function($i) use ($row) {
        return "[" . $row[$i * 2] . "," . $row[$i * 2 + 1] . "]";
    }, range(0, $nceldas - 1)));
} else {
    die("ERROR: No se puede ejecutar $sql. " . mysqli_error($link));
}

$cat = implode(", ", array_map(function($i) {
    return "'C$i'";
}, range(1, $nceldas)));

mysqli_close($link);
?>

<!-- Importo el archivo Javascript directamente desde la web -->
<script src="https://code.jquery.com/jquery.js"></script>
<script src="https://code.highcharts.com/stock/highstock.js"></script>
<script src="https://code.highcharts.com/themes/grid.js"></script>
<script src="https://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>
<script src="https://code.highcharts.com/modules/export-data.js"></script>
<script src="https://code.highcharts.com/modules/accessibility.js"></script>

<div id="container_C" style="width: 100%; height: 480px; margin-left: 0px; float: left"></div>
<?php
for ($j = 1; $j < $nceldas + 1; $j++) {
    echo "<div id='container_C$j' style='width: 25%; height: 240px; margin-left: 0px; float: left'></div>\n";
}
?>

<script>
$(function () {
    Highcharts.setOptions({
        global: {useUTC: false },
        time: { timezone: zona_horaria },
        lang: {
            months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            weekdays: ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'],
            shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            rangeSelectorFrom: "Desde",
            rangeSelectorTo: "A",
            printChart: "Imprimir gráfico",
            loading: "Cargando..."
        }
    });

    var Vceldas = new Highcharts.Chart({
        chart: { renderTo: 'container_C', type: 'columnrange', inverted: false },
        accessibility: { description: 'Voltaje de cada celda de la bateria' },
        title: { text: 'Variacion Max-Min Vceldas (' + <?php echo $dias; ?> + ' dias)' },
        subtitle: { text: 'PVControl+' },
        credits: { enabled: false },
        xAxis: { categories: [<?php echo $cat; ?>] },
        yAxis: {
            title: { text: 'Voltaje Celda' },
            plotBands: [{
                from: Vcelda_franja_min,
                to: Vcelda_franja_max,
                color: 'rgba(68, 170, 213, 0.2)',
                label: { text: '' }
            }]
        },
        tooltip: { valueSuffix: ' V' },
        plotOptions: {
            columnrange: {
                dataLabels: { enabled: true, format: '{point.y:,.3f}' }
            }
        },
        legend: { enabled: false },
        series: [{ name: 'Vceldas', data: [<?php echo $r; ?>] }]
    });

    <?php
    for ($j = 1; $j <= $nceldas; $j++) {
        $Cx = "C" . $j;
        echo "
        var Vcelda$j = new Highcharts.Chart({
            chart: { renderTo: 'container_$Cx', zoomType: 'xy'} ,
            title: { text: '$Cx - Med, Máx y Mín' },
            subtitle: { //text: 'Permite Zoom XY'
            },
            credits: { enabled: false },
            xAxis: { dateTimeLabelFormats: { day: '%e %b' }, type: 'datetime' },
            yAxis: {
                title: { text: null },
                min: Vcelda_min[0],
                max: Vcelda_max[0],
                plotBands: [{
                    from: Vcelda_franja_min[0],
                    to: Vcelda_franja_max[0],
                    color: 'rgba(21, 242, 13, 0.2)',
                    label: { text: '' }
                }]
            },
            tooltip: { crosshairs: true, shared: true, valueSuffix: 'V' },
            legend: { enabled: false },
            series: [
                {
                    name: 'AVG',
                    zIndex: 1,
                    color: Highcharts.getOptions().colors[1],
                    marker: { fillColor: 'white', lineWidth: 2, lineColor: Highcharts.getOptions().colors[1] },
                    tooltip: { valueSuffix: ' V', valueDecimals: 2 },
                    data: (function() {
                        var data = [];
                        ";
                        for ($i = 0; $i < count($rawdata2) - 1; $i++) {
                            echo "data.push([" . $rawdata2[$i]["Fecha"] . "," . $rawdata2[$i]["Med_$Cx"] . "]);";
                        }
                        echo "
                        return data;
                    })()
                },
                {
                    name: 'Máx-Mín',
                    type: 'arearange',
                    lineWidth: 0,
                    color: Highcharts.getOptions().colors[2],
                    fillOpacity: 0.3,
                    zIndex: 0,
                    tooltip: { valueSuffix: ' V', valueDecimals: 2 },
                    data: (function() {
                        var data = [];
                        ";
                        for ($i = 0; $i < count($rawdata2) - 1; $i++) {
                            echo "data.push([" . $rawdata2[$i]["Fecha"] . "," . $rawdata2[$i]["Max_$Cx"] . "," . $rawdata2[$i]["Min_$Cx"] . "]);";
                        }
                        echo "
                        return data;
                    })()
                }
            ]
        });";
    }
    ?>
});
</script>

<?php
include("pie.inc");
?>
