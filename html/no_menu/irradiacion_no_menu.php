<?php
// Definir el SQL y el título para este gráfico específico


$titulo = "Histórico 2 días antes - 3 dias despues";

$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, Wirradiacion, Wh_placa/1000 as Kwh_placa, Wh_bat/1000 as Kwh_bat, Wh_red/1000 as Kwh_red, Wh_consumo/1000 as Kwh_consumo, SOC, Temperatura
        FROM TABLA_IRRADIACION WHERE Tiempo >= (NOW() - INTERVAL 2 DAY)
        ORDER BY Tiempo";

$rangeSelectorOptions = [
    'buttons' => [
        ['type' => 'day', 'count' => 5, 'text' => '5d'],
        ['type' => 'day', 'count' => 7, 'text' => '7d'],
        ['type' => 'day', 'count' => 10, 'text' => '10d'],
        ['type' => 'all', 'text' => 'Todo']
    ],
    'selected' => 0,
    'inputEnabled' => false // Opcional, desactiva el selector manual de fechas
];


// Conexión a la base de datos
require('../conexion.php');

// Variables que se deben definir en el archivo específico
if (!isset($sql) || !isset($titulo)) {
    die("Debe definir la consulta SQL y el título.");
}

$result = $link->query($sql);

// Preparar arrays para los datos
$campos = ['Tiempo', 'Wirradiacion', 'Kwh_placa', 'Kwh_bat', 'Kwh_red', 'Kwh_consumo', 'SOC', 'Temperatura'];

$d_ = array_fill_keys($campos, []); // Inicializa los arrays vacíos


if ($result->num_rows > 0) {
	
    while ($row = $result->fetch_assoc()) {
		foreach ($campos as $campo) {
			if ($campo === 'Tiempo') {
				$d_[$campo][] = (int)$row[$campo];
			} elseif ($campo === 'Kwh_placa') {
				$d_[$campo][] = round((float)$row[$campo], 1); 
			} elseif ($campo === 'Kwh_bat') {
				$d_[$campo][] = round((float)$row[$campo], 1); 
			} elseif ($campo === 'Kwh_consumo') {
				$d_[$campo][] = round((float)$row[$campo], 1); 
			} elseif ($campo === 'Kwh_red') {
				$d_[$campo][] = round((float)$row[$campo], 1); 
			} 
			else {
				$d_[$campo][] = (float)$row[$campo];
			}
        }
    }
    // Mostrar los datos capturados
    //echo '<pre>';
    //print_r($d_);
    //echo '</pre>';
} else {
    echo "0 resultados";
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
	<script src="https://code.highcharts.com/themes/grid.js"></script>
</head>
<body>
<div id="container" style="width:100%; height:500px; margin-left: 5; float: left"></div>


<script>
// Datos del servidor en formato JSON
const campos = <?php echo json_encode($campos); ?>; // Aquí se pasan los nombres de los campos
const d_ = <?php echo json_encode($d_); ?>; // Datos capturados


// Crear las series dinámicamente con configuraciones personalizadas
const series = [
    {name: 'Wirradiacion',
      type: 'spline',
      yAxis: 1,
      visible: true,
      color: Highcharts.getOptions().colors[2],
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 0,
        },
      data: d_['Wirradiacion'].map((value, i) => [d_['Tiempo'][i], value]),
    },
    {name: 'Kwh_placa',
      type: 'spline',
      yAxis: 0,
      visible: true,
      color: Highcharts.getOptions().colors[3],
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: d_['Kwh_placa'].map((value, i) => [d_['Tiempo'][i], value]),
    },
    {name: 'Kwh_bat',
      type: 'spline',
      visible: false,
	  yAxis: 0,
      color: Highcharts.getOptions().colors[0],
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: d_['Kwh_bat'].map((value, i) => [d_['Tiempo'][i], value]),
    },
    {name: 'Kwh_red',
      type: 'spline',
      visible: false,
	  yAxis: 0,
      color: Highcharts.getOptions().colors[4],
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: d_['Kwh_red'].map((value, i) => [d_['Tiempo'][i], value]),
    },
    {name: 'Kwh_consumo',
      type: 'spline',
      visible: false,
	  yAxis: 0,
      color: Highcharts.getOptions().colors[6],
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: d_['Kwh_consumo'].map((value, i) => [d_['Tiempo'][i], value]),
    },
    
    {name: 'SOC',
      type: 'spline',
      visible: false,
      yAxis: 2,
      color: Highcharts.getOptions().colors[1],
      tooltip: {
        valueSuffix: ' %',
        valueDecimals: 2,
        },
     data: d_['SOC'].map((value, i) => [d_['Tiempo'][i], value]),
      
     },

     {name: 'Temperatura',
      type: 'spline',
      visible: false,
      yAxis: 2,
      color: 'black',
      tooltip: {
        valueSuffix: ' ºC',
        valueDecimals: 1,
        },
      data: d_['Temperatura'].map((value, i) => [d_['Tiempo'][i], value]),
      },    
      
];

// Crear el gráfico

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

let grafica = Highcharts.stockChart('container', {
//Highcharts.stockChart('container', {
	
	chart: {
      zoomType: 'xy',
      alignTicks: false,
      panning: true,
      panKey: 'shift',
      events: {
        load: function () {
            const chart = this;

            // Calcula el rango inicial
            const min = chart.xAxis[0].dataMin;
            const max = chart.xAxis[0].dataMax;

            // Obtén los datos del botón seleccionado por defecto
            const selectedButton = chart.options.rangeSelector.selected;
            const button = chart.options.rangeSelector.buttons[selectedButton];

            // Si no es "Todo", calcula el rango inicial y ajústalo
            if (button.type !== 'all') {
                const range = min + button.count * 24 * 3600 * 1000;
                chart.xAxis[0].setExtremes(min, Math.min(range, max));
            }

            // Sobrescribir el comportamiento del rangeSelector
            const customButtons = chart.options.rangeSelector.buttons.map(button => {
                return {
                    type: button.type,
                    count: button.count,
                    text: button.text,
                    events: {
                        click: function () {
                            // Calcula el rango desde el inicio
                            let range;
                            if (button.type === 'all') {
                                range = max; // Muestra todo el rango
                            } else {
                                range = min + button.count * 24 * 3600 * 1000;
                            }

                            // Actualiza los extremos
                            chart.xAxis[0].setExtremes(min, Math.min(range, max));
                        }
                    }
                };
            });

            // Actualizar rangeSelector con los nuevos botones
            chart.update({
                rangeSelector: {
                    buttons: customButtons
                }
            });
        }
      }
      
      
    },
	
	credits: {
      enabled: false
      },
        yAxis: [
     {// ########## 0 - Valores eje KWh ######################
      visible: true,
      opposite: true,
      min: 0,
      max: 10,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: -15,
        text: 'Kwh',
        rotation: 0,
        y: -5
        },
      },
     
     {// ########## 1 - Valores eje Watios irradiacion #######
      visible: true,
      opposite: false,
      min: 0,
      max: 1000,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'W',
        rotation: 0,
        y: -10
        },
      plotLines: [{
        value: 500,
        width: 2,
        color: 'red',
        dashStyle: 'shortdash',
        label: {
           text: '500W / 5Kwh'
        }
      }] 

     },
    
     {// ########## 2 - SOC - Temp  ######################
      visible: false,
      opposite: false,
      min: 0,
      max: 100,
      tickInterval: 10,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      title: {
        align: 'high',
        offset: 0,
        text: Nombre_Aux1,
        rotation: 0,
        y: -5
        },
      },
    
      
     ],

    xAxis: {
      dateTimeLabelFormats: { day: '%e %b' },
      type: 'datetime'
      },
    legend: {
      enabled: true
      },

	rangeSelector: <?php echo json_encode($rangeSelectorOptions); ?>,  // Aquí se inyecta el parámetro del selector

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


    series: series,
    // Otras configuraciones de Highcharts...
});



</script>
</body>
</html>










