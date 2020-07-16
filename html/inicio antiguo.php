
<HTML>

<body>

<meta charset="utf-8">

<!-- Importo el archivo Javascript de Highcharts directamente desde la RPi 
<script src="js/jquery.js"></script>

<script src="js/highcharts.js"></script>
<script src="js/highcharts-more.js"></script>
<script src="js/highcharts-3d.js"></script>

<script src="js/themes/grid.js"></script>

<script src="js/modules/solid-gauge.js"></script>
-->

<!-- Latest compiled and minified JavaScript -->
<script src="https://code.jquery.com/jquery.js"></script>

<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/highcharts-3d.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>
<script src="https://code.highcharts.com/modules/solid-gauge.js"></script>

<div id="grafica_voltaje" style="width: 40%; height: 260px; margin-left: 0%; float: left"></div>

<div id="containertemp"  style="width: 20%; height: 180px; margin-left: 0%; float: right"></div>
<div id="containerSOC"  style="width: 20%; height: 180px; margin-left: 0%; float: right"></div>
<div id="containervbat"  style="width: 20%; height: 180px; margin-left: 0%; float: right"></div>

<div id="containerconsumo"  style="width: 20%; height: 180px; margin-left: 0%; float: right"></div>
<div id="containeribat"  style="width: 20%; height: 180px; margin-left: 0%; float: right"></div>
<div id="containerwplaca"  style="width: 20%; height: 180px; margin-left: 0%; float: right"></div>

<div id="grafica_intensidad" style="width: 40%; height: 260px; margin-left: 0%;float: left"></div>
<div id="container_reles" style="width: 60%; height: 160px; margin-right: 0; float: right"></div>


<!--
<script src='https://openweathermap.org/themes/openweathermap/assets/vendor/owm/js/d3.min.js'></script>

<script>window.myWidgetParam ? window.myWidgetParam : window.myWidgetParam = []; 
 window.myWidgetParam.push({id: 11,cityid: '6359366',appid: '755658d8a95ced40e5fd850f33183f9d',units: 'metric',containerid: 'openweathermap-widget-11',  }); 
 (function() {var script = document.createElement('script');script.async = true;script.charset = "utf-8";
 script.src = "https://openweathermap.org/themes/openweathermap/assets/vendor/owm/js/weather-widget-generator.js";
 var s = document.getElementsByTagName('script')[0];s.parentNode.insertBefore(script, s);  })();
 </script>

<div id="openweathermap-widget-11"></div>
-->


<br>
<br style="clear:both;"/>
<br>

</body>

<script>

$(function () {
    var Vbat=24;
    var Ibat=0;
    var Iplaca=10;
    var Vplaca=0;
    var Aux1=0;
    var Aux2=0;
    var PWM=0;
    requestData(); 

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
            events: {
                load: requestData
                }
            },
        title: {
            y:140,
            floating: true,
            text: 'Vbat',
            },
        credits: {
            enabled: false
            },
        pane: {
            size: '90%',
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
                outerRadius: '120%'
                }, {
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#333'],
                        [1, '#FFF']
                        ]
                    },
                borderWidth: 1,
                outerRadius: '107%'
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
            min: 22,
            max: 32,
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
                from: 25.7,
                to: 28.8,
                color: '#55BF3B' // green
              }, {
                from: 24,
                to: 25.7,
                color: '#DDDF0D' // yellow
              }, {
                from: 28.8,
                to: 30,
                color: '#DDDF0D' // yellow
              }, {
                from: 22,
                to: 24,
                color: '#DF5353' // red
              }, {
                from: 30,
                to: 32,
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
            data: [],//requestData(),
            dataLabels: {
                enabled: true,
                allowOverlap: true,
                borderWidth: 0,
                y: 0,
                style: {
                   fontSize: '20px'
                  },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,1) + " V"
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
            plotShadow: false
          },
        title: {
            y:150,
            floating: true,
            text: 'SOC',
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
                innerRadius: '60%',
                outerRadius: '100%',
                shape: 'arc'
              }
          },
        tooltip: {
            enabled: false
          },
        yAxis: {
            min: 60,
            max: 100,
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
                y:20,//-30,
                x:0,
                style: {
                   fontSize: '20px'
                  },
                text: 'PP' //null //'V_BAT'
                },
            
            labels: { // valores de la escala
                y: 0,
                min: 50,
                max: 100,
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
            data: [], //[88.5],
            dataLabels: {
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
            plotShadow: false
          },
        title: {
            y:140,
            floating: true,
            text: 'Temp',
          },
        credits: {
            enabled: false
          },   
        pane: [{
            size: '90%',
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
                outerRadius: '120%'
              }, {
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#333'],
                        [1, '#FFF']
                      ]
                  },
                borderWidth: 1,
                outerRadius: '107%'
              }, {
                // default background
              }, {
                backgroundColor: '#DDD',
                borderWidth: 0,
                outerRadius: '105%',
                innerRadius: '103%'
              }]

          }, {
            size: '90%',
            startAngle: 20,
            endAngle: 150,
            background: []
          }],
            // the value axis
        yAxis: [{
            min: -10,
            max: 50,

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
                from: 20,
                to: 30,
                color: '#55BF3B' // green
              }, {
                from: 10,
                to: 20,
                color: '#DDDF0D' // yellow
              },{
                from: -10,
                to: 10,
                color: '#3C14BF' // blue
              }, {
                from: 30,
                to: 50,
                color: '#DF5353' // red
              }]
          }, {    
            reversed: true,
            min: 0,
            max: 100,
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
                from: 0,
                to: 50,
                color: '#55BF3B' // green
              }, {
                from: 50,
                to: 70,
                color: '#DDDF0D' // yellow
              }, {
                from: 70,
                to: 100,
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
                    return Highcharts.numberFormat(this.y,1) + "ºC"
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
                    fontSize: '15px'
                  },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,0) + "ºC"
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
            alignTicks: false
          },
        title: {
            y:140,
            floating: true,
            text: 'Consumo',
          },
        credits: {
            enabled: false
          },
        pane: [{
            size: '90%',
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
                outerRadius: '120%'
              }, {
                backgroundColor: {
                    linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                    stops: [
                        [0, '#333'],
                        [1, '#FFF']
                      ]
                  },
                borderWidth: 1,
                outerRadius: '107%'
              }, {
                // default background
              }, {
                backgroundColor: '#DDD',
                borderWidth: 0,
                outerRadius: '105%',
                innerRadius: '103%'
              }]

          }, {
            size: '90%',
            startAngle: 10,
            endAngle: 150,
            background: []
          }],

            // the value axis
        yAxis: [{
            min: 0,
            max: 5000,
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
                from: 0,
                to: 3000,
                color: '#55BF3B' // green
              }, {
                from: 3000,
                to: 4000,
                color: '#DDDF0D' // yellow
              }, {
                from: 4000,
                to: 5000,
                color: '#DF5353' // red
              }]
          }, {
            reversed: true,
            min: 0,
            max: 210,
            pane: 1,

            minorTickInterval: 'auto',
            minorTickWidth: 1,
            minorTickLength: 10,
            minorTickPosition: 'inside',
            minorTickColor: '#666',
            tickPixelInterval: 30,
            tickInterval: 40,
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
                from: 0,
                to: 125,
                color: '#55BF3B' // green
              }, {
                from: 125,
                to: 166,
                color: '#DDDF0D' // yellow
              }, {
                from: 166,
                to: 210,
                color: '#DF5353' // red
              }]
          }],
        
        navigation: {
            buttonOptions: {
                enabled: false
              }
          },
        tooltip: {
            enabled: false
          },
        series: [{
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
          },{
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
                    fontSize: '15px'
                  },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,0) + "A"
                  }
              },
            dial: {
                backgroundColor : 'red',   //Color de la aguja
                radius: '80%' //longitud de la aguja
              },
          }]        
      });
    
    chart_ibat = new Highcharts.Chart ({
        chart: {
            renderTo: 'containeribat',
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false
            },
        title: {
            y:130,
            floating:true,
            text: 'Ibat',
            style: {
                fontSize: '12px',
                color: 'red'
                },
            },
        subtitle: {
            y:142,
            floating:true,
            text: 'Iplaca',
            style: {
                fontSize: '14px',
                color: 'green'
                },
            },
            
            
        credits: {
                enabled: false
            },
        pane: {
                size: '90%',
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
                    outerRadius: '120%'
                }, {
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, '#333'],
                            [1, '#FFF']
                        ]
                    },
                    borderWidth: 1,
                    outerRadius: '107%'
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
                min: -130,
                max: 130,

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
                    text: null, //'I_BAT'
                },
                plotBands: [{
                    from: 0,
                    to: 80,
                    color: '#55BF3B' // green
                }, {
                    from: -40,
                    to: 0,
                    color: '#DDDF0D' // yellow
                }, {
                    from: -130,
                    to: -40,
                    color: '#DF5353' // red
                }, {
                    from: 80,
                    to: 130,
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
            name: 'Ibat',
            data: [],
            dataLabels: {
                allowOverlap:true,
                enabled: true,
                borderWidth: 0,
                y: 0,
                style: {
                    fontSize: '14px',
                    color: 'red'
                    },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,1) + " A"
                    },
                },
            dial: {
                backgroundColor: (([this.y] <= 0) ? 'red' : 'green')
                }
            },{
            name: 'Iplaca',
            data: [],
            dataLabels: {
                allowOverlap:true,
                enabled: true,
                borderWidth: 0,
                y: 12,
                style: {
                    fontSize: '14px',
                    color: 'green'
                    },
                formatter: function() {
                    return Highcharts.numberFormat(this.y,1) + " A"
                    },
                },
            dial: {
                backgroundColor: (([this.y] <= 0) ? 'green' : 'red')
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
            plotShadow: false
            },
        title: {
            y:140,
            floating:true,
            text: 'Wplacaaaa',
            },
        credits: {
                enabled: false
            },
        pane: {
                size: '90%',
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
                    outerRadius: '120%'
                }, {
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, '#333'],
                            [1, '#FFF']
                        ]
                    },
                    borderWidth: 1,
                    outerRadius: '107%'
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
            max: 6000,
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
                distance: -25,
                step: 1,
                style:{
                  fontWeight:'bold',
                  //color:#666666,
                  //cursor:default,
                  fontSize:'14px',
                  },
                rotation: 'auto'
            },
            title: {
                y:20,//-30,
                x:0,
                style: {
                   fontSize: '11px'
                  },
                text: '' //null 
                },
            
        plotBands: [{
                    from: 500,
                    to: 3000,
                    color: '#55BF3B' // green
                }, {
                    from: 3000,
                    to: 5000,
                    color: '#DDDF0D' // yellow
                }, {
                    from: 5000,
                    to: 6000,
                    color: '#DF5353' // red
                }, {
                    from: 0,
                    to: 500,
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
            name: 'Wplacaa',
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
                            
    chart_reles =new Highcharts.Chart({
        chart: {
            renderTo: 'container_reles',
            type: 'column',
            options3d: {
                enabled: true,
                alpha: 0,
                beta: 10,
                depth: 100
            },
            events: {
               load: requestRele
                }
            
        },
        //Data: {
            // table: 'reles_estado'
        //},

        plotOptions: {
                  column: {
                    dataLabels: {
                        enabled: true,
                        crop: false,
                        overflow: 'none',
                    },
                    enableMouseTracking: false
                  }
            },

        //     plotOptions: {
        //         column: {
        //             depth: 40
        //           }
        //        },

        credits: {
             enabled: false
             },
        title: {
              y:10,
              text: 'SITUACION RELES'
             },
        subtitle: {
              text: null
             },
        xAxis: {
             categories: [] //Nombre_Reles()
               },
        yAxis: {
              min: 0,
              max: 100,
              tickInterval:10,
              allowDecimals: false,
              labels: {
                    enabled: true
               },
              title: {
                    enabled: false
               }
             },

        series: [{
                name: 'Estado Relés',
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
                
    grafica_v = new Highcharts.Chart ({
        chart: {
            renderTo: 'grafica_voltaje',
            zoomType: 'xy',
            plotBorderWidth: 1,
            alignTicks: false,
            animation: Highcharts.svg, // don't animate in old IE
            marginRight: 10,
            },
        title: {
            text: '', //'Grafico Tiempo Real', //'Vbateria',
            x:-0
            },
        //subtitle: {
        //text: 'Prueba Dinamica'
        //},
        credits: {
            enabled: false
            },
        xAxis: {
            type: 'datetime'
            },
        yAxis: [{ // 1er yAxis (num0)
            gridLineWith: 0,
            min: 11, //22
            max: 33,
            tickInterval:1,
            minorGridLineColor: 'transparent',
            labels: {
                format: '{value} V',
                style: {
                    color: Highcharts.getOptions().colors[0]
                    }
            },
            title: {
                text: null
                },
            opposite: false,
            plotLines: [{
                value: 28.5,
                width: 2,
                color: 'green',
                dashStyle: 'shortdash',
                label: {
                    text: 'Vabs'
                    }
                },{
                value: 27.6,
                width: 2,
                color: 'red',
                dashStyle: 'shortdash',
                label: {
                    text: 'Vflot'
                    }
                }]
            }],

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

        legend: {
            layout: 'vertical',
            floating: true,
            align: 'left',
            verticalAlign: 'bottom',
            //x: -100,
            y: 10,
            borderWidth: 0
            },

        series: [{
            name: 'Vbat',
            data: (function () {
            // generate an array of random data
                var data = [],
                time = (new Date()).getTime(),
                i;
                for (i = -100; i <= 0; i += 1) {
                    data.push({
                        x: time + i * 5000,
                        y: 24
                      });
                    }
                return data;
                }())
            },]
                        
        });
                
    grafica_i = new Highcharts.Chart ({
        chart: {
         renderTo: 'grafica_intensidad',
         plotBorderWidth: 1,
         zoomType: 'xy',
         alignTicks: false,
         animation: Highcharts.svg, // don't animate in old IE
         marginRight: 10,
               },
        title: {
                text: null,
                // x:-0
            // },
        // subtitle: {
        // text: 'Prueba Dinamica'
         },
        credits: {
        enabled: false
        },
        xAxis: {
        type: 'datetime'
        },
        yAxis: {
            gridLineWith: 2,
            min: -180,
            max: 220,
            tickInterval:40,
            minorGridLineColor: 'transparent',
            //endOnTick: true,
            //maxPadding: 0.2,
            //tickAmount: 7,
            labels: {
                    format: '{value} A',
                    style: {
                        color: Highcharts.getOptions().colors[0]
                    }
                },
            title: {
                    text: null,
                    style: {
                        color: Highcharts.getOptions().colors[0]
                    }
                },
            opposite: false,
            plotLines: [{
                value: 120,
                width: 2,
                color: 'green',
                dashStyle: 'shortdash',
                label: {
                text: 'Max Carga'
                }
              },{
                value: -120,
                width: 2,
                color: 'red',
                dashStyle: 'shortdash',
                label: {
                  text: 'Max Descarga'
                }
            }]
          },
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
        {      name: 'Ibat',
                data: (function () {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -100; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 5000,
                            y: 0
                        });
                    }
                    return data;
                }())
            },
        {      name: 'IPlaca',
                data: (function () {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -100; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 5000,
                            y: 0
                        });
                    }
                    return data;
                }())
            },
        {      name: 'VPlaca',
                data: (function () {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -100; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 5000,
                            y: 0
                        });
                    }
                    return data;
                }())
            },
        {      name: 'Aux1',
                data: (function () {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -100; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 5000,
                            y: 0
                        });
                    }
                    return data;
                }())
            },
        {      name: 'PWM',
                data: (function () {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -100; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 5000,
                            y: 0
                        });
                    }
                    return data;
                }())
            },
        
                ]
                                
      });

    function requestData() {
      $.ajax({
        url: 'datos_fv.php',
        success: function(data) {
                        
            chart_vbat.series[0].setData([data[0][3]]);
            chart_vbat.yAxis[0].setTitle({
              text: data[0][8] - data[0][9]+ ' Wh' //Wh bateria  posi-neg
                });
            
            chart_soc.series[0].setData([data[0][4]]);
            chart_soc.yAxis[0].setTitle({
              text: data[0][17] // Mod_bat
                });
                
            chart_temp.series[0].setData([data[0][14]]); //Temp Bat
            chart_temp.series[1].setData([data[1]]);     //CPU

            chart_ibat.series[0].setData([data[0][2]]);  //Ibat
            chart_ibat.series[1].setData([data[0][10]]); //Iplaca
            
            chart_wplaca.series[0].setData([data[0][12]]);
            //chart_wplaca.setTitle({
            //  text: data[0][12] // ejem de cambio de titulo
            //   });
            chart_wplaca.yAxis[0].setTitle({
              text: [data[0][13]+'Wh'] // Wh_placa
                });
            
            chart_consumo.series[0].setData([(data[0][16])]); // Consumo
            chart_consumo.series[1].setData([data[0][10]-data[0][2]]); //Iplaca -Ibat
            
            x = (new Date()).getTime(), // current time
            
            grafica_v.series[0].addPoint([x, data[0][3]], true, true);
            grafica_v.setTitle({
              text: 'Hora ' + data[0][1]
                });
            
            
            grafica_i.series[0].addPoint([x, data[0][2]], true, true); //Ibat
            grafica_i.series[1].addPoint([x, data[0][10]], true, true); //Iplaca
            grafica_i.series[2].addPoint([x, data[0][11]], true, true); //Vplaca
            grafica_i.series[3].addPoint([x, data[0][6]], true, true); //Aux1
            grafica_i.series[4].addPoint([x, data[0][15]], true, true); //PWM
            
            
            setTimeout(requestData, 3000);
          },
        cache: false
      });
      }
    
    function requestRele() {
      $.ajax({
        url: 'datos_reles.php',
        success: function(data) {
            var tCategories = [];
            chart_reles.series[0].setData(data);
            for (i = 0; i < chart_reles.series[0].data.length; i++) {
                tCategories.push(chart_reles.series[0].data[i].name);
            }
            chart_reles.xAxis[0].setCategories(tCategories);
         //   chart_reles.xAxis[0].setCategories(data);
         //    console.log(data)
            setTimeout(requestRele, 3000);
        },
        cache: false
      });
      }     

});

</script>
</html>
