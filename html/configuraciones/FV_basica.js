const config = {


    graficas: {

        columnas: 2, // Número de columnas en la cuadrícula

        archivos: {
            H1: {archivo: 'historico1_red.php', width: '100%', height: '400px', border: 'none', gridArea: '1 / 1 / 2 / 3'},
            Kwh_Bat: {archivo: 'wh.php', width: '100%', height: '700px', border: 'none', gridArea: '2 / 1 / 3 / 3'},
            Prevision: {archivo: '/no_menu/irradiacion_comparativa_no_menu.php', width: '100%', height: '1400px', border: 'none', gridArea: '3 / 1 / 4 / 3'},
            Promedios: {archivo: 'prom_30.php', width: '100%', height: '500px', border: 'none', gridArea: '4 / 1 / 5 / 3'},
            
        },
    },

    menu_web:{
        Inicio: {
            Dibujo:'fv.html',
            Relojes:'inicio_con_celdas.php',
        },
        Utilidades:{
            Meteo:'meteogram.php',
            SOC:'actualizar_soc.php',
            Log: 'log.php',
            //Parametros: 'parametros.php',
            Servicios: 'servicios.php',
            Copia_Seg: 'copia_seguridad/',
            Actualizar: 'actualizar.php',
            Terminal: 'terminal.html',
            Configuracion: 'configuracion.html',


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
            H_Producion: 'grafica_elige.php',
            Diario: 'diario.php',
            Carga_Desc: 'wh_2.php',
            Irradiacion: 'no_menu/irradiacion_comparativa_no_menu.php',
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
            Resumen: 'historico_celdas_max_min.php'
        },

        Ayuda : {
            PVControl: 'ayuda.php',
            Manuales: 'manuales.php',
        }
           
        
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
    
    blockMargin: '30px 25px 0px 0px', // separacion bloques ..arriba derecha abajo izquierda 
    
    filas: {
        fila1: {
            Placa1: {
                image: 'placa1.avif',
                size: { width: 100, height: 100 },
                connectTo: { id: 'Inversor1', from: 'bottom',  to: 'top', control: 'Wplaca', max: 3000, min: 0,},
                avisos: {
                    Rojo: {color:'red', condicion:'d_["FV"]["Wplaca"] < 5 '},
                    Amarillo: {color:'yellow', condicion:'(d_["FV"]["Wplaca"] < 300 && d_["FV"]["Wplaca"] >= 5)'},
                    Azul: {color:'cyan', condicion:'new Date(d_["FV"]["tiempo"]) < new Date(now.getTime() - 1 * 60 * 1000)'},//1 minuto
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
                        campoBD: 'FV.Wplaca',
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
                            1: {color:'yellow', condicion:'value > 5'},
                        },
                        
                    },
                    Vplaca: {
                        campoBD: 'FV.Vplaca',
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
                    Wh_placa: {
                        campoBD: 'FV.Wh_placa',
                        value: 99,
                        unit: 'Wh',
                        size: '18px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'green',
                        bold: true,
                        position: { x: 0, y: -5 },
                        //width: 100,
                        showTitle: false
                    },
                    Iplaca: {campoBD: 'FV.Iplaca', value: 0, unit: 'A', visualizacion: 'modal'},
    
                }
            },
        },  
        fila2: {
            Red1: {
                image: "red.jpg",
                size: { width: 110, height: 150 },
                blockMargin: '22px 25px 0px 0px',
                connectTo: {
                    id: "Inversor1",
                    from: "right",
                    to: "left",
                    control: 'Wred',
                    max: 4000,
                    min: 0,
                    //flujoColor: 'inverso' // por defecto vacio o 'normal' = color negro positivo y rojo negativo
                },
                elements: {
                    
                    Wred: { campoBD: 'FV.Wred', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: 100, y: 50 }, width: 70,
                    showTitle: false },
                    
                    Wh_red: { campoBD: 'FV.Wh_red', value: 0, unit: "Wh", size: "16px", titleColor: 'black',  valueColor: 'blue',
                    backgroundColor: '',bold: true, position: { x: 25, y: 144 }, width: 70,
                    showTitle: false  },
                    
                    
                    Vred: { campoBD: 'FV.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Whp_red: { campoBD: 'FV.Whp_red', value: 0, unit: "W", visualizacion: 'modal'  },
                    Whn_red: { campoBD: 'FV.Whn_red', value: 0, unit: "W", visualizacion: 'modal'  },
                    
                }
            },

            Inversor1: {
                image: "Anenji.jpg",
                size: { width: 100, height: 150 },
                blockMargin: '20px 20px 0px 55px',
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
                    
                    Wbat: { campoBD: 'FV.Wbat', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'blue', 
                    backgroundColor: '',bold: true, position: { x: -10, y: 146 }, width: 70,
                    showTitle: false  },
                    
                    Vred: { campoBD: 'FV.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'FV.Wred', value: 0, unit: "W", visualizacion: 'modal'  },
                    
                }
            },
            Casa1: {
                image: "casa.jpg",
                size: { width: 150, height: 100 },
                blockMargin: '45px 0px 0px 45px',
                
                connectTo: {
                    id: "Inversor1",
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
                    backgroundColor: '',bold: true, position: { x: 42, y: 100 }, width: 70,
                    showTitle: false  },
                    
                    
                    Vred: { campoBD: 'FV.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'FV.Wred', value: 0, unit: "W", visualizacion: 'modal'  },
                    
                }
            },
            
        },
        fila3: {
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
                        position: { x: 20, y: -10 },
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

                    Whp_bat: {
                        campoBD: 'FV.Whp_bat',
                        value: 0,
                        unit: 'Wh',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 40, y: 12 },
                        width: 100,
                        showTitle: false,
                    },
                    Whn_bat: {
                        campoBD: 'FV.Whn_bat',
                        value: 0,
                        unit: 'Wh',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'red',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 40, y: 30 },
                        width: 100,
                        showTitle: false,
                    },
                    Vbat_max: {
                        campoBD: 'FV.Vbat_max',
                        value: 0,
                        unit: 'V',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'red',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -65, y: 12 },
                        width: 80,
                        showTitle: false,
                    },
                    Vbat_min: {
                        campoBD: 'FV.Vbat_min',
                        value: 0,
                        unit: 'V',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -65, y: 30 },
                        width: 80,
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
                        position: { x: -65, y: 60 },
                        width: 80,
                        showTitle: false,
                    },
 
                }
            },


            
        },
        
    },


};
