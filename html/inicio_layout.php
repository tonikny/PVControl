<?php
$titulo = "Inicio";
include("cabecera.inc");
?>



<?php
require('conexion.php');
//Coger datos grafica tiempo real
$sql = "SELECT * FROM (SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo,  Ibat, Iplaca, Vbat, PWM, Vplaca
        FROM datos   
        ORDER BY id DESC
        LIMIT 240)
		a ORDER BY Tiempo ASC";

if ($result = mysqli_query($link, $sql)) {

  $i = 0;
  while ($row = mysqli_fetch_assoc($result)) {
    $rawdata3[$i] = $row;
    $i++;
  }
} else {
  echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
}



//Datos de FV en tabla equipos
$dataFV = [];
$sql = "SELECT * FROM equipos WHERE `id_equipo` IN ('FV')";

if($result = mysqli_query($link, $sql)){
    while ($row = mysqli_fetch_array($result)){
        $dataFV[$row[0]]=json_decode($row[2], true);
        $dataFV[$row[0]]["tiempo"]=$row[1];
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }

if(time() - strtotime($dataFV['FV']['tiempo']) > 60 ){
      echo "datos Antiguos en FV=> ";
      print json_encode($dataFV['FV']['tiempo'], JSON_NUMERIC_CHECK);
      echo "<br />";
      }


//Datos de BMS en tabla equipos
$dataC = [];
$sql = "SELECT * FROM equipos WHERE SUBSTRING(`id_equipo`, 1, 3) IN ('BMS') ORDER BY id_equipo";

if($result = mysqli_query($link, $sql)){
    while ($row = mysqli_fetch_array($result)){
        $dataC[$row[0]]=json_decode($row[2], true);
        $dataC[$row[0]]["tiempo"]=$row[1];
    }
} else {
    echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
    }
    
mysqli_close($link); 

$nbms = count($dataC);

if($nbms != 0 ){
  //echo "Numero de BMS ".count($dataC)."<br />";
  //print json_encode($dataC, JSON_NUMERIC_CHECK);
  //echo "<br />";

  foreach ($dataC as $clave => $valor) {
   
    if(time() - strtotime($dataC[$clave]['tiempo']) > 60 ){
      echo "datos Antiguos en ".$clave."=> ";
      print json_encode($dataC[$clave]['tiempo'], JSON_NUMERIC_CHECK);
      echo "<br />";
      }
    
  }
}
?>

<!-- Latest compiled and minified JavaScript -->
<script src="https://code.jquery.com/jquery.js"></script>

<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/highcharts-3d.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>


<div style="display: flex; flex-direction: row">
  <div class="divTable" style="color:black; width: 10%; height: 350px; margin-left: 1%; margin-right:2%; float: left">
    <div class="divTableBody">
      <div class="divTableRow">
        <div class="divTableCell">Wh Placa</div>
        <div id="Wh_placa" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div class="divTableCell">Wh Cons</div>
        <div id="Wh_cons" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div class="divTableCell">Wh Bat+</div>
        <div id="Whp_bat" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div class="divTableCell">Wh Bat-</div>
        <div id="Whn_bat" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div class="divTableCell">SOC máx</div>
        <div id="SOC_max" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div class="divTableCell">SOC mín</div>
        <div id="SOC_min" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div class="divTableCell">Vbat mín</div>
        <div id="Vbat_min" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div class="divTableCell">Vbat_máx</div>
        <div id="Vbat_max" class="divTableCell">&nbsp;</div>
      </div>

      <div class="divTableRow">
        <div class="divTableCell">Mod_bat</div>
        <div id="Mod_bat" class="divTableCell">&nbsp;</div>
      </div>

      <div class="divTableRow">
        <div id="Aux1n" class="divTableCell">Aux1</div>
        <div id="Aux1" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div id="Aux2n" class="divTableCell">Aux2</div>
        <div id="Aux2" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div id="Aux3n" class="divTableCell">Aux3</div>
        <div id="Aux3" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div id="Aux4n" class="divTableCell">Aux4</div>
        <div id="Aux4" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div id="Aux5n" class="divTableCell">Aux5</div>
        <div id="Aux5" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div id="Aux6n" class="divTableCell">Aux6</div>
        <div id="Aux6" class="divTableCell">&nbsp;</div>
      </div>
      <div class="divTableRow">
        <div id="Aux7n" class="divTableCell">Aux7</div>
        <div id="Aux7" class="divTableCell">&nbsp;</div>
      </div>
    </div>
  </div>
  
  <div class="layout" style="width: 85%; position: relative">
    <object data="svg/Inicio.svg" type="image/svg+xml" height="535" id="InicioSvg" style="position: absolute; left:0; right:0; margin-right: auto; margin-left:auto"></object>
	<object data="svg/Bubble_bat.svg" type="image/svg+xml" height="535" id="BubbleSvg_bat" style="position: absolute; top: 0; left:0; right:0; margin-right: auto; margin-left:auto"></object>
	<object data="svg/Bubble_placa.svg" type="image/svg+xml" height="535" id="BubbleSvg_placa" style="position: absolute; top: 0; left:0; right:0; margin-right: auto; margin-left:auto"></object>
	<object data="svg/Bubble_inv.svg" type="image/svg+xml" height="535" id="BubbleSvg_inv" style="position: absolute; top: 0; left:0; right:0; margin-right: auto; margin-left:auto"></object>
	<object data="svg/Bubble_cons.svg" type="image/svg+xml" height="535" id="BubbleSvg_cons" style="position: absolute; top: 0; left:0; right:0; margin-right: auto; margin-left:auto"></object>
  </div>

</div>

 <br></br>

<?php
foreach ($dataC as $clave => $valor) {
    echo "<div id='container_".$clave."' style='width: 100%; height: 200px; margin-left: 0%; float: left'></div>"."\n";
}
?>

<div id="container_reles" style="width: 100%; height: 200px; margin-left: 0%;float: left"></div>
<div id="grafica_t_real" style="width: 100%; height: 280px; margin-left: 0%; margin-bottom: 0% ;float: left"></div>

<br>

<br style="clear:both;" />

<script>
  $(function () {

    recibirDatosFV();

    if (typeof color_rotulos == 'undefined') { color_rotulos = '#18F905' }; // Verde claro 

    Highcharts.setOptions({

		global: {
			useUTC: false
			},
		lang: {
			months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
			weekdays: ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'],
			shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
			rangeSelectorFrom: "Desde",
			rangeSelectorTo: "A",
			printChart: "Imprimir gráfico",
			loading: "Cargando..."
			},
		credits: {
			enabled: false
			},
		pane: {
			background: {
				backgroundColor: 'white',//#DDD null = transp
				borderWidth: 0,
				outerRadius: '105%',
				//innerRadius: '103%'
				}
			},
		yAxis: { 
            showLastLabel:false,
            showFirstLabel:false,
            minorTickInterval: null,
            minorTickWidth: 1,
            minorTickLength: 10,
            minorTickPosition: 'inside',
            minorTickColor: '#666',
            tickPixelInterval: 0, //Intensidad_max,
            //tickPositions: [0],
            tickWidth: 1,
            tickPosition: 'inside',
            lineWidth: 1,
            tickLength: 10,
            tickColor: '#666',
            labels: {
                //enabled: false,
                //step: 2,
                //distance: -15,
                //rotation: 'false' // 'auto'
				},      
			},
        navigation: {
            buttonOptions: {
                enabled: false
				}
			},
        tooltip: {
            enabled: false
			},
		});

    chart_reles = new Highcharts.Chart({
      chart: {
        renderTo: 'container_reles',
        backgroundColor: null,//'#ffffff',//'#f2f2f2',
        borderColor: 'black',
		borderWidth: 0,
		plotBorderWidth: 0,
        type: 'column',
        shadow: false,
		plotShadow: false,
        options3d: {
          enabled: false,
          alpha: 0,
          beta: 10,
          depth: 100,
          viewDistance: 25,
          //backgroundColor: null,//'#ffffff',//'#f2f2f2',
          //borderColor: null,

        },
      },

      plotOptions: {
        column: {
          dataLabels: {
            enabled: true,
            inside: true, //valor de la columna en el interior
            crop: false,
            overflow: 'none',
            borderWidth: 1,
            //borderColor: 'red',
          },
          enableMouseTracking: false
        }
      },

      credits: {
        enabled: false
      },
      title: {
        y: 20,
        text: 'SITUACION RELES'
      },
      subtitle: {
        text: null
      },
      xAxis: {
		  gridLineWidth: 0,
        labels: {
          y: 10,
          align: 'right',
          reserveSpace: true,
        },
        categories: [] //Nombre_Reles()
      },
      yAxis: {
        gridLineWidth: 0,
        minorGridLineWidth: 0,
        gridLineColor: 'transparent',
        min: 0,
        max: 100,
        //minPadding:0,
        //maxPadding:0,
		lineWidth: 0,
		tickWidth: 0,
        tickInterval: 10,
        allowDecimals: false,
        visible: true, //desactivar grid i resta
        labels: {
          enabled: false
        },
        title: {
          enabled: false
        }
      },

      series: [{
        name: 'Estado Relés',
        colorByPoint: false,//Color aleatorio para cada columna de un rele
        color: '#2b5dc7',
        borderColor: '#303030',
        data: [],

        dataLabels: {
          enabled: true,
          formatter: function () {
            return Highcharts.numberFormat(this.y, 0) + " %"
          }
        }
      }],

      legend: {
        enabled: false,
        layout: 'vertical',
        floating: true,
        align: 'center',
        verticalAlign: 'center',
        //x: -100,
        y: 30,
        borderWidth: 0
      },
      tooltip: {
        formatter: function () {
          return '<b>' + this.series.name + '</b><br/>' +
            this.point.y + ' ' + this.point.name.toLowerCase();
        }
      }

    });

<?php

$ng = 0; // nº de grafico

foreach ($dataC as $clave => $valor) {
    
    echo "

    chart_bms_".$clave." = new Highcharts.Chart({
      chart: {
        renderTo: 'container_".$clave."',
        backgroundColor: null,//'#ffffff',//'#f2f2f2',
        borderColor: null,
        type: 'column',
		    plotShadow: false,
		    plotBorderWidth: 0,
        shadow: false,//true,false,
        options3d: {
          enabled: false,
          alpha: 0,
          beta: 0,//10,
          depth: 100,
          viewDistance: 0 //25,
        },
      },
      
      plotOptions: {
        column: {
          dataLabels: {
            enabled: true,
            //inside: false, //valor de la columna en el interior
            crop: false,
            allowOverlap: true,//false,
            overflow: 'allow',//'none',
          },
          enableMouseTracking: true,
          grouping: false,
          shadow: false,
          borderWidth: 0
        }
      },
      
       credits: {
        enabled: false
      },
      
      title: {
        y: 25,
        text: '".$clave."'
      },
      subtitle: {
        y: 40,
        text: 'xx'//null
      },
      xAxis: {
		  visible: true,
		  gridLineWidth: 0, //lineas entre columnas
      minorGridLineWidth: 0,
		  tickWidth: 0,
        labels: {
          y: 15,
          align: 'center',
          reserveSpace: false,
        },
        categories:";
        print json_encode($dataC[$clave]['Nombres'], JSON_NUMERIC_CHECK);
        echo "
        
        
      },
      
      yAxis: {
		
        gridLineWidth: 0,
        minorGridLineWidth: 0,
        gridLineColor: 'transparent',
		    showFirstLabel: true,
		    showLastLabel: true,
		    startOnTick: true,
        min: Vcelda_min[".$ng."],
        max: Vcelda_max[".$ng."],
        //minPadding:0,
        //maxPadding:0,
        tickWidth: 0,
        tickInterval: 0.2,
        allowDecimals: false,
        lineWidth: 0,
        visible: true, //desactivar grid
        labels: {
          enabled: false
        },
        title: {
          enabled: false
        },

        plotBands: [{
          from: Vcelda_franja_min[".$ng."], //Vcelda_franja_inferior,
          to: Vcelda_franja_max[".$ng."], //Vcelda_franja_superior,
          color: 'rgba(68, 170, 213, 0.2)',
          label: {
            text: ''
          }
        }],

      },

      series: [
        {
          name: 'V max',
		      visible: false,
          color: 'rgba(43,132,221,1)', //'rgba(243,41,45,1)',
          //color: 'rgba(165,170,217,1)',
          pointPadding: 0.45,
          pointPlacement: -0.3,
          colorByPoint: false,//Color aleatorio para cada columna de un rele
          borderColor: '#303030',
          data: ";
           print json_encode($dataC[$clave]['Max'], JSON_NUMERIC_CHECK);
          echo ",
		  
          dataLabels: {
            enabled: true,
            inside: false,
            rotation: 270,
            y: -20,
            format: \"{point.y:.2f}\"
          }
        },
		
		
        {
          name: 'Vcelda',
          colorByPoint: false,//Color aleatorio para cada columna de un rele
          color: 'blue', //'rgba(43,132,221,1)',
          opacity: 1,
          pointPadding: 0.1,
          pointPlacement: 0,
          borderColor: '#303030',
		      borderRadius: 1,
          data: ";
           print json_encode($dataC[$clave]['Vceldas'], JSON_NUMERIC_CHECK);
          echo ",
		      showInLegend: false,
          dataLabels: {
            borderRadius: 5,
            backgroundColor: null, //'rgba(252, 255, 197, 0.7)',
            borderWidth: 0,
            borderColor: 'black',
            padding: 1,

            enabled: true,
            inside: true,
            align: 'center',
            style: {
              fontWeight: 'bold',
              fontSize: '14px',
              color: 'white'
            },
            y: 0,
            format: \"{point.y:.2f}\"

          }
        },
        {
          name: 'V min',
		      visible: false,
          color: 'rgba(43,132,221,1)', //'rgba(243,240,41,1)',
          pointPadding: 0.45,
          pointPlacement: 0.3,
          colorByPoint: false,//Color aleatorio para cada columna de un rele
          borderColor: '#303030',
          data: ";
           print json_encode($dataC[$clave]['Min'], JSON_NUMERIC_CHECK);
          echo ",
          dataLabels: {
            enabled: true,
            inside: false,
            allowOverlap: true,
            rotation: 270,
            y: -25,
            align: 'center',
            format: \"{point.y:.2f}\"
          }
        },
      ],

    navigation: {
        buttonOptions: {
          enabled: false
        }
      },
      
    legend: {
        enabled: true,
		    itemStyle: {
			    display: 'none',
		    },
        layout: 'horizontal',
        floating: true,
        align: 'left',
        verticalAlign: 'center',
        //x: -100,
        y: 0,
		    itemDistance: 0,
        borderWidth: 0
      },
      
      tooltip: {
        formatter: function () {
          return '<b>' + this.series.name + '</b><br/>' +
            this.point.y + ' V';
        }
      }
      
      
    });
   ";
  $ng++;
  
  }
?>

    grafica_t_real = new Highcharts.Chart({
      chart: {
        renderTo: 'grafica_t_real',
        backgroundColor: null,//'#ffffff',//'#f2f2f2',
        borderColor: null,
		shadow: false,
		plotShadow: false,
		plotBackgroundColor: 'rgba(68, 170, 213, 0.1)',
        plotBorderWidth: 1,
        zoomType: 'xy',
        alignTicks: false,
        animation: Highcharts.svg, // don't animate in old IE
        //marginRight: 10,
      },
      title: {
        text: '',
        floating: true,
        y: 12,
        x: -0
      },
      subtitle: {
        text: 'Prueba Dinamica',
        floating: true,
        align: 'right',
        verticalAlign: 'bottom',
        y: 25,
      },
      credits: {
        enabled: false
      },
      xAxis: {
        type: 'datetime',
		gridLineWidth: 0,
      },
      yAxis: [
        {// ########## Valores eje Intensidad ####################
			visible: true,
          gridLineWith: 0,
          min: Escala_intensidad_min,
          max: Escala_intensidad_max,
          opposite: true,
          tickInterval: 40,
          //gridLineColor: '',
          minorGridLineColor: 'transparent',
		  tickWidth: 0,
		  lineWidth: 0,
          //endOnTick: true,
          //maxPadding: 0.2,
          //tickAmount: 7,
          labels: {
            format: '{value} A',
            style: {
              color: Highcharts.getOptions().colors[2]
            }
          },
          title: {
            text: null,
          },
          //opposite: false,
        },
        { // ########## Valores eje Vbat ######################
		// visible: false,
          opposite: false,
          min: Escala_Vbat_min,
          max: Escala_Vbat_max,
          tickInterval: 1,
		  tickWidth: 0,
          gridLineColor: 'transparent',
		  gridLineWith: 0,
          minorGridLineColor: 'transparent',
		  lineWidth: 0,
          labels: {
            format: '{value} V',
            style: {
              color: Highcharts.getOptions().colors[0]
            }
          },
          title: {
            text: '',
          },
          plotLines:
            [{ // ########## Valores Linea Vabs #####################
			
              value: Vabs,
              width: 1,
              color: 'green',
              dashStyle: 'longdash',
              label: {
                text: 'Vabs'
              }
            },
            {// ########## Valores Linea Vflot ######################
			
              value: Vflot,
              width: 1,
              color: 'red',
              dashStyle: 'longdash',
              label: {
                text: 'Vflot'
              }
            }]
        },
        { // ########## Valores eje PWM ######################
		visible: false,
          opposite: true,
          min: 0,
          max: Escala_PWM_max,
          tickInterval: 20,
          gridLineColor: 'transparent',
          minorGridLineColor: 'transparent',

          title: {
            text: '',
          },
        },
        { // ########## Valores eje Vplaca ######################
		visible: false,
          opposite: false,
          min: 0,
          max: Escala_Vplaca_max,
          tickInterval: 20,
          gridLineColor: 'transparent',
          minorGridLineColor: 'transparent',

          title: {
            text: '',
          },
        }
      ],

      tooltip: {
		  enabled: true,
        crosshairs: true,
        shared: true,
        valueDecimals: 2
      },
      navigation: {
        buttonOptions: {
          enabled: false
        }

      },
      plotOptions: {
        series: {
          marker: {
            enabled: false
          }
        }
      },

      legend: {
        layout: 'horizontal',
        floating: true,
        align: 'left',
        verticalAlign: 'bottom',
        //x: -100,
        y: 20,
        borderWidth: 0
      },
      series: [
        {
          name: 'Ibat',
          yAxis: 0,
          color: Highcharts.getOptions().colors[2],
          data: (function () {
            var data = [];
                <?php
                for ($i = 0; $i < count($rawdata3); $i++) {
                  ?>
                  data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["Ibat"]; ?>]);
                <?php } ?>
              return data;
              }) ()

            },

  {
    name: 'IPlaca',
      yAxis: 0,
        color: Highcharts.getOptions().colors[3],
          data: (function () {
            var data = [];
                <?php
                for ($i = 0; $i < count($rawdata3); $i++) {
                  ?>
                  data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["Iplaca"]; ?>]);
                <?php } ?>
              return data;
          })()

  },
  {
    name: 'Vbat',
      color: Highcharts.getOptions().colors[0],
        yAxis: 1,
          data: (function () {
            var data = [];
                <?php
                for ($i = 0; $i < count($rawdata3); $i++) {
                  ?>
                  data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["Vbat"]; ?>]);
                <?php } ?>
              return data;
          })()

  },
  {
    name: 'VPlaca',
      yAxis: 3,
	  visible: false,
        data: (function () {
          var data = [];
                <?php
                for ($i = 0; $i < count($rawdata3); $i++) {
                  ?>
                data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["Vplaca"]; ?>]);
                <?php } ?>
                    return data;
        }())
  },
  {
    name: 'PWM',
      yAxis: 2,
        color: Highcharts.getOptions().colors[4],
          data: (function () {
            var data = [];
                <?php
                for ($i = 0; $i < count($rawdata3); $i++) {
                  ?>
                  data.push([<?php echo $rawdata3[$i]["Tiempo"]; ?>,<?php echo $rawdata3[$i]["PWM"]; ?>]);
                <?php } ?>
              return data;
          })()
  },
            ]
                                
      });



  function recibirDatosFV() {
    $.ajax({
      url: 'datos_fv.php',
      success: function (data) {
        try {
          //console.log(data)
          fecha = data['FV']['tiempo'];

          //Vbat,Ibat,Wbat,Whp_bat,Whn_bat,Vbat_min,Vbat_max
          Vbat = data['FV']['Vbat'];
          Ibat = data['FV']['Ibat'];
          Wbat = data['FV']['Wbat'];
          Whp_bat = data['FV']['Whp_bat'];
          Whn_bat = data['FV']['Whn_bat'];
          Wh_bat = Whp_bat - Whn_bat;
          Vbat_min_dia = data['FV']['Vbat_min'];
          Vbat_max_dia = data['FV']['Vbat_max'];

          //DS,SOC,SOC_min,SOC_max
          DS = data['FV']['DS'];
          SOC = data['FV']['SOC'];
          SOC_min_dia = data['FV']['SOC_min'];
          SOC_max_dia = data['FV']['SOC_max'];

          //Mod_bat,Tabs,Tflot,Tflot_bulk
          Mod_bat = data['FV']['Mod_bat'];
          Tabs = data['FV']['Tabs'];
          Tflot = data['FV']['Tflot'];
          Tflot_bulk = data['FV']['Tflot_bulk'];

          // Vplaca,Iplaca,Wplaca,Wh_placa
          Vplaca = data['FV']['Vplaca'];
          Iplaca = data['FV']['Iplaca'];
          Wplaca = data['FV']['Wplaca']
          Wh_placa = data['FV']['Wh_placa'];

          //(Vred,Wred,Whp_red,Whn_red,Vred_min,Vred_max,EFF,EFF_min,EFF_max)
          Vred = data['FV']['Vred'];
          Wred = data['FV']['Wred'];
          Whp_red = data['FV']['Whp_red'];
          Whn_red = data['FV']['Whn_red'];
          Wh_red = Whp_red - Whn_red;
          Vred_min_dia = data['FV']['Vred_min'];
          Vred_max_dia = data['FV']['Vred_max'];
          EFF = data['FV']['EFF'];
          EFF_min_dia = data['FV']['EFF_min'];
          EFF_max_dia = data['FV']['EFF_max'];

          if (Vred == 0) { Ired = 0; }
          else { Ired = Wred / Vred; };

          //Wconsumo, Wh_consumo
          Wconsumo = data['FV']['Wconsumo'];
          Wh_consumo = data['FV']['Wh_consumo'];

          //Temp,int(PWM)
          Temp = data['FV']['Temp'];
          PWM = data['FV']['PWM'];

          //Aux1,Aux2,Aux3,Aux4....
          Aux1 = data['FV']['Aux1'];
          Aux2 = data['FV']['Aux2'];
          Aux3 = data['FV']['Aux3'];
          Aux4 = data['FV']['Aux4'];
          Aux5 = data['FV']['Aux5'];
          Aux6 = data['FV']['Aux6'];
          Aux7 = data['FV']['Aux7'];
		  
		  Iinv = Ibat - Iplaca;
		  
		  
		  
		Bubble_bat = document.getElementById("BubbleSvg_bat").contentDocument;
		Bubble_placa = document.getElementById("BubbleSvg_placa").contentDocument;
        Bubble_inv = document.getElementById("BubbleSvg_inv").contentDocument;
		Bubble_cons = document.getElementById("BubbleSvg_cons").contentDocument;
		Inicio = document.getElementById("InicioSvg").contentDocument;
		
		Inicio.SetBatteryStateOfCharge(SOC, 620.0);
		Inicio.Animation(Ibat,Ibat,Temp,'Bateria');
		Inicio.Animation(Wplaca,Iplaca,Vplaca,'Placa');
		Inicio.Animation(Wconsumo,Iinv,Iinv,'Inversor');
		Inicio.Animation(Wconsumo,Iinv,Iinv,'Consumo');
		
		Bubble_bat.Animation(Ibat,70);
		Bubble_placa.Animation(Iplaca,70);
		Bubble_inv.Animation(Iinv,70);
		Bubble_cons.Animation(Iinv,70);
	
		

          // Actualizacion Grafica a tiempo real
          grafica_t_real.setTitle({
            text: 'Fecha: ' + fecha
          });
          grafica_t_real.setSubtitle({
            text: 'PWM=' + PWM
          });

          x = (new Date()).getTime(); // current time

          grafica_t_real.series[0].addPoint([x, Ibat], true, true); //Ibat
          grafica_t_real.series[1].addPoint([x, Iplaca], true, true); //Iplaca
          grafica_t_real.series[3].addPoint([x, Vplaca], true, true); //Vplaca
          //grafica_t_real.series[3].addPoint([x, Aux1], true, true); //Aux1
          grafica_t_real.series[4].addPoint([x, PWM], true, true); //PWM
          grafica_t_real.series[2].addPoint([x, Vbat], true, true); //Vbat

          //Valores de la tabla
          $("#Wh_placa").text(Wh_placa + " Wh");
          $("#Wh_cons").text(Wh_consumo + " Wh")
          $("#Whp_bat").text(Whp_bat + " Wh");
          $("#Whn_bat").text(Whn_bat + " Wh");
          $("#SOC_min").text(SOC_min_dia + "%");
          $("#SOC_max").text(SOC_max_dia + "%");
          $("#Vbat_min").text(Vbat_min_dia + "V");
          $("#Vbat_max").text(Vbat_max_dia + "V");

          $("#Mod_bat").text(Mod_bat);

          $("#Aux1").text(Aux1 + Unidades_Aux1);
          $("#Aux1n").text(Nombre_Aux1);

          $("#Aux2").text(Aux2 + Unidades_Aux2);
          $("#Aux2n").text(Nombre_Aux2);

          $("#Aux3").text(Aux3 + Unidades_Aux3);
          $("#Aux3n").text(Nombre_Aux3);

          $("#Aux4").text(Aux4 + Unidades_Aux4);
          $("#Aux4n").text(Nombre_Aux4);

          $("#Aux5").text(Aux5 + Unidades_Aux5);
          $("#Aux5n").text(Nombre_Aux5);

          $("#Aux6").text(Aux6 + Unidades_Aux6);
          $("#Aux6n").text(Nombre_Aux6);

          $("#Aux7").text(Aux7 + Unidades_Aux7);
          $("#Aux7n").text(Nombre_Aux7);

          //Evaluacion del color de la celda segun la variable ... (Colores definidos en inicio.css)
          if (Mod_bat == "ABS") {
            document.getElementById("Mod_bat").className = "ABS";
          }
          else if (Mod_bat == "BULK") {
            document.getElementById("Mod_bat").className = "BULK";
          }
          else if (Mod_bat == "FLOT") {
            document.getElementById("Mod_bat").className = "FLOT";
          }
          else if (Mod_bat == "EQU") {
            document.getElementById("Mod_bat").className = "EQU";
          };

          //SOC_min_dia
          if (SOC_min_dia <= SOC_min_rojo) {
            document.getElementById("SOC_min").className = "rojo";
          }
          else if (SOC_min_dia < SOC_min_naranja) {
            document.getElementById("SOC_min").className = "naranja";
          }
          else {
            document.getElementById("SOC_min").className = "verde";
          };

          //SOC_max_dia
          if (SOC_max_dia <= SOC_max_rojo) {
            document.getElementById("SOC_max").className = "rojo";
          }
          else if (SOC_max_dia < SOC_max_naranja) {
            document.getElementById("SOC_max").className = "naranja";
          }
          else {
            document.getElementById("SOC_max").className = "verde";
          };

          //Vbat_min_dia
          if (Vbat_min_dia <= Vbat_min_rojo) {
            document.getElementById("Vbat_min").className = "rojo";
          }
          else if (Vbat_min_dia < Vbat_min_naranja) {
            document.getElementById("Vbat_min").className = "naranja";
          }
          else {
            document.getElementById("Vbat_min").className = "verde";
          };

          //Vbat_max_dia
          if (Vbat_max_dia >= Vbat_max_alta_rojo) {
            document.getElementById("Vbat_max").className = "rojo";
          }
          else if (Vbat_max_dia >= Vbat_max_alta_naranja) {
            document.getElementById("Vbat_max").className = "naranja";
          }
          else if (Vbat_max_dia <= Vbat_max_baja_rojo) {
            document.getElementById("Vbat_max").className = "rojo";
          }
          else if (Vbat_max_dia <= Vbat_max_baja_naranja) {
            document.getElementById("Vbat_max").className = "naranja";
          }
          else {
            document.getElementById("Vbat_max").className = "verde";
          };

          //Aux1
          if (Usar_color_Aux1 == 1) {
            if ((Aux1 > Aux1_punto2) && (Aux1 <= Aux1_punto3))  {
               document.getElementById("Aux1").className = "verde";}
            else if ((Aux1 > Aux1_punto1) && (Aux1 <= Aux1_punto2))   {
              document.getElementById("Aux1").className = "naranja";}
            else if ((Aux1 > Aux1_punto3) && (Aux1 <= Aux1_punto4))   {
              document.getElementById("Aux1").className = "naranja";}                
          else  {
            document.getElementById("Aux1").className = "rojo";};
          }
            
          //Aux2
          if (Usar_color_Aux2 == 1) {
            if ((Aux2 > Aux2_punto2) && (Aux2 <= Aux2_punto3))  {
              document.getElementById("Aux2").className = "verde";}
            else if ((Aux2 > Aux2_punto1) && (Aux2 <= Aux2_punto2))   {
              document.getElementById("Aux2").className = "naranja";}
            else if ((Aux2 > Aux2_punto3) && (Aux2 <= Aux2_punto4))   {
              document.getElementById("Aux2").className = "naranja";}                
          else  {
            document.getElementById("Aux2").className = "rojo";};
          }                
  
          //Aux3
          if (Usar_color_Aux3 == 1) {
            if ((Aux3 > Aux3_punto2) && (Aux3 <= Aux3_punto3))  {
              document.getElementById("Aux3").className = "verde";}
            else if ((Aux3 > Aux3_punto1) && (Aux3 <= Aux3_punto2))   {
              document.getElementById("Aux3").className = "naranja";}
            else if ((Aux3 > Aux3_punto3) && (Aux3 <= Aux3_punto4))   {
              document.getElementById("Aux3").className = "naranja";}                
          else  {
            document.getElementById("Aux3").className = "rojo";};
          }
            
            //Aux4
            if (Usar_color_Aux4 == 1) {
                if ((Aux4 > Aux4_punto2) && (Aux4 <= Aux4_punto3))  {
                    document.getElementById("Aux4").className = "verde";}
                else if ((Aux4 > Aux4_punto1) && (Aux4 <= Aux4_punto2))   {
                document.getElementById("Aux4").className = "naranja";}
                else if ((Aux4 > Aux4_punto3) && (Aux4 <= Aux4_punto4))   {
                document.getElementById("Aux4").className = "naranja";}                
            else  {
                document.getElementById("Aux4").className = "rojo";};
            }
                
            //Aux5
            if (Usar_color_Aux5 == 1) {
                if ((Aux5 > Aux5_punto2) && (Aux5 <= Aux5_punto3))  {
                    document.getElementById("Aux5").className = "verde";}
                else if ((Aux5 > Aux5_punto1) && (Aux5 <= Aux5_punto2))   {
                document.getElementById("Aux5").className = "naranja";}
                else if ((Aux5 > Aux5_punto3) && (Aux5 <= Aux5_punto4))   {
                document.getElementById("Aux5").className = "naranja";}                
            else  {
                document.getElementById("Aux5").className = "rojo";};
            }
                
           //Aux6
            if (Usar_color_Aux6 == 1) {
                if ((Aux6 > Aux6_punto2) && (Aux6 <= Aux6_punto3))  {
                    document.getElementById("Aux6").className = "verde";}
                else if ((Aux6 > Aux6_punto1) && (Aux6 <= Aux6_punto2))   {
                document.getElementById("Aux6").className = "naranja";}
                else if ((Aux6 > Aux6_punto3) && (Aux6 <= Aux6_punto4))   {
                document.getElementById("Aux6").className = "naranja";}                
            else  {
                document.getElementById("Aux6").className = "rojo";};
            }                
                
           //Aux7
            if (Usar_color_Aux7 == 1) {
                if ((Aux7 > Aux7_punto2) && (Aux7 <= Aux7_punto3))  {
                    document.getElementById("Aux7").className = "verde";}
                else if ((Aux7 > Aux7_punto1) && (Aux7 <= Aux7_punto2))   {
                document.getElementById("Aux7").className = "naranja";}
                else if ((Aux7 > Aux7_punto3) && (Aux7 <= Aux7_punto4))   {
                document.getElementById("Aux7").className = "naranja";}                
            else  {
                document.getElementById("Aux7").className = "rojo";};
            }


          // Actualizacion Reles     
          var t_Datos_Reles = [];
          for (var i in data['RELES']) {
            n = data['RELES'][i]['nombre'] + '</br>' + data['RELES'][i]['modo'] + '-P' + data['RELES'][i]['prioridad'] + '-' +
              data['RELES'][i]['potencia'] + 'w-' + data['RELES'][i]['retardo'] + 'sg(' + data['RELES'][i]['espera'] + ')';
            t_Datos_Reles.push([n, data['RELES'][i]['estado']]);
          }
          t_Datos_Reles.pop(); // quito el ultimo elemento dado que es la fecha

          chart_reles.series[0].setData(t_Datos_Reles);

          var tCategories = []; // se cambian los nombres en funcion de los datos recibidos
          for (i = 0; i < chart_reles.series[0].data.length; i++) {
            tCategories.push(chart_reles.series[0].data[i].name);
          }

          chart_reles.xAxis[0].setCategories(tCategories);

          //Number(Vbat_min_dia.toFixed(1)) 


          // Actualizacion datos BMS
          
          for (var key in data['BMS']){
             //console.log( key, data['BMS'][key] );
            
             var sum_celda = Number(data['BMS'][key]['Vceldas'].reduce((a, b) => a + b, 0).toFixed(2));
             var max_celda = Math.max(...data['BMS'][key]['Vceldas']);
             var min_celda = Math.min(...data['BMS'][key]['Vceldas']);
             var dif_celda = Number(((max_celda - min_celda) * 1000).toFixed(0));
             var dif_vbat_celda = Number(((Vbat - sum_celda) * 1000).toFixed(0));
			       var ibal = Number(data['BMS'][key]['Ibalance']);
             var nceldas = data['BMS'][key]['Vceldas'].length;

             var cc1 = "chart_bms_"+key;
             //console.log(cc1);
             
             var cc = eval(cc1);
             
             cc.setSubtitle({
             text: data['BMS'][key]['tiempo'] + ' --- Sum_Celdas=' + sum_celda + 'V -- Max-Min=' + dif_celda + 'mV -- Vbat-Sum_Celdas=' + dif_vbat_celda + 'mV -- Ibalance=' + ibal + 'A'
             });
					 
			 
			       max_id = data['BMS'][key]['Vceldas'].indexOf(max_celda);
			       min_id = data['BMS'][key]['Vceldas'].indexOf(min_celda);
			 
            
             // Nombres, Min, Valor, Max
             cc.xAxis[0].setCategories(data['BMS'][key]['Nombres']);
             cc.series[0].setData(data['BMS'][key]['Max']);
             cc.series[1].setData(data['BMS'][key]['Vceldas']);
             cc.series[2].setData(data['BMS'][key]['Min']);
			 
			       for(i = 0; i < nceldas; i++) {cc.series[1].data[i].update({color: 'blue'}, false)};
			       cc.series[1].data[max_id].update({color: 'green'}, false);
			       cc.series[1].data[min_id].update({color: 'rgba(16, 224, 87, 1)'}, false);
    
             cc.redraw();

            }
           
          
          //console.log(data)

        }

        catch (e) {
          var d = new Date();
          s = d.getSeconds()
          t = d.getHours() + ':' + d.getMinutes() + ':' + s;

          // console.log(data)

          chart_vplaca.series[0].setData([s]); //Vplaca
          chart_temp.series[0].setData([s]);    //Temp 

          grafica_t_real.setTitle({
            text: 'SIN RESPUESTA - Hora=' + t,
          });

        }
      },

      // código a ejecutar sin importar si falla o no la petición
      complete: function (xhr, status) {
        setTimeout(recibirDatosFV, 3000);
      },

      cache: false
    });
  }

  function round(value, precision) {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
  }

});
</script>


<?php
include("pie.inc");
?>
