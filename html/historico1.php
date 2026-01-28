<?php
$titulo="Historico 1 Dia";
include ("cabecera.inc");



// Conexión a la base de datos
require('conexion.php');

// Consulta SQL para capturar los datos de 3 día

$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo, SOC, Ibat, Iplaca, Vbat, Vplaca, PWM, Wplaca,Vred, Wred, Temp,
          Wplaca - Vbat*Ibat - Wred as Wconsumo,
          Wh_placa/1000 as Kwh_placa, (Whp_bat-Whn_bat)/1000 as Kwh_bat,(Whp_red-Whn_red)/1000 as Kwh_red,
          (Wh_placa - Whp_bat + Whn_bat - Whp_red + Whn_red)/1000 as Kwh_consumo,
          Mod_bat * 1 as Modo, Aux1, Aux2
        FROM datos WHERE Tiempo >= (NOW()- INTERVAL 25 HOUR)
        ORDER BY Tiempo";


$result = $link->query($sql);

// Preparar arrays para los datos
$campos = ['Tiempo', 'SOC', 'Ibat', 'Iplaca', 'Vbat', 'Vplaca', 'PWM', 'Wplaca', 'Vred', 'Wred',
           'Temp', 'Wconsumo', 'Kwh_placa', 'Kwh_bat', 'Kwh_red', 'Kwh_consumo', 'Modo', 'Aux1', 'Aux2'];

$d_ = array_fill_keys($campos, []); // Inicializa los arrays vacíos

if ($result->num_rows > 0) {
	
    while ($row = $result->fetch_assoc()) {
		foreach ($campos as $campo) {
			if ($campo === 'Tiempo') {
				$d_[$campo][] = (int)$row[$campo];
			} elseif ($campo === 'Vplaca') {
				$d_[$campo][] = (int)$row[$campo]; 
			} elseif ($campo === 'Wplaca') {
				$d_[$campo][] = (int)$row[$campo]; 	
			} elseif ($campo === 'Wred') {
				$d_[$campo][] = (int)$row[$campo]; 
			} elseif ($campo === 'Vred') {
				$d_[$campo][] = (int)$row[$campo]; 
			} elseif ($campo === 'Wconsumo') {
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
    <title>Histórico 1 día</title>
	
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
    {name: 'Ibat',
      type: 'spline',
      visible: Ibat_visible,
      color: Highcharts.getOptions().colors[2],
      tooltip: {
        valueSuffix: ' A',
        valueDecimals: 1,
        },
      data: d_['Ibat'].map((value, i) => [d_['Tiempo'][i], value]),
    },
    {name: 'Iplaca',
      type: 'spline',
      visible: Iplaca_visible,
      color: Highcharts.getOptions().colors[3],
      tooltip: {
        valueSuffix: ' A',
        valueDecimals: 1,
        },
      data: d_['Iplaca'].map((value, i) => [d_['Tiempo'][i], value]),
    },
    {name: 'Vbat',
      type: 'spline',
      visible: Vbat_visible,
	  yAxis: 1,
      color: Highcharts.getOptions().colors[0],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 2,
        },
      data: d_['Vbat'].map((value, i) => [d_['Tiempo'][i], value]),
    },

    {name: 'SOC',
      type: 'spline',
      visible: SOC_visible,
      yAxis: 2,
      color: Highcharts.getOptions().colors[1],
      tooltip: {
        valueSuffix: ' %',
        valueDecimals: 2,
        },
     data: d_['SOC'].map((value, i) => [d_['Tiempo'][i], value]),
      
     },
    {name: 'PWM',
      type: 'spline',
      visible: PWM_visible,
      yAxis: 3,
      color: Highcharts.getOptions().colors[5],
      tooltip: {
        valueSuffix: ' ',
        valueDecimals: 0,
        },
      data: d_['PWM'].map((value, i) => [d_['Tiempo'][i], value]),
        
     },
     {name: 'Vplaca',
      type: 'spline',
      visible: Vplaca_visible,
      yAxis: 4,
      color: '#632D2D', //Highcharts.getOptions().colors[20],
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 0,
        },
      data: d_['Vplaca'].map((value, i) => [d_['Tiempo'][i], value]),
     },   
     {name: 'Wplaca',
      type: 'spline',
      visible: Wplaca_visible,
      yAxis: 5,
      color: '#E55FE5',
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 0,
        },
      data: d_['Wplaca'].map((value, i) => [d_['Tiempo'][i], value]),
      },     
     {name: 'Wred',
      type: 'spline',
      visible: Wred_visible,
      yAxis: 5,
      color: '#D882C9',
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 0,
        },
      data: d_['Wred'].map((value, i) => [d_['Tiempo'][i], value]),
      },             
     {name: 'Wconsumo',
      type: 'spline',
      visible: Wconsumo_visible,
      yAxis: 5,
      color: '#F39610',
      tooltip: {
        valueSuffix: ' W',
        valueDecimals: 0,
        },
      data: d_['Wconsumo'].map((value, i) => [d_['Tiempo'][i], value]),
      },         
     
     {name: 'Vred',
      type: 'spline',
      visible: Vred_visible,
      yAxis: 6,
      color: '#C55FE5',
      tooltip: {
        valueSuffix: ' V',
        valueDecimals: 0,
        },
      data: d_['Vred'].map((value, i) => [d_['Tiempo'][i], value]),
      },     

     {name: 'Kwh_placa',
      type: 'area',
      visible: Kwh_placa_visible,
      yAxis: 7,
      fillOpacity: 0.2,
      color: "#E55FE5",
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: d_['Kwh_placa'].map((value, i) => [d_['Tiempo'][i], value]),
     },     
     {name: 'Kwh_bat',
      type: 'area',
      visible: Kwh_bat_visible,
      yAxis: 8,
      fillOpacity: 0.2,
      color: "#7C75D7",
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: d_['Kwh_bat'].map((value, i) => [d_['Tiempo'][i], value]),
     },     
     {name: 'Kwh_red',
      type: 'area',
      visible: Kwh_red_visible,
      yAxis: 9,
      fillOpacity: 0.2,
      color: "#D882C9",
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: d_['Kwh_red'].map((value, i) => [d_['Tiempo'][i], value]),
      },
     {name: 'Kwh_consumo',
      type: 'area',
      visible: Kwh_consumo_visible,
      yAxis: 10,
      fillOpacity: 0.2,
      color: "#F39610",
      tooltip: {
        valueSuffix: ' Kwh',
        valueDecimals: 1,
        },
      data: d_['Kwh_consumo'].map((value, i) => [d_['Tiempo'][i], value]),
      },
  
     {name: 'Temp',
      type: 'spline',
      visible: Temp_visible,
      yAxis: 11,
      color: 'black',
      tooltip: {
        valueSuffix: ' ºC',
        valueDecimals: 1,
        },
      data: d_['Temp'].map((value, i) => [d_['Tiempo'][i], value]),
      },
     
     {name: 'Modo',
      type: 'spline',
      visible: Modo_visible,
      yAxis: 12,
      color: '#1604FA',
      tooltip: {
        valueSuffix: ' ',
        valueDecimals: 0,
        },
      data: d_['Modo'].map((value, i) => [d_['Tiempo'][i], value]),
      },
       
     {name: Nombre_Aux1,
      type: 'spline',
      visible: Aux1_visible,
      yAxis: 13,
      color: Highcharts.getOptions().colors[6],
      tooltip: {
        valueSuffix: Unidades_Aux1,
        valueDecimals: 2,
        },
      data: d_['Aux1'].map((value, i) => [d_['Tiempo'][i], value]),
      },     
     {name: Nombre_Aux2,
      type: 'spline',
      visible: Aux2_visible,
      yAxis: 14,
      color: Highcharts.getOptions().colors[8],
      tooltip: {
        valueSuffix: Unidades_Aux2,
        valueDecimals: 2,
        },
      data: d_['Aux2'].map((value, i) => [d_['Tiempo'][i], value]),
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

Highcharts.stockChart('container', {
	
	chart: {
      zoomType: 'xy',
      alignTicks: false,
      panning: true,
      panKey: 'shift'
      },
	
	credits: {
      enabled: false
      },
        yAxis: [
     {// ########## 0 - Valores eje Intensidad ######################
      visible: Eje_Intensidad,
      opposite: false,
      min: Escala_intensidad_min,
      max: Escala_intensidad_max,
      tickInterval: 20,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Ibat',
        rotation: 0,
        y: -5
        },
      plotLines: [{
        value: 0,
        width: 2,
        color: 'black',
        dashStyle: 'shortdash'
        }]
     },
     
     {// ########## 1 - Valores eje Vbat ######################
      visible: Eje_Vbat,
      opposite: false,
      min: Escala_Vbat_min,
      max: Escala_Vbat_max,
      tickInterval: 1,
      //gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Vbat',
        rotation: 0,
        y: -10
        },
      plotLines: [{
        // ########## Valores Linea Vabs #####################
        value: Vabs,
        width: 2,
        color: 'green',
        dashStyle: 'shortdash',
        label: {
          text: 'Vabs'
          }
       },{
        
        // ########## Valores Linea Vflot ######################
        value: Vflot,
        width: 2,
        color: 'red',
        dashStyle: 'shortdash',
        label: {
          y: 12,
          text: 'Vflot'
          }
       }]
     },
     
     {// ########## 2 - Valores eje SOC ######################
      visible: Eje_SOC,
      opposite: true,
      min: 20,
      max: 100 ,
      tickInterval: 20,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'SOC',
        rotation: 0,
        y: -10
        },
      plotLines: [{
        value: 100,
        width: 2,
        color: 'green',
        dashStyle: 'shortdash',
        label: {
          text: '100%'
          }
       },{
        value: 80,
        width: 2,
        color: 'red',
        dashStyle: 'shortdash',
        label: {
          text: '80%'
          }
       }]
      },
      
     {// ########## 3 - Valores eje PWM ######################
      visible: Eje_PWM,
      opposite: true,
      min: 0,
      max: Escala_PWM_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'PWM',
        rotation: 0,
        y: -10
        },
                  
     },
      
     {// ########## 4 - Valores eje Vplaca ######################
      visible: Eje_Vplaca,
      opposite: false,
      min: 0,
      max: Escala_Vplaca_max,
      tickInterval: 20,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      title: {
        align: 'high',
        offset: 0,
        text: 'Vplaca',
        rotation: 0,
        y: -5
        },
      },
   
     {// ########## 5 - Valores eje Wplaca, Wred, Wconsumo #################
      visible: Eje_Wplaca,
      opposite: true,
      min: Escala_Wred_min,
      max: Escala_Wred_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Wplaca',
        rotation: 0,
        y: -10
        },
      },
            
     
     {// ########## 6 - Valores eje Vred ######################
      visible: Eje_Vred,
      opposite: true,
      min: Escala_Vred_min,
      max: Escala_Vred_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Vred',
        rotation: 0,
        y: -10
        },
      },
          
     {// ########## 7 - Valores eje Kwh_placa ######################
      visible: Eje_Kwh_placa,
      opposite: true,
      min: 0,
      max: Kwh_placa_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Kwh_placa',
        rotation: 0,
        y: -10
        },
      },
  
     {// ########## 8 - Valores eje Kwh_bat ######################
      visible: Eje_Kwh_bat,
      opposite: true,
      min: Kwh_bat_min,
      max: Kwh_bat_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Kwh_bat',
        rotation: 0,
        y: -10
        },
      },
            
     {// ########## 9 - Valores eje Kwh_red ######################
      visible: Eje_Kwh_red,
      opposite: true,
      min: Kwh_red_min,
      max: Kwh_red_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Kwh_red',
        rotation: 0,
        y: -10
        },
      },
   
     {// ########## 10 - Valores eje Kwh_consumo ######################
      visible: Eje_Kwh_consumo,
      opposite: true,
      min: Kwh_consumo_min,
      max: Kwh_consumo_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Kwh_consumo',
        rotation: 0,
        y: -10
        },
      },
     
     {// ########## 11 - Valores eje Temp ######################
      visible: Eje_Temp,
      opposite: true,
      min: Temp_min,
      max: Temp_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Temp',
        rotation: 0,
        y: -10
        },
      },
     
     {// ########## 12 - Valores eje Modo ######################
      visible: Eje_Modo,
      opposite: true,
      min: 2,
      max: Modo_max,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      labels: {
        //align: 'left',
        y: 5
        },
      title: {
        align: 'high',
        offset: 0,
        text: 'Temp',
        rotation: 0,
        y: -10
        },
      },
    
     {// ########## 13 - Valores eje Aux1  ######################
      visible: Eje_Aux1,
      opposite: true,
      min: Aux1_min,
      max: Aux1_max,
      tickInterval: 1,
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
    
     {// ########## 14 - Valores eje Aux2  ######################
      visible: Eje_Aux2,
      opposite: true,
      min: Aux2_min,
      max: Aux2_max,
      tickInterval: 1,
      gridLineColor: 'transparent',
      minorGridLineColor: 'transparent',
      title: {
        align: 'high',
        offset: 0,
        text: Nombre_Aux2,
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
    rangeSelector: {
      buttons: [{
        type: 'hour',
        count: 12,
        text: '12h'
       }, {
        type: 'day',
        count: 1,
        text: '1día'
       }, {
        type: 'day',
        count: 2,
        text: '2días'
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


    series: series,
    // Otras configuraciones de Highcharts...
});
</script>

<?php
include ("pie.inc");
?>

