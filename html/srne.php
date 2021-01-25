<?php
$titulo="SRNE";
include ("cabecera.inc");
?>

<!-- Latest compiled and minified JavaScript -->
<script src="https://code.jquery.com/jquery.js"></script>

<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/highcharts-3d.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>
<script src="https://code.highcharts.com/modules/solid-gauge.js"></script>

<div class="divTable" style="color:black; width: 10%; height: 350px; margin-left: 1%; margin-right:2%;margin-top: -1%; margin-bottom: 0%; float: left">
</div>
<div id="containervbat"  style="width: 20%; height: 180px; margin-left: 2%; margin-right: 0%;margin-top: -1%; float: left">
  <p>&nbsp;</p>
  <p>&nbsp;</p>
  </div>
<div id="containeriplaca"  style="width: 20%; height: 180px; margin-left: 0%; margin-top: -1%; float: left"></div>
<div id="containertemp"  style="width: 20%; height: 180px; margin-left: 0%; margin-top: -1%; float: left"></div>
<div id="containervplaca"  style="width: 20%; height: 180px; margin-left: 0%; margin-top: -1%; float: left"></div>
<div id="containerSOC"  style="width: 23%; height: 180px; margin-bottom: 0%; margin-left: 9%;margin-top: -2%; float: left"></div>
<div id="fecha"  style="width: 15%; height: 180px; margin-left: 2%; margin-top: 0%;margin-top: 5%; float: left; font-weight: bold; font-size: large"></div>
<div id="containerwplaca"  style="width: 20%; height: 180px; margin-left: 2%; margin-top: 0%;margin-top: -2%; float: left"></div>


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

    chart_vbat = new Highcharts.Chart ({
        chart: {
            renderTo: 'containervbat',
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
                //text : 'kkkk'
                },
            
        title: {
            y:155,
            floating: true,
            /*style:{
                color: 'Purple',
                fontSize:'18px',
                },*/
            text: 'Vbat',
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
            min: Vbat_min,
            max: Vbat_max,
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
                //text: 'pp1' 
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
                from: Vbat_min,
                to: Vbat_bajo_amarillo,
                color: '#DF5353' // red
              },
              {
                from: Vbat_bajo_amarillo,
                to: Vbat_verde,
                color: '#DDDF0D' // yellow
              },
              {
                from: Vbat_verde,
                to: Vbat_alto_amarillo,
                color: '#55BF3B' // green
              },
              {
                from: Vbat_alto_amarillo,
                to: Vbat_alto_rojo,
                color: '#DDDF0D' // yellow
              },
              {
                from: Vbat_alto_rojo,
                to: Vbat_max,
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
            name: 'Vbat',
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
                    return Highcharts.numberFormat(this.y,2) + " V"
                    },
              }
          }]
        });
    
    chart_soc = new Highcharts.Chart ({
        chart: {
            renderTo: 'containerSOC',
            type: 'solidgauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false,
            backgroundColor: null,//'#ffffff',//'#f2f2f2',
            borderColor: null
              
          },
        title: {
            y:60,
            widthAdjust: 0,
            style: {
                fontSize: '30px'
                },
            floating: true,
            text: 'SOC'
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
            min: SOC_min,
            max: SOC_max,
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
                y: 80,//-30,
                floating: true,
                //align: 'right',
                //verticalAlign: 'bottom',
                //x:0,
                style: {
                   fontSize: '15px'
                  },
                text: 'PoP' //null //'V_BAT'
                },
            
            labels: { // valores de la escala
                y: 0,
                min: SOC_min,
                max: SOC_max,
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
                text: 'HOLA', //null //'V_BAT'
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
            min: Temp_bat_min,
            max: Temp_bat_max,
            pane: 1,
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
            name: 'TempBat',
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
                    return Highcharts.numberFormat(this.y,1) + "ºC Bat"
                  }
              },
            dial: {
                backgroundColor : 'black',   //Color de la aguja
                radius: '80%' //longitud de la aguja
              },
          },{
            yAxis: 1,
            name: 'TempReg',
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
                    return Highcharts.numberFormat(this.y,0) + "ºC Reg"
                  }
              },
            dial: {
                backgroundColor : 'red',   //Color de la aguja
                radius: '80%' //longitud de la aguja
              },
          }]        
      });
    
    chart_iplaca = new Highcharts.Chart ({
        chart: {
            renderTo: 'containeriplaca',
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
            text: 'Iplaca',
            style: {
                fontSize: '14px',
                color: 'black'
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
                min: Intensidad_min,
                max: Intensidad_max,

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
                    y:20,
                    text: null, //'I_PLACA'
                },
                plotBands: [{
                    from: 0,
                    to: Intensidad_carga_rojo,
                    color: '#55BF3B' // green
                }, {
                    from: Intensidad_descarga_amarillo,
                    to: 0,
                    color: '#DDDF0D' // yellow
                }, {
                    from: Intensidad_min,
                    to: Intensidad_descarga_amarillo,
                    color: '#DF5353' // red
                }, {
                    from: Intensidad_carga_rojo,
                    to: Intensidad_max,
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
            name: 'Iplaca',
            data: [],
            dataLabels: {
                allowOverlap:true,
                enabled: true,
                borderWidth: 0,
                y: 0,
                style: {
                    fontSize: '14px',
                    color: 'black'
                    },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,1) + " A"
                    },
                },
            dial: {
                backgroundColor: (([this.y] <= 0) ? 'black' : 'red')
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
                    return Highcharts.numberFormat(this.y,1) + " V"
                    },
              }
          }]
        });
                             

    function recibirDatosFV() {
      $.ajax({
        url: 'datos_srne.php',
        success: function(data) {
          try {             
            // tiempo_sg, "%d-%B-%Y -- %H:%M:%S"
            fecha = data["Tiempo"];
            
            Vbat = data["Vbat"]; 
            SOC = data["SoC"];
            Mod_bat = data["Estado"];
            Vplaca = data["Vplaca"];
            Iplaca = data["Iplaca"];
            Wplaca = Iplaca * Vbat
            TempBat = data["Temp0"];
            TempReg = data["Temp1"];
                        
            $('#fecha').text(fecha);

            // Actualizacion reloj Vbat 
            chart_vbat.series[0].setData([Vbat]);
            chart_iplaca.series[0].setData([Iplaca]); 
            
            // Actualizacion SOC   
            chart_soc.series[0].setData([SOC]);
            chart_soc.yAxis[0].setTitle({
              text: Mod_bat
                });
                
            // Actualizacion reloj Temp
            chart_temp.series[0].setData([TempBat]); //Bat 
            chart_temp.series[1].setData([TempReg]); //Reg

            // Actualizacion reloj Vplaca
            chart_vplaca.series[0].setData([Vplaca]); //Vplaca

             // Actualizacion reloj Wplaca 
            chart_wplaca.series[0].setData([Wplaca]); 

            x = (new Date()).getTime(); // current time                                       
          }           
          catch (e) {
            var d = new Date();
            s = d.getSeconds()
            t = d.getHours() + ':' + d.getMinutes() + ':' + s;
                
            chart_vplaca.series[0].setData([s]); //Vplaca
            chart_temp.series[0].setData([s]);    //Temp 
                
            //grafica_t_real.setTitle({
            //    text: 'SIN RESPUESTA - Hora=' + t,
            //     });              
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
include("pie.inc");
?>

