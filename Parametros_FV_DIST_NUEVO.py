# ------------------------------------------------------------------
######    PARAMETROS INSTALACION PVControl+  -- version: 2025-11-28
# ------------------------------------------------------------------

CONFIG = {
    # ====================================================================
    # 2.- SENSORES Y VARIABLES
    # ====================================================================
    'SENSORES': {
        'definiciones': {
            'Vbat': {'Equipo': "d_['HIBRIDO']['Vbat']", 'Max': 66, 'Min': 11},
            'Vplaca': {'Equipo': "d_['HIBRIDO']['Vplaca']", 'Max': 500, 'Min': -5},
            'Ibat': {'Equipo': "d_['HIBRIDO']['Ibat']", 'Max': 200, 'Min': -200},
            'Iplaca': {'Equipo': "d_['HIBRIDO']['Iplaca']", 'Max': 200, 'Min': -1},
            'Aux1': {},
            'Aux2': {},
            'Aux3': {},
            'Aux4': {},
            'Aux5': {},
            'Aux6': {},
            'Aux7': {},
            'Vred': {},
            'Ired': {},
            'EFF': {},
            'Temp_Bat': {},
            'Wbat': {"Ibat * Vbat"},
            'Wplaca': {"d_['HIBRIDO']['Wplaca']"},
            'Wred': {"Ired * Vred"},
            'Wconsumo': {"Wplaca-Wred-Wbat"},
            'Temp': {'Equipo': "Temp_Bat"},
            
        },
        'graficas_auxiliares': {
            'TABLA_1': {'activo': 0, 'tmuestra': 5, 'variables': "Vbat, Ibat,Vplaca"},
            'TABLA_2': {'activo': 0, 'tmuestra': 1, 'variables': ""},
            'TABLA_3': {'activo': 0, 'tmuestra': 1, 'variables': ""}
        }
    },
    
    # ====================================================================
    # 3.- CONFIGURACIÓN DE BATERÍA
    # ====================================================================
    'BATERIA': {
        'AH': 100.0,
        'CP': 1.0,
        'EC': 1.0,
        'vsis': 4.0,
        'vflotacion': 13.7,
        'SOC_incremento_rapido_condicion': 'Ibat>0 and Ibat<0.005*AH and abs(Vbat-Vflot)<0.2',
        'SOC_incremento_rapido_accion': 'DS += (AH-DS)/50',
        'Bulk_Absorcion_accion': [],
        'Absorcion_Flotacion_accion': [],
        'Flotacion_Bulk_accion': [],
        'Tflot_bulk_tiempo': 10000
    },
    
    # ====================================================================
    # 4.- EQUIPOS (Estructura Plana)
    # ====================================================================
    'EQUIPOS': {
        # --- Conversores/Inversores ---
         'VICTRON': {
            'VEDIRECT': {
                'VICTRON1': {'usar': 0, 'dev': "/dev/ttyUSB1"},
                'VICTRON2': {'usar': 0, 'dev': "/dev/ttyUSB2"}
            },
            'MK2': {
                'MULTIPLUS1': {
                    'usar': 0,
                    'dev': '/dev/ttyUSB0',
                    'tiempo_captura': 5,
                    'ciclos_grabacion': 1
                }
            },
            'VENUS': {
                'mqtt_broker_venus': "192.168.X.XX",
                'mqtt_puerto_venus': 1883,
                'mqtt_usuario_venus': "XXXX",
                'mqtt_clave_venus': "YYY",
                'usar_mqtt_suscripciones_venus': 0,
                'mqtt_suscripciones_venus': [],
                'usar_mqtt_publicaciones_venus': 0,
                'mqtt_publicaciones_venus': [
                    ["R/XXXX/keepalive", "", 60],
                    ["R/YYYY/keepalive", "", 60]
                ]
            }
        },
       
        
        
        'HIBRIDO': {
        
            'HIBRIDO1' : {
                'usar' : 1,
                'puerto': "/dev/hidraw0",
                'usar_crc': 1,
                't_muestra': 5,
                'publicar_mqtt': 1,
                'grabar_datos': 1,
                'n_muestras': 1,
                'protocolo': 30,
                'QPIGS2h_enviar': 0
                },
                
            'HIBRIDO2' : {
                'usar' : 1,
                'puerto': "/dev/hidraw0",
                'usar_crc': 1,
                't_muestra': 5,
                'publicar_mqtt': 1,
                'grabar_datos': 1,
                'n_muestras': 1,
                'protocolo': 30,
                'QPIGS2h_enviar': 0
                },
                
            
        },
        
        
        'SRNE': {
            'SRNE1': {
                    'usar': 0,
                    'dev': '/dev/ttyUSB0',
                    'baudrate': 9600,
                    'id_modbus': 1,
                    'tiempo_captura': 5
                },
            
            'comandos': {
                'ayuda': ['h','?','i', 'info',''],
                'lectura_multiple': {
                    'usar': 1,
                    'rangos': [[0x0100,0x0114],[0x0120,0x0120],[0xE005,0xE014]]
                },
                'SOC': {'reg': 0x0100},
                'Vbat': {'reg': 0x0101, 'dec': 1},
                'Iplaca': {'reg': 0x0102, 'dec': 1},
                'Temp0': {'reg': 0x0103, 'tipo': 'adaptar', 'adaptar': ["datos['Temp0']=int(format(d,'04x')[:2],16)"]},
                'Temp1': {'reg': 0x0103, 'tipo': 'adaptar', 'adaptar': ["datos['Temp1']=int(format(d,'04x')[2:],16)"]},
                'Vplaca': {'reg': 0x0107, 'dec': 1},
                'Ipanel': {'reg': 0x0108, 'dec': 2},
                'Wplaca': {'reg': 0x0109},
                'bat_min_today': {'reg': 0x010B, 'dec': 1},
                'bat_max_today': {'reg': 0x010C, 'dec': 1},
                'max_charging_power_today': {'reg': 0x010F},
                'max_discharging_power_today': {'reg': 0x0110},
                'charging_amp_hours_today': {'reg': 0x0111},
                'discharging_amp_hours_today': {'reg': 0x0112},
                'power_generation_today': {'reg': 0x0113},
                'power_consumption_today': {'reg': 0x0114},
                'charging_status': {'reg': 0x0120, 'tipo': 'adaptar', 'adaptar': [
                    "if d==0: datos['charging_status']='DEACTIVATED'",
                    "elif d==1: datos['charging_status']='ACTIVATED'",
                    "elif d==2: datos['charging_status']='BULK'",
                    "elif d==3: datos['charging_status']='EQUALIZE'",
                    "elif d==4: datos['charging_status']='ABSORTION'",
                    "elif d==5: datos['charging_status']='FLOAT'",
                    "elif d==6: datos['charging_status']='LIMITING'"
                ]},
                'over_voltage_threshold': {'reg': 0xE005, 'escritura': True, 'rango': [70, 170]},
                'charging_voltage_limit': {'reg': 0xE006, 'escritura': True, 'rango': [70, 170]},
                'equalizing_charging_voltage': {'reg': 0xE007, 'escritura': True, 'rango': [70, 170]},
                'boost_charging_voltage': {'reg': 0xE008, 'escritura': True, 'rango': [70, 170]},
                'floating_charging_voltage': {'reg': 0xE009, 'escritura': True, 'rango': [70, 170]},
                'boost_recovery_voltage': {'reg': 0xE00A, 'escritura': True, 'rango': [70, 170]},
                'over_discharge_recovery_voltage': {'reg': 0xE00B, 'escritura': True, 'rango': [70, 170]},
                'under_voltage_warning_level': {'reg': 0xE00C, 'escritura': True, 'rango': [70, 170]},
                'over_discharge_voltage': {'reg': 0xE00D, 'escritura': True, 'rango': [70, 170]},
                'discharging_limit_voltage': {'reg': 0xE00E, 'escritura': True, 'rango': [70, 170]},
                'over_discharge_time_delay': {'reg': 0xE010, 'escritura': True, 'rango': [0, 120]},
                'equalizing_charging_time': {'reg': 0xE011, 'escritura': True, 'rango': [0, 300]},
                'boost_charging_time': {'reg': 0xE012, 'escritura': True, 'rango': [10, 300]},
                'equalizing_charging_interval': {'reg': 0xE013, 'escritura': True, 'rango': [0, 255]},
                'temperature_compensation_factor': {'reg': 0xE014, 'escritura': True, 'rango': [0, 5]}
            }
        },
        
        'ANENJI': {
           'ANENJI1': {
                    'usar': 0,
                    'dev': '/dev/ttyUSB0', # puerto 
                    'id_modbus': 1,
                    'tiempo_captura': 5
            },
            'comandos': {
                'ayuda': ['h','?','i', 'info',''],
                'lectura_multiple': {
                    'usar': 1,
                    'rangos': [[201,234],[300,337],[406,420]]
                },
                'WM': {'reg': 201, 'tipo': 'adaptar', 'adaptar': [
                    "if d == 0: datos['WM'] = '0-Power On'",
                    "elif d == 1: datos['WM'] = '1-Standby'",
                    "elif d == 2: datos['WM'] = '2-Mains'",
                    "elif d == 3: datos['WM'] = '3-Off-Grid'",
                    "elif d == 4: datos['WM'] = '4-Bypass'",
                    "elif d == 5: datos['WM'] = '5-Charging'",
                    "elif d == 6: datos['WM'] = '6-Fault'"
                ]},
                'Vred': {'reg': 202, 'dec': 1},
                'Fred': {'reg': 203, 'dec': 2},
                'Wred': {'reg': 204},
                'Vred_aff': {'reg': 205, 'dec': 1},
                'Ired_aff': {'reg': 206, 'dec': 1},
                'Finv': {'reg': 207, 'dec': 2},
                'Winv': {'reg': 208, 'tipo': 's16'},
                'Winv_bat': {'reg': 209},
                'Vout': {'reg': 210, 'dec': 1},
                'Iout': {'reg': 211, 'dec': 1},
                'Fout': {'reg': 212, 'dec': 2},
                'Wout': {'reg': 213, 'tipo': 's16'},
                'VAout': {'reg': 214},
                'Vbat': {'reg': 215, 'dec': 1},
                'Ibat': {'reg': 216, 'dec': 1, 'tipo': 's16'},
                'Ibat1': {'reg': 232, 'dec': 1, 'tipo': 's16'},
                'Vplaca': {'reg': 219, 'dec': 1},
                'Iplaca': {'reg': 220, 'dec': 1},
                'Wplaca': {'reg': 223},
                'Wplaca_bat': {'reg': 224},
                'Carga%': {'reg': 225},
                'Temp_dc': {'reg': 226},
                'Temp_inv': {'reg': 227},
                'SOC': {'reg': 229},
                'I_carga_inv': {'reg': 233, 'dec': 1, 'tipo': 's16'},
                'I_carga_pla': {'reg': 234, 'dec': 1, 'tipo': 's16'},
                'Out_modo': {'reg': 300, 'rango': [0,4], 'tipo': 'adaptar', 'adaptar': [
                    "if d == 0: datos['Out_modo'] = '0-Single'",
                    "elif d == 1: datos['Out_modo'] = '1-Paralelo'",
                    "elif d == 2: datos['Out_modo'] = '2-Fase1'",
                    "elif d == 3: datos['Out_modo'] = '3-Fase2'",
                    "elif d == 4: datos['Out_modo'] = '4-Fase3'"
                ]},
                'Out_prio': {'reg': 301, 'tipo': 'adaptar', 'rango': [0,2], 'adaptar': [
                    "if d == 0: datos['Out_prio'] = '0-Util_PV_Bat'",
                    "elif d == 1: datos['Out_prio'] = '1-PV_Util_Bat'",
                    "elif d == 2: datos['Out_prio'] = '2-PV_Bat_Util'"
                ]},
                'Input_range': {'reg': 302, 'rango': [0,1], 'escritura': True, 'parametro': 3},
                'Buzzer_mode_range': {'reg': 303, 'rango': [0,2], 'escritura': True, 'parametro': 18},
                'LCD_light': {'reg': 305, 'rango': [0,1], 'escritura': True, 'parametro': 20},
                'LCD_return': {'reg': 306, 'rango': [0,1], 'escritura': True, 'parametro': 19},
                'Over_load_return': {'reg': 308, 'rango': [0,1], 'escritura': True, 'parametro': 6},
                'Over_Temp_return': {'reg': 309, 'rango': [0,1], 'escritura': True, 'parametro': 7},
                'Over_load_bypass': {'reg': 310, 'rango': [0,1], 'escritura': True, 'parametro': 6},
                'Vbat_max': {'reg': 323, 'dec': 1, 'rango': [55,66], 'escritura': True},
                'Vabs': {'reg': 324, 'dec': 1, 'rango': [48,62], 'escritura': True},
                'Vflot': {'reg': 325, 'dec': 1, 'rango': [48,62], 'escritura': True},
                'Voff_r_main': {'reg': 326, 'dec': 1, 'rango': [40,48], 'escritura': True},
                'Voff_main': {'reg': 327, 'dec': 1, 'rango': [40,48], 'escritura': True},
                'R328': {'reg': 328, 'rango': [0,10000], 'escritura': True},
                'Voff': {'reg': 329, 'dec': 1, 'rango': [40,48], 'escritura': True},
                'Tabs': {'reg': 330, 'rango': [0,900], 'escritura': True, 'parametro': 32},
                'Prioridad_carga': {'reg': 331, 'rango': [0,3], 'escritura': True, 'parametro': 16},
                'Icarga_max': {'reg': 332, 'dec': 1, 'rango': [2,80], 'escritura': True, 'parametro': 11},
                'Icarga_main': {'reg': 333, 'dec': 1, 'rango': [2,30], 'escritura': True, 'parametro': 2},
                'Vequ': {'reg': 334, 'dec': 1, 'rango': [48,62], 'escritura': True, 'parametro': 34},
                'Tequ': {'reg': 335, 'dec': 0, 'rango': [0,900], 'escritura': True, 'parametro': 35},
                'Tequ_timeout': {'reg': 336, 'dec': 0, 'rango': [0,900], 'escritura': True, 'parametro': 36},
                'Tequ_dias': {'reg': 337, 'dec': 0, 'rango': [0,90], 'escritura': True, 'parametro': 37},
                'Modo_On_Off': {'reg': 406, 'rango': [0,2], 'escritura': True},
                'Remote_Switch': {'reg': 420, 'rango': [0,1], 'escritura': True}
            }
        },
        
        # --- Sistemas de Monitorización de Baterías ---
        'DALY': {
            'activo': 0,
            'config': {
                't_muestra': 1,
                'puerto': "/dev/ttyUSB0",
                'grabar_datos': 1,
                'leer_soc': 1,
                'leer_temp': 0,
                'leer_ciclos': 1,
                'leer_V_Max_Min': 1,
                'n_muestras': 5,
                'Valor_error_max': 4.5,
                'Valor_error_min': 2.8
            }
        },
        
        'BMS_JK': {
            
            'JK1': {
                'usar': 0,
                'MAC': 'C8:47:80:01:D8:CC',
                'tiempo_captura': 5,
                'ciclos_grabacion': 3
            },
            'JK2': {
                'usar': 0,
                'MAC': 'C8:47:80:01:D9:0B',
                'tiempo_captura': 5,
                'ciclos_grabacion': 3
        
            }
        },
        
        'PYLONTECH': {
            'activo': 0,
            'config': {
                'puerto': '/dev/ttyUSB0',
                'baudrate': 115200,
                'timeout': 1,
                'n_baterias': 4
            }
        },
        
        # --- Sensores y Adquisición de Datos ---
        'ADS1115': {
            'activo': [0, 0],
            'dispositivos': [
                {
                    'nombre': 'ADS1',
                    'direccion': 72,
                    'variables': ['Vbat', 'Aux1', 'Vplaca', 'Aux2'],
                    'config': {
                        'tmuestra': 1,
                        'rate': [250, 250, 250, 250],
                        'bucles': [10, 5, 5, 5],
                        'gain': [2, 2, 2, 2],
                        'modo': [1, 1, 1, 1],
                        'res': [47.46, 47.46, 47.46, 47.46]
                    }
                },
                {
                    'nombre': 'ADS4', 
                    'direccion': 75,
                    'variables': ['Ibat', '', 'Iplaca', ''],
                    'config': {
                        'tmuestra': 1,
                        'rate': [250, 0, 250, 0],
                        'bucles': [5, 0, 5, 0],
                        'gain': [16, 0, 16, 0],
                        'modo': [3, 0, 3, 0],
                        'res': [100/0.075, 0, 100/0.075, 0]
                    }
                }
            ]
        },
        
        'MULTIPLEXOR': {
            'activo': 0,
            'config': {
                't_muestra': 5,
                'n_muestras': 4,
                'pin_ADS_mux1': "A2_2",
                'pin_ADS_mux2': 'A3_2',
                'captura_mux': "S",
                'gain_mux': 1,
                'r_mux': [47] * 32,
                'celdas_log_dif': 0.5
            }
        },
        
        'SDM120': {
            'activo': [0],
            'dispositivos': [
                {
                    'nombre': 'SDM120_1',
                    'puerto': "/dev/ttyUSB0",
                    't_muestra': 5,
                    'publicar_mqtt': 0,
                    'grabar_datos': 1,
                    'n_muestras': 1
                }
            ]
        },
        
        'SDM230': {
            'activo': [0],
            'dispositivos': [
                {
                    'nombre': 'SDM230_1',
                    'puerto': "/dev/ttyUSB0", 
                    't_muestra': 5
                }
            ]
        },
        
        # --- Equipos de Comunicación y Control ---
        'BROADLINK': {
            'activo': 0,
            'config': {
                'array_IP': ['192.168.1.234','192.168.1.235'],
                'array_reles': [271, 281]
            }
        },
        
        'TUYA': {
            'activo': 0,
            'config': {
                'tmuestra': 15,
                'SCAN': True
            },
            'reles': {
                801: {'Nombre': 'Rele 801', 'ID': 'XXXX1', 'KEY': 'YYYY1'},
                802: {'Nombre': 'Rele 802', 'ID': 'XXXX2', 'KEY': 'YYYY2', 'TABLA': False, 'CREAR_RELE': False}
            }
        },
        
        'ECOWITT': {
            'activo': 0,
            'config': {
                'APPLICATION_KEY': 'XXXXXXXXXXXXXXX',
                'API_KEY': 'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy',
                'MAC': 'ZZ:ZZ:ZZ:ZZ:ZZ:ZZ',
                't_muestra': 60
            }
        },
        
        # --- Otros Equipos ---
        'EVSE': {
            'activo': 0,
            'config': {
                'usar_diario2': 0,
                'SOC_cut_off': 35,
                'SOC_warning': 40,
                'SOC_cut_on': 70,
                'SOC_export': 84,
                'Voltage_cut_off': 50.0
            }
        },
        
        'DERIVA_DC': {
            'activo': 0,
            'config': {
                'baudrate': 9600,
                'parity': 'N',
                'puerto': '/dev/ttyACM0',
                'timeout': 1,
                'simular': 0
            }
        },
        
        'OLED': {
            'activo': True,
            'pantallas': {
                'OLED1': {
                    'tipo': 'ssd1306',
                    'i2c_direccion': 0x3C,
                    'salida': [0, 1, 2, 3, 4, 5]
                },
                'OLED2': {
                    'tipo': 'ssd1306', 
                    'i2c_direccion': 0x3D,
                    'salida': ['JK1', 'JK2']
                }
            },
            'pantallas_personalizadas': {
                'JK1': [
                    "draw.rectangle((0, 0, 127, 20), outline=255, fill=0)",
                    "draw.text((8, 0), 'JK1'+' - '+str(d_['BMS_JK1']['SOC'])+'%', font=font16, fill=255)",
                    "draw.rectangle((0, 20, 127, 63), outline=255, fill=0)",
                    "draw.text((4, 22), 'Vbat='+str(d_['BMS_JK1']['Vbat'])+'V' +' / '+'Ibat='+str(d_['BMS_JK1']['Ibat'])+'A', font=font, fill=255)",
                    "draw.text((4, 34), str(max(d_['BMS_JK1']['Vceldas']))+' - '+str(min(d_['BMS_JK1']['Vceldas']))+' = '+str(int((round((max(d_['BMS_JK1']['Vceldas']))-(min(d_['BMS_JK1']['Vceldas'])),3))*1000))+'mV', font=font, fill=255)",
                    "draw.text((4, 46), 'AH = '+str(d_['BMS_JK1']['AH_p'])+' - '+str(d_['BMS_JK1']['AH_n'])+' = '+str((d_['BMS_JK1']['AH_p'])-(d_['BMS_JK1']['AH_n'])), font=font, fill=255)"
                ],
                'JK2': [
                    "draw.rectangle((0, 0, 127, 20), outline=255, fill=0)",
                    "draw.text((8, 0), 'JK2'+' - '+str(d_['BMS_JK2']['SOC'])+'%', font=font16, fill=255)",
                    "draw.rectangle((0, 20, 127, 63), outline=255, fill=0)",
                    "draw.text((4, 22), 'Vbat='+str(d_['BMS_JK2']['Vbat'])+'V' +' / '+'Ibat='+str(d_['BMS_JK2']['Ibat'])+'A', font=font, fill=255)",
                    "draw.text((4, 34), str(max(d_['BMS_JK2']['Vceldas']))+' - '+str(min(d_['BMS_JK2']['Vceldas']))+' = '+str(int((round((max(d_['BMS_JK2']['Vceldas']))-(min(d_['BMS_JK2']['Vceldas'])),3))*1000))+'mV', font=font, fill=255)",
                    "draw.text((4, 46), 'AH = '+str(d_['BMS_JK2']['AH_p'])+' - '+str(d_['BMS_JK2']['AH_n'])+' = '+str((d_['BMS_JK2']['AH_p'])-(d_['BMS_JK2']['AH_n'])), font=font, fill=255)"
                ]
            }
        }
    },
    
    # ====================================================================
    # 5.- SERVICIOS Y COMUNICACIONES
    # ====================================================================
    'SERVICIOS': {
       
       'base_datos': {
            'servidor': "localhost",
            'usuario': "rpi", 
            'clave': "fv",
            'basedatos': "control_solar",
            'grabar_datos_s': "False",
            't_muestra_max': 6,
            'limpieza_tablas': [
                ['datos_s', 10],
                ['datos', 366],
                ['reles_grab', 366],
                ['log', 30],
                ['datos_aux', 366],
                ['datos_celdas', 366],
                ['hibrido', 366],
                ['victron', 366],
                ['bmv', 366],
                ['srne', 366]
            ],
            'tablas_d': [
                ['reles_segundos_on', 366]
            ]
        },        
        
        'MQTT': {
            'activo': 1,
            'config': {
                'broker': "localhost",
                'puerto': 1883,
                'usuario': "rpi",
                'clave': "fv"
            },
            'suscripciones': {
                'activo': 0,
                'topics': []
            },
            'publicaciones': {
                'activo': 0,
                'topic_raiz': "PVControl/",
                'topics': [
                    ["Wplaca", "Wplaca"],
                    ["Vbat", "Vbat"],
                    ["Ibat", "Ibat", 10],
                    ["SOC", "SOC", 15],
                    ["DatosFV", "d_['FV']", 0]
                ]
            }
        },
        
        
        'PVOUTPUT': {
            'activo': 0,
            'config': {
                'api_key': "xxxxxxxx",
                'system_id': "1233455"
            }
        },
        
        'MOTION': {
            'activo': 0,
            'config': {
                'motion_telegram': 0,
                'motion_clarifai': 0,
                'api_key': 'xxxxxxxxxxxx',
                'workflow_id': 'yyyyyyyy',
                'horario_alarma': {
                    1: '111111110000000000000000',
                    2: '111111110000000000000000',
                    3: '111111110000000000000000',
                    4: '111111110000000000000000',
                    5: '111111110000000000000000',
                    6: '111111111000000000000000',
                    7: '111111111000000000000000'
                }
            }
        },
        
        'AEMET': {
            'activo': 0,
            'config': {
                'localidad': '',
                'variables': 'ctl',
                'Cielo_Kwh': {
                    "Despejado": {"06-12": 0, "12-18": 0},
                    "Poco nuboso": {"06-12": 0, "12-18": 0},
                    "Nubes altas": {"06-12": 0, "12-18": 0},
                    "Intervalos nubosos": {"06-12": 0, "12-18": 0},
                    "Nuboso": {"06-12": 0, "12-18": 0},
                    "Muy Nuboso": {"06-12": 0, "12-18": 0},
                    "Cubierto": {"06-12": 0, "12-18": 0}
                }
            }
        },
        
        'IRRADIACION': {
            'activo': 0,
            'config': {
                'url': "https://www.tutiempo.net/radiacion-solar/titulcia.html"
            }
        },
        
        'simulacion': {'simular': 0, 'simular_reles': 0 },        
    },
    
    # ====================================================================
    # 6.- AUTOMATIZACIÓN Y PROGRAMACIÓN
    # ====================================================================
    'TELEGRAM': {
        'activo': 0,
        'config': {
            'TOKEN': 'XXXXXX:YYYYYYYYYY......',
            'usuarios_autorizados': [111111, 22222],
            'cid_alarma': 1111111,
            'msg_periodico': 0
        },
        'mensajes': {
            'region_captura_pantalla': [0, 0, 0, 0, 0],
            'acciones_mouse': [''],
            'unicode_reles': [('ñññ###','\U0001F6A6'),('luz','\U0001F526'),('cale','\U0001F525')],
            'lineas_mensaje': [
                "\U0001F50B <b><u>Batería</u></b>: (<code>{d_['FV']['Mod_bat']}</code>)",
                "     SOC: <b>{d_['FV']['SOC']:.1f}</b>%     \U000024CB <b>{d_['FV']['Vbat']:.1f}</b>V     \U000024BE <b>{d_['FV']['Ibat']:.1f}</b>A",
                "\U0001F31E <b><u>Placas</u></b>:",
                "     \U000024C5 <b>{d_['FV']['Wplaca']:.0f}</b>W     \U000024BE <b>{d_['FV']['Iplaca']:.1f}</b>A     \U000024CB <b>{d_['FV']['Vplaca']:.0f}</b>V",
                "\U0001F4A1 <b><u>Consumo</u></b>:",
                "     \U000024C5 <b>{d_['FV']['Wconsumo']:.0f}</b>W     \U000024BE <b>{d_['FV']['Iplaca']-d_['FV']['Ibat']:.1f}</b>A     PWM: <b>{d_['FV']['PWM']:.0f}</b>",
                "\U00002753 <b><u>Relés</u></b>:",
                "<b>{L_reles_unicode}</b>",
                "\U0001F4C6 <b><u>Diario (KWh)</u></b>:",
                "     \U0001F31E <b>{d_['FV']['Wh_placa']/1000:.1f}</b> \U0001F50B <i>{d_['FV']['Whp_bat']/1000:.1f}-{d_['FV']['Whn_bat']/1000:.1f}</i> = <b>{(d_['FV']['Whp_bat']-d_['FV']['Whn_bat'])/1000:.1f}</b> \U0001F4A1 <b>{(d_['FV']['Wh_consumo'])/1000:.1f}</b>",
                "\U0001F321 <b><u>Temperaturas (ºC)</u></b>:",
                "     Bat: <b>{d_['FV']['Temp']}</b> / CPU: <b>{d_['TEMP']['Temp_cpu']:.1f}</b>",
                "\U0001F4BB <b><u>Conexión (IP)</u></b>:",
                "     \U0001F3E0 {L_ip_local}  \U0001F30D <span class='tg-spoiler'>{L_ip}</span>"
            ],
            'comandos_personalizados': [
                '#i : Informacion'
            ],
            'botones_visibles_una_vez': False
        }
    },


    'CRONTAB': {
            'mensaje_telegram': {
                'activo': 1,
                'comando': ['python', 'fvbot_msg.py'],
                'horas': ['01:00','02:00','03:00','04:00','05:00','06:00',
                         '07:00','08:00','09:00','10:00','11:00','12:00',
                         '13:00','14:00','15:00','16:00','17:00','18:00',
                         '19:00','20:00','21:00','22:00','23:00','23:59'],
                'periodo': 0,
                'log': 0
            },
            'comprimir_bd': {
                'activo': 1,
                'comando': ['python', 'fv_comprimir_BD.py'],
                'horas': [],
                'periodo': 10,
                'log': 0
            },
            'gestion_bd': {
                'activo': 1,
                'comando': ['python', 'fv_gestionbd.py','-v','-c','-b'],
                'horas': ['05:32'],
                'periodo': 0,
                'log': 1
            },
            'diario': {
                'activo': 1,
                'comando': ['python', 'diario.py'],
                'horas': [],
                'periodo': 30,
                'log': 0
            },
            'diario_back': {
                'activo': 1,
                'comando': ['python', 'diario.py','-ini0', '-fin7'],
                'horas': ['00:10'],
                'periodo': 0,
                'log': 0
            },
            'SOH': {
                'activo': 1,
                'comando': ['python', 'fv_soh.py'],
                'horas': ['01:03'],
                'periodo': 0,
                'log': 0
            },
            'fv_temp': {
                'activo': 1,
                'comando': ['sudo','systemctl','restart', 'fv_temp'],
                'horas': [],
                'periodo': 60,
                'log': 0
            },
            'fv_oled': {
                'activo': 1,
                'comando': ['sudo','systemctl','restart', 'fv_oled'],
                'horas': [],
                'periodo': 60,
                'log': 0
            },
            'fvbot': {
                'activo': 0,
                'comando': ['sudo','systemctl','restart', 'fvbot'],
                'horas': [],
                'periodo': 60,
                'log': 0
            },
            'AEMET': {
                'activo': 0,
                'comando': ['python', 'aemet.py'],
                'horas': ['01:03'],
                'periodo': 0,
                'log': 0
            },
            'IRRADIACION': {
                'activo': 0,
                'comando': ['python', 'fv_irradiacion.py'],
                'horas': ['00:30','08:03','20:12'],
                'periodo': 0,
                'log': 1
            },
            'PVOutput': {
                'activo': 0,
                'comando': ['python', 'pvoutput_live.py'],
                'horas': [],
                'periodo': 5,
                'log': 0
            },
            'Hibrido_Inicio_dia': {
                'activo': 0,
                'comando': ['python', 'fvbot_msg_hibrido.py','PCVV29.2','PCVV29.2','PBFT29.2'],
                'horas': ['09:10'],
                'periodo': 0,
                'log': 1
            }
        },
    

    'RELES_PERSONALIZADOS': {},
    
}

    

# ====================================================================
# VARIABLES DE COMPATIBILIDAD (para scripts existentes)
# ====================================================================
# Estas variables mantienen la compatibilidad con scripts que no usan CONFIG

# Configuración general
simular = CONFIG['GENERAL']['simulacion']['simular']
simular_reles = CONFIG['GENERAL']['simulacion']['simular_reles']

# Base de datos
servidor = CONFIG['GENERAL']['base_datos']['servidor']
usuario = CONFIG['GENERAL']['base_datos']['usuario']
clave = CONFIG['GENERAL']['base_datos']['clave']
basedatos = CONFIG['GENERAL']['base_datos']['basedatos']
grabar_datos_s = CONFIG['GENERAL']['base_datos']['grabar_datos_s']
t_muestra_max = CONFIG['GENERAL']['base_datos']['t_muestra_max']
limpieza_tablas = CONFIG['GENERAL']['base_datos']['limpieza_tablas']
tablas_d = CONFIG['GENERAL']['base_datos']['tablas_d']

# Sensores
sensores = CONFIG['SENSORES']['definiciones']
Graficas_Aux = CONFIG['SENSORES']['graficas_auxiliares']

# Batería
AH = CONFIG['BATERIA']['AH']
CP = CONFIG['BATERIA']['CP']
EC = CONFIG['BATERIA']['EC']
vsis = CONFIG['BATERIA']['vsis']
vflotacion = CONFIG['BATERIA']['vflotacion']
SOC_incremento_rapido_condicion = CONFIG['BATERIA']['SOC_incremento_rapido_condicion']
SOC_incremento_rapido_accion = CONFIG['BATERIA']['SOC_incremento_rapido_accion']
Bulk_Absorcion_accion = CONFIG['BATERIA']['Bulk_Absorcion_accion']
Absorcion_Flotacion_accion = CONFIG['BATERIA']['Absorcion_Flotacion_accion']
Flotacion_Bulk_accion = CONFIG['BATERIA']['Flotacion_Bulk_accion']
Tflot_bulk_tiempo = CONFIG['BATERIA']['Tflot_bulk_tiempo']

# MQTT
mqtt_broker = CONFIG['SERVICIOS']['MQTT']['config']['broker']
mqtt_puerto = CONFIG['SERVICIOS']['MQTT']['config']['puerto']
mqtt_usuario = CONFIG['SERVICIOS']['MQTT']['config']['usuario']
mqtt_clave = CONFIG['SERVICIOS']['MQTT']['config']['clave']
usar_mqtt_suscripciones = CONFIG['SERVICIOS']['MQTT']['suscripciones']['activo']
mqtt_suscripciones = CONFIG['SERVICIOS']['MQTT']['suscripciones']['topics']
usar_mqtt_publicaciones = CONFIG['SERVICIOS']['MQTT']['publicaciones']['activo']
mqtt_topic_raiz = CONFIG['SERVICIOS']['MQTT']['publicaciones']['topic_raiz']
mqtt_publicaciones = CONFIG['SERVICIOS']['MQTT']['publicaciones']['topics']

# Reles
reles_personalizados = CONFIG['AUTOMATIZACION']['RELES_PERSONALIZADOS']

# ADS1115
usar_ADS = CONFIG['EQUIPOS']['ADS1115']['activo']
nombre_ADS = [dev['nombre'] for dev in CONFIG['EQUIPOS']['ADS1115']['dispositivos']]
direccion_ADS = [dev['direccion'] for dev in CONFIG['EQUIPOS']['ADS1115']['dispositivos']]
var_ADS = [dev['variables'] for dev in CONFIG['EQUIPOS']['ADS1115']['dispositivos']]
tmuestra_ADS = [dev['config']['tmuestra'] for dev in CONFIG['EQUIPOS']['ADS1115']['dispositivos']]
rate_ADS = [dev['config']['rate'] for dev in CONFIG['EQUIPOS']['ADS1115']['dispositivos']]
bucles_ADS = [dev['config']['bucles'] for dev in CONFIG['EQUIPOS']['ADS1115']['dispositivos']]
gain_ADS = [dev['config']['gain'] for dev in CONFIG['EQUIPOS']['ADS1115']['dispositivos']]
modo_ADS = [dev['config']['modo'] for dev in CONFIG['EQUIPOS']['ADS1115']['dispositivos']]
res_ADS = [dev['config']['res'] for dev in CONFIG['EQUIPOS']['ADS1115']['dispositivos']]

# Multiplexor
usar_mux = CONFIG['EQUIPOS']['MULTIPLEXOR']['activo']
t_muestra_mux = CONFIG['EQUIPOS']['MULTIPLEXOR']['config']['t_muestra']
n_muestras_mux = CONFIG['EQUIPOS']['MULTIPLEXOR']['config']['n_muestras']
pin_ADS_mux1 = CONFIG['EQUIPOS']['MULTIPLEXOR']['config']['pin_ADS_mux1']
pin_ADS_mux2 = CONFIG['EQUIPOS']['MULTIPLEXOR']['config']['pin_ADS_mux2']
captura_mux = CONFIG['EQUIPOS']['MULTIPLEXOR']['config']['captura_mux']
gain_mux = CONFIG['EQUIPOS']['MULTIPLEXOR']['config']['gain_mux']
r_mux = CONFIG['EQUIPOS']['MULTIPLEXOR']['config']['r_mux']
celdas_log_dif = CONFIG['EQUIPOS']['MULTIPLEXOR']['config']['celdas_log_dif']

# Híbrido
usar_hibrido = CONFIG['EQUIPOS']['HIBRIDO']['activo']
dev_hibrido = [dev['puerto'] for dev in CONFIG['EQUIPOS']['HIBRIDO']['dispositivos']]
usar_crc = [dev['usar_crc'] for dev in CONFIG['EQUIPOS']['HIBRIDO']['dispositivos']]
t_muestra_hibrido = [dev['t_muestra'] for dev in CONFIG['EQUIPOS']['HIBRIDO']['dispositivos']]
publicar_hibrido_mqtt = [dev['publicar_mqtt'] for dev in CONFIG['EQUIPOS']['HIBRIDO']['dispositivos']]
grabar_datos_hibrido = [dev['grabar_datos'] for dev in CONFIG['EQUIPOS']['HIBRIDO']['dispositivos']]
n_muestras_hibrido = [dev['n_muestras'] for dev in CONFIG['EQUIPOS']['HIBRIDO']['dispositivos']]
protocolo_hibrido = [dev['protocolo'] for dev in CONFIG['EQUIPOS']['HIBRIDO']['dispositivos']]
QPIGS2h_enviar = [dev['QPIGS2h_enviar'] for dev in CONFIG['EQUIPOS']['HIBRIDO']['dispositivos']]


# Daly
usar_daly = CONFIG['EQUIPOS']['DALY']['activo']
t_muestra_daly = CONFIG['EQUIPOS']['DALY']['config']['t_muestra']
grabar_datos_daly = CONFIG['EQUIPOS']['DALY']['config']['grabar_datos']
leer_soc_daly = CONFIG['EQUIPOS']['DALY']['config']['leer_soc']
leer_temp_daly = CONFIG['EQUIPOS']['DALY']['config']['leer_temp']
leer_ciclos_daly = CONFIG['EQUIPOS']['DALY']['config']['leer_ciclos']
leer_V_Max_Min_daly = CONFIG['EQUIPOS']['DALY']['config']['leer_V_Max_Min']
n_muestras_daly = CONFIG['EQUIPOS']['DALY']['config']['n_muestras']
Valor_error_max_daly = CONFIG['EQUIPOS']['DALY']['config']['Valor_error_max']
Valor_error_min_daly = CONFIG['EQUIPOS']['DALY']['config']['Valor_error_min']
dev_daly = CONFIG['EQUIPOS']['DALY']['config']['puerto']

# Victron
usar_victron = 1 if any(dev['usar'] for dev in CONFIG['EQUIPOS']['VICTRON']['VEDIRECT'].values()) else 0
dev_victron = next((dev['dev'] for dev in CONFIG['EQUIPOS']['VICTRON']['VEDIRECT'].values() if dev['usar']), "/dev/ttyUSB0")
VICTRON_VEDIRECT = CONFIG['EQUIPOS']['VICTRON']['VEDIRECT']
VICTRON_MK2 = CONFIG['EQUIPOS']['VICTRON']['MK2']
mqtt_broker_venus = CONFIG['EQUIPOS']['VICTRON']['config_mqtt_venus']['mqtt_broker_venus']
mqtt_puerto_venus = CONFIG['EQUIPOS']['VICTRON']['config_mqtt_venus']['mqtt_puerto_venus']
mqtt_usuario_venus = CONFIG['EQUIPOS']['VICTRON']['config_mqtt_venus']['mqtt_usuario_venus']
mqtt_clave_venus = CONFIG['EQUIPOS']['VICTRON']['config_mqtt_venus']['mqtt_clave_venus']
usar_mqtt_suscripciones_venus = CONFIG['EQUIPOS']['VICTRON']['config_mqtt_venus']['usar_mqtt_suscripciones_venus']
mqtt_suscripciones_venus = CONFIG['EQUIPOS']['VICTRON']['config_mqtt_venus']['mqtt_suscripciones_venus']
usar_mqtt_publicaciones_venus = CONFIG['EQUIPOS']['VICTRON']['config_mqtt_venus']['usar_mqtt_publicaciones_venus']
mqtt_publicaciones_venus = CONFIG['EQUIPOS']['VICTRON']['config_mqtt_venus']['mqtt_publicaciones_venus']

# MUST
usar_must = 0  # Configurar según necesidad
n_equipos_must = 0
dev_must = "/dev/ttyUSB0"
grabar_datos_must = 0
t_muestra_must = 1
iplaca_must_max = 99
iplaca_must_min = 0

# BMV
usar_bmv = 0
dev_bmv = "/dev/serial0"
grabar_datos_bmv = 0
n_muestra_bmv = 5

# SMA
usar_SI = 0
usar_SB1 = 0
usar_SB2 = 0
usar_smameter = 0
IP_SI = "192.168.0.24"
IP_SB1 = "192.168.1.154"
IP_SB2 = "192.168.0.252"
t_muestra_SB1 = 5
t_muestra_SB2 = 5

# Fronius
usar_fronius = [0]
usar_meter_fronius = [0]
IP_FRONIUS = ["192.168.0.24"]
t_muestra_fronius = [5]

# Huawei
usar_huawei = 0
IP_HUAWEI = "192.168.200.1"
puerto_huawei = 6607
t_muestra_huawei = 5

# Goodwe
usar_goodwe = 0
IP_GOODWE = "192.168.0.100"
t_muestra_goodwe = 5
usar_batgoodwe = 0

# SRNE
SRNE = {
    'SRNE1': CONFIG['EQUIPOS']['SRNE']['dispositivos']['SRNE1'],
    'COMANDOS': CONFIG['EQUIPOS']['SRNE']['comandos']
}

# SDM120C
usar_sdm120c = CONFIG['EQUIPOS']['SDM120']['activo']
dev_sdm120c = [dev['puerto'] for dev in CONFIG['EQUIPOS']['SDM120']['dispositivos']]
t_muestra_sdm120c = [dev['t_muestra'] for dev in CONFIG['EQUIPOS']['SDM120']['dispositivos']]
publicar_sdm120c_mqtt = [dev['publicar_mqtt'] for dev in CONFIG['EQUIPOS']['SDM120']['dispositivos']]
grabar_datos_sdm120c = [dev['grabar_datos'] for dev in CONFIG['EQUIPOS']['SDM120']['dispositivos']]
n_muestras_sdm120c = [dev['n_muestras'] for dev in CONFIG['EQUIPOS']['SDM120']['dispositivos']]

# SDM230M
usar_sdm230m = CONFIG['EQUIPOS']['SDM230']['activo']
dev_sdm230m = [dev['puerto'] for dev in CONFIG['EQUIPOS']['SDM230']['dispositivos']]
t_muestra_sdm230m = [dev['t_muestra'] for dev in CONFIG['EQUIPOS']['SDM230']['dispositivos']]

# Eastron
usar_eastron = 0
dev_eastron = ""

# DEYE
usar_deye = [0, 0]
nombre_deye = ['DEYE', 'DEYE1']
dev_deye = ["/dev/ttyUSB0", "192.168.0.195"]
n_serie_dongle = [0, 11111111]
mb_slave_id = [0, 1]
t_muestra_deye = [5, 5]

# DiY BMS
usar_diybms = 0

# Pylontech Consola
usar_pylontech_consola = CONFIG['EQUIPOS']['PYLONTECH']['activo']
baudrate_pylontech_consola = CONFIG['EQUIPOS']['PYLONTECH']['config']['baudrate']
port_pylontech_consola = CONFIG['EQUIPOS']['PYLONTECH']['config']['puerto']
timeout_pylontech_consola = CONFIG['EQUIPOS']['PYLONTECH']['config']['timeout']
n_pylontech = CONFIG['EQUIPOS']['PYLONTECH']['config']['n_baterias']

# EVSE
usar_evse = CONFIG['EQUIPOS']['EVSE']['activo']
usar_diario2 = CONFIG['EQUIPOS']['EVSE']['config']['usar_diario2']
SOC_cut_off = CONFIG['EQUIPOS']['EVSE']['config']['SOC_cut_off']
SOC_warning = CONFIG['EQUIPOS']['EVSE']['config']['SOC_warning']
SOC_cut_on = CONFIG['EQUIPOS']['EVSE']['config']['SOC_cut_on']
SOC_export = CONFIG['EQUIPOS']['EVSE']['config']['SOC_export']
Voltage_cut_off = CONFIG['EQUIPOS']['EVSE']['config']['Voltage_cut_off']

# Broadlink
array_IP = CONFIG['EQUIPOS']['BROADLINK']['config']['array_IP']
array_reles = CONFIG['EQUIPOS']['BROADLINK']['config']['array_reles']

# OLED
OLED = {
    'OLED1': CONFIG['EQUIPOS']['OLED']['pantallas']['OLED1'],
    'OLED2': CONFIG['EQUIPOS']['OLED']['pantallas']['OLED2'],
    'PANTALLAS': CONFIG['EQUIPOS']['OLED']['pantallas_personalizadas']
}

# Deriva DC
usar_deriva_dc = CONFIG['EQUIPOS']['DERIVA_DC']['activo']
baudrate_deriva_dc = CONFIG['EQUIPOS']['DERIVA_DC']['config']['baudrate']
parity_deriva_dc = CONFIG['EQUIPOS']['DERIVA_DC']['config']['parity']
port_deriva_dc = CONFIG['EQUIPOS']['DERIVA_DC']['config']['puerto']
timeout_deriva_dc = CONFIG['EQUIPOS']['DERIVA_DC']['config']['timeout']
simular_deriva_dc = CONFIG['EQUIPOS']['DERIVA_DC']['config']['simular']

# Sofar
usar_sofar = [0, 0]
dir_modbus_sofar = [1, 2]
t_muestra_sofar = [5, 5]
n_muestras_sofar = [1, 1]
dev_sofar = ["/dev/ttyUSB0", "/dev/ttyUSB0"]

# Pylontech CAN
usar_pylontech = 0
dbcfile = "/home/pi/PVControl+/pylontech_US2000B_Plus_PVControl.dbc"
caninterface = "can0"
id_equipo = 'PYLON'

# BMS JK
BMS_JK = CONFIG['EQUIPOS']['BMS_JK']['dispositivos']

# BMS JK RS485
BMS_JK_RS485 = {
    'JK1': {'usar': 0, 'dev': '/dev/ttyUSB0', 'tiempo_captura': 5, 'ciclos_grabacion': 3},
    'JK2': {'usar': 0, 'dev': '/dev/ttyUSB1', 'tiempo_captura': 5, 'ciclos_grabacion': 3},
    'COMANDOS': {
        0x79: {'Captura': True, 'Nombre': 'Vceldas', 'Nbytes': 99, 'Estructura': {'Nbytes': 1, 'Nceldas': 1, 'Vcelda': 2}},
        0x80: {'Captura': True, 'Nombre': 'Temp_tube', 'Nbytes': 2, 'Adaptar': 'x if x<100 else 100-x'},
        # ... resto de comandos JK RS485
    }
}

# MPPT EASUN
MPPT_EASUN = {
    'MPPT1': {'usar': 0, 'dev': '/dev/ttyUSB0', 'id_modbus': 1, 'tiempo_captura': 5},
    'MPPT2': {'usar': 0, 'dev': '/dev/ttyUSB0', 'id_modbus': 2, 'tiempo_captura': 5},
    'COMANDOS': {
        'ayuda': ['h','?','i', 'info',''],
        'lectura_multiple': {'usar': 1, 'rangos': [[0x102,0x10D],[0x204,0x20C]]},
        'Vbat': {'reg': 0x102, 'dec': 1},
        'Ibat': {'reg': 0x103, 'dec': 2, 'tipo': 's16'},
        # ... resto de comandos EASUN
    }
}

# ANENJI 11Kw
ANENJI11 = {
    'ANENJI11': {'usar': 0, 'dev': '/dev/ttyUSB0', 'id_modbus': 1, 'tiempo_captura': 5},
    'ANENJI12': {'usar': 0, 'dev': '/dev/ttyUSB1', 'id_modbus': 1, 'tiempo_captura': 3},
    'COMANDOS': {
        'ayuda': ['h','?','i', 'info',''],
        'lectura_multiple': {'usar': 1, 'rangos': [[201,290],[301,391],[600,650],[702,702]]},
        'WM': {'reg': 201},
        'Fred': {'reg': 203, 'dec': 2},
        # ... resto de comandos ANENJI11
    }
}

# EPEVER
EPEVER = {
    'EPEVER1': {'usar': 0, 'dev': '/dev/ttyACM0', 'id_modbus': 1, 'baudrate': 115200, 'tiempo_captura': 5},
    'EPEVER2': {'usar': 0, 'dev': '/dev/ttyACM1', 'id_modbus': 1, 'baudrate': 115200, 'tiempo_captura': 3},
    'COMANDOS': {
        'ayuda': ['h','?','i', 'info',''],
        'lectura_multiple': {'usar': 0, 'rangos': [], 'rangos_input': []},
        'Vplaca': {'reg': 0x3100, 'dec': 2, 'fc': 4},
        'Wplaca': {'reg': 0x3102, 'dec': 2, 'fc': 4},
        # ... resto de comandos EPEVER
    }
}

# GROWATT
GROWATT = {
    'GROWATT1': {'usar': 0, 'dev': '/dev/ttyUSB0', 'id_modbus': 1, 'tiempo_captura': 5},
    'GROWATT2': {'usar': 0, 'dev': '/dev/ttyUSB1', 'id_modbus': 1, 'tiempo_captura': 3},
    'COMANDOS': {
        'ayuda': ['h','?','i', 'info',''],
        'lectura_multiple': {'usar': 1, 'rangos': [[2,10],[35,56],[3045,3097]]},
        'Pv1': {'reg': 3, 'dec': 1, 'fc': 4},
        'Pv1a': {'reg': 4, 'dec': 1, 'fc': 4},
        # ... resto de comandos GROWATT
    }
}

# POWMR
POWMR = {
    'POWMR1': {'usar': 0, 'dev': '/dev/ttyUSB0', 'baudrate': 2400, 'id_modbus': 5, 'tiempo_captura': 5},
    'POWMR2': {'usar': 0, 'dev': '/dev/ttyUSB0', 'id_modbus': 5, 'tiempo_captura': 5},
    'COMANDOS': {
        'ayuda': ['h','?','i', 'info',''],
        'lectura_multiple': {'usar': 1, 'rangos': [[4501,4564]]},
        'Sprio': {'reg': 4501},
        'Vac': {'reg': 4502, 'dec': 1},
        # ... resto de comandos POWMR
    }
}

# ECOWITT
ECOWITT = {
    'ECOWITT': CONFIG['EQUIPOS']['ECOWITT']['config']
}

# TUYA
TUYA = {
    'usar': CONFIG['EQUIPOS']['TUYA']['activo'],
    'tmuestra': CONFIG['EQUIPOS']['TUYA']['config']['tmuestra'],
    'SCAN': CONFIG['EQUIPOS']['TUYA']['config']['SCAN'],
    'RELES': CONFIG['EQUIPOS']['TUYA']['reles']
}

# Telegram
usar_telegram = CONFIG['SERVICIOS']['TELEGRAM']['activo']
TOKEN = CONFIG['SERVICIOS']['TELEGRAM']['config']['TOKEN']
Aut = CONFIG['SERVICIOS']['TELEGRAM']['config']['usuarios_autorizados']
cid_alarma = CONFIG['SERVICIOS']['TELEGRAM']['config']['cid_alarma']
msg_periodico_telegram = CONFIG['SERVICIOS']['TELEGRAM']['config']['msg_periodico']
region_captura_pantalla = CONFIG['SERVICIOS']['TELEGRAM']['mensajes']['region_captura_pantalla']
acciones_mouse = CONFIG['SERVICIOS']['TELEGRAM']['mensajes']['acciones_mouse']
unicode_reles_telegram = CONFIG['SERVICIOS']['TELEGRAM']['mensajes']['unicode_reles']
msg_telegram = CONFIG['SERVICIOS']['TELEGRAM']['mensajes']['lineas_mensaje']
cmd_telegram = CONFIG['SERVICIOS']['TELEGRAM']['mensajes']['comandos_personalizados']
botones_visibles_una_vez = CONFIG['SERVICIOS']['TELEGRAM']['mensajes']['botones_visibles_una_vez']

# PVOutput
usar_pvoutput = CONFIG['SERVICIOS']['PVOUTPUT']['activo']
pvoutput_key = CONFIG['SERVICIOS']['PVOUTPUT']['config']['api_key']
pvoutput_id = CONFIG['SERVICIOS']['PVOUTPUT']['config']['system_id']

# Motion
usar_motioneye = CONFIG['SERVICIOS']['MOTION']['activo']
motion_telegram = CONFIG['SERVICIOS']['MOTION']['config']['motion_telegram']
motion_clarifai = CONFIG['SERVICIOS']['MOTION']['config']['motion_clarifai']
api_key = CONFIG['SERVICIOS']['MOTION']['config']['api_key']
workflow_id = CONFIG['SERVICIOS']['MOTION']['config']['workflow_id']
horario_alarma = CONFIG['SERVICIOS']['MOTION']['config']['horario_alarma']

# AEMET
localidad = CONFIG['SERVICIOS']['AEMET']['config']['localidad']
variables = CONFIG['SERVICIOS']['AEMET']['config']['variables']
Cielo_Kwh = CONFIG['SERVICIOS']['AEMET']['config']['Cielo_Kwh']

# Irradiacion
irradiacion = CONFIG['SERVICIOS']['IRRADIACION']['config']

# Crontab
crontab = CONFIG['AUTOMATIZACION']['CRONTAB']
