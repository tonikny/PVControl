<?php
$titulo="Inicio";
include ("cabecera.inc");


require('conexion.php');
//Coger datos grafica tiempo real
$sql = "SELECT UNIX_TIMESTAMP(Tiempo)*1000 as Tiempo,  Wred, Wplaca, Vred, PWM, Vplaca
        FROM datos WHERE Tiempo >= (NOW()- INTERVAL 3 MINUTE)
        ORDER BY Tiempo";

if($result = mysqli_query($link, $sql)){

  $i=0;
  while($row = mysqli_fetch_assoc($result)) {
        //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
        $rawdata3[$i] = $row;
        $i++;
  }
} else{
        echo "ERROR: No se puede ejecutar $sql. " . mysqli_error($link);
}

mysqli_close($link);

?>




<!-- Latest compiled and minified JavaScript -->
<script src="https://code.jquery.com/jquery.js"></script>

<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/highcharts-3d.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>
<script src="https://code.highcharts.com/modules/solid-gauge.js"></script>

<div class="divTable" style="color:black; width: 10%; height: 350px; margin-left: 1%; margin-right:2%;margin-top: -1%; margin-bottom: 0%; float: left">
    <div class="divTableBody">
        <div class="divTableRow">
                <div class="divTableCell">Wh Placa</div>
                <div id= "Wh_placa" class="divTableCell">&nbsp;</div>
        </div>
        <div class="divTableRow">
            <div class="divTableCell">Wh Cons</div>
            <div id= "Wh_cons" class="divTableCell">&nbsp;</div>
        </div>
        <div class="divTableRow">
            <div class="divTableCell">Wh Red+</div>
            <div id= "Whp_red" class="divTableCell">&nbsp;</div>
        </div>
        <div class="divTableRow">
            <div class="divTableCell">Wh Red-</div>
            <div id= "Whn_red" class="divTableCell">&nbsp;</div>
        </div>
        <div class="divTableRow">
            <div class="divTableCell">&nbsp;EFF máx</div>
            <div id = "EFF_max" class="divTableCell">&nbsp;</div>
        </div>
        <div class="divTableRow">
            <div class="divTableCell">EFF mín</div>
            <div id ="EFF_min" class="divTableCell">&nbsp;</div>
        </div>
        <div class="divTableRow">
            <div class="divTableCell">&nbsp;Vred mín</div>
            <div id = "Vred_min" class="divTableCell">&nbsp;</div>
        </div>
        <div class="divTableRow">
            <div class="divTableCell">&nbsp;Vred máx</div>
               <div id ="Vred_max" class="divTableCell">&nbsp;</div>
            </div>
        <div class="divTableRow">
            <div class="divTableCell"></div>
            <div class="divTableCell">&nbsp;</div>
        </div>
        <div class="divTableRow">
            <div class="divTableCell">Estado</div>
            <div id ="Estado" class="divTableCell">&nbsp;</div>
        </div>
        </div>
    </div>
</div>

<div id="containervred"  style="width: 20%; height: 180px; margin-left: 2%; margin-right: 0%;margin-top: -1%; float: left">
  <p>&nbsp;</p>
  <p>&nbsp;</p>
  </div>

  <div id="containerwred"  style="width: 20%; height: 180px; margin-left: 0%; margin-top: -1%; float: left"></div>
<div id="containertemp"  style="width: 20%; height: 180px; margin-left: 0%; margin-top: -1%; float: left"></div>
<div id="containervplaca"  style="width: 20%; height: 180px; margin-left: 0%; margin-top: -1%; float: left"></div>

<div id="containerEFF"  style="width: 23%; height: 180px; margin-bottom: 0%; margin-left: 9%;margin-top: -2%; float: left"></div>
<div id="containerconsumo"  style="width: 20%; height: 180px; margin-left: 0%; margin-top: 0%;margin-top: -2%; float: left"></div>
<div id="containerwplaca"  style="width: 20%; height: 180px; margin-left: 0%; margin-top: 0%;margin-top: -2%; float: left"></div>
<div id="container_reles" style="width: 80%; height: 160px; margin-left: 1%;float: left"></div>
<div id="grafica_t_real" style="width: 100%; height: 280px; margin-left: 0%; margin-bottom: 0% ;float: left"></div>


<br>
<br style="clear:both;"/>
<br>

<script>

$(function () {
    
    recibirDatosFV(); 

    
    Highcharts.setOptions({
        
        global: {
           useUTC: false
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

    chart_vred = new Highcharts.Chart ({
        chart: {
            renderTo: 'containervred',
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false,
            backgroundColor: null,//'#ffffff',//'#f2f2f2',
            borderColor: null,
            },
        
        caption: {
                align : 'center',
                floating: true,
                y: -20,
                text : 'kkkk'
                },
                
        title: {
            y:155,
            floating: true,
            /*style:{
                color: 'Purple',
                fontSize:'18px',
                },*/
            text: 'Vred',
            },
        subtitle: {
            y:60,
            floating: true,
            text: '',
          },
        credits: {
            enabled: false
            },
        pane: {
            size: '105%',
            startAngle: -150,
            endAngle: 150,
            background: [{
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#FFF'],
                        [1, '#333']
                        ]
                    },
                borderWidth: 0,
                //outerRadius: '109%' - orla
                outerRadius: '100%'
                }, {
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#333'],
                        [1, '#FFF']
                        ]
                    },
                borderWidth: 0,
                outerRadius: '100%'
                }, {
                // default background
                }, {
                backgroundColor: null,//#DDD
                borderWidth: 0,
                outerRadius: '105%',
                innerRadius: '103%'
                
                }]
            },
        yAxis: {
            min: Vred_min,
            max: Vred_max,
            minorTickInterval: 'auto',
            minorTickWidth: 1,
            minorTickLength: 10,
            minorTickPosition: 'inside',
            minorTickColor: '#666',
            tickPixelInterval: 30,
            tickWidth: 2,
            tickPosition: 'inside',
            tickLength: 10,
            tickColor: '#666',
            labels: {
                step: 1,
                rotation: 'auto'
              },
            title: {
                y:10,//-30,
                x:0,
                floating:true,
                reserveSpace:false,
                style: {
                   fontSize: '16px'
                  },
                text: 'pp1' //'V_BAT'
                },
            subtitle: {
                y:50,//-30,
                x:0,
                floating:true,
                reserveSpace:false,
                style: {
                   fontSize: '16px'
                  },
                text: 'pp2' //null //'V_BAT'
                },
                
            plotBands: [
              {
                from: Vred_min,
                to: Vred_bajo_amarillo,
                color: '#DF5353' // red
              },
              {
                from: Vred_bajo_amarillo,
                to: Vred_verde,
                color: '#DDDF0D' // yellow
              },
              {
                from: Vred_verde,
                to: Vred_alto_amarillo,
                color: '#55BF3B' // green
              },
              {
                from: Vred_alto_amarillo,
                to: Vred_alto_rojo,
                color: '#DDDF0D' // yellow
              },
              {
                from: Vred_alto_rojo,
                to: Vred_max,
                color: '#DF5353' // red
              }]
            },
        navigation: {
            buttonOptions: {
                enabled: false
              }
          },
        tooltip: {
            enabled: false
          },
        series: [{
            name: 'Vred',
            data: [],
            dataLabels: {
                enabled: true,
                allowOverlap: true,
                borderWidth: 0,
                y: 0,
                style: {
                   fontSize: '18px'
                  },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,0) + " V"
                    },
              }
          }]
        });
    
    chart_eff = new Highcharts.Chart ({
        chart: {
            renderTo: 'containerEFF',
            type: 'solidgauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false,
            backgroundColor: null,//'#ffffff',//'#f2f2f2',
            borderColor: null
            
          },
        title: {
            y:130,
            widthAdjust: 0,
            style: {
                fontSize: '30px'
                },
            floating: true,
            text: 'DC/AC EFICIENCIA INVERSOR'
          },
        credits: {
            enabled: false
          },
        pane: {
            center: ['50%', '65%'],
            size: '130%',
            startAngle: -90,
            endAngle: 90,
            background: {
                backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || '#EEE',
                innerRadius: '100%',
                outerRadius: '100%',
                shape: 'arc'
              }
          },
        tooltip: {
            enabled: false
          },
        yAxis: {
            min: EFF_min,
            max: EFF_max,
            stops: [
                [0.6,'rgba(223,83,83,0.7)' ], // red'#DF5353'
                [0.7, 'rgba(221,223,13,0.7)'], // yellow'#DDDF0D'
                [0.85, 'rgba(85,191,59,0.7)'] // green'#55BF3B'
              ],
            lineWidth: 1,
            minorTickInterval: 1, //null,
            tickAmount: 9,
            
            //title: {
            //    y: -30
            // },
             
            title: {
                y: 100,//-30,
                floating: true,
                //align: 'right',
                //verticalAlign: 'bottom',
                //x:0,
                style: {
                   fontSize: '15px'
                  },
                text: '' //null //'V_BAT'
                },
            
            labels: { // valores de la escala
                y: 0,
                min: EFF_min,
                max: EFF_max,
              }, // valores max y min
            //title: {
                //y: -50,
            //  text: null
             //},

          },
        plotOptions: {
            solidgauge: {
                dataLabels: {
                    y: 35,    // Valor dato
                    borderWidth: 2,
                    useHTML: true
                  }
             }
          },
        navigation: {
            buttonOptions: {
                enabled: false
              }
          },
        series: [{
            name: '%',
            title: {
                floating:true,
                y:150,//-30,
                x:0,
                text: 'HOLA', 
                style: {
                   fontSize: '15px'
                  },
                },
            data: [],
            dataLabels: {
                y:-35,
                format: '<div style="text-align:center"><span style="font-size:25px;color:' +
                  ((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">{y}</span>' +
                       '<span style="font-size:15px;color:silver">%</span></div>'
              },
          }]
      });
    
    chart_temp = new Highcharts.Chart ({
        chart: {
            renderTo: 'containertemp',
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false,
            backgroundColor: null,//'#ffffff',//'#f2f2f2',
            borderColor: null
          },
        title: {
            y:155,
            floating: true,
            text: 'Temp',
          },
        credits: {
            enabled: false
          },   
        pane: [{
            size: '105%',
            startAngle: -150,
            endAngle: -10,
            background: [{
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#FFF'],
                        [1, '#333']
                      ]
                  },
                borderWidth: 0,
                //outerRadius: '109%' - orla
                outerRadius: '100%'
              }, {
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#333'],
                        [1, '#FFF']
                      ]
                  },
                borderWidth: 1,
                outerRadius: '105%'
              }, {
                // default background
              }, {
                backgroundColor: '#DDD',
                borderWidth: 0,
                outerRadius: '105%',
                innerRadius: '103%'
              }]

          }, {
            size: '105%',
            startAngle: 20,
            endAngle: 150,
            background: []
          }],
            // the value axis
        yAxis: [{
            min: Temp_bat_min,
            max: Temp_bat_max,

            minorTickInterval: 5,
            minorTickWidth: 1,
            minorTickLength: 10,
            minorTickPosition: 'inside',
            minorTickColor: '#666',

            tickPixelInterval: 30,
            tickInterval: 10,
            tickWidth: 2,
            tickPosition: 'inside',
            tickLength: 10,
            tickColor: '#666',

            title: {
                y: 10,
                text: null, //'TEMP.'
              },
                
            labels: {
                allowOverlap:true,
                step: 1,
                rotation: 'auto'
              },
                
            plotBands: [{
                from: Temp_bat_normal,
                to: Temp_bat_alta,
                color: '#55BF3B' // green
              
               },{
                from: Temp_bat_baja,
                to: Temp_bat_normal,
                color: '#DDDF0D' // yellow
              },{
                from: Temp_bat_min,
                to: Temp_bat_baja,
                color: '#3C14BF' // blue
              }, {
                from: Temp_bat_alta,
                to: Temp_bat_max,
                color: '#DF5353' // red
              }]
          }, {    
            reversed: true,
            min: Temp_rpi_min,
            max: Temp_rpi_max,
            pane: 1,
            minorTickInterval: 10,
            minorTickWidth: 1,
            minorTickLength: 10,
            minorTickPosition: 'inside',
            minorTickColor: '#666',

            tickPixelInterval: 30,
            tickInterval: 20,
            tickWidth: 2,
            tickPosition: 'inside',
            tickLength: 10,
            tickColor: '#666',
                
            labels: {
                allowOverlap:true,
                step: 1,
                rotation: 'auto'
              },

            plotBands: [{
                from: Temp_rpi_min,
                to: Temp_rpi_normal,
                color: '#55BF3B' // green
              }, {
                from: Temp_rpi_normal,
                to: Temp_rpi_alta,
                color: '#DDDF0D' // yellow
              }, {
                from: Temp_rpi_alta,
                to: Temp_rpi_max,
                color: '#DF5353' // red
              }]
 
          }],
        navigation: {
            buttonOptions: {
                enabled: true
              }
          },
        tooltip: {
            enabled: true
          },
        series: [{
            yAxis: 0,
            name: 'TEMP',
            data: [],
            dataLabels: {
                allowOverlap: true,
                enabled: true,
                borderWidth: 0,
                y: -35, //-35,
                x: 0,
                style: {
                    fontSize: '15px'
                  },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,1) + "ºC Inv"
                  }
              },
            dial: {
                backgroundColor : 'black',   //Color de la aguja
                radius: '80%' //longitud de la aguja
              },
          },{
            yAxis: 1,
            name: 'CPU',
            data: [],
            dataLabels: {
                allowOverlap: true,
                enabled: true,
                borderWidth: 0,
                y: 20, //10,
                x: 0,
                style: {
                    fontSize: '15px',
                    color: 'red'
                  },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,0) + "ºC Rpi"
                  }
              },
            dial: {
                backgroundColor : 'red',   //Color de la aguja
                radius: '80%' //longitud de la aguja
              },
          }]        
      });
    
    chart_consumo = new Highcharts.Chart ({
        chart: {
            renderTo: 'containerconsumo',
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false,
            alignTicks: false,
            backgroundColor: null,//'#ffffff',//'#f2f2f2',
            borderColor: null
          },
        title: {
            y:155,
            floating: true,
            text: 'Consumo',
          },
        subtitle: {
            y:42,
            floating: true,
            text: '',
          },
        credits: {
            enabled: false
          },
        pane: [{
            size: '105%',
            startAngle: -150,
            endAngle: -10,
            background: [{
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#FFF'],
                        [1, '#333']
                      ]
                  },
                borderWidth: 0,
                //outerRadius: '109%' - orla
                outerRadius: '100%'
              }, {
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#333'],
                        [1, '#FFF']
                      ]
                  },
                borderWidth: 0,
                outerRadius: '100%'
              }, {
                // default background
              }, {
                backgroundColor: '#DDD',
                borderWidth: 0,
                outerRadius: '105%',
                innerRadius: '103%'
              }]

          }, {
            size: '105%',
            startAngle: 10,
            endAngle: 150,
            background: []
          }],

        yAxis: [
          { // Wconsumo
            min: Consumo_watios_min,
            max: Consumo_watios_max,
            pane: 0,
            minorTickInterval: 'auto',
            minorTickWidth: 1,
            minorTickLength: 10,
            minorTickPosition: 'inside',
            minorTickColor: '#666',
            tickPixelInterval: 30,
            tickInterval: 1000,
            tickWidth: 2,
            tickPosition: 'inside',
            tickLength: 10,
            tickColor: '#666',
            title: {
                y: 10,
                text: null, //'CONSUMO'
              },
            labels: {
                allowOverlap:true,
                step: 1,
                rotation: 'auto'
              },
            plotBands: [{
                from: Consumo_watios_min,
                to: Consumo_watios_amarillo,
                color: '#55BF3B' // green
              }, {
                from: Consumo_watios_amarillo,
                to: Consumo_watios_rojo,
                color: '#DDDF0D' // yellow
              }, {
                from: Consumo_watios_rojo,
                to: Consumo_watios_max,
                color: '#DF5353' // red
              }]
          },
          { // Aconsumo
            reversed: true,
            min: Consumo_amperios_min,
            max: Consumo_amperios_max,
            pane: 1,
            minorTickInterval: 'auto',
            minorTickWidth: 1,
            minorTickLength: 10,
            minorTickPosition: 'inside',
            minorTickColor: '#666',
            tickPixelInterval: 30,
            tickInterval: Consumo_amperios_max/5,
            tickWidth: 2,
            tickPosition: 'inside',
            tickLength: 10,
            tickColor: '#666',
            labels: {
                allowOverlap:true,
                step: 1,
                rotation: 'auto'
              },
            plotBands: [{
                from: Consumo_amperios_min,
                to: Consumo_amperios_amarillo,
                color: '#55BF3B' // green
              }, {
                from: Consumo_amperios_amarillo,
                to: Consumo_amperios_rojo,
                color: '#DDDF0D' // yellow
              }, {
                from: Consumo_amperios_rojo,
                to: Consumo_amperios_max,
                color: '#DF5353' // red
              }]
          }
          ],
        
        navigation: {
            buttonOptions: {
                enabled: false
              }
          },
        tooltip: {
            enabled: false
          },
        series: [
          { // WConsumo
            yAxis: 0,
            name: 'Consumo W',
            data: [],
            dataLabels: {
                allowOverlap:true,
                enabled: true,
                borderWidth: 0,
                y: -35,
                x: 0,
                style: {
                    fontSize: '15px'
                  },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,0) + "W"
                  }
              },
            dial: {
                backgroundColor : 'black',   //Color de la aguja
                radius: '80%' //longitud de la aguja
              },
          },
          { //Aconsumo
            yAxis: 1,
            name: '',
            data: [],
            dataLabels: {
                allowOverlap:true,
                enabled: true,
                borderWidth: 0,
                y: 20,
                x: 0,
                style: {
                    fontSize: '15px',
                    color : 'red'
                  },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,0) + "A"
                  }
              },
            dial: {
                backgroundColor : 'red',   //Color de la aguja
                radius: '80%' //longitud de la aguja
              },
          }
          ]        
      });
    
    chart_wred = new Highcharts.Chart ({ 
        chart: {
            renderTo: 'containerwred',
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false,
            backgroundColor: null,//'#ffffff',//'#f2f2f2',
            borderColor: null
            },
        title: {
            y:145,
            floating:true,
            text: 'Wred',
            style: {
                fontSize: '12px',
                color: 'black'
                },
            },
        subtitle: {
            y:155,
            floating:true,
            text: 'Wplaca',
            style: {
                fontSize: '12px',
                color: 'red'
                },
            },
                       
        credits: {
                enabled: false
            },
        pane: {
                size: '105%',
                startAngle: -150,
                endAngle: 150,
                background: [{
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, '#FFF'],
                            [1, '#333']
                        ]
                    },
                    borderWidth: 0,
                    //outerRadius: '109%' - orla
                    outerRadius: '100%'
                }, {
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, '#333'],
                            [1, '#FFF']
                        ]
                    },
                    borderWidth: 0,
                    outerRadius: '100%'
                }, {
                    // default background
                    //backgroundColor: 'red'
                }, {
                    backgroundColor: '#DDD',
                    borderWidth: 0,
                    outerRadius: '105%',
                    innerRadius: '103%'
                 }]
            },
        yAxis: {
                min: Wred_min,
                max: Wred_max,

                minorTickInterval: 'auto',
                minorTickWidth: 1,
                minorTickLength: 2,
                minorTickPosition: 'inside',
                minorTickColor: '#666',

                tickPixelInterval: 30,
                tickWidth: 2,
                tickPosition: 'inside',
                tickLength: 10,
                tickColor: '#666',
                labels: {
                    step: 2,
                    rotation: 'auto'
                },
                title: {
                    y:20,
                    text: null, //'I_BAT'   
                },
                plotBands: [{
                    from: Wred_min,
                    to: Wred_negativo_rojo,
                    color: '#DF5353' // red
                }, {
                    from: Wred_negativo_rojo,
                    to: Wred_negativo_amarillo,
                    color: '#DDDF0D' // yellow
                }, {
                    from: Wred_negativo_amarillo,
                    to: Wred_positivo_amarillo,
                    color: '#55BF3B' // green
                }, {
                    from:  Wred_positivo_amarillo,
                    to: Wred_positivo_rojo,
                    color: '#DDDF0D' // yellow
                },{
                    from:  Wred_positivo_rojo,
                    to: Wred_max,
                    color: '#DF5353' // red
                }]
            },
        navigation: {
            buttonOptions: {
                enabled: false
            }
        },
        
        tooltip: {
                  enabled: false
                 },

        series: [{
            name: 'Wred',
            data: [],
            dataLabels: {
                allowOverlap:true,
                enabled: true,
                borderWidth: 0,
                y: 10,
                style: {
                    fontSize: '14px',
                    color: 'black'
                    },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,0) + " W"
                    },
                },
            dial: {
                backgroundColor: (([this.y] <= 0) ? 'black' : 'green')
                }
            },{
            name: 'Wplaca',
            data: [],
            dataLabels: {
                allowOverlap:true,
                enabled: true,
                borderWidth: 0,
                y: 25,
                style: {
                    fontSize: '14px',
                    color: 'red'
                    },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,0) + " W"
                    },
                },
            dial: {
                backgroundColor: (([this.y] <= 0) ? 'red' : 'blue')
                }

                
            }]
        });
    
    chart_wplaca = new Highcharts.Chart ({
        chart: {
            renderTo: 'containerwplaca',
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false,
            backgroundColor: null,//'#ffffff',//'#f2f2f2',
            borderColor: null
            },
        title: {
            y:155,
            floating:true,
            text: 'Wplaca',
            },
        credits: {
                enabled: false
            },
        pane: {
                size: '105%',
                startAngle: -150,
                endAngle: 150,
                background: [{
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, '#FFF'],
                            [1, '#333']
                        ]
                    },
                    borderWidth: 0,
                    //outerRadius: '109%' - orla
                    outerRadius: '100%'
                }, {
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, '#333'],
                            [1, '#FFF']
                        ]
                    },
                    borderWidth: 0,
                    outerRadius: '100%'
                }, {
                    // default background
                }, {
                    backgroundColor: '#DDD',
                    borderWidth: 0,
                    outerRadius: '105%',
                    innerRadius: '103%'
                 }]
            },
        yAxis: {
            min: 0,
            max: Watios_placa_max,
            minorTickInterval: 'auto',
            minorTickWidth: 1,
            minorTickLength: 10,
            minorTickPosition: 'inside',
            minorTickColor: '#666',
            tickPixelInterval: 30,
            tickInterval: 1000,
            tickWidth: 1,
            tickPosition: 'inside',
            tickLength: 10,
            tickColor: '#666',
            labels: {
                allowOverlap:true,
                step: 1,
                rotation: 'auto'
            },
            title: {
                y:20,//-30,
                x:0,
                allowOverlap:true,
                style: {
                   fontSize: '16px'
                  },
                text: '' //null 
                },
            
        plotBands: [{
                    from: 0,
                    to: Watios_placa_baja_rojo,
                    color: '#DF5353' // red
                }, {
                    from: Watios_placa_baja_rojo,
                    to: Watios_placa_verde,
                    color: '#55BF3B' // green
                }, {
                    from: Watios_placa_verde,
                    to: Watios_placa_alta_amarillo,
                    color: '#DDDF0D' // yellow
                }, {
                    from: Watios_placa_alta_amarillo,
                    to: Watios_placa_max,
                    color: '#DF5353' // red
                }]
            },
        navigation: {
            buttonOptions: {
                enabled: false
            }
        },

        tooltip: {
                  enabled: false
                 },
        series: [{
            name: 'Wplaca',
            data: [],
            dataLabels: {
                allowOverlap:true,
                enabled: true,
                borderWidth: 0,
                y: 10,                   
                style: {
                    fontSize: '20px'                        
                    },
                formatter: function() {
                     return Highcharts.numberFormat(this.y,0) + " W"
                    },
                }
            }]
        });
        
    chart_vplaca = new Highcharts.Chart ({
        chart: {
            renderTo: 'containervplaca',
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false,
            backgroundColor: null,//'#ffffff',//'#f2f2f2',
            borderColor: null,
            },
        title: {
            y:155,
            floating: true,
            style: {
                    color: 'Black',
                    fontWeight: 'bold',
                    fontSize:'18px',
                },
            text: 'Vplaca',
            },
        credits: {
            enabled: false
            },
        pane: {
            size: '105%',
            startAngle: -150,
            endAngle: 150,
            background: [{
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#FFF'],
                        [1, '#333']
                        ]
                    },
                borderWidth: 0,
                //outerRadius: '109%' - orla
                outerRadius: '100%'
                }, {
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#333'],
                        [1, '#FFF']
                        ]
                    },
                borderWidth: 0,
                outerRadius: '100%'
                }, {
                // default background
                }, {
                backgroundColor: '#DDD',//#DDD
                borderWidth: 0,
                outerRadius: '105%',
                innerRadius: '103%'
                }]
            },
        yAxis: {
            min: 0,
            max: Vplaca_max,
            minorTickInterval: 'auto',
            minorTickWidth: 1,
            minorTickLength: 10,
            minorTickPosition: 'inside',
            minorTickColor: '#666',
           
            tickPixelInterval: 30,
            tickWidth: 2,
            tickPosition: 'inside',
            tickLength: 10,
            tickColor: '#666',
            labels: {
                step: 2,
                rotation: 'auto'
              },
            title: {
                y:20,//-30,
                x:0,
                reserveSpace:false,
                style: {
                   fontSize: '16px'
                  },
                text: '' //null //'V_BAT'
                },
            subtitle: {
                y:0,//-30,
                x:-30,
                style: {
                   fontSize: '10px'
                  },
                text: 'pp' //null //'V_BAT'
                },
                
            plotBands: [{
                from: 0,
                to: Vplaca_baja_amarillo,
                color: '#DDDF0D' // amarillo
              }, {
                from: Vplaca_baja_amarillo,
                to: Vplaca_baja_verde,
                color: '#d5f09d' // low green
              }, {
                from: Vplaca_baja_verde,
                to: Vplaca_verde,
                color: '#55BF3B' // green
              }, {
                from: Vplaca_verde,
                to: Vplaca_alta_amarillo,
                color: '#DDDF0D' // amarillo
              }, {
                from: Vplaca_alta_amarillo,
                to: Vplaca_max,
                color: '#DF5353' // red
              }]
            },
        navigation: {
            buttonOptions: {
                enabled: false
              }
          },
        tooltip: {
            enabled: false
          },
        series: [{
            name: 'Vplaca',
            data: [],
            dataLabels: {
                enabled: true,
                allowOverlap: true,
                borderWidth: 0,
                y: 10,
                style: {
                   fontSize: '20px'
                  },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,0) + " V"
                    },
              }
          }]
        });
                            
    chart_reles =new Highcharts.Chart({
        chart: {
            renderTo: 'container_reles',
            backgroundColor: null,//'#ffffff',//'#f2f2f2',
            borderColor: null,
            type: 'column',
            shadow: false,
            options3d: {
                enabled: true,
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
                //borderWidth: null,
                //borderColor: 'red',
            },
            enableMouseTracking: false
          }
        },

        credits: {
             enabled: false
             },
        title: {
              y:20,
              text: 'SITUACION RELES'
             },
        subtitle: {
              text: null
             },
        xAxis: {
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
              tickInterval: 10,
              allowDecimals: false,
              visible: true, //desactivar grid i resta
              labels: {
                    enabled: true
               },
              title: {
                    enabled: false
               }              
             },

        series: [{
                name: 'Estado Relés',
                colorByPoint: false,//Color aleatorio para cada columna de un rele
                color : '#2b5dc7',
                borderColor: '#303030',
                data: [],
                
                dataLabels: {
                    enabled: true, 
                    formatter: function() {
                        return Highcharts.numberFormat(this.y,0) + " %"
                    }
                }
                }],
        
        navigation: {
              buttonOptions: {
                enabled: false
               }
             },
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
 
  
    grafica_t_real = new Highcharts.Chart ({
        chart: {
         renderTo: 'grafica_t_real',
         backgroundColor: null,//'#ffffff',//'#f2f2f2',
         borderColor: null,
         plotBorderWidth: 1,
         zoomType: 'xy',
         alignTicks: false,
         animation: Highcharts.svg, // don't animate in old IE
         //marginRight: 10,
               },
       title: {
            text: '',
            floating:true,
            y: 12,
            x:-0
            },
        subtitle: {
            text: 'Prueba Dinamica',
            floating:true,
            align: 'right',
            verticalAlign: 'bottom',
            y: 25,
            },
        credits: {
            enabled: false
            },
        xAxis: {
            type: 'datetime'
            },
        yAxis: [
            {// ########## Valores eje Wred #################
            gridLineWith: 2,
            min: Escala_Wred_min,
            max: Escala_Wred_max,
            opposite: true,
            tickInterval:40,
            gridLineColor: 'transparent',
            minorGridLineColor: 'transparent',
            //endOnTick: true,
            //maxPadding: 0.2,
            //tickAmount: 7,
            labels: {
                //format: '{value} W',
                style: {
                    color: Highcharts.getOptions().colors[2]
                    }
                },
            title: {
                text: null,
                },
            //opposite: false,
            },
            {// ########## Valores eje Vred ######################
            opposite: false,
            min: Escala_Vred_min,
            max: Escala_Vred_max,
            tickInterval: 1,
            //gridLineColor: 'transparent',
            minorGridLineColor: 'transparent',
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
              [{ // ########## Valores Linea Vred alta ###################
                value: Vred_alto,
                width: 2,
                color: 'green',
                dashStyle: 'shortdash',
                label: {
                    text: 'Vred_alto'
                    }
                },
                {// ########## Valores Linea Vflot ######################
                value: Vred_bajo,
                width: 2,
                color: 'red',
                dashStyle: 'shortdash',
                label: {
                    text: 'Vred_bajo'
                    }
              }]
            },
            {// ########## Valores eje PWM ######################
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
        {name: 'Wred',
            yAxis: 0,
            color: Highcharts.getOptions().colors[2],
            data: (function() {
                var data = [];
                <?php
                for($i = 0 ;$i<count($rawdata3);$i++){
                ?>
                    data.push([<?php echo $rawdata3[$i]["Tiempo"];?>,<?php echo $rawdata3[$i]["Wred"];?>]);
                <?php } ?>
              return data;
              })()

            },
        
        {name: 'WPlaca',
            yAxis: 0,
            color: Highcharts.getOptions().colors[3],
            data: (function() {
                var data = [];
                <?php
                for($i = 0 ;$i<count($rawdata3);$i++){
                ?>
                    data.push([<?php echo $rawdata3[$i]["Tiempo"];?>,<?php echo $rawdata3[$i]["Wplaca"];?>]);
                <?php } ?>
              return data;
              })()

            },
            {name: 'Vred',
            color: Highcharts.getOptions().colors[0],
            yAxis: 1,
            data: (function() {
                var data = [];
                <?php
                for($i = 0 ;$i<count($rawdata3);$i++){
                ?>
                    data.push([<?php echo $rawdata3[$i]["Tiempo"];?>,<?php echo $rawdata3[$i]["Vred"];?>]);
                <?php } ?>
              return data;
              })()
            
            },
        {      name: 'VPlaca',
            yAxis: 3,
                data: (function () {
                     var data = [];
                <?php
                for($i = 0 ;$i<count($rawdata3);$i++){
                ?>
                    data.push([<?php echo $rawdata3[$i]["Tiempo"];?>,<?php echo $rawdata3[$i]["Vplaca"];?>]);
                <?php } ?>
                    return data;
                }())
            },
            {name: 'PWM',
            yAxis: 2,
            color: Highcharts.getOptions().colors[4],
            data: (function() {
                var data = [];
                <?php
                for($i = 0 ;$i<count($rawdata3);$i++){
                ?>
                    data.push([<?php echo $rawdata3[$i]["Tiempo"];?>,<?php echo $rawdata3[$i]["PWM"];?>]);
                <?php } ?>
              return data;
              })()
            },
            ]
                                
      });
      

    function recibirDatosFV() {
      $.ajax({
        url: 'datos_fv.php',
        success: function(data) {
          try {
            // tiempo_sg, "%d-%B-%Y -- %H:%M:%S"
            fecha = data[0][0][1];
            /* 
            //Vbat,Ibat,Wbat,Whp_bat,Whn_bat,Vbat_min,Vbat_max
            Vbat = data[0][1][0]; 
            Ibat = data[0][1][1]; 
            Wbat = data[0][1][2]; 
            Whp_bat = data[0][1][3];
            Whn_bat = data[0][1][4];
            Wh_bat = Whp_bat -Whn_bat;
            Vbat_min = data[0][1][5];
            Vbat_max = data[0][1][6];
            
            //DS,SOC,SOC_min,SOC_max
            DS = data[0][2][0];
            SOC = data[0][2][1];
            SOC_min = data[0][2][2];
            SOC_max = data[0][2][3];
            
            //Mod_bat,Tabs,Tflot,Tflot_bulk
            Mod_bat = data[0][3][0];
            Tabs = data[0][3][1];
            Tflot = data[0][3][2];
            Tflot_bulk = data[0][3][3];
            */
            // Vplaca,Iplaca,Wplaca,Wh_placa
            Vplaca = data[0][4][0];
            Iplaca = data[0][4][1];
            Wplaca = data[0][4][2]
            Wh_placa = data[0][4][3];
            
            //(Vred,Wred,Whp_red,Whn_red,Vred_min,Vred_max,EFF,EFF_min,EFF_max)
            Vred = data[0][5][0];
            Wred = data[0][5][1];
            Whp_red = data[0][5][2];
            Whn_red = data[0][5][3];
            Wh_red = Whp_red -Whn_red;
            Vred_min = data[0][5][4];
            Vred_max = data[0][5][5];
            EFF = data[0][5][6];
            EFF_min = data[0][5][7];
            EFF_max = data[0][5][8];
            Ired = Wred / Vred
            
            //Wconsumo, Wh_consumo
            Wconsumo = data[0][6][0];
            Wh_consumo = data[0][6][1];
            
            //Temp,int(PWM)
            Temp = data[0][7][0];
            PWM  = data[0][7][1];          
           
            // Actualizacion reloj Vred
            chart_vred.series[0].setData([Vred]);
            chart_vred.yAxis[0].setTitle({
              text: Wh_red + ' Wh' 
                });
            chart_vred.setSubtitle({
              text: Whp_red + '/' + Whn_red + ' Wh' 
                });
            
            chart_vred.caption.update({
                text: Vred_min +'/'+ Vred_max+ ' V'
                });
                
            // Actualizacion reloj Wred/Wplaca
            chart_wred.series[0].setData([Wred]); 
            chart_wred.series[1].setData([Wplaca]);
                      
            // Actualizacion EFF
            chart_eff.series[0].setData([EFF]);
            chart_eff.yAxis[0].setTitle({
              text: 'min='+EFF_min +' - max'+ EFF_max+ '%'
                });
            
             // Actualizacion reloj Temp
            chart_temp.series[0].setData([Temp]);    //Temp 
            chart_temp.series[1].setData([data[1]]); //CPU

            // Actualizacion reloj Wplaca 
            chart_wplaca.series[0].setData([Wplaca]);
            //chart_wplaca.setTitle({
            //  text: data[0][12] // ejem de cambio de titulo
            //   });
            chart_wplaca.yAxis[0].setTitle({
              text: Wh_placa+' Wh' 
                });
            
            // Actualizacion reloj Consumo 
            chart_consumo.series[0].setData([Wconsumo]); // Consumo
            chart_consumo.series[1].setData([Iplaca-Ired]); // Iplaca - Ired
            chart_consumo.setSubtitle({
              text: Wh_consumo + ' Wh'
                });
            
            //var consumo_wh= parseInt(data[0][13] - (data[0][8] -data[0][9]))
            //var consumo_wh= Math.round(data[0][13] - (data[0][8] -data[0][9]))
           
            // Actualizacion reloj Vplaca
            chart_vplaca.series[0].setData([Vplaca]); //Vplaca
            
             // Actualizacion Grafica a tiempor real
            grafica_t_real.setTitle({
              text: 'Fecha: ' + fecha
                });
            grafica_t_real.setSubtitle({
              text: 'PWM=' + PWM
                });
            
            x = (new Date()).getTime(); // current time
            
            grafica_t_real.series[0].addPoint([x, Wred], true, true); //Wred
            grafica_t_real.series[1].addPoint([x, Wplaca], true, true); //Wplaca
            grafica_t_real.series[3].addPoint([x, Vplaca], true, true); //Vplaca
            //grafica_t_real.series[3].addPoint([x, Aux1], true, true); //Aux1
            grafica_t_real.series[4].addPoint([x, PWM], true, true); //PWM
            grafica_t_real.series[2].addPoint([x, Vred], true, true); //Vred
            
            //Valores de la tabla
            $("#Wh_placa").text(Wh_placa + " Wh");
            $("#Wh_cons").text(Wh_consumo +' Wh')
            $("#Whp_red").text(Whp_red + " Wh");
            $("#Whn_red").text(Whn_red + " Wh");
            $("#EFF_min").text(EFF_min + "%");
            $("#EFF_max").text(EFF_max + "%");
            $("#Vred_min").text(Vred_min + "V");
            $("#Vred_max").text(Vred_max + "V");
            
            //Evaluacion del color de la celda segun la variable ... (Colores definidos en inicio.css)
            if (Wred > 0)  {
                Estado ="INYECCION";
                document.getElementById("Estado").className = "rojo";
                }
            else {
                Estado ="CONSUMO";
                document.getElementById("Estado").className = "verde";
                }
            $("#Estado").text(Estado);
            
  
            //EFF_min
            if (EFF <= EFF_min_rojo)  {
                document.getElementById("EFF_min").className = "rojo";}
            else if (EFF < EFF_min_naranja)  {
                document.getElementById("EFF_min").className = "naranja";}
            else  {
                document.getElementById("EFF_min").className = "verde";};
             
            //EFF_max
            if (EFF <= EFF_max_rojo)  {
                document.getElementById("EFF_max").className = "rojo";}
            else if (EFF < EFF_max_naranja)  {
                document.getElementById("EFF_max").className = "naranja";}
            else  {
                document.getElementById("EFF_max").className = "verde";};
            
            //Vred_min
            if (Vred <= Vred_min_rojo)  {
                document.getElementById("Vred_min").className = "rojo";}
            else if (Vred < Vred_min_naranja)  {
                document.getElementById("Vred_min").className = "naranja";}
            else  {
                document.getElementById("Vred_min").className = "verde";};
            
            //Vred_max
            if (Vred >= Vred_max_alta_rojo)  {
                document.getElementById("Vred_max").className = "rojo";}
            else if (Vred >= Vred_max_alta_naranja)  {
                document.getElementById("Vred_max").className = "naranja";}
            else if (Vred <= Vred_max_baja_rojo)  {
                document.getElementById("Vred_max").className = "rojo";}
            else if (Vred <= Vred_max_baja_naranja)  {
                document.getElementById("Vred_max").className = "naranja";}
                
            else  {
                document.getElementById("Vred_max").className = "verde";};

            // Actualizacion Reles     
            var tCategories = [];
            chart_reles.series[0].setData(data[2]);
            
            for (i = 0; i < chart_reles.series[0].data.length; i++) {
                tCategories.push(chart_reles.series[0].data[i].name);
            }
            
            chart_reles.xAxis[0].setCategories(tCategories);            
            
            //console.log(data)

            //setTimeout(recibirDatosFV, 3000);
          }
 
          catch {
            var d = new Date();
            s = d.getSeconds()
            t = d.getHours() + ':' + d.getMinutes() + ':' + s;
                
            chart_vplaca.series[0].setData([s]); //Vplaca
            chart_temp.series[0].setData([s]);    //Temp 
                
            grafica_t_real.setTitle({
                text: 'SIN RESPUESTA - Hora=' + t,
                 });
              
            //setTimeout(recibirDatosFV, 3000);
            }       
          },
          
         // código a ejecutar sin importar si la petición falló o no
        complete : function(xhr, status) {
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
include ("pie.inc");
?>
