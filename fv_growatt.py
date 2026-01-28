# -*- coding: utf-8 -*-

# Versión 2024-03-18
#

# ######## INICIO PARAMETRIZACION EQUIPO ####################
# 
# UN BLOQUE COMO ESTE SE DEBE INCLUIR EN Parametros_FV.py
#
# ¡¡¡¡ NO MODIFICAR ESTE FICHERO !!!!
#
# ###########################################################


GROWATT = {
    'GROWATT1': {'usar':0,
                'dev': '/dev/ttyUSB0',
                'id_modbus': 1,
                'tiempo_captura': 5,
          },
          
    'GROWATT2': {'usar':0,
                'dev': '/dev/ttyUSB1',
                'id_modbus': 1,
                'tiempo_captura': 3,
          },
          
    'COMANDOS':{
              'ayuda' : ['h','?','i', 'info',''],
              
              # permite la lectura multiple de los registros lo que acelera el tiempo de captura
              'lectura_multiple': {'usar': 1, 'rangos':[[2,10],[35,56],[3045,3097]]},
              
              # reg: numero de registro
              # dec: numero de decimales..... si no se pone se considera = 0
              # rango: [min,max] ... si no se pone no se realiza chequeo de rango
              # tipo: u16= sin signo / s16= con signo ....por defecto= u16
              # adaptar= casos especificos de cada equipo que obliga a especificar como se interpreta (el dato en bruto esta en variabe "d")
              # offset: valor de offset ..... si no se pone se considera = 0
              # escritura: True implica que es posible escribir en el registro ....por defecto= False 
              # grabar: True implica que se guarda en el registro en BD / False: No graba ..... por defecto= True
              # fc : codigo de funcion de Modbus ...por defecto 3 
              
              'Pv1'      : {'reg':3,  'dec':1, 'fc' : 4},                 # Voltaje  Pv1
              'Pv1a'     : {'reg':4,  'dec':1, 'fc' : 4},                 # Amperios Pv1
              'Pv1w'     : {'reg':6,  'dec':1, 'fc' : 4},                 # Power Pv1
              'Pv2'      : {'reg':7,  'dec':1, 'fc' : 4},                 # Voltaje Pv2
              'Pv2a'     : {'reg':8,  'dec':1, 'fc' : 4},                 # Amperios Pv2
              'Pv2w'     : {'reg':10, 'dec':1, 'fc' : 4},                 # Power Pv2
              'Ppv'      : {'reg':2,  'dec':1, 'fc' : 4},                 # watios total
              'Vac1'     : {'reg':38, 'dec':1, 'fc' : 4},                 # Voltaje red AC entrada
              'Fac'      : {'reg':37, 'dec':2, 'fc' : 4},                 # Frecuencia red AC entrada   
              'Temp1'    : {'reg':93, 'dec':1, 'fc' : 4},                 # Inverter temperature
              'Temp2'    : {'reg':94, 'dec':1, 'fc' : 4},                 # The inside Ipm in inverter temperature
              'Temp3'    : {'reg':95, 'dec':1, 'fc' : 4},                 # Boost temperature
              'Temp4'    : {'reg':3097, 'dec':1, 'fc' : 4},               # Communication broad temperature
              'Etoday'   : {'reg':53, 'dec':1, 'tipo': 'u32', 'fc' : 4},  # Energia Today High
              'Etoday'   : {'reg':54, 'dec':1, 'fc' : 4},                 # Energia Today Low
              'Etotal'   : {'reg':55, 'dec':1, 'tipo': 'u32', 'fc' : 4},  # Energia Total High
              'Etotal'   : {'reg':56, 'dec':1, 'fc' : 4},                 # Energia Total Low
              'Pac'      : {'reg':35, 'dec':1, 'tipo': 'u32', 'fc' : 4},  # consumo casa watios Hight
              'Pac'      : {'reg':36, 'dec':1, 'fc' : 4},                 # Consumo casa watios Low
              'Iac'      : {'reg':39, 'dec':1, 'fc' : 4},                 # Consumo casa Amperios
              'Pctotal'  : {'reg':3046, 'dec':1, 'fc': 4},                # Potencia total Low
              'Pctotal'  : {'reg':3045, 'dec':1, 'tipo': 'u32', 'fc' : 4} # Potencia total Hight
          
            
            }
    }



# ########### FIN PARAMETRIZACION EQUIPO ####################
  


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'GROWATT'
servicio = 'fv_growatt'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


exec(open("/home/pi/PVControl+/fv_rs485.py").read(),globals())#cargo estructura programa de captura generica de RS485
