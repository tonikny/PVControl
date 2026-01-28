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

                // Agregar elementos según sea necesario
                
                Separador_2: {backgroundColor: 'lightgray', value: '&nbsp;', size: '10px', showTitle: false,},
                 
                // Agregar elementos según sea necesario
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
                connectTo: { id: 'ANENJI11', from: 'bottom',  to: 'top', control: 'Wplaca', max: 3000, min: 0,},
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
                        campoBD: 'ANENJI11.Wplaca1',
                        //sensor: 'd_["FV"]["Wplaca"]',
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
                            1: {color:'yellow', condicion:'value > 5000'},
                        },
                        
                    },
                    Vplaca: {
                        campoBD: 'ANENJI11.Vplaca1',
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
                        
                    },
                    Kwh_placa: {
                        //campoBD: 'MPPT1.Wh_placa',
                        sensor: '(d_["TABLA_MPPT"]["Wh_MPPT1"]/1000).toFixed(1)',
                        unit: 'Kwh -> ', size: '18px', valueColor: '#2a5d6a', bold: true, position: { x: -55, y: -5 }, showTitle: false
                    },
                    Wh_Wp: {sensor: '(d_["TABLA_MPPT"]["Wh_MPPT1"]/5500).toFixed(1)', unit: 'Wh/Wp', size: '14px', valueColor: 'blue', bold: true,
                        position: { x: 45, y: -3 },showTitle: false, width: 80
                    }, 

                }
            },
            Placa2: {
                image: 'placa1.avif',
                size: { width: 100, height: 100 },
                connectTo: { id: 'ANENJI11', from: 'bottom',  to: 'top', control: 'Wplaca', max: 3000, min: 0,},
                elements: {
                    Solar1: {
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
                        campoBD: 'ANENJI11.Wplaca2',
                        //sensor: 'd_["FV"]["Wplaca"]',
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
                            1: {color:'yellow', condicion:'value > 5000'},
                        },
                        
                    },
                    Vplaca: {
                        campoBD: 'ANENJI11.Vplaca2',
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
                        
                    },

                    Kwh_placa: {
                        //campoBD: 'MPPT1.Wh_placa',
                        sensor: '(d_["TABLA_MPPT"]["Wh_MPPT2"]/1000).toFixed(1)',
                        unit: 'Kwh -> ', size: '18px', valueColor: '#2a5d6a', bold: true, position: { x: -55, y: -5 }, showTitle: false
                    },
                    Wh_Wp: {sensor: '(d_["TABLA_MPPT"]["Wh_MPPT2"]/3300).toFixed(1)', unit: 'Wh/Wp', size: '14px', valueColor: 'blue', bold: true,
                        position: { x: 45, y: -3 },showTitle: false, width: 80
                    }, 

                }
            },

        },  
        fila2: {
            Red1: {
                image: "red.jpg",
                size: { width: 110, height: 150 },
                connectTo: {
                    id: "ANENJI11",
                    from: "right",
                    to: "left",
                    control: 'Wred',
                    max: 4000,
                    min: 0,
                    flujoLinea: 'inverso' // por defecto vacio o 'normal' = color negro positivo y rojo negativo
                },
                elements: {
                    
					
                    Wred: { campoBD: 'FV.Wred', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: 100, y: 50 }, width: 70,
                    showTitle: false },
                
					R511: { campoBD: 'RELES.511.estado', value: -1, unit: "", size: "16px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -150, y: -50 }, width: 70,
                    showTitle: true },
                

				
				    ANENJI11_tiempo: { campoBD: 'ANENJI11.tiempo', size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: 'lightgray',bold: true, position: { x: -150, y: -30 }, width: 150,
                    showTitle: false },
                    
					Wplaca: { campoBD: 'ANENJI11.Wplaca', value: 0, unit: "W", size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -150, y: -10 }, width: 150,
                    showTitle: true },
                    
					
					W_red_L1: { campoBD: 'ANENJI11.W_red_L1', value: 0, unit: "W", size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -150, y: 10 }, width: 150,
                    showTitle: true },

                    Winv: { campoBD: 'ANENJI11.Winv', value: 0, unit: "W", size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -150, y: 30 }, width: 150,
                    showTitle: true },

                    W_salida_L1: { campoBD: 'ANENJI11.W_salida_L1', value: 0, unit: "W", size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -150, y: 50 }, width: 150,
                    showTitle: true },


                    Wout: { campoBD: 'ANENJI11.Wout', value: 0, unit: "W", size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -150, y: 70 }, width: 150,
                    showTitle: true },


				    SDM_tiempo: { campoBD: 'SDM230M.tiempo', size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: 'lightgray',bold: true, position: { x: -150, y: 120 }, width: 150,
                    showTitle: false },


                    SDM_Wac: { campoBD: 'SDM230M.Wac', value: 0, unit: "W", size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -150, y: 140 }, width: 150,
                    showTitle: true },

                    SDM_Wred: { campoBD: 'SDM230M.Wred', value: 0, unit: "W", size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -150, y: 160 }, width: 150,
                    showTitle: true },
                    
                    
				
                    Whp_red: { campoBD: 'FV.Whp_red', value: 0, unit: "Wh Inyeccion", size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: 0, y: 144 }, width: 150,
                    showTitle: false  },
                    
					Whn_red: { campoBD: 'FV.Whn_red', value: 0, unit: "Wh Consumo", size: "14px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: 0, y: 164 }, width: 150,
                    showTitle: false  },
                    
                    
                    Vred: { campoBD: 'FV.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    
                }
            },

            ANENJI11: {
                image: "Anenji.jpg",
                size: { width: 100, height: 150 },
                connectTo: {
                    id: "BATERIA",
                    from: "button",
                    to: "top",
                    control: 'Wbat',
                    max: 4000,
                    min: 0,
                    //flujoColor: 'inverso' // por defecto vacio o 'normal' = color negro positivo y rojo negativo
                },
                elements: {

					Placas: {
                        sensor : '(d_["FV"]["Wh_placa"] / 1000).toFixed(1)',
                        value: 99, unit: 'Kwh', size: '18px', titleColor: 'black', valueColor: 'blue', backgroundColor: 'lightgrey',
                        bold: true, position: { x: -20, y: -30 }, width: 120, showTitle: false
                    },
                    Wplaca: {
                        campoBD: 'FV.Wplaca',
                        unit: 'W', size: '16x', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true, position: { x: 8, y: -8 }, width: 80, showTitle: false
                    },

                    
                    Wbat: { campoBD: 'FV.Wbat', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'blue', 
                    backgroundColor: '',bold: true, position: { x: -10, y: 146 }, width: 70,
                    showTitle: false  },
                    
                    Vred: { campoBD: 'FV.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'FV.Wred', value: 0, unit: "W", visualizacion: 'modal'  },
					
					Out_prio: { campoBD: 'ANENJI11.Out_prio', size: "14px", valueColor: 'black', 
                    backgroundColor: 'lightgrey',bold: true, position: { x: 30, y: 50 }, width: 50,
                    showTitle: false  },

                    Temp_dc: {
                        campoBD: 'ANENJI11.Temp_dc', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 45, y: 82 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 40'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 50'},
                        },
                    },
                    Temp_inv: {
                        campoBD: 'ANENJI11.Temp_inv', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 45, y: 95 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 40'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 50'},
                        },
                    },

                    Temp_PV: {
                        campoBD: 'ANENJI11.Temp_PV', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 45, y: 108 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 40'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 50'},
                        },
                    },

                    
                }
            },
            Casa1: {
                image: "casa.jpg",
                size: { width: 150, height: 100 },
                blockMargin: '45px 45px',
                connectTo: {
                    id: "ANENJI11",
                    from: "left",
                    to: "right",
                    control: 'Wconsumo',
                    max: 4000,
                    min: 0,
                    flujoLinea: 'inverso', // por defecto vacio o 'normal'
                    colorLineaPositiva: "green",
                    colorLineaNegativa: "pink",
                    
                },
                elements: {
                    
                    Wconsumo: { campoBD: 'FV.Wconsumo', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: -34, y: 20 }, //width: 70,
                    showTitle: false },
                    
                    Wh_consumo: { campoBD: 'FV.Wh_consumo', value: 0, unit: "Wh", size: "16px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: 42, y: 100 }, width: 100,
                    showTitle: false  },
                    
                    
                    Vred: { campoBD: 'FV.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'FV.Wred', value: 0, unit: "W", visualizacion: 'modal'  },
                    
                }
            },
            
        },
        fila3: {
            BATERIA: {
                image: 'bateria_transparente75.png',
                size: { width: 65, height: 120 },
                blockMargin: '35px 75px',

                avisos: {
                    100: {image: 'bateria100.png', verAviso: false, condicion:'d_["FV"]["SOC"] >= 95'},
                    83: {image: 'bateria83.png', verAviso: false, condicion:'d_["FV"]["SOC"] < 95 && d_["FV"]["SOC"] >= 83'},
                    66: {image: 'bateria66.png', verAviso: false, condicion:'d_["FV"]["SOC"] < 83 && d_["FV"]["SOC"] >= 66'},
                    50: {image: 'bateria50.png', verAviso: false, color: 'yellow', condicion:'d_["FV"]["SOC"] < 66 && d_["FV"]["SOC"] >= 50'},
                    33: {image: 'bateria33.png', color: 'yellow', condicion:'d_["FV"]["SOC"] < 50 && d_["FV"]["SOC"] >= 33'},
                    16: {image: 'bateria16.png', color: 'red', condicion:'d_["FV"]["SOC"] < 33'},
                },
                
                connectTo: null,
                
                elements: {
                    MODO: {
                        campoBD: 'FV.Mod_bat',
                        size: '10x', valueColor: 'blue', backgroundColor: 'lightgray', bold: true, position: { x: 16, y: 50 }, width: 35, showTitle: false
                    },
					

                    SOC: {
                        campoBD: 'FV.SOC',
                        unit: '%', size: '20px', valueColor: 'blue', backgroundColor: 'lightgreen',bold: true,
                        position: { x: -5, y: 110 }, width: 80, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value < 80'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < 60'},
                        },
                        
                    },
                    SOC_max: {
                        campoBD: 'FV.SOC_max', unit: '%', size: '12px', valueColor: 'blue', backgroundColor: 'lightgreen', bold: true,
                        position: { x: 80, y: 113 }, width: 50, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value < 90 && value >= 80 '},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value < 80'},
                        },
                        
                    },
                    SOC_min: {
                        campoBD: 'FV.SOC_min', unit: '%', size: '12px', valueColor: 'blue', backgroundColor: 'lightgreen',  bold: true,
                        position: { x: -60, y: 113}, width: 50, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value < 80 && value >= 60 '},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value < 60'},
                        },
                    },
                    Vbat: {
                        campoBD: 'FV.Vbat',
                        unit: 'V', size: '16px', valueColor: 'blue', backgroundColor: 'lightgreen', bold: true,
                        position: { x: -5, y: 133 },width: 80, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'(value < 3.3*16 && value >= 3.25*16) || (value > 3.4*16 && value <= 3.42*16)'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value < 3.25*16 || value > 3.42*16'},
                        },
                    },
                    Vbat_max: {
                        campoBD: 'FV.Vbat_max',
                        unit: 'V', size: '12px', valueColor: 'blue',backgroundColor: 'lightgreen', bold: true, position: { x: 80, y: 136 }, width: 50, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 3.42*16 && value <= 3.45*16'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 3.45*16'},
                        },
                    },
                    Vbat_min: {
                        campoBD: 'FV.Vbat_min',
                        unit: 'V', size: '12px', valueColor: 'blue', backgroundColor: 'lightgreen', bold: true,
                        position: { x: -60, y: 136 }, width: 50, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value < 3.25*16 && value >= 3.21*16'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value < 3.21*16'},
                        },
                    },

                    Ibat: {
                        campoBD: 'FV.Ibat',
                        unit: 'A', size: '16px', valueColor: 'blue', backgroundColor: 'lightgreen', bold: true,
                        position: { x: -5, y: 155 }, width: 80, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'(value < -30 && value >= -60) || (value > 30 && value <= 60)'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value < -60 || value > 60'},
                        },
                    },
                    Whp_bat: {
                        //campoBD: 'FV.Whp_bat',
                        sensor: '(d_["FV"]["Whp_bat"]/1000).toFixed(1)',
                        value: 0,
                        unit: 'Kwh',
                        size: '14px',
                        valueColor: 'blue',
                        bold: true,
                        position: { x: 48, y: 12 },
                        width: 100,
                        showTitle: false,
                    },
                    Whn_bat: {
                        //campoBD: 'FV.Whn_bat',
                        sensor: '(-d_["FV"]["Whn_bat"]/1000).toFixed(1)',
                        unit: 'Kwh',
                        size: '14px',
                        valueColor: '#00BFFF',
                        bold: true,
                        position: { x: 46, y: 30 },
                        width: 100,
                        showTitle: false,
                    },
                    Temp_bat: {
                        campoBD: 'FV.Temp',
                        value: 0,
                        unit: 'ºC',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -65, y: 70 },
                        width: 80,
                        showTitle: false,
                        avisos: {
                            calor: {color:'red', valueColor: 'yellow',size:'20px', condicion:'value >= 34'},
                            calorcito: {color:'orange', size:'16px',condicion:'value < 34 && value >=30'},
                            fresco: {color:'cyan', size:'16px',condicion:'value < 10'},
                        },
                    },
 
                }
            },

            F3_1: {image: ''},

            JK1: {
                image: 'bateria.jpg',
                size: { width: 100, height: 100 },
                blockMargin: '44px 45px',

                avisos: {KO: {color:'red', condicion:'new Date(d_["BMS_JK1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                connectTo: {id: 'BATERIA', from: 'left', to: 'right', control: 'Ibat', max: 50, min: 0, flujoLinea:'inverso', colorLineaPositiva:'green',},
                elements: {
                    Banco: {
                        campoBD: '', value: 'JK1',
                        size: '16x', valueColor: '#B03A2E', backgroundColor: 'lightgray', bold: true, position: { x: 30, y: 13 }, width: 50, showTitle: false
                    },
                    Nciclos: {
                        campoBD: 'BMS_JK1.Nciclos',
                        unit: ' ciclos', size: '10px', valueColor: 'black', backgroundColor: 'lightgray', bold: true, position: { x: 30, y: 33 }, width: 50, showTitle: false
                    },
                    SOC: {
                        campoBD: 'BMS_JK1.SOC',
                        unit: '%', size: '20px', valueColor: 'blue', bold: true, position: { x: 15, y: 95 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 80'},
                            Amarillo: {color:'yellow', condicion:'value < 80'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < 60'},
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
                            Verde: {color:'lightgreen', condicion:'value >= 52.7 || value <= 54.6'},
                            Amarillo: {color:'yellow', condicion:'value < 52.7 && value >= 51.7'},
                            Rojo: {color:'red', condicion:'value < 51.7'},
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
                            Verde: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            Rojo: {color:'red', condicion:'value < -50 || value > 50 '},
                            Amarillo: {color:'yellow', condicion:'value < -20 || value > 20'},
                            
                        },
                    },
                    Dif: {
                        sensor: '(Math.max(...d_["BMS_JK1"]["Vceldas"]) - Math.min(...d_["BMS_JK1"]["Vceldas"])) * 1000',
                        unit: 'mV', size: '14px', titleColor: 'black', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true,
                        width: 82, position: { x: -65, y: -5 }, //showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 50'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 200'},
                        },
                    },
                    Vcelda_max_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK1"]["Vceldas"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 10 }, showTitle: false,
                    },
                    Vcelda_max: {
                        sensor: 'Math.max(...d_["BMS_JK1"]["Vceldas"])',
                        unit: 'V', size: '14px', valueColor: 'red', position: { x: -30, y: 10 }, showTitle: false,
                    },
                    Vcelda_min_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK1"]["Vceldas"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 25 }, showTitle: false,
                    },
                    Vcelda_min: {
                        sensor: 'Math.min(...d_["BMS_JK1"]["Vceldas"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 25 }, showTitle: false,
                    },

                    Vcelda_dia: {
                        //campoBD: 'FV.Aux4.0',
                        unit: '-DIA-', size: '14px', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true, width: 82, position: { x: -65, y: 45 }, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 100'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 150'},
                        },
                    },
                    Vcelda_max_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK1"]["Max"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 60 }, showTitle: false,
                    },
                    Vcelda_max_dia: {
                        sensor: 'Math.max(...d_["BMS_JK1"]["Max"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 60 },showTitle: false,
                    },
                    Vcelda_min_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK1"]["Min"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 75 }, showTitle: false,
                    },
                    Vcelda_min_dia: {
                        sensor: 'Math.max(...d_["BMS_JK1"]["Min"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 75 }, showTitle: false,
                    },
                    AH_p: {
                        sensor: 'Math.floor(d_["BMS_JK1"]["AH_p"])',
                        unit: 'Ah', size: '16px', bold: true, valueColor: 'blue', position: { x: -44, y: 100 }, showTitle: false,
                    },
                    AH_n: {
                        sensor: 'Math.floor(-d_["BMS_JK1"]["AH_n"])',
                        unit: 'Ah', size: '16px', bold: true, valueColor: '#00BFFF', position: { x: -49, y: 118 }, showTitle: false,
                    },
                    T1_bat: {
                        campoBD: 'BMS_JK1.Temperaturas.0', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 30, y: 55 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 30'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 34'},
                        },
                    },
                    T2_bat: {
                        campoBD: 'BMS_JK1.Temperaturas.0', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 30, y: 68 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 30'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 34'},
                        },
                    },
                    Carga: {
                        sensor: '"C"', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgreen',
                        position: { x: 90, y: 25 }, showTitle: false, width: 15,
                        avisos: {
                            Apagado: {color:'lightgray', condicion:'d_.BMS_JK1.Interruptores.carga == false'},
                        },
                    },
                    Descarga: {
                        sensor: '"D"', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgreen',
                        position: { x: 90, y: 40 }, showTitle: false, width: 15,
                        avisos: {
                            Apagado: {color:'lightgray', condicion:'d_.BMS_JK1.Interruptores.descarga == false'},
                        },
                    },
                    Balance: {
                        sensor: '"B"', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgreen',
                        position: { x: 90, y: 55 }, showTitle: false, width: 15,
                        avisos: {
                            Apagado: {color:'lightgray', condicion:'d_.BMS_JK1.Interruptores.balance == false'},
                        },
                    },
                    I_balance: {
                        sensor: 'Math.floor(d_["BMS_JK1"]["Ibalance"])',
                        unit: 'A', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgray', position: { x: 90, y: 69 }, showTitle: false, width: 30,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 0'},
                            Red: {color:'red', condicion:'value < 0'},
                        },
                    },

                    
                }
            },
            
        },

        
    }
};
