# -*- coding: utf-8 -*-

# Versión 2024-03-09
#

# ######## INICIO PARAMETRIZACION EQUIPO ####################
# 
# UN BLOQUE COMO ESTE SE DEBE INCLUIR EN Parametros_FV.py
#
# ¡¡¡¡ NO MODIFICAR ESTE FICHERO !!!!
#
# ###########################################################


ANENJI11 = {
    'ANENJI11': {'usar':0,
                'dev': '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_ERDQb11BS14-if00-port0',
                #'dev': '/dev/ttyUSB0',
                
                'id_modbus': 1,
                'tiempo_captura': 5,
          },
          
    'ANENJI2': {'usar':0,
                'dev': '/dev/ttyUSB1',
                'id_modbus': 1,
                'tiempo_captura': 3,
          },
          
    'COMANDOS':{
              'ayuda' : ['h','?','i', 'info',''],
              
              # permite la lectura multiple de los registros lo que acelera el tiempo de captura
              'lectura_multiple': {'usar': 1, 'rangos':[[201,290],[301,391],[600,650],[702,702]]},
              
              # reg: numero de registro
              # dec: numero de decimales..... si no se pone se considera = 0
              # rango: [min,max] ... si no se pone no se realiza chequeo de rango
              # tipo: u16= sin signo / s16= con signo ....por defecto= u16
              # adaptar= casos especificos de cada equipo que obliga a especificar como se interpreta (el dato en bruto esta en variabe "d")
              # offset: valor de offset ..... si no se pone se considera = 0
              # escritura: True implica que es posible escribir en el registro ....por defecto= False 
              # grabar: True implica que se guarda en el registro en BD / False: No graba ..... por defecto= True
              
            
              'WM'       :  {'reg':201,         # Working Mode
                             'tipo':'adaptar',
                             'adaptar':[
                                     "if d == 0: datos['WM'] = '0-Power On'",
                                     "elif d == 1: datos['WM'] = '1-Standby'",
                                     "elif d == 2: datos['WM'] = '2-Mains'",
                                     "elif d == 3: datos['WM'] = '3-Off-Grid'",
                                     "elif d == 4: datos['WM'] = '4-Bypass'",
                                     "elif d == 5: datos['WM'] = '5-Charging'",
                                     "elif d == 6: datos['WM'] = '6-Fault'",
                                     ]
                            },

              'Fred'      : {'reg':203, 'dec':2},     # Frecuencia red AC entrada
              'Wred'      : {'reg':204},              # W de red AC.... ver  signo ??
              'Winv_bat'  : {'reg':206},              # Watios de AC entrada a bateria
              'R_207'     : {'reg':207},              # Bits flujo de potencia
              
              'Wred1_208' : {'reg':208},              #
              'Finv'      : {'reg':227, 'dec':2},     # Frecuencia Hibrido
              'W_228'     : {'reg':228},              # Potencia Activa Inversor
              
              'I_carga_inv' : {'reg':230, 'dec':1,'tipo':'s16'}, # Intensidad carga Inverter
              'Temp_inv'  : {'reg':231},                         # Watios Placas
              
              #'Ibat1'     : {'reg':232},             # Reservado 70 bytes
              
              'Iout'      : {'reg':252, 'dec':1},     # Salida Intensidad efectiva
              'Fout'      : {'reg':253, 'dec':2},     # Frecuencia Salida 
              'Wout'      : {'reg':254, 'tipo':'s16'},# W de salida total
              'VAout'     : {'reg':255},              # VA de salida
              'Carga%'    : {'reg':256},                # % Carga%
              
              'Vbat'      : {'reg':277, 'dec':1},                # Voltaje baterias
              'Ibat'      : {'reg':278, 'dec':1,'tipo':'s16'},   # Intensidad baterias
              'Wbat'      : {'reg':279, 'tipo':'s16'},           # Watios baterias....signo ??
              
              'SOC'       : {'reg':280},              # % SOC
              'Temp_dc'   : {'reg':281},              # Watios Placas
              
              'Wplaca'    : {'reg':302},              # Watios Placas
              'Wplaca_bat': {'reg':303},              # Watios Placas a baterias
              'I_carga_pla' : {'reg':304, 'dec':1},   # Intensidad carga Placas
              'Temp_PV'    : {'reg':305},             # Watios Placas
              
              'W_326'      : {'reg':326},             # 'Long ... positivo: producción energía de la red / negativo: energía vertida a la red;
              
              'W_red_L1'      : {'reg':340, 'tipo':'s16'},   # Potencia activa red L1
                
              'Vred_aff'   : {'reg':342, 'dec':1},     # Voltaje Affectivo red AC entrada
              'Ired_aff'   : {'reg':343, 'dec':1},     # Intensidad Affectiva red AC entrada
              'Winv'       : {'reg':344, 'tipo':'s16'},# W del inversor L1
              
              'Vout'       : {'reg':346, 'dec':1},     # Salida Voltaje efectivo
              'W_salida_L1': {'reg':348},              # Potencia activa salida L1
              'Carga%_L1'  : {'reg':350},              # % Carga L1
              
              'Vplaca1'    : {'reg':351, 'dec':1},     # Voltaje Placas
              'Iplaca1'    : {'reg':352, 'dec':1},     # Intensidad Placas
              'Wplaca1'    : {'reg':353},              # Watios Placas
              
              'V_red_L2'   : {'reg':376},              # Voltaje red L2
              'W_red_L2'   : {'reg':378},              # Potencia activa red L2
              
              'Winv_L2'    : {'reg':382, 'tipo':'s16'},# W promedio del inversor L2
              'W_L2'       : {'reg':386},              # W promedio potencia salida L2
                      
              'Vplaca2'    : {'reg':389, 'dec':1},     # Voltaje Placas
              'Iplaca2'    : {'reg':390, 'dec':1},     # Intensidad Placas
              'Wplaca2'    : {'reg':391},              # Watios Placas
              
              'Out_modo' :  {'reg':600,
                             'rango':[0,4],
                             'tipo':'adaptar',
                             'adaptar':[
                                     "if d == 0: datos['Out_modo'] = '0-Single'",
                                     "elif d == 1: datos['Out_modo'] = '1-Paralelo'",
                                     "elif d == 2: datos['Out_modo'] = '2-Fase1'",
                                     "elif d == 3: datos['Out_modo'] = '3-Fase2'",
                                     "elif d == 4: datos['Out_modo'] = '4-Fase3'"
                                     ]
                            },
              
              'Out_prio' : {'reg':601,
                             'tipo':'adaptar',
                             'rango':[1,3],
                             'escritura': True,
                             'adaptar':[
                                     "if d == 0: datos['Out_prio'] = '0-???Util_PV_Bat'",
                                     "elif d == 1: datos['Out_prio'] = '1-SUB'",
                                     "elif d == 2: datos['Out_prio'] = '2-SBU'",
                                     "elif d == 3: datos['Out_prio'] = '3-SUF'"                                     
                                     ]
                            },
              'Tipo_Bat' : {'reg':630,
                             'tipo':'adaptar',
                             'rango':[0,8],
                             'escritura': True,
                             'adaptar':[
                                     "if d == 0: datos['Tipo_Bat'] = '0-AGM'",
                                     "elif d == 1: datos['Tipo_Bat'] = '1-FLD'",
                                     "elif d == 2: datos['Tipo_Bat'] = '2-USER'",
                                     "elif d == 4: datos['Tipo_Bat'] = '4-Li2'",
                                     "elif d == 6: datos['Tipo_Bat'] = '6-Li4'",
                                     "elif d == 8: datos['Tipo_Bat'] = '8-LiB'"                                     
                                     ]
                            },
              'Prioridad_carga' : {'reg':632,
                                   'tipo':'adaptar',
                                   'rango':[0,4],
                                   'escritura': True,
                                   'adaptar':[
                                     "if d == 1: datos['Prioridad_carga'] = '1-SOF'",
                                     "elif d == 2: datos['Prioridad_carga'] = '2-SNU'",
                                     "elif d == 3: datos['Prioridad_carga'] = '3-OSO'",
                                     "elif d == 4: datos['Prioridad_carga'] = '4-SOR'",
                                     "elif d == 0: datos['Prioridad_carga'] = '0 ??'"
                                     ]
                                  },
              
              'Vabs'           : {'reg':637, 'dec': 1, 'rango':[48,62], 'escritura': True},
              'Vflot'          : {'reg':638, 'dec': 1, 'rango':[48,62], 'escritura': True},
              'Tabs'           : {'reg':639, 'rango':[0,900], 'escritura': True, 'parametro': 32},
              'Icarga_max'     : {'reg':640, 'dec': 1, 'rango':[2,80], 'escritura': True, 'parametro': 11},
              'Icarga_main'    : {'reg':641, 'dec': 1, 'rango':[2,30], 'escritura': True, 'parametro': 2},
              
              'R643'           : {'reg':643, 'dec': 1, 'rango':[48,62], 'escritura': True},
              'R644'           : {'reg':644, 'dec': 1, 'rango':[48,62], 'escritura': True},
              'R645'           : {'reg':645, 'dec': 1, 'rango':[48,62], 'escritura': True},
              'R646'           : {'reg':646, 'dec': 1, 'rango':[48,62], 'escritura': True},
              

              'R_702'    : {'reg':702},              # Generación de energía en el día Kwh
              
              
    }

}

# ########### FIN PARAMETRIZACION EQUIPO ####################
  


# #################### Control Ejecucion Servicio ########################################
print('OK')
NEQUIPO = 'ANENJI11'
servicio = 'fv_anenji11kw'

control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"
print (control)
print (eval(NEQUIPO))

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


exec(open("/home/pi/PVControl+/fv_rs485.py").read(),globals())#cargo estructura programa de captura generica de RS485
