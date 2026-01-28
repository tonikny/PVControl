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


ANENJI = {
    'ANENJI1': {'usar':0,
                'dev': '/dev/ttyUSB0',
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
              'lectura_multiple': {'usar': 1, 'rangos':[[201,234],[300,337],[406,420]]},
              
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
              'Vred'      : {'reg':202, 'dec':1},     # Voltaje red AC entrada
              'Fred'      : {'reg':203, 'dec':2},     # Frecuencia red AC entrada
              'Wred'      : {'reg':204},              # W de red AC.... ver  signo ??
              'Vred_aff'  : {'reg':205, 'dec':1},     # Voltaje Affectivo red AC entrada
              'Ired_aff'  : {'reg':206, 'dec':1},     # Intensidad Affectiva red AC entrada
              'Finv'      : {'reg':207, 'dec':2},     # Frecuencia Hibrido
              'Winv'      : {'reg':208, 'tipo':'s16'},# W del inversor
              'Winv_bat'  : {'reg':209},              # Watios de AC entrada a bateria
              'Vout'      : {'reg':210, 'dec':1},     # Salida Voltaje efectivo
              'Iout'      : {'reg':211, 'dec':1},     # Salida Intensidad efectiva
              'Fout'      : {'reg':212, 'dec':2},     # Frecuencia Salida 
              'Wout'      : {'reg':213, 'tipo':'s16'},# W de salida
              'VAout'     : {'reg':214},              # VA de salida
              'Vbat'      : {'reg':215, 'dec':1},     # Voltaje baterias
              'Ibat'      : {'reg':216, 'dec':1,'tipo':'s16'},   # Intensidad baterias
              'Ibat1'     : {'reg':232, 'dec':1,'tipo':'s16'},   # Intensidad baterias ??
              'Vplaca'    : {'reg':219, 'dec':1},     # Voltaje Placas
              'Iplaca'    : {'reg':220, 'dec':1},     # Intensidad Placas
              'Wplaca'    : {'reg':223},              # Watios Placas
              'Wplaca_bat': {'reg':224},              # Watios Placas a baterias
              'Carga%'    : {'reg':225},              # % Carga%
              'Temp_dc'   : {'reg':226},              # Watios Placas
              'Temp_inv'  : {'reg':227},              # Watios Placas
              'SOC'       : {'reg':229},              # % SOC
              'I_carga_inv' : {'reg':233, 'dec':1,'tipo':'s16'}, # Intensidad carga Inverter
              'I_carga_pla' : {'reg':234, 'dec':1,'tipo':'s16'}, # Intensidad carga Placas
            
              'Out_modo' :  {'reg':300,
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
                          
              'Out_prio' : {'reg':301,
                             'tipo':'adaptar',
                             'rango':[0,2],
                             'adaptar':[
                                     "if d == 0: datos['Out_prio'] = '0-Util_PV_Bat'",
                                     "elif d == 1: datos['Out_prio'] = '1-PV_Util_Bat'",
                                     "elif d == 2: datos['Out_prio'] = '2-PV_Bat_Util'"
                                     ]
                            },
                            
              'Input_range': {'reg':302, 'rango':[0,1], 'escritura': True, 'parametro': 3},
              'Buzzer_mode_range': {'reg':303, 'rango':[0,2], 'escritura': True, 'parametro': 18},
              'LCD_light': {'reg':305, 'rango':[0,1], 'escritura': True, 'parametro': 20},
              'LCD_return': {'reg':306, 'rango':[0,1], 'escritura': True, 'parametro': 19},
              'Over_load_return': {'reg':308, 'rango':[0,1], 'escritura': True, 'parametro': 6},
              'Over_Temp_return': {'reg':309, 'rango':[0,1], 'escritura': True, 'parametro': 7},
              'Over_load_bypass': {'reg':310, 'rango':[0,1], 'escritura': True, 'parametro': 6},
              
              'Vbat_max'   : {'reg':323, 'dec': 1, 'rango':[55,66], 'escritura': True}, # rango??
              'Vabs'       : {'reg':324, 'dec': 1, 'rango':[48,62], 'escritura': True},
              'Vflot'      : {'reg':325, 'dec': 1, 'rango':[48,62], 'escritura': True},
              'Voff_r_main': {'reg':326, 'dec': 1, 'rango':[40,48], 'escritura': True},
              'Voff_main'  : {'reg':327, 'dec': 1, 'rango':[40,48], 'escritura': True},
              'R328'       : {'reg':328, 'rango':[0,10000], 'escritura': True},
              'Voff'       : {'reg':329, 'dec': 1, 'rango':[40,48], 'escritura': True},
              'Tabs'       : {'reg':330, 'rango':[0,900], 'escritura': True, 'parametro': 32},
              'Prioridad_carga' : {'reg':331, 'rango':[0,3], 'escritura': True, 'parametro': 16},
              'Icarga_max'      : {'reg':332, 'dec': 1, 'rango':[2,80], 'escritura': True, 'parametro': 11},
              'Icarga_main'     : {'reg':333, 'dec': 1, 'rango':[2,30], 'escritura': True, 'parametro': 2},
              'Vequ'            : {'reg':334, 'dec': 1, 'rango':[48,62], 'escritura': True, 'parametro': 34},
              'Tequ'            : {'reg':335, 'dec': 0, 'rango':[0,900], 'escritura': True, 'parametro': 35},
              'Tequ_timeout'    : {'reg':336, 'dec': 0, 'rango':[0,900], 'escritura': True, 'parametro': 36},
              'Tequ_dias'       : {'reg':337, 'dec': 0, 'rango':[0,90], 'escritura': True, 'parametro': 37},
              
              'Modo_On_Off'     : {'reg':406, 'rango':[0,2], 'escritura': True},
              'Remote_Switch'   : {'reg':420, 'rango':[0,1], 'escritura': True},
                            
            }
    }


# ########### FIN PARAMETRIZACION EQUIPO ####################
  


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'ANENJI'
servicio = 'fv_anenji'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


exec(open("/home/pi/PVControl+/fv_rs485.py").read(),globals())#cargo estructura programa de captura generica de RS485
