# -*- coding: utf-8 -*-

# Versión 2024-03-23
#

# ######## INICIO PARAMETRIZACION EQUIPO ####################
# 
# UN BLOQUE COMO ESTE SE DEBE INCLUIR EN Parametros_FV.py
#
# ¡¡¡¡ NO MODIFICAR ESTE FICHERO !!!!
#
# ###########################################################


EPEVER = {
    'EPEVER1': {'usar':0,
                'dev': '/dev/ttyACM0',
                'id_modbus': 1,
                'baudrate': 115200,
                'tiempo_captura': 5,
          },
          
    'EPEVER2': {'usar':0,
                'dev': '/dev/ttyACM1',
                'id_modbus': 1,
                'baudrate': 115200,
                'tiempo_captura': 3,
          },
          
    'COMANDOS':{
              'ayuda' : ['h','?','i', 'info',''],
              
              # permite la lectura multiple de los registros lo que acelera el tiempo de captura
              'lectura_multiple': {'usar': 0, 'rangos':[], 'rangos_input':[]},
              
              # reg: numero de registro
              # dec: numero de decimales..... si no se pone se considera = 0
              # rango: [min,max] ... si no se pone no se realiza chequeo de rango
              # tipo: u16= sin signo / s16= con signo ....por defecto= u16
              # adaptar= casos especificos de cada equipo que obliga a especificar como se interpreta (el dato en bruto esta en variabe "d")
              # offset: valor de offset ..... si no se pone se considera = 0
              # escritura: True implica que es posible escribir en el registro ....por defecto= False 
              # grabar: True implica que se guarda en el registro en BD / False: No graba ..... por defecto= True
              
              'Vplaca'    : {'reg':0x3100, 'dec':2, 'fc': 4},     # Voltaje Placas
              'Wplaca'    : {'reg':0x3102, 'dec':2, 'fc': 4},     # Watios Placas ...registro bajo
               
              'Vbat'      : {'reg':0x331A, 'dec':2, 'fc': 4},    # Voltaje baterias
              'Ibat'      : {'reg':0x331B, 'dec':2, 'fc': 4},   # Intensidad baterias
              
              
              'Bat_tipo'   : {'reg':0x9000,         # Tipo Bateria
                             'tipo':'adaptar',
                             'rango': [0,3],
                             'escritura': True,
                              
                             'adaptar':[
                                     "if   d == 0: datos['Bat_tipo'] = '0-User'",
                                     "elif d == 1: datos['Bat_tipo'] = '1-Sealed'",
                                     "elif d == 2: datos['Bat_tipo'] = '2-Gel'",
                                     "elif d == 3: datos['Bat_tipo'] = '3-Flooded'",
                                     ]
                            },
              
              
              'Bat_AH'     : {'reg':0x9001, 'dec': 0,  'escritura': True},
              'Bat_coef_temp'     : {'reg':0x9002, 'dec': 2, 'rango':[0,9], 'escritura': True},
              
              'Vbat_off_alto'     : {'reg':0x9003, 'dec': 2, 'escritura': True}, # Voltaje desconexion
              'Vbat_carga_off'    : {'reg':0x9004, 'dec': 2, 'escritura': True},
              'Vbat_reconectar'   : {'reg':0x9005, 'dec': 2, 'escritura': True},
              
              'Vequ'       : {'reg':0x9006, 'dec': 2, 'rango':[48,62], 'escritura': True},
              'Vabs'       : {'reg':0x9007, 'dec': 2, 'rango':[48,62], 'escritura': True},
              'Vflot'      : {'reg':0x9008, 'dec': 2, 'rango':[48,62], 'escritura': True},
              'Vabs_reconectar'    : {'reg':0x9009, 'dec': 2, 'rango':[48,62], 'escritura': True},
              
              'Tabs'       : {'reg':0x906C, 'dec': 0, 'rango':[0,600], 'escritura': True},
              
              
            }
    }



# ########### FIN PARAMETRIZACION EQUIPO ####################
  


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'EPEVER'
servicio = 'fv_epever'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


exec(open("/home/pi/PVControl+/fv_rs485.py").read(),globals())#cargo estructura programa de captura generica de RS485
