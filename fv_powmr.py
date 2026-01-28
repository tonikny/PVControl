# -*- coding: utf-8 -*-

# Versión 2024-05-20
#

# ######## INICIO PARAMETRIZACION EQUIPO ####################
# 
# UN BLOQUE COMO ESTE SE DEBE INCLUIR EN Parametros_FV.py
#
# ¡¡¡¡ NO MODIFICAR ESTE FICHERO !!!!
#
# ###########################################################

orden_bytes = 1

POWMR = {
    'POWMR1': {'usar':0,              # Poner a 1 para activar
              'dev': '/dev/ttyUSB0',  # Puerto de comunicaciones
              'baudrate': 2400,       # Baudrate
              'id_modbus': 5,         # Identificador Modbus
              'tiempo_captura': 5,    # Tiempo en segundos entre cada captura
             },
             
    'POWMR2': {'usar':0,
              'dev': '/dev/ttyUSB0',
              'id_modbus': 5,
              'tiempo_captura': 5,
          },
          
          
    'COMANDOS': {
              'ayuda' : ['h','?','i', 'info',''],
              
              # permite la lectura multiple de los registros lo que acelera el tiempo de captura
              'lectura_multiple': {'usar': 1, 'rangos':[[4501,4564]]},
              
              # reg: numero de registro
              # dec: numero de decimales..... si no se pone se considera = 0
              # rango: [min,max] ... si no se pone no se realiza chequeo de rango
              # tipo: u16= sin signo / s16= con signo ....por defecto= u16
              #       adaptar= casos especificos de cada equipo que obliga a especificar como se interpreta (el dato en bruto esta en variabe "d"
              # offset: valor de offset ..... si no se pone se considera = 0
              # escritura: True implica que es posible escribir en el registro ....por defecto= False 
              # grabar: True implica que se guarda en el registro en BD / False: No graba ..... por defecto= True
              
              'Sprio' : {'reg':4501}, 
              'Vac' : {'reg':4502, 'dec':1},
              'Fac' : {'reg':4503, 'dec':1},
              'Vplaca1' : {'reg':4504, 'dec':1},
              'Wplaca1' : {'reg':4505},
              'Vbat' : {'reg':4506, 'dec':1}, 
              'SOC' : {'reg':4507},
              'Icarga' : {'reg':4508}, 
              'Idescarga' : {'reg':4509}, 
              'Vac_out' : {'reg':4510, 'dec':1}, 
              'Fac_out' : {'reg':4511, 'dec':1}, 
              'Wconsumo' : {'reg':4512},
              'Wconsumo_VA' : {'reg':4513},
              'Wconsumo_%' : {'reg':4514},
              'Wconsumo_%2' : {'reg':4515},
              'Flags_4516' : {'reg':4516},
              
              '4517' : {'reg':4517},
              '4518' : {'reg':4518},
              '4519' : {'reg':4519},
              '4520' : {'reg':4520},
              '4521' : {'reg':4521},
              '4522' : {'reg':4522},
              '4523' : {'reg':4523},
              '4524' : {'reg':4524},
              '4525' : {'reg':4525},
              '4526' : {'reg':4526},
              '4527' : {'reg':4527},
              '4528' : {'reg':4528},
              '4529' : {'reg':4529},
              
              'Error_code' : {'reg':4530},
              
              '4531' : {'reg':4531},
              '4532' : {'reg':4532},
              '4533' : {'reg':4533},
              '4534' : {'reg':4534},
              
              'Flags_4535' : {'reg':4535},
              
              'Carga_prio' : {'reg':4536},
              'Source_prio' : {'reg':4537},
              'Vac_input_target' : {'reg':4538},
              
              '4539' : {'reg':4539},
              
              'Fac_out_target' : {'reg':4538},
              
              '4541' : {'reg':4541},
              '4542' : {'reg':4542},
              
              'Carga_max_util' : {'reg':4543},
              'Vbat_back_utility' : {'reg':4544, 'dec':1},
              'Vbat_back_bateria' : {'reg':4545, 'dec':1},
              
              'Vabs' : {'reg':4546, 'dec':1, 'rango':[48,64], 'escritura': True},
              'Vflot' : {'reg':4547, 'dec':1},
              'Vbat_cutoff' : {'reg':4548, 'dec':1},
              'Vequ' : {'reg':4549, 'dec':1},
              'Vequ_time' : {'reg':4550},
              'Vequ_timeout' : {'reg':4551},
              'Vequ_intervalo' : {'reg':4552},
              
              'Flags_4553' : {'reg':4553},
              'Flags_4554' : {'reg':4554},
              'Carga_estado' : {'reg':4555},
              
              '4556' : {'reg':4556},
              'Temp_placas' : {'reg':4557},
              
              'Wplaca_?' : {'reg':4558 },
              
              '4559' : {'reg':4559},
              '4560' : {'reg':4560},
              '4561' : {'reg':4561},
              '4562' : {'reg':4562},
              
              'Vplaca2' : {'reg':4563, 'dec':1},
              'Wplaca2' : {'reg':4564, },
                
            },
    }



# ########### FIN PARAMETRIZACION EQUIPO ####################
  


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'POWMR'
servicio = 'fv_powmr'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


exec(open("/home/pi/PVControl+/fv_rs485.py").read(),globals())#cargo estructura programa de captura generica de RS485
