# -*- coding: utf-8 -*-

# Versión 2024-03-04
#

# ######## INICIO PARAMETRIZACION EQUIPO ####################
# 
# UN BLOQUE COMO ESTE SE DEBE INCLUIR EN Parametros_FV.py
#
# ¡¡¡¡ NO MODIFICAR ESTE FICHERO !!!!
#
# ###########################################################

MPPT_EASUN = {
    'MPPT1': {'usar':0,               # Poner a 1 para activar
              'dev': '/dev/ttyUSB0',  # Puerto de comunicaciones
              'id_modbus': 1,         # Identificador Modbus
              'tiempo_captura': 5,    # Tiempo en segundos entre cada captura
             },
             
    'MPPT2': {'usar':0,
              'dev': '/dev/ttyUSB0',
              'id_modbus': 2,
              'tiempo_captura': 5,
          },
          
          
    'COMANDOS': {
              'ayuda' : ['h','?','i', 'info',''],
              
              # permite la lectura multiple de los registros lo que acelera el tiempo de captura
              'lectura_multiple': {'usar': 1, 'rangos':[[0x102,0x10D],[0x204,0x20C]]},
              
              # reg: numero de registro
              # dec: numero de decimales..... si no se pone se considera = 0
              # rango: [min,max] ... si no se pone no se realiza chequeo de rango
              # tipo: u16= sin signo / s16= con signo ....por defecto= u16
              #       adaptar= casos especificos de cada equipo que obliga a especificar como se interpreta (el dato en bruto esta en variabe "d"
              # offset: valor de offset ..... si no se pone se considera = 0
              # escritura: True implica que es posible escribir en el registro ....por defecto= False 
              # grabar: True implica que se guarda en el registro en BD / False: No graba ..... por defecto= True
              
              'Vbat' : {'reg':0x102, 'dec':1}, 
              'Ibat' : {'reg':0x103, 'dec':2, 'tipo':'s16' },
              'Wbat' : {'reg':0x104, 'tipo':'s16' },
              
              'Temp' : {'reg':0x105,
                        'tipo':'adaptar',
                        'adaptar':[
                                  "x = d.to_bytes(length=2, byteorder='big')",
                                  "datos['Temp_reg'] = int.from_bytes(x[0:1], signed=True)",
                                  "datos['Temp_bat'] = int.from_bytes(x[1:2], signed=True)"
                                  ]
                            }, 
               
              'Vload' : {'reg':0x106, 'dec':1}, 
              'Iload' : {'reg':0x107, 'dec':2}, 
              'Wload' : {'reg':0x108}, 
              
              'Vplaca' : {'reg':0x109, 'dec':1}, 
              'Wplaca_max' : {'reg':0x10A}, 
              'Wh_placa' : {'reg':0x10B},
              'Wh_load' : {'reg':0x10C},
              
              'Estado' :  {'reg':0x10D,
                           'tipo':'adaptar',
                           'adaptar':[
                                     "x = d.to_bytes(length=2, byteorder='big')", # tabla 6 protocolo
                                     "datos['Estado_consumo'] = 'ON' if int.from_bytes(x[0:1])>0 else 'OFF'",
                                     "x = int.from_bytes(x[1:2])",
                                     "if x == 0: datos['Estado_regulador'] = 'NOCHE'",
                                     "elif x == 1: datos['Estado_regulador'] = 'ABIERTO'",
                                     "elif x == 2: datos['Estado_regulador'] = 'MPPT'",
                                     "elif x == 3: datos['Estado_regulador'] = 'EQUALIZACION'",
                                     "elif x == 4: datos['Estado_regulador'] = 'ABSORCION'",
                                     "elif x == 5: datos['Estado_regulador'] = 'FLOTACION'",
                                     "elif x == 6: datos['Estado_regulador'] = 'LIMITAR'"
                                     ]
                          }, 
              
              'Vequ': {'reg':0x204, 'dec': 1, 'rango':[7,17], 'escritura': True},
              'Vabs': {'reg':0x205, 'dec': 1, 'rango':[7,17], 'escritura': True},
              'Vflot': {'reg':0x206, 'dec': 1, 'rango':[7,17], 'escritura': True},
              'Vabs_r': {'reg':0x207, 'dec': 1, 'rango':[7,17], 'escritura': True},
              'Voff_r': {'reg':0x208, 'dec': 1, 'rango':[7,17], 'escritura': True},
              'Valarm': {'reg':0x209, 'dec': 1, 'rango':[7,17], 'escritura': True},
              'Voff': {'reg':0x20A, 'dec': 1, 'rango':[7,17], 'escritura': True},
              'Tequ': {'reg':0x20B, 'dec': 0, 'rango':[0,600], 'escritura': True, 'grabar':False},
              'Tabs': {'reg':0x20C, 'dec': 0, 'rango':[0,600], 'escritura': True},
               
            },
    }



# ########### FIN PARAMETRIZACION EQUIPO ####################
  


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'MPPT_EASUN'
servicio = 'fv_mppt_easun'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


exec(open("/home/pi/PVControl+/fv_rs485.py").read(),globals())#cargo estructura programa de captura generica de RS485
