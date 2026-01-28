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


MUST = {
    'MUST1': {'usar':0,
              'dev': '/dev/ttyUSB0',
              'baudrate' : 19200,
              'id_modbus': 1,
              'tiempo_captura': 5,
          },
          
    'MUST2': {'usar':0,
              'dev': '/dev/ttyUSB1',
              'baudrate' : 19200,
              'id_modbus': 1,
              'tiempo_captura': 3,
          },
          
    'COMANDOS':{
              'ayuda' : ['h','?','i', 'info',''],
              
              # permite la lectura multiple de los registros lo que acelera el tiempo de captura
              'lectura_multiple': {'usar': 0, 'rangos':},
              
              # reg: numero de registro
              # dec: numero de decimales..... si no se pone se considera = 0
              # rango: [min,max] ... si no se pone no se realiza chequeo de rango
              # tipo: u16= sin signo / s16= con signo ....por defecto= u16
              # adaptar= casos especificos de cada equipo que obliga a especificar como se interpreta (el dato en bruto esta en variabe "d")
              # offset: valor de offset ..... si no se pone se considera = 0
              # escritura: True implica que es posible escribir en el registro ....por defecto= False 
              # grabar: True implica que se guarda en el registro en BD / False: No graba ..... por defecto= True
              
              # https://gist.github.com/vladyspavlov/5ac21cb58923482eff8e7bbb2d0854b3
              
              'Cargador_Estado'    : {'reg':15201},     # PV Charger Workstate
              'MPPT_Estado'        : {'reg':15202},     # PV Charger MPPT state
              'MPPT_Estado_carga'  : {'reg':15203},     # PV Charger Charging state
              
              'Vplaca'    : {'reg':15205, 'dec':1},     # Voltaje Placas
              'Vbat_1'    : {'reg':15206, 'dec':1},     # PV Charger Battery voltage
              'Iplaca'    : {'reg':15207, 'dec':1},     # PV Charger Current
              'Wplaca'    : {'reg':15208, 'dec':0},     # PV Charger power
              'Temp_rad'  : {'reg':15209, 'dec':0},     # PV Charger Radiator temp
              'Temp_ext'  : {'reg':15210, 'dec':0},     # PV Charger External temp
              
              'Vbat'      : {'reg':25205, 'dec':1},     # Voltaje baterias
             
              'Wout'      : {'reg':25214, 'tipo':'s16'},# W de salida
              'Wred'      : {'reg':25215},              # W de red AC.... ver  signo ??
              
              'Ibat'      : {'reg':25274, 'dec':0,'tipo':'s16'},   # Intensidad baterias
              
              
                            
            }
    }


# ########### FIN PARAMETRIZACION EQUIPO ####################
  


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'MUST'
servicio = 'fv_must'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


exec(open("/home/pi/PVControl+/fv_rs485.py").read(),globals())#cargo estructura programa de captura generica de RS485
