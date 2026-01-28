const config = {
    
    menu_web:{
        Inicio: {
            Dibujo:'fv.html',
            Relojes:'inicio_con_celdas.php',
        },
        Utilidades:{
            Meteo:'meteogram.php',
            SOC:'actualizar_soc.php',
            Log: 'log.php',
            Parametros: 'parametros.php',
            Servicios: 'servicios.php',
        },
        Graficas :{
            Kwh_Bat: 'wh.php',
            Promedios: 'prom_30.php',
            H_Fechas: 'historico_fechas.php',
            H_8_horas: 'historico_horas.php',
            H_1_dia: 'historico1.php',
            H_3_dias: 'historico3c.php',
            H_Mes: 'historico_mes.php',
            H_Personal: 'historico_aux.php',
            H_Ciclado: 'historico_soh.php',
            Extra: 'grafica_elige.php',
            Diario: 'diario.php',
            Carga_Desc: 'wh_2.php',
        },
        Equipos :{
            Equipos: 'equipos.php',
        },
        Reles :{
            Estado: 'reles.php',
            T_Activ: 'horas_reles.php'  
        },
        
        Celdas :{
            H_Celdas: 'historico_celdas.php',   
        },
        
        Ayuda : 'ayuda.php',
            
        
    },
    
    laterales: {
        izquierdo: {
            elements: {
                CONTROL: {
                    campoBD: '',
                    value: 'CONTROL',
                    unit: '',
                    size: '20px',
                    //titleColor: 'black',
                    //valueColor: 'black',
                    backgroundColor: '#FFE36C',
                    bold: true,
                    showTitle: false,
                },
                FV: {
                    campoBD: '_PVControl+.PVControl+',
                    value: '',
                    unit: '',
                    size: '18px',
                    titleColor: 'black',
                    valueColor: 'black',
                    backgroundColor: 'lightgreen',
                    bold: true,
                    
                },
                Separador_1: {backgroundColor: 'lightgray', value: '&nbsp;', size: '10px',showTitle: false,},

                SOC: {
                    campoBD: 'FV.SOC',
                    value: 0,
                    unit: '%',
                    size: '18px',
                    titleColor: 'black',
                    valueColor: 'blue',
                    //backgroundColor: '#d6d6d6',
                    bold: true,
                    //width: 100,
                    avisos: {
                        1: {backgroundColor:'lightgreen', condicion:'value > 85'},
                    }
                },
                SOC_MAX: {
                    campoBD: 'FV.SOC_max',
                    value: 0,
                    unit: '%',
                    size: '16px',
                    titleColor: 'black',
                    valueColor: 'blue',
                    //backgroundColor: '',
                    bold: true,
                    avisos: {
                        1: {color:'lightpink', condicion:'value < 85'},
                    }
                },
                SOC_MIN: {
                    campoBD: 'FV.SOC_min',
                    value: 0,
                    unit: '%',
                    size: '16px',
                    titleColor: 'black',
                    valueColor: 'blue',
                    //backgroundColor: 'pink',
                    bold: true,
                    avisos: {
                        1: {color:'lightpink', condicion:'value < 70'},
                    }
                },
                
                Separador_2: {backgroundColor: 'lightgray', value: '&nbsp;', size: '10px', showTitle: false,},
                
                AEMET: {
                    campoBD: 'AEMET.0.cielo.12-24',
                    value: '',
                    unit: '',
                    size: '12px',
                    titleColor: 'black',
                    valueColor: 'blue',
                    //backgroundColor: 'pink',
                    bold: true,
                    //width: 100,
                    
                },
 
                TEXTO: {
                    campoBD: '',
                    value: 'En un lugar de la mancha .....',
                    unit: '',
                    size: '12px',
                    titleColor: 'black',
                    valueColor: 'blue',
                    //backgroundColor: 'pink',
                    bold: true,
                    width: 150,
                  
                },
                // Agregar más elementos según sea necesario
            }
        },
        derecho_desactivado: {
            elements: {
                SOC_MAX: {
                    campoBD: 'FV.SOC_max',
                    value: 0,
                    unit: '%',
                    size: '12px',
                    titleColor: 'black',
                    valueColor: 'blue',
                    backgroundColor: 'pink',
                    bold: true,
                    position: { x: 0, y: 0 },
                    width: 100,
                    visualizacion: 'siempre'
                }
                // Agregar más elementos según sea necesario
            }
        }
    },
    
    blockMargin: '20px 45px', // separacion entre filas, columnas al dibujar
    
    filas: {
        fila1: {
            Placa1: {
                image: 'placa1.avif',
                size: { width: 100, height: 100 },
                connectTo: { id: 'MPPT1', from: 'bottom',  to: 'top', control: 'Wplaca', max: 3000, min: 0,},
                avisos: {
                    Rojo: {color:'red', condicion:'d_["MPPT1"]["Wbat"] < 5 && d_["MPPT2"]["Estado_regulador"] !== "NOCHE"'},
                    Amarillo: {color:'yellow', condicion:'(d_["MPPT1"]["Wbat"]) > 1000'},
                    Cyan: {color:'cyan', condicion:'new Date(d_["MPPT1"]["tiempo"]) < new Date(now.getTime() - 1 * 60 * 1000)'},
                    Rojo: {color:'red', condicion:'new Date(d_["MPPT1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                    KO: {image: 'luna.JPG', size: { width: 100, height: 100 }, verAviso: false, color:'red', condicion:'d_["MPPT1"]["Vplaca"] < 5'},
                    OK: {image: 'placa1.avif', size: { width: 100, height: 100 }, verAviso: false, color:'transparent', condicion:'d_["MPPT1"]["Wbat"] > 5'},
                    
                },
                elements: {
                    Solar1: {
                        campoBD: '',
                        value: 'S1',
                        unit: '',
                        size: '20px',
                        titleColor: 'yellow',
                        valueColor: 'yellow',
                        bold: true,
                        position: { x: 36, y: 47 },
                        showTitle: false
                    },
                    Wplaca: {
                        sensor: 'd_["MPPT1"]["Wbat"]',
                        value: 0,
                        unit: 'W',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 60, y: 80 },
                        width: 80,
                        showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 2500'},
                        },
                        
                    },
                    Vplaca: {
                        campoBD: 'MPPT1.Vplaca',
                        value: 0,
                        unit: 'V',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 80, y: 45 },
                        width: 70,
                        //visualizacion: 'modal',
                        showTitle: false,
                        avisos: {
                            Amarillo: {
                                color:'yellow', // tamien se puede usar backgroundColor
                                valueColor:'red',
                                //size: '20px',
                                //position: { x: 80, y: 50 },
                                condicion:'value < 5'
                            },
                        },
                    },
                    Total: {
                        //campoBD: 'MPPT1.Wh_placa',
                        sensor : 'Math.floor(d_["FV"]["Wh_placa"]/1000)',
                        value: 99,
                        unit: 'Kwh',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        backgroundColor: 'lightgrey',
                        bold: true,
                        position: { x: -115, y: 50 },
                        width: 125,
                        //showTitle: false
                    },

                    Wh_placa: {
                        campoBD: 'MPPT1.Wh_placa',
                        value: 99,
                        unit: 'Wh',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'green',
                        bold: true,
                        position: { x: 0, y: -5 },
                        //width: 100,
                        visualizacion: 'siempre',
                        showTitle: false
                    },
                    Wplaca_max: {campoBD: 'MPPT1.Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},
                }
            },
            Placa2: {
                image: 'placa1.avif',
                size: { width: 100, height: 100 },
                connectTo: {
                    id: 'MPPT2',
                    from: 'bottom',
                    to: 'top',
                    control: 'Wplaca',
                    max: 3000,
                    min: 0
                },
                 avisos: {
                    KO: {color:'red', condicion:'new Date(d_["MPPT2"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                elements: {
                    Solar2: {
                        campoBD: '',
                        value: 'S2',
                        unit: '',
                        size: '20px',
                        titleColor: 'yellow',
                        valueColor: 'yellow',
                        //backgroundColor: 'green',
                        bold: true,
                        position: { x: 36, y: 47 },
                        //width: 100,
                        visualizacion: 'siempre',
                        showTitle: false
                    },
                    Wplaca: {
                        campoBD: 'MPPT2.Wbat',
                        value: 0,
                        unit: 'W',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'yellow',
                        bold: true,
                        position: { x: 60, y: 80 },
                        width: 80,
                        visualizacion: 'siempre',
                        showTitle: false,
                        
                    },
                    Vplaca: {
                        campoBD: 'MPPT2.Vplaca',
                        value: 0,
                        unit: 'V',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        bold: true,
                        width: 100,
                        position: { x: 60, y: 45 },
                        showTitle: false
                    },
                    Wh_placa: {
                        campoBD: 'MPPT2.Wh_placa',
                        value: 99,
                        unit: 'Wh',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'green',
                        bold: true,
                        position: { x: 0, y: -5 },
                        //width: 100,
                        visualizacion: 'siempre',
                        showTitle: false
                    },
                    Wplaca_max: {campoBD: 'MPPT2.Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},

                }
            },   
            Placa3: {
                image: 'placa1.avif',
                size: { width: 100, height: 100 },
                connectTo: {id: 'MPPT3', from: 'bottom', to: 'top', control: 'Wplaca', max: 3000, min: 0},
                 avisos: {KO: {color:'red', condicion:'new Date(d_["TABLA_MPPT"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'}},
                
                elements: {
                    Solar2: {
                        campoBD: '',
                        value: 'S3',
                        unit: '',
                        size: '20px',
                        titleColor: 'yellow',
                        valueColor: 'yellow',
                        //backgroundColor: 'green',
                        bold: true,
                        position: { x: 36, y: 47 },
                        //width: 100,
                        visualizacion: 'siempre',
                        showTitle: false
                    },
                    Wplaca: {
                        //campoBD: 'TABLA_MPPT.MPPT3_Wplaca',
                        sensor : 'Math.floor(d_["TABLA_MPPT"]["MPPT3_Wplaca"])',
                        value: 0,
                        unit: 'W',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'yellow',
                        bold: true,
                        position: { x: 60, y: 80 },
                        width: 80,
                        visualizacion: 'siempre',
                        showTitle: false,
                        
                    },
                    
                    Wh_placa: {
                        //campoBD: 'TABLA_MPPT.Wh_MPPT3',
                        sensor : 'Math.floor(d_["TABLA_MPPT"]["Wh_MPPT3"])',
                        value: 99,
                        unit: 'Wh',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'green',
                        bold: true,
                        position: { x: 0, y: -5 },
                        //width: 100,
                        visualizacion: 'siempre',
                        showTitle: false
                    },
                    //Wplaca_max: {campoBD: 'MPPT2.Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},

                }
            },   

 
        },
        fila2: {
            MPPT1: {
                image: 'MPPT.jpg',
                size: { width: 50, height: 80 },
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["MPPT1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                connectTo: {
                    id: 'BATERIA',
                    from: 'bottom',
                    to: 'top',
                    control: 'Ibat',
                    max: 60,
                    min: 0
                },
                elements: {
                    MODO: {
                        campoBD: 'MPPT1.Estado_regulador',
                        value: '',
                        unit: '',
                        size: '10px',
                        titleColor: 'black',
                        valueColor: 'red',
                        backgroundColor: 'white',
                        bold: true,
                        position: { x: -3, y: 9 },
                        //width: 100,
                        showTitle: false
                    },
                    Vbat: {
                        campoBD: 'MPPT1.Vbat',
                        value: 0,
                        unit: 'V',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -40, y: 30 },
                        //width: 100,
                        showTitle: false
                    },
                    Ibat: {
                        campoBD: 'MPPT1.Ibat',
                        value: 0,
                        unit: 'A',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -35, y: 78 },
                        //width: 100,
                        showTitle: false
                        
                    },
                    Vabs: { campoBD: 'MPPT1.Vabs', value: 0, unit: "V",  visualizacion: 'modal'  },
                    Vflot: { campoBD: 'MPPT1.Vflot', value: 0, unit: "V",  visualizacion: 'modal'  },
                                        // Agregar más elementos según sea necesario
                }
            },
            MPPT2: {
                image: 'MPPT.jpg',
                size: { width: 50, height: 80 },
                connectTo: {
                    id: 'BATERIA',
                    from: 'bottom',
                    to: 'top',
                    control: 'Ibat',
                    max: 60,
                    min: 0
                },
                 avisos: {
                    KO: {color:'red', condicion:'new Date(d_["MPPT2"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                elements: {
                    MODO: {
                        campoBD: 'MPPT2.Estado_regulador',
                        value: '',
                        unit: '',
                        size: '10px',
                        titleColor: 'black',
                        valueColor: 'red',
                        backgroundColor: 'white',
                        bold: true,
                        position: { x: -3, y: 9 },
                        //width: 100,
                        showTitle: false
                    },
                    Vbat: {
                        campoBD: 'MPPT2.Vbat',
                        value: 0,
                        unit: 'V',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 30, y: 30 },
                        width: 100,
                        showTitle: false
                    },
                    Ibat: {
                        campoBD: 'MPPT2.Ibat',
                        value: 0,
                        unit: 'A',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 22, y: 78 },
                        width: 100,
                        showTitle: false
                    },
                    Vabs: { campoBD: 'MPPT2.Vabs', value: 0, unit: "V",  visualizacion: 'modal'  },
                    Vflot: { campoBD: 'MPPT2.Vflot', value: 0, unit: "V",  visualizacion: 'modal'  },
                                        
                }
            },
            MPPT3: {
                image: 'mppt_easun_1.JPG',
                size: { width: 50, height: 80 },
                connectTo: {
                    id: 'BATERIA',
                    from: 'bottom',
                    to: 'top',
                    control: 'Wplaca',
                    max: 3000,
                    min: 0
                },
                 avisos: {
                    KO: {color:'red', condicion:'new Date(d_["TABLA_MPPT"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                elements: {
                    Wplaca: {
                        campoBD: 'TABLA_MPPT.MPPT3_Wplaca',
                        sensor : 'Math.floor(d_["TABLA_MPPT"]["MPPT3_Wplaca"])',
                        value: 0,
                        unit: 'W',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 22, y: 8 },
                        width: 100,
                        showTitle: false
                    },
                                        
                }
            },
        },
        fila3: {
            R551_Termo: {
                image: 'termo_agua.jpg',
                size: { width: 53, height: 80 },
                connectTo: { id: 'ANENJI1', from: 'right',  to: 'left', control: 'Wconsumo', max: 2000, min: 10, colorLineaPositiva:'red',flujoLinea:'inverso',},
                
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["MQTT"]["tele/PVControl/Reles/55/SENSOR"]["Time"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                elements: {
                    Modo: {
                        campoBD: 'RELES.551.modo',
                        value: 0,
                        unit: '',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -29, y: 33 },
                        width: 30,
                        showTitle: false,
                        avisos1: {
                            OFF: {color:'grey', condicion:'value === "OFF"'},
                            ON: {color:'red', condicion:'value === "ON"'},
                            PRG: {color:'cyan', condicion:'value === "PRG"'},
                            
                        },
                        
                    },
                    Estado: {
                        campoBD: 'RELES.551.estado',
                        value: 0,
                        unit: '',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -29, y: 53 },
                        width: 30,
                        showTitle: false,
                        avisos: {
                            0: {color:'grey', condicion:'value === 0'},
                            100: {color:'red', condicion:'value === 100'},
                            PWM: {color:'cyan', condicion:'value > 0 && value < 100'},    
                        },
                        
                    },
                    Nombre: {
                        campoBD: 'RELES.551.nombre',
                        value: 0,
                        unit: '',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -10, y: 75 },
                        width: 80,
                        showTitle: false,
                            
                        
                    },
                    Wconsumo: {
                        campoBD: 'MQTT.tele/PVControl/Reles/55/SENSOR.ENERGY.Power',
                        value: 0,
                        unit: 'W',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 55, y: 20 },
                        width: 60,
                        showTitle: false,
                        avisos: {
                            ON: {color:'pink', condicion:'value >50'},
                        },    
                        
                    },
                    Hoy: {
                        campoBD: 'MQTT.tele/PVControl/Reles/55/SENSOR.ENERGY.Today',
                        value: 0,
                        unit: 'Kwh',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        bold: true,
                        position: { x: -15, y: 90 },
                        width: 100,
                        //showTitle: false,     
                    },
                    Ayer: {
                        campoBD: 'MQTT.tele/PVControl/Reles/55/SENSOR.ENERGY.Yesterday',
                        value: 0,
                        unit: 'Kwh',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        bold: true,
                        position: { x: -15, y: 105 },
                        width: 100,
                        //showTitle: false,     
                    },
    
                }
            },

            ANENJI1: {
                image: 'Anenji.jpg',
                size: { width: 100, height: 150 },
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["ANENJI1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                connectTo: {
                    id: 'BATERIA',
                    from: 'right',
                    to: 'left',
                    control: 'Winv',
                    max: 4000,
                    min: 0,
                    flujoLinea: 'inverso',
                    colorLineaPositiva:'red',
                    colorLineaNegativa:'green',
                },
                
                elements: {
                    WM: { campoBD: 'ANENJI1.WM', value: 0, unit: "",  visualizacion: 'modal'  },
                    Out_prio: { campoBD: 'ANENJI2.Out_prio', value: 0, unit: "",  visualizacion: 'modal'  },
                    
                    Winv: { campoBD: 'ANENJI1.Winv', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'yellow', backgroundColor: '', 
                            bold: true, position: { x: 30, y: 40 }, //width: 70,
                            showTitle: false, },
                    Wh_inv: {sensor: 'Math.floor(d_["TABLA_ANENJI"]["ANENJI1_Wh"])', value: 0, unit: "Wh", size: "16px", titleColor: 'black',  valueColor: 'blue', backgroundColor: '', 
                            bold: true, position: { x: 20, y: -10 }, //width: 70,
                            showTitle: false, },
                    
                    Ibat: { campoBD: 'ANENJI1.Ibat', value: 0, unit: "A", size: "16px", titleColor: 'black',  valueColor: 'blue', 
                    backgroundColor: '',bold: true, position: { x: 82, y: 29 }, width: 70, showTitle: false, 
                    avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 30'},
                        },
                    },
                    
                    Vred: { campoBD: 'ANENJI1.Vred', value: 0, unit: "V",  visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'ANENJI1.Wred', value: 0, unit: "W",  visualizacion: 'modal'  },
                    
                    Vabs: { campoBD: 'ANENJI1.Vabs', value: 0, unit: "V",  visualizacion: 'modal'  },
                    
                    Vflot: { campoBD: 'ANENJI1.Vflot', value: 0, unit: "V",  visualizacion: 'modal'  },
                    
                    
                    // Agregar más elementos según sea necesario
                }
            },
 
            BATERIA: {
                image: 'bateria_transparente75.png',
                size: { width: 60, height: 120 },
                avisos: {
                    100: {image: 'bateria100.png', verAviso: false, condicion:'d_["FV"]["SOC"] >= 95'},
                    83: {image: 'bateria83.png', verAviso: false, condicion:'d_["FV"]["SOC"] < 95 && d_["FV"]["SOC"] >= 83'},
                    66: {image: 'bateria66.png', verAviso: false, condicion:'d_["FV"]["SOC"] < 83 && d_["FV"]["SOC"] >= 66'},
                    50: {image: 'bateria50.png', color: 'yellow', condicion:'d_["FV"]["SOC"] < 66 && d_["FV"]["SOC"] >= 50'},
                    33: {image: 'bateria33.png', color: 'yellow', condicion:'d_["FV"]["SOC"] < 50 && d_["FV"]["SOC"] >= 33'},
                    16: {image: 'bateria16.png', color: 'red', condicion:'d_["FV"]["SOC"] < 33'},
                },
                
                connectTo: null,
                
                elements: {
                    MODO: {
                        campoBD: 'FV.Mod_bat',
                        value: '',
                        unit: '',
                        size: '16x',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 42, y: -3 },
                        width: 80,
                        showTitle: false
                    },
                    SOC: {
                        campoBD: 'FV.SOC',
                        value: 50,
                        unit: '%',
                        size: '20px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        backgroundColor: 'white',
                        bold: true,
                        position: { x: 34, y: 78 },
                        width: 80,
                        showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 80'},
                            Amarillo: {color:'yellow', condicion:'value < 80'},
                            Rojo: {color:'red', condicion:'value < 60'},
                        },
                        
                    },

                    Vbat: {
                        campoBD: 'FV.Vbat',
                        value: 0,
                        unit: 'V',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        backgroundColor: 'pink',
                        bold: true,
                        position: { x: 34, y: 101 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 56 || value <= 58'},
                            Amarillo: {color:'yellow', condicion:'value < 56 && value >= 55'},
                            Rojo: {color:'red', condicion:'value < 55'},
                        },
                    },
                     
                    Ibat: {
                        campoBD: 'FV.Ibat',
                        value: 0,
                        unit: 'A',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        backgroundColor: 'pink',
                        bold: true,
                        position: { x: 34, y: 120 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= -30 && value <= 30'},
                            Rojo: {color:'red', condicion:'value < -60 || value > 60 '},
                            Amarillo: {color:'yellow', condicion:'value < -30 || value > 30'},
                            
                        },
                    },
 
                }
            },
            ANENJI2: {
                image: "Anenji.jpg",
                size: { width: 100, height: 150 },
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["ANENJI2"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                connectTo: {
                    id: "BATERIA",
                    from: "left",
                    to: "right",
                    control: 'Winv',
                    max: 4000,
                    min: 0,
                    flujoLinea: 'inverso',
                    colorLineaPositiva:'red',
                    colorLineaNegativa:'green',
                },
                elements: {
                    WM: { campoBD: 'ANENJI2.WM', value: 0, unit: "",  visualizacion: 'modal'  },
                    Out_prio: { campoBD: 'ANENJI2.Out_prio', value: 0, unit: "",  visualizacion: 'modal'  },
                    
                    Winv: { campoBD: 'ANENJI2.Winv', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'yellow', backgroundColor: '',
                    bold: true, position: { x: 30, y: 40 }, //width: 70,
                    showTitle: false },
   
                    Wh_inv: {sensor: 'Math.floor(d_["TABLA_ANENJI"]["ANENJI2_Wh"])', value: 0, unit: "Wh", size: "16px", titleColor: 'black',  valueColor: 'blue', backgroundColor: '', 
                            bold: true, position: { x: 20, y: -10 }, //width: 70,
                            showTitle: false, },
                    
                    Ibat: { 
                        campoBD: 'ANENJI2.Ibat', value: 0, unit: "A", size: "16px", titleColor: 'black',  valueColor: 'blue',
                        backgroundColor: '',bold: true, position: { x: -48, y: 29 }, width: 70, showTitle: false, 
                    },
                    
                    Vred: { campoBD: 'ANENJI2.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'ANENJI2.Wred', value: 0, unit: "W", visualizacion: 'modal'  },
                    
                    Vabs: { campoBD: 'ANENJI2.Vabs', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Vflot: { campoBD: 'ANENJI2.Vflot', value: 0, unit: "V",  visualizacion: 'modal'  },
                    
                }
            },
           
        },
        fila4: {
            F4_1: {image: '',},
            JK1: {
                image: 'bateria.jpg',
                size: { width: 100, height: 100 },
                avisos: {KO: {color:'red', condicion:'new Date(d_["BMS_JK1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                connectTo: {id: 'BATERIA', from: 'top', to: 'bottom', control: 'Ibat', max: 50, min: 0, flujoLinea:'inverso', colorLineaPositiva:'green',},
                elements: {
                    Banco1: {
                        campoBD: '',
                        value: 'JK1',
                        unit: '',
                        size: '16x',
                        titleColor: 'black',
                        valueColor: 'yellow',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 55, y: 33 },
                        //width: 80,
                        showTitle: false
                    },
                    SOC: {
                        campoBD: 'BMS_JK1.SOC',
                        value: 50,
                        unit: '%',
                        size: '20px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 15, y: 95 },
                        width: 80,
                        //visualizacion: 'siempre',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= 80'},
                            2: {color:'yellow', condicion:'value < 80'},
                            3: {color:'red', condicion:'value < 60'},
                        },
                    },
                    Vbat: {
                        campoBD: 'BMS_JK1.Vbat',
                        value: 0,
                        unit: 'V',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 15, y: 119 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= 56 || value <= 58'},
                            2: {color:'yellow', condicion:'value < 56 && value >= 55'},
                            3: {color:'red', condicion:'value < 55'},
                        },
                    },                   
                    Ibat: {
                        campoBD: 'BMS_JK1.Ibat',
                        value: 0,
                        unit: 'A',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 22, y: -16 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            2: {color:'red', condicion:'value < -50 || value > 50 '},
                            3: {color:'yellow', condicion:'value < -20 || value > 20'},
                            
                        },
                    },

                    Dif: {
                        sensor: '(Math.max(...d_["BMS_JK1"]["Vceldas"]) - Math.min(...d_["BMS_JK1"]["Vceldas"])) * 1000',
                        value: 0, unit: 'mV', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        backgroundColor: 'lightgrey',
                        bold: true,
                        width: 82,
                        position: { x: -65, y: -5 },
                        //showTitle: false,
                    },
                    Vcelda_max_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK1"]["Vceldas"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 10 },
                        showTitle: false,
                    },
                    Vcelda_max: {
                        sensor: 'Math.max(...d_["BMS_JK1"]["Vceldas"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'red',
                        //bold: true,
                        position: { x: -30, y: 10 },
                        showTitle: false,
                    },
                    Vcelda_min_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK1"]["Vceldas"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 25 },
                        showTitle: false,
                    },                    
                    Vcelda_min: {
                        sensor: 'Math.min(...d_["BMS_JK1"]["Vceldas"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 25 },
                        showTitle: false,
                    },

                    Vcelda_dia: {
                        //sensor: '',
                        value: '- DIA -', unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        backgroundColor: 'lightgrey',
                        bold: true,
                        width: 82,
                        position: { x: -65, y: 45 },
                        showTitle: false,
                    },
                    Vcelda_max_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK1"]["Max"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 60 },
                        showTitle: false,
                    },                  
                    Vcelda_max_dia: {
                        sensor: 'Math.max(...d_["BMS_JK1"]["Max"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 60 },
                        showTitle: false,
                    },
                    Vcelda_min_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK1"]["Min"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 75 },
                        showTitle: false,
                    },
                    Vcelda_min_dia: {
                        sensor: 'Math.max(...d_["BMS_JK1"]["Min"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 75 },
                        showTitle: false,
                    },

                    AH_p: {sensor: 'Math.floor(d_["BMS_JK1"]["AH_p"])', unit: 'Ah_p', size: '16px', bold: true, valueColor: 'blue', position: { x: -60, y: 100 }, showTitle: false,},
                    AH_n: {sensor: 'Math.floor(d_["BMS_JK1"]["AH_n"])', unit: 'Ah_n', size: '16px', bold: true, valueColor: 'red', position: { x: -60, y: 115 }, showTitle: false,},
                    I_balance: {sensor: 'Math.floor(d_["BMS_JK1"]["Ibalance"])', unit: 'A', size: '10px', bold: true, 
                        valueColor: 'black', position: { x: 53, y: 60 }, showTitle: false, width: 30,
                        avisos: {
                            Gris: {color:'lightgray', condicion:'value === 0'},
                            Amarillo: {color:'yellow', condicion:'value > 0'},
                            Red: {color:'red', condicion:'value < 0'},
                        },
                    },

                    
                    Carga: { campoBD: 'BMS_JK1.Interruptores.carga',  visualizacion: 'modal'  },
                    Descarga: { campoBD: 'BMS_JK1.Interruptores.descarga', visualizacion: 'modal'  },
                    Balance: { campoBD: 'BMS_JK1.Interruptores.balance', visualizacion: 'modal'  },
                    Nciclos: { campoBD: 'BMS_JK1.Nciclos', visualizacion: 'modal'  },
                    T_bat: { campoBD: 'BMS_JK1.Temperaturas', unit: "ºC",  visualizacion: 'modal'  },
                    
                    
                }
            },
            JK2: {
                image: 'bateria.jpg',
                size: { width: 100, height: 100 },
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["BMS_JK2"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                connectTo: {
                    id: 'BATERIA',
                    from: 'top',
                    to: 'bottom',
                    control: 'Ibat',
                    max: 50,
                    min: 0,
                    flujoLinea:'inverso',
                    colorLineaPositiva:'green',
                },
                elements: {
                    Banco1: {
                        campoBD: '',
                        value: 'JK2',
                        unit: '',
                        size: '16x',
                        titleColor: 'black',
                        valueColor: 'yellow',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 55, y: 33 },
                        //width: 80,
                        showTitle: false
                    },
                    SOC: {
                        campoBD: 'BMS_JK2.SOC',
                        value: 50,
                        unit: '%',
                        size: '20px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 15, y: 95 },
                        width: 80,
                        //visualizacion: 'siempre',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= 80'},
                            2: {color:'yellow', condicion:'value < 80'},
                            3: {color:'red', condicion:'value < 60'},
                        },
                    },
                    Vbat: {
                        campoBD: 'BMS_JK2.Vbat',
                        value: 0,
                        unit: 'V',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 15, y: 120 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= 56 || value <= 58'},
                            2: {color:'yellow', condicion:'value < 56 && value >= 55'},
                            3: {color:'red', condicion:'value < 55'},
                        },
                    },                   
                    Ibat: {
                        campoBD: 'BMS_JK2.Ibat',
                        value: 0,
                        unit: 'A',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 22, y: -16 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            2: {color:'red', condicion:'value < -50 || value > 50 '},
                            3: {color:'yellow', condicion:'value < -20 || value > 20'},
                            
                        },
                    },
 
                    Dif: {
                        sensor: '(Math.max(...d_["BMS_JK2"]["Vceldas"]) - Math.min(...d_["BMS_JK2"]["Vceldas"])) * 1000',
                        value: 0, unit: 'mV', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        backgroundColor: 'lightgrey',
                        bold: true,
                        width: 82,
                        position: { x: -65, y: -5 },
                        //showTitle: false,
                    },
                    Vcelda_max_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK2"]["Vceldas"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 10 },
                        showTitle: false,
                    },
                    Vcelda_max: {
                        sensor: 'Math.max(...d_["BMS_JK2"]["Vceldas"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'red',
                        //bold: true,
                        position: { x: -30, y: 10 },
                        showTitle: false,
                    },
                    Vcelda_min_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK2"]["Vceldas"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 25 },
                        showTitle: false,
                    },                    
                    Vcelda_min: {
                        sensor: 'Math.min(...d_["BMS_JK2"]["Vceldas"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 25 },
                        showTitle: false,
                    },

                    Vcelda_dia: {
                        //sensor: '',
                        value: '- DIA -', unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        backgroundColor: 'lightgrey',
                        bold: true,
                        width: 82,
                        position: { x: -65, y: 45 },
                        showTitle: false,
                    },
                    Vcelda_max_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK2"]["Max"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 60 },
                        showTitle: false,
                    },                  
                    Vcelda_max_dia: {
                        sensor: 'Math.max(...d_["BMS_JK2"]["Max"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 60 },
                        showTitle: false,
                    },
                    Vcelda_min_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK2"]["Min"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 75 },
                        showTitle: false,
                    },
                    Vcelda_min_dia: {
                        sensor: 'Math.max(...d_["BMS_JK2"]["Min"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 75 },
                        showTitle: false,
                    },
 
                    AH_p: {sensor: 'Math.floor(d_["BMS_JK2"]["AH_p"])', unit: 'Ah_p', size: '16px', bold: true, valueColor: 'blue', position: { x: -60, y: 100 }, showTitle: false,},
                    AH_n: {sensor: 'Math.floor(d_["BMS_JK2"]["AH_n"])', unit: 'Ah_n', size: '16px', bold: true, valueColor: 'red', position: { x: -60, y: 115 }, showTitle: false,},
                    
                    I_balance: {sensor: 'Math.floor(d_["BMS_JK2"]["Ibalance"])', unit: 'A', size: '10px', bold: true, 
                        valueColor: 'black', position: { x: 53, y: 60 }, showTitle: false, width: 30,
                        avisos: {
                            Gris: {color:'lightgrey', condicion:'value === 0'},
                            Amarillo: {color:'yellow', condicion:'value > 0'},
                            Red: {color:'red', condicion:'value < 0'},
                        },
                    },
                    Carga: { campoBD: 'BMS_JK2.Interruptores.carga', value: 0, unit: "",  visualizacion: 'modal'  },
                    Descarga: { campoBD: 'BMS_JK2.Interruptores.descarga', value: 0, unit: "",  visualizacion: 'modal'  },
                    Balance: { campoBD: 'BMS_JK2.Interruptores.balance', value: 0, unit: "",  visualizacion: 'modal'  },
                    Nciclos: { campoBD: 'BMS_JK2.Nciclos', value: 0, unit: "",  visualizacion: 'modal'  },
                    T_bat: { campoBD: 'BMS_JK2.Temperaturas', value: 0, unit: "ºC",  visualizacion: 'modal'  },
                    
                    
                }
            },
            JK3: {
                image: 'bateria.jpg',
                size: { width: 100, height: 100 },
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["BMS_JK3"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                connectTo: {
                    id: 'BATERIA',
                    from: 'top',
                    to: 'bottom',
                    control: 'Ibat',
                    max: 50,
                    min: 0,
                    flujoLinea:'inverso',
                    colorLineaPositiva:'green',
                },
                elements: {
                    Banco1: {
                        campoBD: '',
                        value: 'JK3',
                        unit: '',
                        size: '16x',
                        titleColor: 'black',
                        valueColor: 'yellow',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 55, y: 33 },
                        //width: 80,
                        showTitle: false
                    },
                    SOC: {
                        campoBD: 'BMS_JK3.SOC',
                        value: 50,
                        unit: '%',
                        size: '20px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 15, y: 95 },
                        width: 80,
                        //visualizacion: 'siempre',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= 80'},
                            2: {color:'yellow', condicion:'value < 80'},
                            3: {color:'red', condicion:'value < 60'},
                        },
                    },
                    Vbat: {
                        campoBD: 'BMS_JK3.Vbat',
                        value: 0,
                        unit: 'V',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 15, y: 120 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= 56 || value <= 58'},
                            2: {color:'yellow', condicion:'value < 56 && value >= 55'},
                            3: {color:'red', condicion:'value < 55'},
                        },
                    },                   
                    Ibat: {
                        campoBD: 'BMS_JK3.Ibat',
                        value: 0,
                        unit: 'A',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 22, y: -16 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            2: {color:'red', condicion:'value < -50 || value > 50 '},
                            3: {color:'yellow', condicion:'value < -20 || value > 20'},
                            
                        },
                    },
 
                    Dif: {
                        sensor: '(Math.max(...d_["BMS_JK3"]["Vceldas"]) - Math.min(...d_["BMS_JK3"]["Vceldas"])) * 1000',
                        value: 0, unit: 'mV', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        backgroundColor: 'lightgrey',
                        bold: true,
                        width: 82,
                        position: { x: -65, y: -5 },
                        //showTitle: false,
                    },
                    Vcelda_max_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK3"]["Vceldas"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 10 },
                        showTitle: false,
                    },
                    Vcelda_max: {
                        sensor: 'Math.max(...d_["BMS_JK3"]["Vceldas"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'red',
                        //bold: true,
                        position: { x: -30, y: 10 },
                        showTitle: false,
                    },
                    Vcelda_min_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK3"]["Vceldas"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 25 },
                        showTitle: false,
                    },                    
                    Vcelda_min: {
                        sensor: 'Math.min(...d_["BMS_JK3"]["Vceldas"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 25 },
                        showTitle: false,
                    },

                    Vcelda_dia: {
                        //sensor: '',
                        value: '- DIA -', unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        backgroundColor: 'lightgrey',
                        bold: true,
                        width: 82,
                        position: { x: -65, y: 45 },
                        showTitle: false,
                    },
                    Vcelda_max_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK3"]["Max"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 60 },
                        showTitle: false,
                    },                  
                    Vcelda_max_dia: {
                        sensor: 'Math.max(...d_["BMS_JK3"]["Max"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 60 },
                        showTitle: false,
                    },
                    Vcelda_min_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK3"]["Min"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 75 },
                        showTitle: false,
                    },
                    Vcelda_min_dia: {
                        sensor: 'Math.max(...d_["BMS_JK3"]["Min"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 75 },
                        showTitle: false,
                    },
 
                    AH_p: {sensor: 'Math.floor(d_["BMS_JK3"]["AH_p"])', unit: 'Ah_p', size: '16px', bold: true, valueColor: 'blue', position: { x: -60, y: 100 }, showTitle: false,},
                    AH_n: {sensor: 'Math.floor(d_["BMS_JK3"]["AH_n"])', unit: 'Ah_n', size: '16px', bold: true, valueColor: 'red', position: { x: -60, y: 115 }, showTitle: false,},
                    
                    I_balance: {sensor: 'Math.floor(d_["BMS_JK3"]["Ibalance"])', unit: 'A', size: '10px', bold: true, 
                        valueColor: 'black', position: { x: 53, y: 60 }, showTitle: false, width: 30,
                        avisos: {
                            Gris: {color:'lightgrey', condicion:'value === 0'},
                            Amarillo: {color:'yellow', condicion:'value > 0'},
                            Red: {color:'red', condicion:'value < 0'},
                        },
                    },
                    Carga: { campoBD: 'BMS_JK3.Interruptores.carga', value: 0, unit: "",  visualizacion: 'modal'  },
                    Descarga: { campoBD: 'BMS_JK3.Interruptores.descarga', value: 0, unit: "",  visualizacion: 'modal'  },
                    Balance: { campoBD: 'BMS_JK3.Interruptores.balance', value: 0, unit: "",  visualizacion: 'modal'  },
                    Nciclos: { campoBD: 'BMS_JK3.Nciclos', value: 0, unit: "",  visualizacion: 'modal'  },
                    T_bat: { campoBD: 'BMS_JK3.Temperaturas', value: 0, unit: "ºC",  visualizacion: 'modal'  },
                    
                    
                }
            },
            JK4: {
                image: 'bateria.jpg',
                size: { width: 100, height: 100 },
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["BMS_JK4"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                connectTo: {
                    id: 'BATERIA',
                    from: 'top',
                    to: 'bottom',
                    control: 'Ibat',
                    max: 50,
                    min: 0,
                    flujoLinea:'inverso',
                    colorLineaPositiva:'green',
                },
                elements: {
                    Banco1: {
                        campoBD: '',
                        value: 'JK4',
                        unit: '',
                        size: '16x',
                        titleColor: 'black',
                        valueColor: 'yellow',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 55, y: 33 },
                        //width: 80,
                        showTitle: false
                    },
                    SOC: {
                        campoBD: 'BMS_JK4.SOC',
                        value: 50,
                        unit: '%',
                        size: '20px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 15, y: 95 },
                        width: 80,
                        //visualizacion: 'siempre',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= 80'},
                            2: {color:'yellow', condicion:'value < 80'},
                            3: {color:'red', condicion:'value < 60'},
                        },
                    },
                    Vbat: {
                        campoBD: 'BMS_JK4.Vbat',
                        value: 0,
                        unit: 'V',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 15, y: 120 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= 56 || value <= 58'},
                            2: {color:'yellow', condicion:'value < 56 && value >= 55'},
                            3: {color:'red', condicion:'value < 55'},
                        },
                    },                   
                    Ibat: {
                        campoBD: 'BMS_JK4.Ibat',
                        value: 0,
                        unit: 'A',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 22, y: -16 },
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            1: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            2: {color:'red', condicion:'value < -50 || value > 50 '},
                            3: {color:'yellow', condicion:'value < -20 || value > 20'},
                            
                        },
                    },

                    Dif: {
                        sensor: '(Math.max(...d_["BMS_JK4"]["Vceldas"]) - Math.min(...d_["BMS_JK4"]["Vceldas"])) * 1000',
                        value: 0, unit: 'mV', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        backgroundColor: 'lightgrey',
                        bold: true,
                        width: 82,
                        position: { x: -65, y: -5 },
                        //showTitle: false,
                    },
                    Vcelda_max_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK4"]["Vceldas"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 10 },
                        showTitle: false,
                    },
                    Vcelda_max: {
                        sensor: 'Math.max(...d_["BMS_JK4"]["Vceldas"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'red',
                        //bold: true,
                        position: { x: -30, y: 10 },
                        showTitle: false,
                    },
                    Vcelda_min_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK4"]["Vceldas"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 25 },
                        showTitle: false,
                    },                    
                    Vcelda_min: {
                        sensor: 'Math.min(...d_["BMS_JK4"]["Vceldas"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 25 },
                        showTitle: false,
                    },

                    Vcelda_dia: {
                        //sensor: '',
                        value: '- DIA -', unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        backgroundColor: 'lightgrey',
                        bold: true,
                        width: 82,
                        position: { x: -65, y: 45 },
                        showTitle: false,
                    },
                    Vcelda_max_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK4"]["Max"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 60 },
                        showTitle: false,
                    },                  
                    Vcelda_max_dia: {
                        sensor: 'Math.max(...d_["BMS_JK4"]["Max"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 60 },
                        showTitle: false,
                    },
                    Vcelda_min_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK4"]["Min"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', 
                        size: '14px', titleColor: 'black', valueColor: 'black',
                        bold: true,
                        position: { x: -60, y: 75 },
                        showTitle: false,
                    },
                    Vcelda_min_dia: {
                        sensor: 'Math.max(...d_["BMS_JK4"]["Min"])',
                        value: 0, unit: 'V', 
                        size: '14px', titleColor: 'black', valueColor: 'blue',
                        //bold: true,
                        position: { x: -30, y: 75 },
                        showTitle: false,
                    },

                    AH_p: {sensor: 'Math.floor(d_["BMS_JK4"]["AH_p"])', unit: 'Ah_p', size: '16px', bold: true, valueColor: 'blue', position: { x: -60, y: 100 }, showTitle: false,},
                    AH_n: {sensor: 'Math.floor(d_["BMS_JK4"]["AH_n"])', unit: 'Ah_n', size: '16px', bold: true, valueColor: 'red', position: { x: -60, y: 115 }, showTitle: false,},
                    I_balance: {sensor: 'Math.floor(d_["BMS_JK4"]["Ibalance"])', unit: 'A', size: '10px', bold: true, 
                        valueColor: 'black', position: { x: 53, y: 60 }, showTitle: false, width: 30,
                        avisos: {
                            Gris: {color:'lightgray', condicion:'value === 0'},
                            Amarillo: {color:'yellow', condicion:'value > 0'},
                            Red: {color:'red', condicion:'value < 0'},
                        },
                    },


                    Carga: { campoBD: 'BMS_JK4.Interruptores.carga', value: 0, unit: "",  visualizacion: 'modal'  },
                    Descarga: { campoBD: 'BMS_JK4.Interruptores.descarga', value: 0, unit: "",  visualizacion: 'modal'  },
                    Balance: { campoBD: 'BMS_JK4.Interruptores.balance', value: 0, unit: "",  visualizacion: 'modal'  },
                    Nciclos: { campoBD: 'BMS_JK4.Nciclos', value: 0, unit: "",  visualizacion: 'modal'  },
                    T_bat: { campoBD: 'BMS_JK4.Temperaturas', value: 0, unit: "ºC",  visualizacion: 'modal'  },
                    
                    
                }
            },
        },
    }
};

