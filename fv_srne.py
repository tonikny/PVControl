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


SRNE = {
      'SRNE1': {'usar':1,
                'dev': '/dev/ttyUSB0',
                'baudrate': 9600,
                'id_modbus': 1,
                'tiempo_captura': 5,
            },
          
      'COMANDOS': {
            'ayuda' : ['h','?','i', 'info',''],
            
            # permite la lectura multiple de los registros lo que acelera el tiempo de captura
            'lectura_multiple': {
                  'usar': 1,
                  'rangos':[[0x0100,0x0114],[0x0120,0x0120],[0xE005,0xE014]]
            },
            
            # reg: numero de registro
            # dec: numero de decimales..... si no se pone se considera = 0
            # rango: [min,max] ... si no se pone no se realiza chequeo de rango
            # tipo: u16= sin signo / s16= con signo ....por defecto= u16
            # adaptar= casos especificos de cada equipo que obliga a especificar como se interpreta (el dato en bruto esta en variabe "d")
            # offset: valor de offset ..... si no se pone se considera = 0
            # escritura: True implica que es posible escribir en el registro ....por defecto= False 
            # grabar: True implica que se guarda en el registro en BD / False: No graba ..... por defecto= True
            
            'SOC'       : {'reg':0x0100},              # % SOC
            'Vbat'      : {'reg':0x0101, 'dec':1},     # Voltaje baterias
            'Iplaca'    : {'reg':0x0102, 'dec':2},     # Intensidad Placas
            'Temp0'     : {'reg':0x0103,
                        'tipo':'adaptar',
                        'adaptar':["datos['Temp0']=int(format(d,'04x')[:2],16)"],
                        },     # Temp Regulador
            'Temp1'     : {'reg':0x0103,
                        'tipo':'adaptar',
                        'adaptar':["datos['Temp1']=int(format(d,'04x')[2:],16)"],
                        },     # Temp Bateria
            # 'load_voltage' : {'reg': 0x0104, 'dec':1},     # Voltaje Carga
            # 'load_current' : {'reg': 0x0105, 'dec':1},     # Intensidad Carga
            # 'load_power'   : {'reg': 0x0106, 'dec':1},     # Potencia Carga
            'Vplaca'    : {'reg':0x0107, 'dec':1},     # Voltaje Placa
            'Ipanel'    : {'reg':0x0108, 'dec':2},     # Intensidad Panel
            'Wplaca'    : {'reg':0x0109},              # Potencia Placa
            'bat_min_today': {'reg':0x010B, 'dec':1},     # Minimo baterias hoy
            'bat_max_today': {'reg':0x010C, 'dec':1},     # Maximo baterias hoy
            'max_charging_power_today': {'reg':0x010F},     # Potencia Carga maxima hoy
            'max_discharging_power_today': {'reg':0x0110},     # Potencia Descarga maxima hoy
            'charging_amp_hours_today': {'reg':0x0111},     # Ah Carga Hoy
            'discharging_amp_hours_today': {'reg':0x0112},     # Ah Descarga Hoy
            'power_generation_today': {'reg':0x0113},     # Potencia Generada Hoy
            'power_consumption_today': {'reg':0x0114},     # Potencia Consumida Hoy
            'charging_status': {
                  'reg':0x0120,
                  'tipo':'adaptar',
                  'adaptar': [
                      "if d==0: datos['charging_status']='DEACTIVATED'",
                      "elif d==1: datos['charging_status']='ACTIVATED'",
                      "elif d==2: datos['charging_status']='BULK'",
                      "elif d==3: datos['charging_status']='EQUALIZE'",
                      "elif d==4: datos['charging_status']='ABSORTION'",
                      "elif d==5: datos['charging_status']='FLOAT'",
                      "elif d==6: datos['charging_status']='LIMITING'",
                  ]
            },     # Estado Carga
            'over_voltage_threshold': {'reg':0xE005, 'escritura':True, 'rango':[70,170]},
            'charging_voltage_limit': {'reg':0xE006, 'escritura':True, 'rango':[70,170]},
            'equalizing_charging_voltage': {'reg':0xE007, 'escritura':True, 'rango':[70,170]},
            'boost_charging_voltage': {'reg':0xE008, 'escritura':True, 'rango':[70,170]},
            'floating_charging_voltage': {'reg':0xE009, 'escritura':True, 'rango':[70,170]},
            'boost_recovery_voltage': {'reg':0xE00A, 'escritura':True, 'rango':[70,170]},
            'over_discharge_recovery_voltage': {'reg':0xE00B, 'escritura':True, 'rango':[70,170]},
            'under_voltage_warning_level': {'reg':0xE00C, 'escritura':True, 'rango':[70,170]},
            'over_discharge_voltage': {'reg':0xE00D, 'escritura':True, 'rango':[70,170]},
            'discharging_limit_voltage': {'reg':0xE00E, 'escritura':True, 'rango':[70,170]},
            'over_discharge_time_delay': {'reg':0xE010, 'escritura':True, 'rango':[0,120]},
            'equalizing_charging_time': {'reg':0xE011, 'escritura':True, 'rango':[0,300]},
            'boost_charging_time': {'reg':0xE012, 'escritura':True, 'rango':[10,300]},
            'equalizing_charging_interval': {'reg':0xE013, 'escritura':True, 'rango':[0,255]},
            'temperature_compensation_factor': {'reg':0xE014, 'escritura':True, 'rango':[0,5]},
      }
}


# ########### FIN PARAMETRIZACION EQUIPO ####################


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'SRNE'
servicio = 'fv_srne'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


exec(open("/home/pi/PVControl+/fv_rs485.py").read(),globals())#cargo estructura programa de captura generica de RS485
