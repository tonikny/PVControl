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
            H_Ciclado: 'grafica_elige.php',
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
                        1: {color:'lightgreen', condicion:'value > 95'},
                    }
                },
                SOC_MAX: {
                    campoBD: 'FV.SOC_max',
                    value: 0,
                    unit: '%',
                    size: '16px',
                    titleColor: 'black',
                    valueColor: 'black',
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
                    backgroundColor: 'pink',
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
                connectTo: { id: 'DEYE', from: 'bottom',  to: 'top', control: 'Wplaca', max: 3000, min: 0,},
                
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
                        //sensor: 'd_["DEYE"]["PV1InputPower"]',
                        campoBD: 'DEYE.PV1InputPower',
                        value: 0,
                        unit: 'W',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -50, y: 80 },
                        width: 100,
                        showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 5'},
                        },
                        
                    },
                    Vplaca: {
                        campoBD: 'DEYE.Vplaca',
                        value: 0,
                        unit: 'V',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -40, y: 45 },
                        //width: 100,
                        //visualizacion: 'modal',
                        showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value < 5'},
                        },
                    },
                    
    
                }
            },
            Placa2: {
                image: 'placa1.avif',
                size: { width: 100, height: 100 },
                connectTo: { id: 'DEYE', from: 'bottom',  to: 'top', control: 'Wplaca', max: 3000, min: 0,},
                
                elements: {
                    Solar2: {
                        campoBD: '',
                        value: 'S2',
                        unit: '',
                        size: '20px',
                        titleColor: 'yellow',
                        valueColor: 'yellow',
                        bold: true,
                        position: { x: 36, y: 47 },
                        showTitle: false
                    },
                    Wplaca: {
                        //sensor: 'd_["DEYE"]["PV2InputPower"]',
                        campoBD: 'DEYE.PV2InputPower',
                        value: 0,
                        unit: 'W',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -50, y: 80 },
                        width: 100,
                        showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 5'},
                        },
                        
                    },
                    Vplaca: {
                        campoBD: 'DEYE.Vplaca2',
                        value: 0,
                        unit: 'V',
                        size: '16px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -40, y: 45 },
                        //width: 100,
                        //visualizacion: 'modal',
                        showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value < 5'},
                        },
                    },
                }
            },
            F1_1:{image:''},
            F1_2:{image:''},
  
        },
        fila2: {
            DEYE: {
                image: 'deye.jpg',
                size: { width: 100, height: 150 },
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["DEYE"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                connectTo: {
                    id: 'BATERIA',
                    from: 'botton',
                    to: 'top',
                    control: 'Ibat',
                    max: 60,
                    min: 0
                },
                elements: {
                    Estado: {
                        campoBD: 'DEYE.EstadoInv',
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
                    PV_dia: {
                        campoBD: 'DEYE.DayPVPower',
                        value: 0,
                        unit: 'W',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -40, y: 30 },
                        //width: 100,
                        showTitle: false
                    },
                    Temp_Rad: {
                        campoBD: 'DEYE.RadiatorTempDC',
                        value: 0,
                        unit: 'ºC',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -45, y: 78 },
                        //width: 100,
                        showTitle: false
                    },
                    Temp_IGTB: {
                        campoBD: 'DEYE.IGBTTemp',
                        value: 0,
                        unit: 'ºC',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -45, y: 95 },
                        //width: 100,
                        showTitle: false
                        
                    },
                    Vbat: { campoBD: 'DEYE.Vbat', value: 0, unit: "V",  visualizacion: 'modal'  },
                    SOC: { campoBD: 'DEYE.SOC', value: 0, unit: "%",  visualizacion: 'modal'  },
                    Ibat: { campoBD: 'FV.Ibat', value: 0, unit: "A",  visualizacion: 'modal'  },

                                        // Agregar más elementos según sea necesario
                }
            },
            Casa1: {
                image: "casa1.png",
                size: { width: 150, height: 100 },
                connectTo: {
                    id: "DEYE",
                    from: "left",
                    to: "right",
                    control: 'Wconsumo',
                    max: 4000,
                    min: 0,
                    flujoLinea: 'inverso', // por defecto vacio o 'normal'
                    colorLineaPositiva: 'red'
                },
                elements: {
                    
                    Wconsumo: { campoBD: 'FV.Wconsumo', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -34, y: 20 }, //width: 70,
                    showTitle: false },
                    
                    Wh_consumo: { campoBD: 'FV.Wh_consumo', value: 0, unit: "Wh", size: "16px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: 42, y: 100 }, width: 70,
                    showTitle: false  },
                    
                    
                    Vred: { campoBD: 'FV.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'FV.Wred', value: 0, unit: "W", visualizacion: 'modal'  },
                    
                }
            },
        
        },
        fila3: {
 
            BATERIA: {
                image: 'bateria.jpg',
                size: { width: 100, height: 100 },
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["FV"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                connectTo: null,
                
                elements: {
                    MODO: {
                        campoBD: 'FV.Mod_bat',
                        value: '',
                        unit: '',
                        size: '16x',
                        titleColor: 'black',
                        valueColor: 'yellow',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 15, y: 50 },
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
                        position: { x: -71, y: 41 },
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
                        position: { x: 100, y: 41 },
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
                        position: { x: 54, y: -20},
                        width: 80,
                        //visualizacion: '',
                        showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            Rojo: {color:'red', condicion:'value < -50 || value > 50 '},
                            Amarillo: {color:'yellow', condicion:'value < -20 || value > 20'},
                            
                        },
                    },
 
                }
            },
           
        },
        fila4: {
            JK1: {
                image: 'bateria.jpg',
                size: { width: 100, height: 100 },
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["BMS_JK1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                connectTo: {id: 'BATERIA', from: 'top', to: 'bottom', control: 'Ibat', max: 50, min: 0, flujoLinea:'inverso' },
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
                        position: { x: 55, y: 45 },
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
                    
                    AH_p: { campoBD: 'BMS_JK1.AH_p', value: 0, unit: "Ah",  visualizacion: 'modal'  },
                    AH_n: { campoBD: 'BMS_JK1.AH_n', value: 0, unit: "Ah",  visualizacion: 'modal'  },
                    Carga: { campoBD: 'BMS_JK1.Interruptores.carga', value: 0, unit: "",  visualizacion: 'modal'  },
                    Descarga: { campoBD: 'BMS_JK1.Interruptores.descarga', value: 0, unit: "",  visualizacion: 'modal'  },
                    Balance: { campoBD: 'BMS_JK1.Interruptores.balance', value: 0, unit: "",  visualizacion: 'modal'  },
                    Nciclos: { campoBD: 'BMS_JK1.Nciclos', value: 0, unit: "",  visualizacion: 'modal'  },
                    T_bat: { campoBD: 'BMS_JK1.Temperaturas', value: 0, unit: "ºC",  visualizacion: 'modal'  },
                    
                    
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
                    flujoLinea:'inverso'
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
                        position: { x: 55, y: 45 },
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
 
 
                    AH_p: { campoBD: 'BMS_JK2.AH_p', value: 0, unit: "Ah",  visualizacion: 'modal'  },
                    AH_n: { campoBD: 'BMS_JK2.AH_n', value: 0, unit: "Ah",  visualizacion: 'modal'  },
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
                    flujoLinea:'inverso'
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
                        position: { x: 55, y: 45 },
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
 
 
                    AH_p: { campoBD: 'BMS_JK3.AH_p', value: 0, unit: "Ah",  visualizacion: 'modal'  },
                    AH_n: { campoBD: 'BMS_JK3.AH_n', value: 0, unit: "Ah",  visualizacion: 'modal'  },
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
                    flujoLinea:'inverso'
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
                        position: { x: 55, y: 45 },
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

 
                    AH_p: { campoBD: 'BMS_JK4.AH_p', value: 0, unit: "Ah",  visualizacion: 'modal'  },
                    AH_n: { campoBD: 'BMS_JK4.AH_n', value: 0, unit: "Ah",  visualizacion: 'modal'  },
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

