const config = {

    MQTT: {
        servidor: {
            VPN : '10.147.17.10', // ***
            Local: '192.168.1.10', // ***  
        },
        puerto: '9001', // ***
        usuario: 'rpi', // ***
        clave: 'fv', // ***
        clave_web: 'fv1' // ***
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
            Parametros: 'parametros.php',
            Config_Web: 'fv_configuracion.html',
            Servicios: 'servicios.php',
            ScanIP: 'scanip.php',
            Copia_Seg: 'copia_seguridad/',
            Actualizar: 'actualizar.php',
            Video: 'video.html',
            Terminal: 'terminal.html',
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
            Irradiacion: 'no_menu/irradiacion_comparativa_no_menu.php',
        },
        Equipos :  'equipos1.php',
        
        Reles :{
            Estado: 'reles.php',
            TUYA: 'tuya.php'            
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
    
    
    blockMargin: '20px 45px 0px 45px', // separacion bloques ..arriba derecha abajo izquierda
    
    filas: {
        
        fila1: {
                   
            Control:{
                image: '', size: { width: 0, height: 0 },blockMargin: '0px 0px',
                elements: {
                    Placas: {
                        sensor : '(d_["FV"]["Wh_placa"] / 1000).toFixed(1)',
                        value: 99, unit: 'Kwh', size: '18px', titleColor: 'black', valueColor: 'blue', backgroundColor: 'lightgrey',
                        bold: true, position: { x: -90, y: 8 }, width: 120, showTitle: false
                    },
                    Prevision: {
                        campoBD: 'SOL1.produccion_estimada.0.total_kwh',
                        unit: 'Kwh', size: '10px', valueColor: '#2a5d6a', bold: true, position: { x: -60, y: 30 }, showTitle: false
                    },
                    
                    
                    Wplaca: {
                        campoBD: 'FV.Wplaca',
                        unit: 'W', size: '18px', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true, position: { x: -70, y: 45 }, width: 80, showTitle: false
                    },

                    Conex: {sensor: 'd_["conexion"]', value: '', unit: '', size: '18px',titleColor: 'black', valueColor: 'blue',
                            backgroundColor: 'aqua', bold: true, position: { x: -100, y:105 }, width: 150, //showTitle: false,
                    },
                    Hora: {sensor: 'd_["_PVControl+"]["tiempo"]', value: '', unit: '', size: '14px',titleColor: 'black', valueColor: 'blue',
                           backgroundColor: 'aqua', bold: true, position: { x: -100, y:125}, width: 150, showTitle: false,
                           avisos: {
                            Rojo: {color:'red', valueColor:'yellow', condicion:'new Date(d_["_PVControl+"]["tiempo"]) < new Date(now.getTime() - 1 * 60 * 1000)'},
                           },
                    },
                },
            },
            Sol: {image: 'Sol1.jpg', size: { width: 40, height: 40}, 
                blockMargin: '60px 0px 0px 0px', connectTo: null,
                avisos:{
                    KO: {image: 'luna.JPG', size: { width: 40, height: 40 }, verAviso: false, color:'red', condicion:'d_["ECOWITT"]["solar_and_uvi_solar"] < 5'},
                    OK: {image: 'Sol1.jpg', size: { width: 40, height: 40 }, verAviso: false, color:'transparent', condicion:'d_["ECOWITT"]["solar_and_uvi_solar"] > 5'},
                },
                elements:{
                    Insolacion: { sensor: 'd_["ECOWITT"]["solar_and_uvi_solar"].toFixed(0)', //campoBD : 'ECOWITT.solar_and_uvi_solar',
                        unit: ' W/m2', size: '16px', valueColor: 'red', bold: true,
                        position: { x: -67, y: 15 },showTitle: false, //width: 80,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value < 1'},
                        },
                    }, 
                }  
                
            },

            PID:{
                image: '', size: { width: 0, height: 0 },blockMargin: '0px 0px',
                elements: {
                    PWM: {campoBD: 'FV.PWM', size: '18px',titleColor: 'black', valueColor: 'yellow',backgroundColor: 'orange', bold: true, 
                          position: { x: -100, y:150 }, width: 150, //showTitle: false,
                          //avisos: { OFF: {visualizacion: 'modal', condicion:'d_["FV"]["Aux3"][1] < 3.39'}},
                    },
                    PID: { campoBD: 'FV.Aux3.0', unit: 'V', size: '14px', titleColor: 'black', valueColor: 'blue',backgroundColor: 'orange', bold: true,
                           position: { x: -100, y:170 }, width: 150, //showTitle: false,
                           avisos: { OFF: {visualizacion: 'modal', condicion:'d_["FV"]["Aux3"][1] < 3.39'}},
                    },
                    V_Exced: { campoBD: 'FV.Aux3.1', unit: 'V', size: '14px', titleColor: 'black', valueColor: 'yellow',backgroundColor: 'orange', bold: true,
                           position: { x: -100, y:186 }, width: 150, //showTitle: false,
                           avisos: { OFF: {visualizacion: 'modal', condicion:'d_["FV"]["Aux3"][1] < 3.38'}},
                    },
                    V_celda_Max: { campoBD: 'FV.Aux3.2', unit: 'V', size: '12px', titleColor: 'black', valueColor: 'blue',backgroundColor: 'orange', bold: true,
                           position: { x: -100, y:202 }, width: 150, //showTitle: false,
                           avisos: { OFF: {visualizacion: 'modal', condicion:'d_["FV"]["Aux3"][1] < 3.39'}},
                    },
                    V_Bat_Exced: { campoBD: 'FV.Aux3.3', unit: 'V', size: '12px', titleColor: 'black', valueColor: 'blue',backgroundColor: 'orange', bold: true,
                           position: { x: -100, y:216 }, width: 150, //showTitle: false,
                           avisos: { OFF: {visualizacion: 'modal', condicion:'d_["FV"]["Aux3"][1] < 3.39'}},
                    },
                    V_Exced_Max: { campoBD: 'FV.Aux3.4', unit: 'V', size: '12px', titleColor: 'black', valueColor: 'blue',backgroundColor: 'pink', bold: true,
                           position: { x: -100, y:240 }, width: 150, //showTitle: false,
                           avisos: { OFF: {visualizacion: 'modal', condicion:'d_["FV"]["Aux3"][1] < 3.39'}},
                    },
                    PWM_Max: { campoBD: 'FV.Aux3.5', size: '12px', titleColor: 'black', valueColor: 'blue',backgroundColor: 'pink', bold: true,
                           position: { x: -100, y:254 }, width: 150, //showTitle: false,
                           avisos: { OFF: {visualizacion: 'modal', condicion:'d_["FV"]["Aux3"][1] < 3.39'}},
                    },  
                },
                comandos: {
                    'PID+': {topic: 'PVControl/SQL', comando: 'UPDATE parametros SET objetivo_PID=objetivo_PID + 0.01 WHERE id_parametros=1', texto: 'PID +0.01'},
                    'PID-': {topic: 'PVControl/SQL', comando: 'UPDATE parametros SET objetivo_PID=objetivo_PID - 0.01 WHERE id_parametros=1', texto: 'PID -0.01'},
                }
                
            },
    
            Placa3: {
                image: 'placa1.avif', size: { width: 100, height: 100 },
                blockMargin: '20px 50px 0px 0px',
                connectTo: {id: 'ANENJI1', from: 'bottom', to: 'top', control: 'Wplaca', max: 3000, min: 0},
                avisos: {KO: {color:'red', condicion:'new Date(d_["ANENJI1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'}},
                
                elements: {
                    Solar: {
                        campoBD: '', value: 'S3-4.8Kwp', unit: '', size: '12px', titleColor: 'yellow', valueColor: 'black', bold: true,
                        backgroundColor: 'lightgray', position: { x: 15, y: 50 }, showTitle: false, width: 70,
                    },
                    Kwh_placa: {
                        sensor: '(d_["TABLA_MPPT"]["Wh_MPPT3"]/1000).toFixed(1)',
                        unit: 'Kwh', size: '16px', valueColor: 'blue', bold: true, position: { x: 5, y: -15 }, showTitle: false
                    },
                    Prevision: {
                        campoBD: 'SOL1.produccion_estimada.0.string_3',
                        unit: 'Kwh', size: '10px', valueColor: '#2a5d6a', bold: true, position: { x: 83, y: -10 }, showTitle: false
                    },
                    
                    
                    Wh_Wp: {sensor: '(d_["TABLA_MPPT"]["Wh_MPPT3"]/4760).toFixed(1)', unit: 'Wh/Wp', size: '11px', valueColor: 'black', bold: true,
                        position: { x: 5, y: 3 },showTitle: false, width: 80
                    }, 
                    Vplaca: {
                        sensor: 'd_["ANENJI1"]["Vplaca"].toFixed(1)', unit: 'V', size: '16px', valueColor: 'blue', bold: true, 
                        position: { x: 72, y: 45 }, width: 85, showTitle: false,
                    },
                    Wplaca: {
                        sensor : 'Math.floor(d_["ANENJI1"]["Wplaca"])',
                        unit: 'W', size: '18px', valueColor: 'blue', bold: true, position: { x: 50, y: 80 }, width: 80, showTitle: false,
                    },                   
                    Wh_Wp_i: {
                        sensor : '(d_["ANENJI1"]["Wplaca"] / 47.6).toFixed(0)',
                        unit: '% W/Wp', size: '12px', valueColor: 'blue', bold: true, backgroundColor: 'lightgrey',
                        position: { x: 70, y: 100 }, showTitle: false, width: 70
                    },
                    Iplaca: { campoBD: 'ANENJI1.Iplaca', value: 0, unit: "A", size: "15px", valueColor: 'blue', 
                            backgroundColor: 'lightblue',
                            bold: true, position: { x: 85 , y: 180 }, showTitle: false, width: 60,
                            avisos: {
                                Amarillo: {color:'yellow', condicion:'value > 25'},
                            },
                    },
                    Iplaca_b: { sensor: '(d_["ANENJI1"]["Wplaca"]/d_["ANENJI2"]["Vbat"]).toFixed(1)',
                            value: 0, unit: "A", size: "15px", valueColor: 'blue', backgroundColor: 'lightblue',
                            bold: true, position: { x: 85 , y: 205 }, showTitle: false, width: 60,
                    },


                    Wplaca_max: {campoBD: 'TABLA_MPPT_MAX.MPPT3_Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},
                }
            },   
            
            Placa1: {
                image: 'placa1.avif', size: { width: 100, height: 100 }, //blockMargin: '20px 45px 0px 0px',
                blockMargin: '20px 50px 0px 0px',
                connectTo: { id: 'MPPT1', from: 'bottom',  to: 'top', control: 'Wplaca', max: 3000, min: 0,},
                avisos: {
                    //Rojo: {color:'red', condicion:'d_["MPPT1"]["Wbat"] < 5 && d_["MPPT1"]["Estado_regulador"] !== "NOCHE"'},
                    Amarillo: {color:'yellow', condicion:'(d_["MPPT1"]["Wbat"]) > 4000'},
                    Cyan: {color:'cyan', condicion:'new Date(d_["MPPT1"]["tiempo"]) < new Date(now.getTime() - 1 * 60 * 1000)'},
                    Rojo1: {color:'red', condicion:'new Date(d_["MPPT1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                elements: {
                    Solar: {
                        campoBD: '', value: 'S1-3.15Kwp', unit: '', size: '12px', titleColor: 'yellow', valueColor: 'black',backgroundColor: 'lightgrey',
                        bold: true, position: { x: 15, y: 50 }, showTitle: false, width: 70
                    },

                    Kwh_placa: {
                        sensor: '(d_["TABLA_MPPT"]["Wh_MPPT1"]/1000).toFixed(1)',
                        unit: 'Kwh', size: '16px', valueColor: 'blue', bold: true, position: { x: 5, y: -15 }, showTitle: false
                    },
                    Prevision: {
                        campoBD: 'SOL1.produccion_estimada.0.string_1',
                        unit: 'Kwh', size: '10px', valueColor: '#2a5d6a', bold: true, position: { x: 83, y: -10 }, showTitle: false
                    },

                    Wh_Wp: {sensor: '(d_["TABLA_MPPT"]["Wh_MPPT1"]/3150).toFixed(1)', unit: 'Wh/Wp', size: '11px', valueColor: 'black', bold: true,
                        position: { x: 5, y: 3 },showTitle: false, width: 80
                    }, 


                    /*
                    Kwh_placa: {
                        //campoBD: 'MPPT1.Wh_placa',
                        sensor: '(d_["MPPT1"]["Wh_placa"]/1000  * (1 - 0.07139)).toFixed(1)',
                        unit: 'Kwh', size: '16px', valueColor: '#2a5d6a', bold: true, position: { x: 5, y: -18 }, showTitle: false
                    },
                    Wh_Wp: {sensor: '(d_["MPPT1"]["Wh_placa"]/3150  * (1 - 0.07139)).toFixed(1)', unit: 'Wh/Wp', size: '14px', valueColor: 'blue', bold: true,
                        position: { x: 5, y: 0 },showTitle: false, width: 80
                    },
                    */

                    
                    Vplaca: {
                        campoBD: 'MPPT1.Vplaca', unit: 'V', size: '16px', valueColor: 'blue', bold: true,
                        position: { x: 72, y: 45 }, width: 85, showTitle: false,
                    },
                    Wplaca: {
                        sensor: '(d_["MPPT1"]["Wbat"]  * (1 - 0.07139)).toFixed(0)', value: 0, unit: 'W', size: '16px', titleColor: 'black', valueColor: 'blue',
                        bold: true, position: { x: 50, y: 80 }, width: 80, showTitle: false,
                    },
                    Wh_Wp_i: {
                        //sensor : '(d_["MPPT1"]["Wbat"] / 31.5  * (1 - 0.07139)).toFixed(0)',
                        sensor : '(d_["MPPT1"]["Wbat"] / 31.5 ).toFixed(0)',
                        
                        unit: '% W/Wp', size: '12px', valueColor: 'blue', bold: true, backgroundColor: 'lightgrey',
                        position: { x: 80, y: 100 },showTitle: false, width: 75
                    },

                    Wplaca_max: {campoBD: 'MPPT1.Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},
                }
            },
            Placa2: {
                image: 'placa1.avif', size: { width: 100, height: 100 },
                blockMargin: '20px 50px 0px 0px',
                connectTo: {id: 'MPPT2', from: 'bottom', to: 'top', control: 'Wplaca', max: 3000, min: 0                },
                avisos: { KO: {color:'red', condicion:'new Date(d_["MPPT2"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                elements: {
                    Solar: {campoBD: '', value: 'S2-1.15Kwp', size: '12px', titleColor: 'yellow', valueColor: 'black', bold: true,
                        backgroundColor: 'lightgrey', position: { x: 15, y: 50 },showTitle: false, width: 70
                    },
                    Kwh_placa: {
                        sensor: '(d_["TABLA_MPPT"]["Wh_MPPT2"]/1000).toFixed(1)',
                        unit: 'Kwh', size: '16px', valueColor: 'blue', bold: true, position: { x: 5, y: -15 }, showTitle: false
                    },
                    Prevision: {
                        campoBD: 'SOL1.produccion_estimada.0.string_2',
                        unit: 'Kwh', size: '10px', valueColor: '#2a5d6a', bold: true, position: { x: 83, y: -10 }, showTitle: false
                    },

                    Wh_Wp: {sensor: '(d_["TABLA_MPPT"]["Wh_MPPT2"]/1150).toFixed(1)', unit: 'Wh/Wp', size: '11px', valueColor: 'black', bold: true,
                        position: { x: 5, y: 3 },showTitle: false, width: 80
                    }, 
                    Vplaca: {
                        campoBD: 'MPPT2.Vplaca', unit: 'V', size: '16px', valueColor: 'blue', bold: true,
                        position: { x: 72, y: 45 }, width: 85, showTitle: false
                    },
                    Wplaca: {
                        campoBD: 'MPPT2.Wbat', unit: 'W', valueColor: 'blue', bold: true,
                        position: { x: 50, y: 80 }, width: 80, showTitle: false,
                    },
                    Wh_Wp_i: {
                        sensor : '(d_["MPPT2"]["Wbat"] / 11.5).toFixed(0)',
                        unit: '% W/Wp', size: '12px', valueColor: 'blue', bold: true, backgroundColor: 'lightgrey',
                        position: { x: 70, y: 100 },showTitle: false, width: 80
                    },
                    Wplaca_max: {campoBD: 'MPPT2.Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},
                }
            },   

            Placa6: {
                image: 'placa1.avif', size: { width: 100, height: 100 },
                blockMargin: '20px 50px 0px 0px',
                connectTo: {id: 'MPPT6', from: 'bottom', to: 'top', control: 'Wplaca', max: 3000, min: 0                },
                avisos: { KO: {color:'red', condicion:'new Date(d_["MPPT3"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                elements: {
                    Solar: {campoBD: '', value: 'S6-1.15Kwp', size: '12px', titleColor: 'yellow', valueColor: 'black', bold: true,
                        backgroundColor: 'lightgrey', position: { x: 15, y: 50 },showTitle: false, width: 70
                    },
                    Kwh_placa: {
                        sensor: '(d_["TABLA_MPPT"]["Wh_MPPT6"]/1000).toFixed(1)',
                        unit: 'Kwh', size: '16px', valueColor: 'blue', bold: true, position: { x: 5, y: -15 }, showTitle: false
                    },
                    Prevision: {
                        campoBD: 'SOL1.produccion_estimada.0.string_6',
                        unit: 'Kwh', size: '10px', valueColor: '#2a5d6a', bold: true, position: { x: 83, y: -10 }, showTitle: false
                    },

                    Wh_Wp: {sensor: '(d_["TABLA_MPPT"]["Wh_MPPT6"]/1150).toFixed(1)', unit: 'Wh/Wp', size: '11px', valueColor: 'black', bold: true,
                        position: { x: 5, y: 3 },showTitle: false, width: 80
                    }, 
                    Vplaca: {
                        campoBD: 'MPPT3.Vplaca', unit: 'V', size: '16px', valueColor: 'blue', bold: true,
                        position: { x: 72, y: 45 }, width: 85, showTitle: false
                    },
                    Wplaca: {
                        campoBD: 'MPPT3.Wbat', unit: 'W', valueColor: 'blue', bold: true,
                        position: { x: 50, y: 80 }, width: 80, showTitle: false,
                    },
                    Wh_Wp_i: {
                        sensor : '(d_["MPPT3"]["Wbat"] / 11.5).toFixed(0)',
                        unit: '% W/Wp', size: '12px', valueColor: 'blue', bold: true, backgroundColor: 'lightgrey',
                        position: { x: 47, y: 100 },showTitle: false, width: 70
                    },
                    Wplaca_max: {campoBD: 'MPPT3.Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},
                }
            },   


            Placa4: {
                image: 'placa1.avif', size: { width: 100, height: 100 },
                blockMargin: '20px 50px 0px 0px',
                connectTo: {id: 'MPPT4', from: 'bottom', to: 'top', control: 'Wplaca', max: 3000, min: 0},
                avisos: {KO: {color:'red', condicion:'new Date(d_["ADS3"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'}},
                
                elements: {
                    Solar: {
                        campoBD: '', value: 'S4-4.6Kwp', size: '12px',  valueColor: 'black', bold: true,
                        backgroundColor: 'lightgray', position: { x: 15, y: 50 }, showTitle: false, width: 70,
                    },
                    Kwh_placa: {
                        sensor: '(d_["TABLA_MPPT"]["Wh_MPPT4"]/1000).toFixed(1)',
                        unit: 'Kwh', size: '16px', valueColor: 'blue', bold: true, position: { x: 5, y: -15 }, showTitle: false
                    },
                    Prevision: {
                        campoBD: 'SOL1.produccion_estimada.0.string_4',
                        unit: 'Kwh', size: '10px', valueColor: '#2a5d6a', bold: true, position: { x: 83, y: -10 }, showTitle: false
                    },

                    Wh_Wp: {sensor: '(d_["TABLA_MPPT"]["Wh_MPPT4"]/4600).toFixed(1)', unit: 'Wh/Wp', size: '11px', valueColor: 'black', bold: true,
                        position: { x: 5, y: 3 },showTitle: false, width: 80
                    }, 
                    Vplaca: {
                        sensor: 'd_["ADS1"]["Vplaca_S4"].toFixed(1)', unit: 'V', size: '16px', valueColor: 'blue', bold: true,
                        position: { x: 72, y: 45 }, width: 85, showTitle: false,
                    },
                    Wplaca: {
                        sensor : 'Math.floor(d_["ADS3"]["Iplaca_S4"] * d_["FV"]["Vbat"])',
                        unit: 'W', size: '18px', valueColor: 'blue', bold: true, position: { x: 50, y: 80 }, width: 80, showTitle: false,
                    },
                    Wh_Wp_i: {
                        sensor : '(d_["ADS3"]["Iplaca_S4"] * d_["FV"]["Vbat"] / 46).toFixed(0)',
                        unit: '% W/Wp', size: '12px', valueColor: 'blue', bold: true, backgroundColor: 'lightgrey',
                        position: { x: 47, y: 100 },showTitle: false, width: 70
                    },
                    Wplaca_max: {campoBD: 'TABLA_MPPT_MAX.MPPT4_Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},
                }
            }, 

            Placa7: {
                image: 'placa1.avif', size: { width: 100, height: 100 },
                blockMargin: '20px 50px 0px 0px',
                connectTo: {id: 'ANENJI3', from: 'bottom', to: 'top', control: 'Wplaca', max: 3000, min: 0},
                avisos: {KO: {color:'red', condicion:'new Date(d_["ANENJI3"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'}},
                
                elements: {
                    Solar: {
                        campoBD: '', value: 'S7-1.15Kwp', unit: '', size: '12px', titleColor: 'yellow', valueColor: 'black', bold: true,
                        backgroundColor: 'lightgray', position: { x: 15, y: 50 }, showTitle: false, width: 70,
                    },
                    Kwh_placa: {
                        sensor: '(d_["TABLA_MPPT"]["Wh_MPPT7"]/1000).toFixed(1)',
                        unit: 'Kwh', size: '16px', valueColor: 'blue', bold: true, position: { x: 5, y: -15 }, showTitle: false
                    },
                    Prevision: {
                        campoBD: 'SOL1.produccion_estimada.0.string_7',
                        unit: 'Kwh', size: '10px', valueColor: '#2a5d6a', bold: true, position: { x: 83, y: -10 }, showTitle: false
                    },

                    Wh_Wp: {sensor: '(d_["TABLA_MPPT"]["Wh_MPPT7"]/1150).toFixed(1)', unit: 'Wh/Wp', size: '11px', valueColor: 'black', bold: true,
                        position: { x: 5, y: 3 },showTitle: false, width: 80
                    }, 
                    Vplaca: {
                        sensor: 'd_["ANENJI3"]["Vplaca"].toFixed(1)', unit: 'V', size: '16px', valueColor: 'blue', bold: true, 
                        position: { x: 72, y: 45 }, width: 85, showTitle: false,
                    },
                    Wplaca: {
                        sensor : 'Math.floor(d_["ANENJI3"]["Wplaca"])',
                        unit: 'W', size: '18px', valueColor: 'blue', bold: true, position: { x: 50, y: 80 }, width: 80, showTitle: false,
                    },                   
                    Wh_Wp_i: {
                        sensor : '(d_["ANENJI3"]["Wplaca"] / 11.5).toFixed(0)',
                        unit: '% W/Wp', size: '12px', valueColor: 'blue', bold: true, backgroundColor: 'lightgrey',
                        position: { x: 47, y: 100 }, showTitle: false, width: 70
                    },
                    Iplaca: { campoBD: 'ANENJI3.Iplaca', value: 0, unit: "A", size: "15px", valueColor: 'blue', 
                            backgroundColor: 'lightblue',
                            bold: true, position: { x: 85 , y: 180 }, showTitle: false, width: 60,
                            avisos: {
                                Amarillo: {color:'yellow', condicion:'value > 25'},
                            },
                    },
                    Iplaca_b: { sensor: '(d_["ANENJI3"]["Wplaca"]/d_["ANENJI3"]["Vbat"]).toFixed(1)',
                            value: 0, unit: "A", size: "15px", valueColor: 'blue', backgroundColor: 'lightblue',
                            bold: true, position: { x: 85 , y: 205 }, showTitle: false, width: 60,
                    },


                    Wplaca_max: {campoBD: 'TABLA_MPPT_MAX.MPPT7_Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},
                }
            },   


            Placa5: {
                image: 'placa1.avif', size: { width: 100, height: 100 },
                blockMargin: '20px 50px 0px 0px',
                connectTo: {id: 'ANENJI2', from: 'bottom', to: 'top', control: 'Wplaca', max: 3000, min: 0},
                avisos: {KO: {color:'red', condicion:'new Date(d_["ANENJI2"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'}},
                
                elements: {
                    Solar: {
                        campoBD: '', value: 'S5-4.8Kwp', size: '12px',  valueColor: 'black', bold: true,
                        backgroundColor: 'lightgray', position: { x: 15, y: 50 }, showTitle: false, width: 70,
                    },
                    Kwh_placa: {
                        sensor: '(d_["TABLA_MPPT"]["Wh_MPPT5"]/1000).toFixed(1)',
                        unit: 'Kwh', size: '16px', valueColor: 'blue', bold: true, position: { x: 5, y: -15 }, showTitle: false
                    },
                    Prevision: {
                        campoBD: 'SOL1.produccion_estimada.0.string_5',
                        unit: 'Kwh', size: '10px', valueColor: '#2a5d6a', bold: true, position: { x: 83, y: -10 }, showTitle: false
                    },

                    Wh_Wp: {sensor: '(d_["TABLA_MPPT"]["Wh_MPPT5"]/4760).toFixed(1)', unit: 'Wh/Wp', size: '11px', valueColor: 'black', bold: true,
                        position: { x: 5, y: 3 },showTitle: false, width: 80
                    }, 
                    Vplaca: {
                        sensor: 'd_["ANENJI2"]["Vplaca"].toFixed(1)', unit: 'V', size: '16px', valueColor: 'blue', bold: true,
                        position: { x: 72, y: 45 }, width: 85, showTitle: false,
                    },
                    Wplaca: {
                        sensor : 'd_["ANENJI2"]["Wplaca"]',
                        unit: 'W', size: '18px', valueColor: 'blue', bold: true, position: { x: 50, y: 80 }, width: 80, showTitle: false,
                    },
                    Wh_Wp_i: {
                        sensor : '(d_["ANENJI2"]["Wplaca"]/47.6).toFixed(0)',
                        unit: '% W/Wp', size: '12px', valueColor: 'blue', bold: true, backgroundColor: 'lightgrey',
                        position: { x: 70, y: 100 },showTitle: false, width: 80
                    },
                    
                    Iplaca: { campoBD: 'ANENJI2.Iplaca', value: 0, unit: "A", size: "15px", valueColor: 'blue', 
                            backgroundColor: 'lightblue',
                            bold: true, position: { x:- 70 , y: 180 }, showTitle: false, width: 60,
                            avisos: {
                                Amarillo: {color:'yellow', condicion:'value > 25'},
                            },
                    },
                    Iplaca_b: { sensor: '(d_["ANENJI2"]["Wplaca"]/d_["ANENJI2"]["Vbat"]).toFixed(1)',
                            value: 0, unit: "A", size: "15px", valueColor: 'blue', backgroundColor: 'lightblue',
                            bold: true, position: { x:- 70 , y: 205 }, showTitle: false, width: 60,
                    },
                    
                    Wplaca_max: {campoBD: 'TABLA_MPPT_MAX.MPPT5_Wplaca_max', value: 0, unit: 'W', visualizacion: 'modal'},
                }
            }, 

            Diario:{
                image: '', size: { width: 0, height: 0 },blockMargin: '0px 0px',
                elements: {
                    "_Kwh_placa__": {sensor: '(d_["FV"]["Wh_placa"]/1000).toFixed(1)', unit: 'Kwh', size: '14px',titleColor: 'black', 
                           valueColor: 'blue',backgroundColor: 'aqua', bold: true, position: { x: -100, y:150 }, width: 190, //showTitle: false,
                    },
                    "Kwh_Consumo": {sensor: '(d_["FV"]["Wh_consumo"]/1000).toFixed(1)', unit: 'Kwh', size: '14px',titleColor: 'black', 
                           valueColor: 'blue',backgroundColor: 'aqua', bold: true, position: { x: -100, y:167 }, width: 190, //showTitle: false,
                    },
                    "_Kwh_Bat___": {sensor: '((d_["FV"]["Whp_bat"] - d_["FV"]["Whn_bat"])/1000).toFixed(1)', unit: 'Kwh', size: '14px',titleColor: 'black', 
                           valueColor: 'blue',backgroundColor: 'aqua', bold: true, position: { x: -100, y:184 }, width: 190, //showTitle: false,
                    },
                    "_Temp_IN_": {campoBD: 'ECOWITT.indoor_temperature', unit: 'ºC', size: '14px',titleColor: 'black', 
                           valueColor: 'blue',backgroundColor: 'aqua', bold: true, position: { x: -100, y:210 }, width: 190, //showTitle: false,
                    },
                    "_Temp_OUT_": {campoBD: 'ECOWITT.outdoor_temperature', unit: 'ºC', size: '14px',titleColor: 'black', 
                           valueColor: 'blue',backgroundColor: 'aqua', bold: true, position: { x: -100, y:227 }, width: 190, //showTitle: false,
                    },
                    
                    "_Lluvia_": {campoBD: 'ECOWITT.rainfall_rain_rate', unit: 'l/m2', size: '14px',titleColor: 'black', 
                           valueColor: 'blue',backgroundColor: 'yellow', bold: true, position: { x: -100, y:244 }, width: 190, //showTitle: false,
                           avisos: {
                             Rojo: {color:'red', condicion:'value > 5'},
                             OFF: {visualizacion: 'modal', condicion:'value == 0'},
                           },
                    },
                    "_Dia_": {campoBD: 'ECOWITT.rainfall_daily', unit: 'l/m2', size: '14px',titleColor: 'black', 
                            valueColor: 'blue',backgroundColor: 'aqua', bold: true, position: { x: -100, y:261 }, width: 190, //showTitle: false,
                            avisos: {
                                Amarillo: {color:'yellow', condicion:'value > 10'},
                                OFF: {visualizacion: 'modal', condicion:'value == 0'},},
                            },
                    "_Tormenta_": {campoBD: 'ECOWITT.rainfall_event', unit: 'l/m2', size: '14px',titleColor: 'black', 
                           valueColor: 'blue',backgroundColor: 'aqua', bold: true, position: { x: -100, y:279 }, width: 190, //showTitle: false,
                           avisos: {
                                OFF: {visualizacion: 'modal', condicion:'value == 0'},
                           },   
                           
                    },
                },
                
            },            
            
        },
        
        fila2: {
            MPPT1: {
                image: 'MPPT.jpg', size: { width: 50, height: 80 },
                blockMargin: '20px 50px 0px 0px',
                                connectTo: {id: 'BATERIA', from: 'bottom', to: 'top', control: 'Ibat', max: 60, min: 0},
                avisos: { KO: {color:'red', condicion:'new Date(d_["MPPT1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'}},
                elements: {
                    MODO: {campoBD: 'MPPT1.Estado_regulador', size: '10px', valueColor: 'red', backgroundColor: 'white', bold: true, position: { x: -3, y: 9 }, showTitle: false},
                    Vbat: {campoBD: 'MPPT1.Vbat', unit: 'V', size: '14px', valueColor: 'blue', bold: true, position: { x: -40, y: 30 }, showTitle: false},
                    Ibat: {campoBD: 'MPPT1.Ibat', unit: 'A', size: '14px', valueColor: 'blue', bold: true, position: { x: -35, y: 75 }, showTitle: false},
                    Vabs: {sensor: 'd_["MPPT1"]["Vabs"] + " ->> " + d_["MPPT1"]["Vabs"] * 4',  value: 0, unit: "V",  visualizacion: 'modal'},
                    Vflot: {sensor: 'd_["MPPT1"]["Vflot"] + " ->> " + d_["MPPT1"]["Vflot"] * 4',  value: 0, unit: "V",  visualizacion: 'modal'},
                },
                
                comandos: {
                    Vabs_14_7 : {topic: 'PVControl/MPPT1', comando: 'Vabs 14.7', texto: 'Vabs=14.7/58.8 ', fila: 1},
                    Vabs_14_5 : {topic: 'PVControl/MPPT1', comando: 'Vabs 14.5', texto: 'Vabs=14.5/58.0', fila: 1},
                    Vflot_14_7 : {topic: 'PVControl/MPPT1', comando: 'Vflot 14.7', texto: 'Vflot=14.7/58.8', fila: 2},
                    Vflot_14_5 : {topic: 'PVControl/MPPT1', comando: 'Vflot 14.5', texto: 'Vflot=14.5/58.0', fila: 2},
                    MPPT1  : {topic: 'PVControl/MPPT1', comando: '', texto: 'MPPT1', fila: 3},
                }                                
            },

            MPPT2: {
                image: 'MPPT.jpg', size: { width: 50, height: 80 }, 
                blockMargin: '20px 50px 0px 0px',
                connectTo: {id: 'BATERIA', from: 'bottom', to: 'top', control: 'Ibat', max: 60, min: 0},
                avisos: { KO: {color:'red', condicion:'new Date(d_["MPPT2"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'}},
                elements: {
                    MODO: {campoBD: 'MPPT2.Estado_regulador', size: '10px', valueColor: 'red', backgroundColor: 'white', bold: true, position: { x: -3, y: 9 }, showTitle: false},
                    Vbat: {campoBD: 'MPPT2.Vbat', unit: 'V', size: '14px', valueColor: 'blue', bold: true, position: { x: -40, y: 30 }, showTitle: false},
                    Ibat: {campoBD: 'MPPT2.Ibat', unit: 'A', size: '14px', valueColor: 'blue', bold: true, position: { x: -35, y: 75 }, showTitle: false},
                    Vabs: {sensor: 'd_["MPPT2"]["Vabs"] + " ->> " + d_["MPPT2"]["Vabs"] * 4',  value: 0, unit: "V",  visualizacion: 'modal'},
                    Vflot: {sensor: 'd_["MPPT2"]["Vflot"] + " ->> " + d_["MPPT2"]["Vflot"] * 4',  value: 0, unit: "V",  visualizacion: 'modal'},
                },

                comandos: {
                    Vabs_14_7 : {topic: 'PVControl/MPPT2', comando: 'Vabs 14.7', texto: 'Vabs=14.7/58.8 ', fila: 1},
                    Vabs_14_5 : {topic: 'PVControl/MPPT2', comando: 'Vabs 14.5', texto: 'Vabs=14.5/58.0', fila: 1},
                    Vflot_14_7 : {topic: 'PVControl/MPPT2', comando: 'Vflot 14.7', texto: 'Vflot=14.7/58.8', fila: 2},
                    Vflot_14_5 : {topic: 'PVControl/MPPT2', comando: 'Vflot 14.5', texto: 'Vflot=14.5/58.0', fila: 2},
                    MPPT2  : {topic: 'PVControl/MPPT2', comando: '', texto: 'MPPT2', fila: 3},
                }
            },

            MPPT6: {
                image: 'MPPT.jpg', size: { width: 50, height: 80 }, 
                blockMargin: '20px 50px 0px 0px',
                connectTo: {id: 'BATERIA', from: 'bottom', to: 'top', control: 'Ibat', max: 60, min: 0},
                avisos: { KO: {color:'red', condicion:'new Date(d_["MPPT3"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'}},
                elements: {
                    MODO: {campoBD: 'MPPT3.Estado_regulador', size: '10px', valueColor: 'red', backgroundColor: 'white', bold: true, position: { x: -3, y: 9 }, showTitle: false},
                    Vbat: {campoBD: 'MPPT3.Vbat', unit: 'V', size: '14px', valueColor: 'blue', bold: true, position: { x: -40, y: 30 }, showTitle: false},
                    Ibat: {campoBD: 'MPPT3.Ibat', unit: 'A', size: '14px', valueColor: 'blue', bold: true, position: { x: -35, y: 75 }, showTitle: false},
                    Vabs: {sensor: 'd_["MPPT3"]["Vabs"] + " ->> " + d_["MPPT3"]["Vabs"] * 4',  value: 0, unit: "V",  visualizacion: 'modal'},
                    Vflot: {sensor: 'd_["MPPT3"]["Vflot"] + " ->> " + d_["MPPT3"]["Vflot"] * 4',  value: 0, unit: "V",  visualizacion: 'modal'},
                },

                comandos: {
                    Vabs_14_7 : {topic: 'PVControl/MPPT3', comando: 'Vabs 14.7', texto: 'Vabs=14.7/58.8 ', fila: 1},
                    Vabs_14_5 : {topic: 'PVControl/MPPT3', comando: 'Vabs 14.5', texto: 'Vabs=14.5/58.0', fila: 1},
                    Vflot_14_7 : {topic: 'PVControl/MPPT3', comando: 'Vflot 14.7', texto: 'Vflot=14.7/58.8', fila: 2},
                    Vflot_14_5 : {topic: 'PVControl/MPPT3', comando: 'Vflot 14.5', texto: 'Vflot=14.5/58.0', fila: 2},
                    MPPT2  : {topic: 'PVControl/MPPT3', comando: '', texto: 'MPPT3', fila: 3},
                }
            },

            /*
            MPPT3: {
                image: 'mppt_easun_1.JPG', size: { width: 50, height: 80 },
                blockMargin: '20px 50px 0px 0px',
                connectTo: { id: 'BATERIA', from: 'bottom', to: 'top', control: 'Ibat', max: 60, min: 0},
                avisos: { KO: {color:'red', condicion:'new Date(d_["ADS3"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                elements: {
                    Ibat: {
                        //campoBD: 'ADS3.Iplaca_S3',
                        sensor : 'parseFloat(d_["ADS3"]["Iplaca_S3"].toFixed(1))',
                        unit: 'A', size: '14px', valueColor: 'blue', bold: true,
                        position: { x: -54, y: 78 }, width: 100, showTitle: false
                    },
                    //Wplaca: {sensor : 'Math.floor(d_["TABLA_MPPT"]["MPPT3_Wplaca"])', unit: 'W', size: '14px', valueColor: 'blue', bold: true,
                    //    position: { x: 22, y: 8 }, width: 100, showTitle: false
                    //},
                }
            },
            */
            MPPT4: {
                image: 'FM80.JPG', size: { width: 34, height: 100 },
                blockMargin: '3px 50px 20px 0px',
                connectTo: { id: 'BATERIA', from: 'bottom', to: 'top', control: 'Ibat', max: 60, min: 0},
                avisos: { KO: {color:'red', condicion:'new Date(d_["ADS3"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                elements: {
                    Ibat: {
                        //campoBD: 'ADS3.Iplaca_S4',
                        sensor : 'parseFloat(d_["ADS3"]["Iplaca_S4"].toFixed(1))',
                        unit: 'A', size: '14px', valueColor: 'blue', bold: true,
                        position: { x: -70, y: 94 }, width: 100, showTitle: false
                    },
                }
            },

            ANENJI3: {
                image: "Anenji.jpg",
                size: { width: 60, height: 100 },
                blockMargin: '20px 40px 0px 10px',
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["ANENJI3"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                connectTo: {
                    id: "BATERIA",
                    from: "bottom",
                    to: "top",
                    control: 'Ibat',
                    max: 70,
                    min: 0,
                    //flujoLinea: 'inverso',
                    colorLineaPositiva:'green',
                    colorLineaNegativa:'red',
                },
                elements: {
                    WM: { campoBD: 'ANENJI3.WM', value: 0, unit: "",  visualizacion: 'modal'  },
                    Out_prio: { campoBD: 'ANENJI3.Out_prio', value: 0, unit: "",  visualizacion: 'modal'  },
                    
                    Winv: { campoBD: 'ANENJI3.Winv', value: 0, unit: "W", size: "10px", titleColor: 'black',  valueColor: 'yellow', backgroundColor: '',
                            bold: true, position: { x: 20, y: 30 }, showTitle: false,//width: 70,
                            avisos: {
                                Amarillo: {color:'red', condicion:'value > 3500'},
                            },
                    },
                                                             
                    Wh_inv: {sensor: 'Math.floor(d_["TABLA_ANENJI"]["ANENJI3_Wh"])', value: 0, unit: "Wh", size: "10px", titleColor: 'black',  valueColor: 'blue', backgroundColor: 'lightblue', 
                            bold: true, position: { x: 5, y: 10 }, width: 75,
                            showTitle: false, },
                    
                    Ibat: { 
                        campoBD: 'ANENJI3.Ibat', value: 0, unit: "A", size: "16px", titleColor: 'black',  valueColor: 'blue',
                        backgroundColor: '',bold: true, position: { x: -55, y: 49 }, width: 70, showTitle: false, 
                            avisos: {
                                    Amarillo: {color:'yellow', condicion:'value > 50'},
                                },
                    
                    },
                                        
                    Temp_dc: {
                        campoBD: 'ANENJI3.Temp_dc', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 45, y: 65 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 40'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 50'},
                        },
                    },
                    Temp_inv: {
                        campoBD: 'ANENJI3.Temp_inv', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 45, y: 78 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 40'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 50'},
                        },
                    },
                    
                    Vbat: { campoBD: 'ANENJI3.Vbat', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Vred: { campoBD: 'ANENJI3.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'ANENJI3.Wred', value: 0, unit: "W", visualizacion: 'modal'  },
                    
                    Vabs: { campoBD: 'ANENJI3.Vabs', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Vflot: { campoBD: 'ANENJI3.Vflot', value: 0, unit: "V",  visualizacion: 'modal'  },
                    
                },
             
                comandos: {
                    Apagar   : {topic: 'PVControl/ANENJI3', comando: 'Remote_Switch 0', texto: 'Apagar', fila: 1},
                    Encender : {topic: 'PVControl/ANENJI3', comando: 'Remote_Switch 1', texto: 'Encender', fila: 1},
                    
                    'Vabs 58.6': {topic: 'PVControl/ANENJI3', comando: 'Vabs=58.6', texto: 'Vabs=58.6', fila:2},
                    'Vabs 58.0': {topic: 'PVControl/ANENJI3', comando: 'Vabs=58.0', texto: 'Vabs=58.0', fila:2},
                    'Vflot 58.6': {topic: 'PVControl/ANENJI3', comando: 'Vflot=58.6', texto: 'Vflot=58.6', fila:3},
                    'Vflot 58.0': {topic: 'PVControl/ANENJI3', comando: 'Vflot=58.0', texto: 'Vflot=58.0', fila:3},
                    
                   
                }    
            },

        },

        fila3: {
            
            /*
            R801_Radiador_Salon: {
                image: 'calefaccion_pared.jpg',
                size: { width: 40, height: 40 },
                connectTo: { id: 'ANENJI1', from: 'right',  to: 'left', control: 'Wconsumo', max: 2000, min: 10, colorLineaPositiva:'red',flujoLinea:'inverso',},
                blockMargin: '93px 45px 0px 0px',
                
                avisos: { // avisos a nivel de BLOQUE
                    KO: {color:'red', condicion:'new Date(d_["TUYA"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                elements: {
                    Modo: {
                        campoBD: 'RELES.801.modo', size: '10px', titleColor: 'black', valueColor: 'blue', //backgroundColor: 'pink',
                        bold: true, position: { x: -29, y: 0 }, width: 30, showTitle: false,
                        avisos_NO_activo: {// avisos a nivel de ELEMENTO
                            OFF: {color:'lightgrey', condicion:'value === "OFF"'},
                            ON: {color:'red', condicion:'value === "ON"'},
                            PRG: {color:'cyan', condicion:'value === "PRG"'},
                        },
                        
                    },
                    Estado: {
                        campoBD: 'TUYA.801.Estado',
                        value: 0,
                        unit: '',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -29, y: 15 },
                        width: 30,
                        showTitle: false,
                        avisos: {
                            0: {color:'lightgray', condicion:'value === 0'},
                            100: {color:'lightpink', condicion:'value === 100'},
                            PWM: {color:'cyan', condicion:'value > 0 && value < 100'},    
                        },
                        
                    },
                    Nombre: {
                        //campoBD: 'TUYA.801.Nombre',
                        value: 'R_Salon',
                        unit: '',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -30, y: 38 },
                        width: 80,
                        showTitle: false,
                        
                        
                    },
                    Wconsumo: {
                        //campoBD: 'TUYA.801.Wac',
                        sensor : 'd_["TUYA"]["801"]["Wac"].toFixed(0)',

                        unit: 'W', size: '14px', valueColor: 'blue', bold: true, position: { x: 30, y: 30 }, width: 60, showTitle: false,
                        avisos: {
                            ON: {color:'pink', condicion:'value >50'},
                        },
                        
                    },
                    Hoy: {
                        sensor : '(d_["TUYA"]["801"]["Wh"] / 1000).toFixed(2)',
                        unit: 'Kwh',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        bold: true,
                        position: { x: -30, y: 50 },
                        width: 100,
                        //showTitle: false,     
                    },
                    Ayer: {
                        sensor : '(d_["TUYA"]["801"]["Wh_ayer"] / 1000).toFixed(2)',
                        unit: 'Kwh',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        bold: true,
                        position: { x: -30, y: 65 },
                        width: 100,
                        //showTitle: false,     
                    },
                    
                },
                comandos: {
                    //PRG : {topic: 'PVControl/RELES/WEB', comando: '801PRG', texto: 'PRG'},
                    ON : {topic: 'PVControl/Reles/TUYA', comando: '801ON', texto: 'ON'},               
                    OFF : {topic: 'PVControl/Reles/TUYA', comando: '801OFF', texto: 'OFF'},
                }
            },
            */
            R561_AA_HAIER: {
                image: 'aa.jpg',
                size: { width: 60, height: 50 },
                connectTo: { id: 'ANENJI1', from: 'right',  to: 'left', control: 'Wconsumo', max: 2000, min: 10, colorLineaPositiva:'red',flujoLinea:'inverso',},
                blockMargin: '50px 0px 0px -20px',
                
                avisos: { // avisos a nivel de BLOQUE
                    KO: {color:'red', condicion:'new Date(d_["MQTT"]["tele/PVControl/Reles/56/SENSOR"]["Time"]) < new Date(now.getTime() - 65 * 60 * 1000)'},
                },
                
                elements: {
                    Tconsigna: {
                        campoBD: 'AA.tempSel', size: '12px', titleColor: 'black', valueColor: 'red', unit: 'ºC',backgroundColor: 'lightgray',
                        bold: true, position: { x: 10, y: 10 }, width: 40, showTitle: false,
                    },    
                    
                    
                    ONOFF: {
                        campoBD: 'AA.onOffStatus', size: '14px', titleColor: 'black', valueColor: 'blue', //backgroundColor: 'pink',
                        bold: true, position: { x: 0, y: 53 }, width: 30, showTitle: true,
                        avisos_NO_activo: {// avisos a nivel de ELEMENTO
                            OFF: {color:'lightgrey', condicion:'value === 0'},
                            ON: {color:'red', condicion:'value === 1'},
                        },
                        
                    },
                    Temp_IN: {
                        campoBD: 'AA.tempIndoor', 
                        size: '10px', titleColor: 'black', valueColor: 'blue', unit: 'ºC', //backgroundColor: 'pink',
                        bold: true, position: { x: -90, y: -10 }, width: 90, showTitle: true,
                    },
                    Temp_OUT: {
                        campoBD: 'AA.tempOutdoor', 
                        size: '10px', titleColor: 'black', valueColor: 'blue',  unit: 'ºC',//backgroundColor: 'pink',
                        bold: true, position: { x: -90, y: 2 }, width: 90, showTitle: true,
                    },                    
                    Modo: {
                        campoBD: 'AA.machMode', 
                        size: '10px', titleColor: 'black', valueColor: 'blue',  unit: '',//backgroundColor: 'pink',
                        bold: true, position: { x: 40, y: 2 }, width: 90, showTitle: true,
                    },                    
                    Comp_Frec: {
                        campoBD: 'AA.compressorFrequency', 
                        size: '10px', titleColor: 'black', valueColor: 'blue',  unit: '',//backgroundColor: 'pink',
                        bold: true, position: { x: 48, y: 13 }, width: 90, showTitle: true,
                    },
                    
                    Rele: {
                        campoBD: 'RELES.561.modo', size: '14px', titleColor: 'black', valueColor: 'blue', //backgroundColor: 'pink',
                        bold: true, position: { x: -10, y: 70 }, width: 30, showTitle: true,
                        avisos_NO_activo: {// avisos a nivel de ELEMENTO
                            OFF: {color:'lightgrey', condicion:'value === "OFF"'},
                            ON: {color:'red', condicion:'value === "ON"'},
                            PRG: {color:'cyan', condicion:'value === "PRG"'},
                        },
                        
                    },
                    
                    
                    Estado: {
                        campoBD: 'RELES.561.estado',
                        value: 0,
                        unit: '',
                        size: '14px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: 37, y: 70 },
                        width: 30,
                        showTitle: false,
                        avisos: {
                            0: {color:'lightgray', condicion:'value === 0'},
                            100: {color:'lightpink', condicion:'value === 100'},
                            PWM: {color:'cyan', condicion:'value > 0 && value < 100'},    
                        },
                        
                    },
                    Nombre: {
                        campoBD: 'RELES.561.nombre',
                        value: 0,
                        unit: '',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'darkmagenta',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -10, y: -12 },
                        width: 80,
                        showTitle: false,
                        
                        
                    },
                    Wconsumo: {
                        campoBD: 'MQTT.tele/PVControl/Reles/56/SENSOR.ENERGY.Power',
                        unit: 'W', size: '14px', valueColor: 'blue', bold: true, position: { x: 57, y: 40 }, width: 60, showTitle: false,
                        avisos: {
                            ON: {color:'pink', condicion:'value >500'},
                        },
                        
                    },
                    Hoy: {
                        campoBD: 'MQTT.tele/PVControl/Reles/56/SENSOR.ENERGY.Today',
                        unit: 'Kwh', size: '12px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: -94, y: 18 }, width: 100, //showTitle: false,     
                    },
                    Ayer: {
                        campoBD: 'MQTT.tele/PVControl/Reles/56/SENSOR.ENERGY.Yesterday',
                        unit: 'Kwh', size: '12px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: -94, y: 35 }, width: 100, //showTitle: false,     
                    },
    
                },
                
                comandos: {
                    ON : {topic: 'PVControl/AA', comando: 'on', texto: 'Enciende AA', fila: 1},
                    OFF: {topic: 'PVControl/AA', comando: 'off', texto: 'Apaga AA', fila: 1},
                    
                    T24 : {topic: 'PVControl/AA', comando: 'temp 24', texto: 'Temp 24ºC', fila: 2},
                    T26 : {topic: 'PVControl/AA', comando: 'temp 26', texto: 'Temp 26ºC', fila: 2},
                    T28 : {topic: 'PVControl/AA', comando: 'temp 28', texto: 'Temp 28ºC', fila: 2},    
                }
            },


            R806_Frigo_Ext: {
                image: 'combi.jpg',
                size: { width: 30, height: 60 },
                connectTo: { id: 'ANENJI1', from: 'right',  to: 'left', control: 'Wconsumo', max: 2000, min: 10, colorLineaPositiva:'red',flujoLinea:'inverso',},
                blockMargin: '140px 60px 0px 0px',
                
                avisos: { // avisos a nivel de BLOQUE
                    KO: {color:'red', condicion:'new Date(d_["TUYA"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                elements: {
                    Modo: {
                        campoBD: 'RELES.806.modo', size: '10px', titleColor: 'black', valueColor: 'blue', //backgroundColor: 'pink',
                        bold: true, position: { x: -35, y: 42 }, width: 30, showTitle: false,
                        avisos_NO_activo: {// avisos a nivel de ELEMENTO
                            OFF: {color:'lightgrey', condicion:'value === "OFF"'},
                            ON: {color:'red', condicion:'value === "ON"'},
                            PRG: {color:'cyan', condicion:'value === "PRG"'},
                        },   
                    },
                    Estado: {
                        campoBD: 'TUYA.806.Estado',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -35, y: 53 },
                        width: 30,
                        showTitle: false,
                        avisos: {
                            0: {color:'lightgray', condicion:'value === 0'},
                            100: {color:'lightpink', condicion:'value === 100'},
                            PWM: {color:'cyan', condicion:'value > 0 && value < 100'},    
                        },
                        
                    },
                    Nombre: {
                        campoBD: 'TUYA.806.Nombre',
                        value: 0,
                        unit: '',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        //backgroundColor: 'pink',
                        bold: true,
                        position: { x: -10, y: 65 },
                        width: 80,
                        showTitle: false,
                        
                        
                    },
                    Wconsumo: {
                        //campoBD: 'TUYA.806.Wac',
                        sensor : 'd_["TUYA"]["806"]["Wac"].toFixed(0)',
                        unit: 'W', size: '14px', valueColor: 'blue', bold: true, position: { x: 15, y: 35 }, width: 60, showTitle: false,
                        avisos: {
                            ON: {color:'pink', condicion:'value >50'},
                        },
                        
                    },
                    Hoy: {
                        //campoBD: 'TUYA.806.Wh',
                        sensor : '(d_["TUYA"]["806"]["Wh"] / 1000).toFixed(2)',
                        unit: 'Kwh',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        bold: true,
                        position: { x: -15, y: 80 },
                        width: 100,
                        //showTitle: false,     
                    },
                    
                },
                comandos: {
                    //PRG : {topic: 'PVControl/RELES/WEB', comando: '806PRG', texto: 'PRG'},
                    ON : {topic: 'PVControl/Reles/TUYA', comando: '806ON', texto: 'ON'},               
                    OFF : {topic: 'PVControl/Reles/TUYA', comando: '806OFF', texto: 'OFF'},
                }
            },


            ANENJI1: {
                image: 'Anenji.jpg',
                size: { width: 100, height: 150 },
                blockMargin: '60px 10px 0px 10px',
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["ANENJI1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                connectTo: {
                    id: 'BATERIA',
                    from: 'right',
                    to: 'left',
                    control: 'Ibat',
                    max: 70,
                    min: 0,
                    //ujoLinea: 'inverso',
                    colorLineaPositiva:'green',
                    colorLineaNegativa:'red',
                },
                
                elements: {
                    WM: { campoBD: 'ANENJI1.WM', value: 0, unit: "",  visualizacion: 'modal'  },
                    Out_prio: { campoBD: 'ANENJI2.Out_prio', value: 0, unit: "",  visualizacion: 'modal'  },
                    
                    Winv: { campoBD: 'ANENJI1.Winv', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'yellow', backgroundColor: '', 
                            bold: true, position: { x: 30, y: 40 }, showTitle: false, //width: 70,
                            avisos: {
                                Amarillo: {color:'red', condicion:'value > 3500'},
                            },
                    },
                            
                    Wh_inv: {sensor: 'Math.floor(d_["TABLA_ANENJI"]["ANENJI1_Wh"])', value: 0, unit: "Wh", size: "16px", titleColor: 'black',  valueColor: 'blue', backgroundColor: 'lightblue', 
                            bold: true, position: { x: 5, y: -10 }, width: 95, showTitle: false, },
                    
                    Ibat: { campoBD: 'ANENJI1.Ibat', value: 0, unit: "A", size: "16px", titleColor: 'black',  valueColor: 'blue', 
                            backgroundColor: '',bold: true, position: { x: 84, y: 49 }, width: 70, showTitle: false, 
                            avisos: {
                                    Amarillo: {color:'yellow', condicion:'value > 50'},
                                },
                    },
                    Temp_dc: {
                        campoBD: 'ANENJI1.Temp_dc', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 45, y: 95 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 40'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 50'},
                        },
                    },
                    Temp_inv: {
                        campoBD: 'ANENJI1.Temp_inv', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 45, y: 108 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 40'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 50'},
                        },
                    },

                    
                    Vred: { campoBD: 'ANENJI1.Vred', value: 0, unit: "V",  visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'ANENJI1.Wred', value: 0, unit: "W",  visualizacion: 'modal'  },
 
                    Vbat: { campoBD: 'ANENJI1.Vbat', value: 0, unit: "V", visualizacion: 'modal'  },
 
                    Vabs: { campoBD: 'ANENJI1.Vabs', value: 0, unit: "V",  visualizacion: 'modal'  },
                    
                    Vflot: { campoBD: 'ANENJI1.Vflot', value: 0, unit: "V",  visualizacion: 'modal'  },
                    
                    
                    // Agregar más elementos según sea necesario
                },
                
                comandos: {
                    Apagar   : {topic: 'PVControl/ANENJI1', comando: 'Remote_Switch 0', texto: 'Apagar', fila: 1},
                    Encender : {topic: 'PVControl/ANENJI1', comando: 'Remote_Switch 1', texto: 'Encender', fila: 1},
                    
                    'Vabs 58.6': {topic: 'PVControl/ANENJI1', comando: 'Vabs=58.6', texto: 'Vabs=58.6', fila:2},
                    'Vabs 58.0': {topic: 'PVControl/ANENJI1', comando: 'Vabs=58.0', texto: 'Vabs=58.0', fila:2},
                    'Vflot 58.6': {topic: 'PVControl/ANENJI1', comando: 'Vflot=58.6', texto: 'Vflot=58.6', fila:3},
                    'Vflot 58.0': {topic: 'PVControl/ANENJI1', comando: 'Vflot=58.0', texto: 'Vflot=58.0', fila:3},
                    
                   
                }    

            },

            BATERIA: {
                image: 'bateria_transparente75.png',
                size: { width: 65, height: 120 },
                blockMargin: '60px 75px',

                avisos: {
                    SOC_100: {image: 'bateria100.png', verAviso: false, condicion:'d_["FV"]["SOC"] >= 95'},
                    SOC_83: {image: 'bateria83.png', verAviso: false, condicion:'d_["FV"]["SOC"] < 95 && d_["FV"]["SOC"] >= 83'},
                    SOC_66: {image: 'bateria66.png', verAviso: false, condicion:'d_["FV"]["SOC"] < 83 && d_["FV"]["SOC"] >= 66'},
                    SOC_50: {image: 'bateria50.png', color: 'yellow', condicion:'d_["FV"]["SOC"] < 66 && d_["FV"]["SOC"] >= 50'},
                    SOC_33: {image: 'bateria33.png', color: 'pink', condicion:'d_["FV"]["SOC"] < 50 && d_["FV"]["SOC"] >= 33'},
                    SOC_16: {image: 'bateria16.png', color: 'red', condicion:'d_["FV"]["SOC"] < 33'},
                },
                
                connectTo: null,
                
                elements: {
                    Placas: {
                        sensor : '(d_["FV"]["Wh_placa"] / 1000).toFixed(1)',
                        value: 99, unit: 'Kwh', size: '22px', titleColor: 'black', valueColor: 'blue', backgroundColor: 'lightgrey',
                        bold: true, position: { x: -75, y: -66 }, width: 220, showTitle: false
                    },
                    Wplaca: {
                        campoBD: 'FV.Wplaca',
                        unit: 'W', size: '22px', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true, position: { x: -34, y: -37 }, width: 150, showTitle: false
                    },
                    
                    
                    
                    MODO: {
                        campoBD: 'FV.Mod_bat',
                        size: '10px', valueColor: 'black', backgroundColor: 'lightgray', bold: true, position: { x: 16, y: 50 }, width: 35, showTitle: false
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
                        sensor: 'd_["FV"]["Vbat"].toFixed(2)',
                        unit: 'V', size: '16px', valueColor: 'blue', backgroundColor: 'lightgreen', bold: true,
                        position: { x: -5, y: 133 },width: 80, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'(value < 56 && value >= 55) || (value > 58 && value <= 58.5)'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value < 55 || value > 58.5'},
                        },
                    },
                    Vbat_max: {
                        campoBD: 'FV.Vbat_max',
                        //campoBD: '', value: 57.5,
                        unit: 'V', size: '12px', valueColor: 'blue',backgroundColor: 'lightgreen', bold: true, position: { x: 80, y: 136 }, width: 50, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'(value < 56 && value >= 55) || (value > 58 && value <= 58.5)'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value < 55 || value > 58.5'},
                        },
                    },
                    Vbat_min: {
                        campoBD: 'FV.Vbat_min',
                        //campoBD: '', value: 56.1,
                        unit: 'V', size: '12px', valueColor: 'blue', backgroundColor: 'lightgreen', bold: true, position: { x: -60, y: 136 }, width: 50, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'(value < 56 && value >= 55) || (value > 58 && value <= 58.5)'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value < 55 || value > 58.5'},
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

                    Wbat: {
                        sensor: 'd_["FV"]["Wbat"].toFixed(0)',
                        unit: 'W', size: '16px', valueColor: 'blue', backgroundColor: 'lightgreen', bold: true,
                        position: { x: -5, y: 175 },width: 80, showTitle: false,
                        
                    },


                    Whp_bat: {
                        //campoBD: 'FV.Whp_bat',
                        sensor: '(d_["FV"]["Whp_bat"]/1000).toFixed(1)',
                        value: 0,
                        unit: 'Kwh',
                        size: '14px',
                        valueColor: 'blue',
                        bold: true,
                        position: { x: 48, y: 66 },
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
                        position: { x: 46, y: 83 },
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

            ANENJI2: {
                image: "Anenji.jpg",
                size: { width: 100, height: 150 },
                blockMargin: '60px 40px 0px 10px',
                avisos: {
                    KO: {color:'red', condicion:'new Date(d_["ANENJI2"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                connectTo: {
                    id: "BATERIA",
                    from: "left",
                    to: "right",
                    control: 'Ibat',
                    max: 70,
                    min: 0,
                    //flujoLinea: 'inverso',
                    colorLineaPositiva:'green',
                    colorLineaNegativa:'red',
                },
                elements: {
                    WM: { campoBD: 'ANENJI2.WM', value: 0, unit: "",  visualizacion: 'modal'  },
                    Out_prio: { campoBD: 'ANENJI2.Out_prio', value: 0, unit: "",  visualizacion: 'modal'  },
                    
                    Winv: { campoBD: 'ANENJI2.Winv', value: 0, unit: "W", size: "16px", titleColor: 'black',  valueColor: 'yellow', backgroundColor: '',
                            bold: true, position: { x: 30, y: 40 }, showTitle: false,//width: 70,
                            avisos: {
                                Amarillo: {color:'red', condicion:'value > 3500'},
                            },
                    },
                    /*
                    Autoconsumo: { 
                            //campoBD: 'TABLA_ANENJI2.H_Autoconsumo',
                            sensor: 'Math.floor(d_["TABLA_ANENJI2"]["H_Autoconsumo"])',
                            value: 0, unit: "W", size: "12px", titleColor: 'black',  valueColor: 'green', backgroundColor: 'lightgrey',
                            bold: true, position: { x: 35, y: 60 }, showTitle: false,//width: 70,
                            avisos: {
                                amarillo: {color:'yellow', condicion:'value > 150 & value < 300'},
                                rojo: {color:'red', condicion:'value > 300'},
                            },
                    },
                    */  
                    
                    Wh_inv: {sensor: 'Math.floor(d_["TABLA_ANENJI"]["ANENJI2_Wh"])', value: 0, unit: "Wh", size: "16px", titleColor: 'black',  valueColor: 'blue', backgroundColor: 'lightblue', 
                            bold: true, position: { x: 5, y: -10 }, width: 95,
                            showTitle: false, },
                    
                    Ibat: { 
                        campoBD: 'ANENJI2.Ibat', value: 0, unit: "A", size: "16px", titleColor: 'black',  valueColor: 'blue',
                        backgroundColor: '',bold: true, position: { x: -55, y: 49 }, width: 70, showTitle: false, 
                            avisos: {
                                    Amarillo: {color:'yellow', condicion:'value > 50'},
                                },
                    
                    },
                    
                    /*
                    Ibat_ads: { sensor: '(d_["MQTT"]["PVControl/ADS1115/Intensidad"]).toFixed(1)',
                            value: 0, unit: "ADS", size: "15px", valueColor: 'blue', backgroundColor: '',
                            bold: true, position: { x:- 60 , y: 30 }, showTitle: false, width: 70,
                    },
                    
                    
                    Iplaca_ads_error: { sensor: '(d_["MQTT"]["PVControl/ADS1115/Intensidad/error"]).toFixed(1)',
                            value: 0, unit: "A_error", size: "12px", valueColor: 'red', backgroundColor: '',
                            bold: true, position: { x:- 65 , y: 15 }, showTitle: false, width: 70,
                    },
                    */
                    
                    Temp_dc: {
                        campoBD: 'ANENJI2.Temp_dc', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 45, y: 95 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 40'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 50'},
                        },
                    },
                    Temp_inv: {
                        campoBD: 'ANENJI2.Temp_inv', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 45, y: 108 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 40'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 50'},
                        },
                    },
                    
                    Vbat: { campoBD: 'ANENJI2.Vbat', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Vred: { campoBD: 'ANENJI2.Vred', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Wred: { campoBD: 'ANENJI2.Wred', value: 0, unit: "W", visualizacion: 'modal'  },
                    
                    Vabs: { campoBD: 'ANENJI2.Vabs', value: 0, unit: "V", visualizacion: 'modal'  },
                    
                    Vflot: { campoBD: 'ANENJI2.Vflot', value: 0, unit: "V",  visualizacion: 'modal'  },
                    
                },
             
                comandos: {
                    Apagar   : {topic: 'PVControl/ANENJI2', comando: 'Remote_Switch 0', texto: 'Apagar', fila: 1},
                    Encender : {topic: 'PVControl/ANENJI2', comando: 'Remote_Switch 1', texto: 'Encender', fila: 1},
                    
                    'Vabs 58.6': {topic: 'PVControl/ANENJI2', comando: 'Vabs=58.6', texto: 'Vabs=58.6', fila:2},
                    'Vabs 58.0': {topic: 'PVControl/ANENJI2', comando: 'Vabs=58.0', texto: 'Vabs=58.0', fila:2},
                    'Vflot 58.6': {topic: 'PVControl/ANENJI2', comando: 'Vflot=58.6', texto: 'Vflot=58.6', fila:3},
                    'Vflot 58.0': {topic: 'PVControl/ANENJI2', comando: 'Vflot=58.0', texto: 'Vflot=58.0', fila:3},
                    
                   
                }    
            },

            R541_Termo: {
                image: 'termo_agua.jpg',
                size: { width: 53, height: 80 },
                connectTo: { id: 'ANENJI2', from: 'left',  to: 'right', control: 'Wconsumo', max: 2000, min: 10, colorLineaPositiva:'red',flujoLinea:'inverso',},
                blockMargin: '20px 0px 0px 50px',
                
                avisos: { // avisos a nivel de BLOQUE
                    KO_54: {color:'red', condicion:'new Date(d_["MQTT"]["tele/PVControl/Reles/54/SENSOR"]["Time"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                    KO_55: {color:'pink', condicion:'new Date(d_["MQTT"]["tele/PVControl/Reles/55/SENSOR"]["Time"]) < new Date(now.getTime() - 5 * 60 * 1000)'},
                },
                
                elements: {
                    Modo_R551: {
                        campoBD: 'RELES.551.modo', size: '10px', valueColor: 'blue', //backgroundColor: 'pink',
                        bold: true, position: { x: -20, y: -10 }, width: 30, showTitle: false,
                        avisos: {
                            OFF: {color:'lightpink', condicion:'value === "OFF"'},
                            ON: {color:'lightgrey', condicion:'value === "ON"'},
                            PRG: {color:'yellow', condicion:'value === "PRG"'},
                        },
                        
                    },
                    Modo_R541: {
                        //campoBD: 'RELES.551.estado',
                        campoBD: 'MQTT.tele/PVControl/Reles/54/STATE.POWER1',
                        
                        size: '10px', valueColor: 'blue',   //backgroundColor: 'pink',
                        bold: true, position: { x: 12, y: -10 }, width: 30, showTitle: false,
                        avisos: {
                            OFF: {color:'lightgray', condicion:'value === "OFF"'},
                            ON: {color:'lightpink', condicion:'value === "ON"'},    
                        },
                        
                    },
                    Estado_Modo_R541: {
                        //campoBD: 'RELES.551.estado',
                        campoBD: 'MQTT.tele/PVControl/Reles/54/STATE.Channel1',
                        
                        size: '10px', valueColor: 'blue',   //backgroundColor: 'pink',
                        bold: true, position: { x: 42, y: -10 }, width: 30, showTitle: false,
                        avisos: {
                            0: {color:'lightgray', condicion:'value === 0'},
                            100: {color:'lightpink', condicion:'value === 100'},
                            PWM: {color:'cyan', condicion:'value > 0 && value < 100'},    
                        },
                        
                    },
                    
                    Temp1: {
                        campoBD: 'MQTT.tele/PVControl/Reles/54/SENSOR.DS18B20-1.Temperature', 
                        unit: 'ºC', size: '11px',
                        valueColor: 'black', backgroundColor: 'lightgray', bold: true,
                        position: { x: 55, y: 4}, width: 40,
                        showTitle: false,
                        avisos: {
                            caliente: {color:'lightpink', condicion:'value >50'},
                            fria: {color:'cyan', condicion:'value < 35'},    
                        }, 
                    },
                    Temp2: {
                        campoBD: 'MQTT.tele/PVControl/Reles/54/SENSOR.DS18B20-2.Temperature',  
                        unit: 'ºC', size: '11px',
                        valueColor: 'black', backgroundColor: 'lightblue', bold: true,
                        position: { x: 55, y: 55}, width: 40,
                        showTitle: false,
                         avisos: {
                            caliente: {color:'lightpink', condicion:'value >40'},
                            fria: {color:'cyan', condicion:'value < 30'},    
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
                        unit: 'W', size: '14px', valueColor: 'blue', bold: true, position: { x: 55, y: 27 }, width: 60, showTitle: false,
                        avisos: {
                            ON: {color:'pink', condicion:'value >50'},
                            OFF: {color:'lightgrey', condicion:'value <50'},
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
    
                },
                comandos: {
                    PRG : {topic: 'PVControl/RELES/WEB', comando: '541PRG', texto: 'PRG'},
                    //ON  : {topic: 'PVControl/SQL', comando: 'UPDATE reles SET modo="ON" WHERE id_rele=541', texto: 'ON', requiereClave: false}, // opcion de usar forma generica SQL
                    ON : {topic: 'PVControl/RELES/WEB', comando: '541ON', texto: 'ON'},               
                    OFF : {topic: 'PVControl/RELES/WEB', comando: '541OFF', texto: 'OFF'},
                
                }
            },


            /*
            R221_Calef_Dormitorio: {
                image: 'acumulador.jpg',
                size: { width: 60, height: 60 },
                connectTo: { id: 'ANENJI2', from: 'left',  to: 'right', control: 'Wconsumo', max: 2000, min: 0, colorLineaPositiva:'red',flujoLinea:'inverso',},
                blockMargin: '0px 0px 0px 20px',
                                
                elements: {
                    Modo: {
                        campoBD: 'RELES.808.modo',
                        size: '12px', valueColor: 'blue', bold: true,
                        position: { x: -35, y: 25 }, width: 40, showTitle: false,
                        avisos: {
                            OFF: {color:'lightgrey', condicion:'value === "OFF"'},
                            ON: {color:'red', condicion:'value === "ON"'},
                            PRG: {color:'cyan', condicion:'value === "PRG"'},
                        },
                        
                    },
                    //Prio: {
                    //    campoBD: 'RELES.221.prioridad',
                    //    size: '14px', titleColor: 'black', backgroundColor: 'yellow', valueColor: 'blue', bold: true,
                    //    position: { x: 65, y: 40 }, width: 30, showTitle: false,  
                    //},
                    
                    Estado: {
                        campoBD: 'RELES.808.estado',
                        size: '14px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: -35, y: 42 }, width: 35, showTitle: false,
                        avisos: {
                            0: {color:'lightgrey', condicion:'value === 0'},
                            100: {color:'lightpink', condicion:'value === 100'},
                            PWM: {color:'cyan', condicion:'value > 0 && value < 100'},    
                        },   
                    },
                    Nombre: {
                        campoBD: 'RELES.221.nombre',
                        size: '8px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: 0, y: 58 }, width: 60, showTitle: false,
                    },    
                
                    Wconsumo: {
                        //campoBD: 'TUYA.808.Wac',
                        sensor : 'd_["TUYA"]["808"]["Wac"].toFixed(0)',

                        unit: 'W', size: '14px', valueColor: 'blue', bold: true, position: { x: 60, y: -10 }, width: 60, showTitle: false,
                        avisos: {
                            ON: {color:'pink', condicion:'value >50'},
                        },
                        
                    },
                    Hoy: {
                        sensor : '(d_["TUYA"]["808"]["Wh"] / 1000).toFixed(2)',
                        unit: 'Kwh',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        bold: true,
                        position: { x: 60, y: 5 },
                        width: 100,
                        //showTitle: false,     
                    },
                    Ayer: {
                        sensor : '(d_["TUYA"]["808"]["Wh_ayer"] / 1000).toFixed(2)',
                        unit: 'Kwh',
                        size: '12px',
                        titleColor: 'black',
                        valueColor: 'blue',
                        bold: true,
                        position: { x: 60, y: 20 },
                        width: 100,
                        //showTitle: false,     
                    },
                },  

            
                comandos: {
                    //PRG : {topic: 'PVControl/RELES/WEB', comando: '221PRG', texto: 'PRG'},
                    //ON  : {topic: 'PVControl/RELES/WEB', comando: '221ON',  texto: 'ON' },
                    //OFF : {topic: 'PVControl/RELES/WEB', comando: '221OFF', texto: 'OFF'},
                    ON  : {topic: 'PVControl/TUYA/721ON', comando: '221ON', texto: 'ON'},
                    OFF : {topic: 'PVControl/TUYA/721OFF', comando: '221OFF', texto: 'OFF'},
                }


            },        
            */
            /*
            R231_Calef_WC: {
                image: 'calefaccion_pared.jpg',
                size: { width: 60, height: 60 },
                connectTo: { id: 'ANENJI2', from: 'left',  to: 'right', control: 'Estado', max: 200, min: 0, colorLineaPositiva:'red',flujoLinea:'inverso',},
                blockMargin: '103px 0px 0px 0px',
                                
                elements: {
                    Modo: {
                        campoBD: 'RELES.231.modo',
                        size: '14px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: 85, y: 25 }, width: 30, showTitle: false,
                        avisos1: {
                            OFF: {color:'lightgrey', condicion:'value === "OFF"'},
                            ON: {color:'red', condicion:'value === "ON"'},
                            PRG: {color:'cyan', condicion:'value === "PRG"'},
                        },
                    },
                    Prio: {
                        campoBD: 'RELES.231.prioridad',
                        size: '14px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: 90, y: 40 }, width: 30, showTitle: true,  
                    },
                    
                    
                    Estado: {
                        campoBD: 'RELES.231.estado',
                        size: '14px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: 85, y: 55 }, width: 30, showTitle: false,
                        avisos: {
                            0: {color:'lightgrey', condicion:'value === 0'},
                            100: {color:'lightpink', condicion:'value === 100'},
                            PWM: {color:'cyan', condicion:'value > 0 && value < 100'},    
                        },
                        
                    },
                    Nombre: {
                        campoBD: 'RELES.231.nombre',
                        size: '12px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: -5, y: 55 }, width: 80, showTitle: false,
                    },
    
                },
            
                comandos: {
                    PRG : {topic: 'PVControl/RELES/WEB', comando: '231PRG', texto: 'PRG'},
                    ON  : {topic: 'PVControl/RELES/WEB', comando: '231ON',  texto: 'ON' },
                    OFF : {topic: 'PVControl/RELES/WEB', comando: '231OFF', texto: 'OFF'},
                    
                    ON_2  : {topic: 'PVControl/TUYA/722ON', comando: '231ON', texto: 'ON TODO', fila: 2},
                    OFF_2 : {topic: 'PVControl/TUYA/722OFF', comando: '231OFF', texto: 'OFF TODO', fila: 2},
                }

            },
            R611_Acu_Salon: {
                image: 'acumulador.jpg',
                size: { width: 60, height: 60 },
                connectTo: { id: 'ANENJI2', from: 'left',  to: 'right', control: 'Estado', max: 100, min: 0, colorLineaPositiva:'red',flujoLinea:'inverso',},
                blockMargin: '160px 40px 0px -120px',
                                
                elements: {
                    Modo: {
                        campoBD: 'RELES.611.modo',
                        size: '14px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: 95, y: 25 }, width: 30, showTitle: false,
                        avisos1: {
                            OFF: {color:'lightgrey', condicion:'value === "OFF"'},
                            ON: {color:'red', condicion:'value === "ON"'},
                            PRG: {color:'cyan', condicion:'value === "PRG"'},
                        },
                        
                    },
                    Prio: {
                        campoBD: 'RELES.611.prioridad',
                        size: '14px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: 95, y: 40 }, width: 30, showTitle: true,  
                    },
                    
                    Estado: {
                        campoBD: 'RELES.611.estado',
                        size: '14px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: 95, y: 55 }, width: 30, showTitle: false,
                        avisos: {
                            0: {color:'lightgrey', condicion:'value === 0'},
                            100: {color:'lightpink', condicion:'value === 100'},
                            PWM: {color:'cyan', condicion:'value > 0 && value < 100'},    
                        },   
                    },
                    Nombre: {
                        campoBD: 'RELES.611.nombre',
                        size: '12px', titleColor: 'black', valueColor: 'blue', bold: true,
                        position: { x: -5, y: 55 }, width: 80, showTitle: false,
                    },    
                },
            
                comandos: {
                    PRG : {topic: 'PVControl/RELES/WEB', comando: '611PRG', texto: 'PRG'},
                    ON  : {topic: 'PVControl/RELES/WEB', comando: '611ON',  texto: 'ON' },
                    OFF : {topic: 'PVControl/RELES/WEB', comando: '611OFF', texto: 'OFF'},
                }
            },
            */
        },
        
        fila4: {
            JK1: {
                image: 'bateria.jpg', size: { width: 100, height: 100 },
                blockMargin: '20px 60px',
                avisos: {KO: {color:'red', condicion:'new Date(d_["BMS_JK1"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                connectTo: {id: 'BATERIA', from: 'top', to: 'bottom', control: 'Ibat', max: 50, min: 0, flujoLinea:'inverso', colorLineaPositiva:'green',},
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
                        unit: 'V', size: '16px', valueColor: 'blue', bold: true, position: { x: 15, y: 119 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 56 || value <= 58'},
                            Amarillo: {color:'yellow', condicion:'value < 56 && value >= 55'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < 55'},
                        },
                    },
                    Ibat: {
                        campoBD: 'BMS_JK1.Ibat',
                        unit: 'A', size: '16px', valueColor: 'blue', bold: true, position: { x: 22, y: -16 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < -50 || value > 50 '},
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
                        campoBD: 'FV.Aux4.0',
                        unit: 'mV -DIA-',  size: '12px', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true, width: 82, position: { x: -65, y: 45 }, showTitle: false,
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
                        sensor: 'Math.min(...d_["BMS_JK1"]["Min"])',
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
                },
            
                comandos: {
                    CON  : {topic: 'PVControl/JK1', comando: 'CON', texto: 'Carga ON', requiereClave: false, fila: 1},
                    COFF  : {topic: 'PVControl/JK1', comando: 'COFF', texto: 'Carga OFF', requiereClave: false, fila: 1},
                    DON  : {topic: 'PVControl/JK1', comando: 'DON', texto: 'Descarga ON', requiereClave: false, fila: 2},
                    DOFF  : {topic: 'PVControl/JK1', comando: 'DOFF', texto: 'Descarga OFF', requiereClave: false, fila: 2},
                    BON  : {topic: 'PVControl/JK1', comando: 'BON', texto: 'Balance ON', requiereClave: false, fila: 3},
                    BOFF  : {topic: 'PVControl/JK1', comando: 'BOFF', texto: 'Balance OFF', requiereClave: false, fila: 3},
                    CBT  : {topic: 'PVControl/JK1', comando: 'C', texto: 'CONECTAR BT', fila: 4},
                    DBT  : {topic: 'PVControl/JK1', comando: 'D', texto: 'DESCONEXION BT', requiereClave: false, fila: 4},  
                }
            },
            JK2: {
                image: 'bateria.jpg', size: { width: 100, height: 100 },
                blockMargin: '20px 60px',
                avisos: {KO: {color:'red', condicion:'new Date(d_["BMS_JK2"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                connectTo: {id: 'BATERIA', from: 'top', to: 'bottom', control: 'Ibat', max: 50, min: 0, flujoLinea:'inverso', colorLineaPositiva:'green',},
                elements: {
                    Banco: {
                        campoBD: '', value: 'JK2',
                        size: '16x', valueColor: '#B03A2E', backgroundColor: 'lightgray', bold: true, position: { x: 30, y: 13 }, width: 50, showTitle: false
                    },
                    Nciclos: {
                        campoBD: 'BMS_JK2.Nciclos',
                        unit: ' ciclos', size: '10px', valueColor: 'black', backgroundColor: 'lightgray', bold: true, position: { x: 30, y: 33 }, width: 50, showTitle: false
                    },
                    SOC: {
                        campoBD: 'BMS_JK2.SOC',
                        unit: '%', size: '20px', valueColor: 'blue', bold: true, position: { x: 15, y: 95 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 80'},
                            Amarillo: {color:'yellow', condicion:'value < 80'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < 60'},
                        },
                    },
                    Vbat: {
                        campoBD: 'BMS_JK2.Vbat',
                        unit: 'V', size: '16px', valueColor: 'blue', bold: true, position: { x: 15, y: 119 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 56 || value <= 58'},
                            Amarillo: {color:'yellow', condicion:'value < 56 && value >= 55'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < 55'},
                        },
                    },
                    Ibat: {
                        campoBD: 'BMS_JK2.Ibat',
                        unit: 'A', size: '16px', valueColor: 'blue', bold: true, position: { x: 22, y: -16 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < -50 || value > 50 '},
                            Amarillo: {color:'yellow', condicion:'value < -20 || value > 20'},
                        },
                    },
                    Dif: {
                        sensor: '(Math.max(...d_["BMS_JK2"]["Vceldas"]) - Math.min(...d_["BMS_JK2"]["Vceldas"])) * 1000',
                        unit: 'mV', size: '14px', titleColor: 'black', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true,
                        width: 82, position: { x: -65, y: -5 }, //showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 50'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 200'},
                        },
                    },
                    Vcelda_max_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK2"]["Vceldas"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 10 }, showTitle: false,
                    },
                    Vcelda_max: {
                        sensor: 'Math.max(...d_["BMS_JK2"]["Vceldas"])',
                        unit: 'V', size: '14px', valueColor: 'red', position: { x: -30, y: 10 }, showTitle: false,
                    },
                    Vcelda_min_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK2"]["Vceldas"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 25 }, showTitle: false,
                    },
                    Vcelda_min: {
                        sensor: 'Math.min(...d_["BMS_JK2"]["Vceldas"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 25 }, showTitle: false,
                    },

                    Vcelda_dia: {
                        campoBD: 'FV.Aux4.1',
                        unit: 'mV -DIA-',  size: '12px', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true, width: 82, position: { x: -65, y: 45 }, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 100'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 150'},
                        },
                    },
                    Vcelda_max_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK2"]["Max"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 60 }, showTitle: false,
                    },
                    Vcelda_max_dia: {
                        sensor: 'Math.max(...d_["BMS_JK2"]["Max"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 60 },showTitle: false,
                    },
                    Vcelda_min_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK2"]["Min"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 75 }, showTitle: false,
                    },
                    Vcelda_min_dia: {
                        sensor: 'Math.min(...d_["BMS_JK2"]["Min"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 75 }, showTitle: false,
                    },
                    AH_p: {
                        sensor: 'Math.floor(d_["BMS_JK2"]["AH_p"])',
                        unit: 'Ah', size: '16px', bold: true, valueColor: 'blue', position: { x: -44, y: 100 }, showTitle: false,
                    },
                    AH_n: {
                        sensor: 'Math.floor(-d_["BMS_JK2"]["AH_n"])',
                        unit: 'Ah', size: '16px', bold: true, valueColor: '#00BFFF', position: { x: -49, y: 118 }, showTitle: false,
                    },
                    T1_bat: {
                        campoBD: 'BMS_JK2.Temperaturas.0', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 30, y: 55 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 30'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 34'},
                        },
                    },
                    T2_bat: {
                        campoBD: 'BMS_JK2.Temperaturas.0', unit: "ºC",size: '10px', bold: true,
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
                            Apagado: {color:'lightgray', condicion:'d_.BMS_JK2.Interruptores.carga == false'},
                        },
                    },
                    Descarga: {
                        sensor: '"D"', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgreen',
                        position: { x: 90, y: 40 }, showTitle: false, width: 15,
                        avisos: {
                            Apagado: {color:'lightgray', condicion:'d_.BMS_JK2.Interruptores.descarga == false'},
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
                        sensor: 'Math.floor(d_["BMS_JK2"]["Ibalance"])',
                        unit: 'A', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgray', position: { x: 90, y: 69 }, showTitle: false, width: 30,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 0'},
                            Red: {color:'red', condicion:'value < 0'},
                        },
                    },
                },
            
                comandos: {
                    CON  : {topic: 'PVControl/JK2', comando: 'CON', texto: 'Carga ON', requiereClave: false, fila: 1},
                    COFF  : {topic: 'PVControl/JK2', comando: 'COFF', texto: 'Carga OFF', requiereClave: false, fila: 1},
                    DON  : {topic: 'PVControl/JK2', comando: 'DON', texto: 'Descarga ON', requiereClave: false, fila: 2},
                    DOFF  : {topic: 'PVControl/JK2', comando: 'DOFF', texto: 'Descarga OFF', requiereClave: false, fila: 2},
                    BON  : {topic: 'PVControl/JK2', comando: 'BON', texto: 'Balance ON', requiereClave: false, fila: 3},
                    BOFF  : {topic: 'PVControl/JK2', comando: 'BOFF', texto: 'Balance OFF', requiereClave: false, fila: 3},
                    CBT  : {topic: 'PVControl/JK2', comando: 'C', texto: 'CONECTAR BT', fila: 4},
                    DBT  : {topic: 'PVControl/JK2', comando: 'D', texto: 'DESCONEXION BT', requiereClave: false, fila: 4},  
                }
            },
            JK3: {
                image: 'bateria.jpg', size: { width: 100, height: 100 },
                blockMargin: '20px 60px',
                avisos: {KO: {color:'red', condicion:'new Date(d_["BMS_JK3"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                connectTo: {id: 'BATERIA', from: 'top', to: 'bottom', control: 'Ibat', max: 50, min: 0, flujoLinea:'inverso', colorLineaPositiva:'green',},
                elements: {
                    Banco: {
                        campoBD: '', value: 'JK3',
                        size: '16x', valueColor: '#B03A2E', backgroundColor: 'lightgray', bold: true, position: { x: 30, y: 13 }, width: 50, showTitle: false
                    },
                    Nciclos: {
                        campoBD: 'BMS_JK3.Nciclos',
                        unit: ' ciclos', size: '10px', valueColor: 'black', backgroundColor: 'lightgray', bold: true, position: { x: 30, y: 33 }, width: 50, showTitle: false
                    },
                    SOC: {
                        campoBD: 'BMS_JK3.SOC',
                        unit: '%', size: '20px', valueColor: 'blue', bold: true, position: { x: 15, y: 95 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 80'},
                            Amarillo: {color:'yellow', condicion:'value < 80'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < 60'},
                        },
                    },
                    Vbat: {
                        campoBD: 'BMS_JK3.Vbat',
                        unit: 'V', size: '16px', valueColor: 'blue', bold: true, position: { x: 15, y: 119 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 56 || value <= 58'},
                            Amarillo: {color:'yellow', condicion:'value < 56 && value >= 55'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < 55'},
                        },
                    },
                    Ibat: {
                        campoBD: 'BMS_JK3.Ibat',
                        unit: 'A', size: '16px', valueColor: 'blue', bold: true, position: { x: 22, y: -16 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < -50 || value > 50 '},
                            Amarillo: {color:'yellow', condicion:'value < -20 || value > 20'},
                        },
                    },
                    Dif: {
                        sensor: '(Math.max(...d_["BMS_JK3"]["Vceldas"]) - Math.min(...d_["BMS_JK3"]["Vceldas"])) * 1000',
                        unit: 'mV', size: '14px', titleColor: 'black', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true,
                        width: 82, position: { x: -65, y: -5 }, //showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 50'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 200'},
                        },
                    },
                    Vcelda_max_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK3"]["Vceldas"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 10 }, showTitle: false,
                    },
                    Vcelda_max: {
                        sensor: 'Math.max(...d_["BMS_JK3"]["Vceldas"])',
                        unit: 'V', size: '14px', valueColor: 'red', position: { x: -30, y: 10 }, showTitle: false,
                    },
                    Vcelda_min_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK3"]["Vceldas"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 25 }, showTitle: false,
                    },
                    Vcelda_min: {
                        sensor: 'Math.min(...d_["BMS_JK3"]["Vceldas"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 25 }, showTitle: false,
                    },

                    Vcelda_dia: {
                        campoBD: 'FV.Aux4.2',
                        unit: 'mV -DIA-',  size: '12px', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true, width: 82, position: { x: -65, y: 45 }, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 100'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 150'},
                        },
                    },
                    Vcelda_max_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK3"]["Max"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 60 }, showTitle: false,
                    },
                    Vcelda_max_dia: {
                        sensor: 'Math.max(...d_["BMS_JK3"]["Max"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 60 },showTitle: false,
                    },
                    Vcelda_min_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK3"]["Min"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 75 }, showTitle: false,
                    },
                    Vcelda_min_dia: {
                        sensor: 'Math.min(...d_["BMS_JK3"]["Min"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 75 }, showTitle: false,
                    },
                    AH_p: {
                        sensor: 'Math.floor(d_["BMS_JK3"]["AH_p"])',
                        unit: 'Ah', size: '16px', bold: true, valueColor: 'blue', position: { x: -44, y: 100 }, showTitle: false,
                    },
                    AH_n: {
                        sensor: 'Math.floor(-d_["BMS_JK3"]["AH_n"])',
                        unit: 'Ah', size: '16px', bold: true, valueColor: '#00BFFF', position: { x: -49, y: 118 }, showTitle: false,
                    },
                    T1_bat: {
                        campoBD: 'BMS_JK3.Temperaturas.0', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 30, y: 55 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 30'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 34'},
                        },
                    },
                    T2_bat: {
                        campoBD: 'BMS_JK3.Temperaturas.0', unit: "ºC",size: '10px', bold: true,
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
                            Apagado: {color:'blue', condicion:'d_.BMS_JK3.Interruptores.carga == false'},
                        },
                    },
                    Descarga: {
                        sensor: '"D"', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgreen',
                        position: { x: 90, y: 40 }, showTitle: false, width: 15,
                        avisos: {
                            Apagado: {color:'lightgray', condicion:'d_.BMS_JK3.Interruptores.descarga == false'},
                        },
                    },
                    Balance: {
                        sensor: '"B"', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgreen',
                        position: { x: 90, y: 55 }, showTitle: false, width: 15,
                        avisos: {
                            Apagado: {color:'lightgray', condicion:'d_.BMS_JK3.Interruptores.balance == false'},
                        },
                    },
                    I_balance: {
                        sensor: 'Math.floor(d_["BMS_JK3"]["Ibalance"])',
                        unit: 'A', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgray', position: { x: 90, y: 69 }, showTitle: false, width: 30,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 0'},
                            Red: {color:'red', condicion:'value < 0'},
                        },
                    },
                },
            
                comandos: {
                    CON  : {topic: 'PVControl/JK3', comando: 'CON', texto: 'Carga ON', requiereClave: false, fila: 1},
                    COFF  : {topic: 'PVControl/JK3', comando: 'COFF', texto: 'Carga OFF', requiereClave: false, fila: 1},
                    DON  : {topic: 'PVControl/JK3', comando: 'DON', texto: 'Descarga ON', requiereClave: false, fila: 2},
                    DOFF  : {topic: 'PVControl/JK3', comando: 'DOFF', texto: 'Descarga OFF', requiereClave: false, fila: 2},
                    BON  : {topic: 'PVControl/JK3', comando: 'BON', texto: 'Balance ON', requiereClave: false, fila: 3},
                    BOFF  : {topic: 'PVControl/JK3', comando: 'BOFF', texto: 'Balance OFF', requiereClave: false, fila: 3},
                    CBT  : {topic: 'PVControl/JK3', comando: 'C', texto: 'CONECTAR BT', fila: 4},
                    DBT  : {topic: 'PVControl/JK3', comando: 'D', texto: 'DESCONEXION BT', requiereClave: false, fila: 4},  
                }

            
            },
            JK4: {
                image: 'bateria.jpg', size: { width: 100, height: 100 },
                blockMargin: '20px 60px 50px 70px',
                avisos: {KO: {color:'red', condicion:'new Date(d_["BMS_JK4"]["tiempo"]) < new Date(now.getTime() - 5 * 60 * 1000)'},},
                connectTo: {id: 'BATERIA', from: 'top', to: 'bottom', control: 'Ibat', max: 50, min: 0, flujoLinea:'inverso', colorLineaPositiva:'green',},
                elements: {
                    Banco: {
                        campoBD: '', value: 'JK4',
                        size: '16x', valueColor: '#B03A2E', backgroundColor: 'lightgray', bold: true, position: { x: 30, y: 13 }, width: 50, showTitle: false
                    },
                    Nciclos: {
                        campoBD: 'BMS_JK4.Nciclos',
                        unit: ' ciclos', size: '10px', valueColor: 'black', backgroundColor: 'lightgray', bold: true, position: { x: 30, y: 33 }, width: 50, showTitle: false
                    },
                    SOC: {
                        campoBD: 'BMS_JK4.SOC',
                        unit: '%', size: '20px', valueColor: 'blue', bold: true, position: { x: 15, y: 95 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 80'},
                            Amarillo: {color:'yellow', condicion:'value < 80'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < 60'},
                        },
                    },
                    Vbat: {
                        campoBD: 'BMS_JK4.Vbat',
                        unit: 'V', size: '16px', valueColor: 'blue', bold: true, position: { x: 15, y: 119 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= 56 || value <= 58'},
                            Amarillo: {color:'yellow', condicion:'value < 56 && value >= 55'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < 55'},
                        },
                    },
                    Ibat: {
                        campoBD: 'BMS_JK4.Ibat',
                        unit: 'A', size: '16px', valueColor: 'blue', bold: true, position: { x: 22, y: -16 }, width: 80, showTitle: false,
                        avisos: {
                            Verde: {color:'lightgreen', condicion:'value >= -20 && value <= 20'},
                            Rojo: {color:'red', valueColor:'yellow', condicion:'value < -50 || value > 50 '},
                            Amarillo: {color:'yellow', condicion:'value < -20 || value > 20'},
                        },
                    },
                    Dif: {
                        sensor: '(Math.max(...d_["BMS_JK4"]["Vceldas"]) - Math.min(...d_["BMS_JK4"]["Vceldas"])) * 1000',
                        unit: 'mV', size: '14px', titleColor: 'black', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true,
                        width: 82, position: { x: -65, y: -5 }, //showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 50'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 200'},
                        },
                    },
                    Vcelda_max_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK4"]["Vceldas"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        value: 0, unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 10 }, showTitle: false,
                    },
                    Vcelda_max: {
                        sensor: 'Math.max(...d_["BMS_JK4"]["Vceldas"])',
                        unit: 'V', size: '14px', valueColor: 'red', position: { x: -30, y: 10 }, showTitle: false,
                    },
                    Vcelda_min_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK4"]["Vceldas"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 25 }, showTitle: false,
                    },
                    Vcelda_min: {
                        sensor: 'Math.min(...d_["BMS_JK4"]["Vceldas"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 25 }, showTitle: false,
                    },

                    Vcelda_dia: {
                        campoBD: 'FV.Aux4.3',
                        unit: 'mV -DIA-',  size: '12px', valueColor: 'blue', backgroundColor: 'lightgrey', bold: true, width: 82, position: { x: -65, y: 45 }, showTitle: false,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 100'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 150'},
                        },
                    },
                    Vcelda_max_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK4"]["Max"]; const Val = Math.max(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 60 }, showTitle: false,
                    },
                    Vcelda_max_dia: {
                        sensor: 'Math.max(...d_["BMS_JK4"]["Max"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 60 },showTitle: false,
                    },
                    Vcelda_min_dia_celda: {
                        sensor: '(() => { const Vceldas = d_["BMS_JK4"]["Min"]; const Val = Math.min(...Vceldas); return "C" + (Vceldas.indexOf(Val) + 1)+":"; })()',
                        unit: '', size: '14px', valueColor: 'black', bold: true, position: { x: -60, y: 75 }, showTitle: false,
                    },
                    Vcelda_min_dia: {
                        sensor: 'Math.min(...d_["BMS_JK4"]["Min"])',
                        unit: 'V', size: '14px', valueColor: 'blue', position: { x: -30, y: 75 }, showTitle: false,
                    },
                    AH_p: {
                        sensor: 'Math.floor(d_["BMS_JK4"]["AH_p"])',
                        unit: 'Ah', size: '16px', bold: true, valueColor: 'blue', position: { x: -44, y: 100 }, showTitle: false,
                    },
                    AH_n: {
                        sensor: 'Math.floor(-d_["BMS_JK4"]["AH_n"])',
                        unit: 'Ah', size: '16px', bold: true, valueColor: '#00BFFF', position: { x: -49, y: 118 }, showTitle: false,
                    },
                    T1_bat: {
                        campoBD: 'BMS_JK4.Temperaturas.0', unit: "ºC",size: '10px', bold: true,
                        valueColor: 'black', backgroundColor: 'lightgray', position: { x: 30, y: 55 }, showTitle: false, width: 40,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 30'},
                            Rojo: {color:'red', valueColor: 'yellow', condicion:'value > 34'},
                        },
                    },
                    T2_bat: {
                        campoBD: 'BMS_JK4.Temperaturas.0', unit: "ºC",size: '10px', bold: true,
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
                            Apagado: {color:'lightgray', condicion:'d_.BMS_JK4.Interruptores.carga == false'},
                        },
                    },
                    Descarga: {
                        sensor: '"D"', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgreen',
                        position: { x: 90, y: 40 }, showTitle: false, width: 15,
                        avisos: {
                            Apagado: {color:'lightgray', condicion:'d_.BMS_JK4.Interruptores.descarga == false'},
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
                        sensor: 'Math.floor(d_["BMS_JK4"]["Ibalance"])',
                        unit: 'A', size: '10px', bold: true, valueColor: 'black', backgroundColor: 'lightgray', position: { x: 90, y: 69 }, showTitle: false, width: 30,
                        avisos: {
                            Amarillo: {color:'yellow', condicion:'value > 0'},
                            Red: {color:'red', condicion:'value < 0'},
                        },
                    },
                },
            
                comandos: {
                    CON  : {topic: 'PVControl/JK4', comando: 'CON', texto: 'Carga ON', requiereClave: false, fila: 1},
                    COFF  : {topic: 'PVControl/JK4', comando: 'COFF', texto: 'Carga OFF', requiereClave: false, fila: 1},
                    DON  : {topic: 'PVControl/JK4', comando: 'DON', texto: 'Descarga ON', requiereClave: false, fila: 2},
                    DOFF  : {topic: 'PVControl/JK4', comando: 'DOFF', texto: 'Descarga OFF', requiereClave: false, fila: 2},
                    BON  : {topic: 'PVControl/JK4', comando: 'BON', texto: 'Balance ON', requiereClave: false, fila: 3},
                    BOFF  : {topic: 'PVControl/JK4', comando: 'BOFF', texto: 'Balance OFF', requiereClave: false, fila: 3},
                    CBT  : {topic: 'PVControl/JK4', comando: 'C', texto: 'CONECTAR BT', fila: 4},
                    DBT  : {topic: 'PVControl/JK4', comando: 'D', texto: 'DESCONEXION BT', requiereClave: false, fila: 4},  
                }
            },
        },
    },


    graficas: {

        columnas: 2, // Número de columnas en la cuadrícula

        archivos: {
            H1: {archivo: '/no_menu/historico3c_no_menu.php', width: '100%', height: '530px', border: 'none', gridArea: '1 / 1 / 2 / 3'},
            Prevision: {archivo: '/no_menu/irradiacion_comparativa_no_menu.php', width: '100%', height: '1400px', border: 'none', gridArea: '2 / 1 / 3 / 3'},
            //Video: {archivo: 'http://10.147.17.71:9082', width: '100%', height: '570px', border: 'none', gridArea: '2 / 2 / 3 / 3'},
            Kwh_Bat: {archivo: 'wh.php', width: '100%', height: '900px', border: 'none', gridArea: '3 / 1 / 4 / 3'},
            
            //Promedios: {archivo: 'prom_30.php', width: '100%', height: '600px', border: 'none', gridArea: '2 / 2 / 3 / 3'},   
            // Meteo: {archivo: 'meteogram.php', width: '100%', height: '800px', border: 'none', gridArea: '3 / 1 / 4 / 3'},    
        },
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
                FV: {campoBD: '_PVControl+.PVControl+', size: '18px', titleColor: 'black', valueColor: 'black', backgroundColor: 'lightgreen', bold: true},
                
                Separador_1: {backgroundColor: 'lightgray', value: '&nbsp;', size: '10px',showTitle: false,},
                
                PWM: { campoBD: 'FV.PWM',  size: '18px',   titleColor: 'black', valueColor: 'blue',bold: true,
                    avisos: { 
                        Rojo: {color:'red', valueColor:'yellow', condicion:'value > 0'},
                        Blue: {color:'none', valueColor:'blue', condicion:'value == 0'},
                    },
                },

                Separador_2: {backgroundColor: 'lightgray', value: '&nbsp;', size: '10px', showTitle: false,},
                
                AEMET: {campoBD: 'AEMET.0.cielo.12-24',  size: '12px', titleColor: 'black', valueColor: 'blue', bold: true, width: 150},
                Kwh: {campoBD: 'AEMET.0.Kwh.dia',  size: '16px', titleColor: 'black', valueColor: 'blue', bold: true, width: 150},
 
                Separador_3: {backgroundColor: 'lightgray', value: '&nbsp;', size: '10px', showTitle: false,},
 
                TEXTO: {campoBD: '', value: 'En un lugar de Titul .....', size: '12px', titleColor: 'black', valueColor: 'blue', bold: true, width: 150},

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

};

