# ------------------------------------------------------------------
######    PARAMETROS INSTALACION PVControl+  -- version: 2026-01-12
# ------------------------------------------------------------------

# ====================================================================
# ====================================================================
#             1.- SECCION PRINCIPAL PARAMETRIZACION        
# ====================================================================
# ====================================================================


########################
###### Simulacion ######
########################
simular = 0         # Simulacion datos FV --- 1 para simular....0 para no simular
simular_reles = 0   # Simular reles fisicos
# -----------------------------------------------

################################
##### Parametros sensores ######
################################

# 'Variable' : {'Equipo':"expresion captura",'Max':Valor maximo, 'Min':Valor minimo,......},

## Se pueden crear las variables que se quieran y con el nombre que se quiera
## La "expresion de captura" puede ser cualquier expresion python3 valida
## En los programas de captura que utilicen la tabla en BD RAM la sintaxis sera.... "d_['CLAVE']['Variable']".... d_['ADS1']['Vbat'], d_['HIBRIDO']['Vbat'],...
## En los programas de captura que aun utilicen los archivos pkl la sintaxis sera.... "d_clave['Variable']".... d_sma['Vbat'], d_srne['Vbat'],...
## Si se definen las claves 'Max' y 'Min' se enviara un log si la captura esta fuera de dichos margenes 
 
sensores ={
'Vbat'    : {'Equipo':"d_['HIBRIDO']['Vbat']", 'Max':66, 'Min':11},     # Sensor de Voltaje bateria
'Vplaca'  : {'Equipo':"d_['HIBRIDO']['Vplaca']", 'Max':500, 'Min':-5},  # Sensor de Voltaje placa

'Ibat'    : {'Equipo':"d_['HIBRIDO']['Ibat']", 'Max':200, 'Min':-200}, # Sensor de Intensidad bateria
'Iplaca'  : {'Equipo':"d_['HIBRIDO']['Iplaca']", 'Max':200, 'Min':-1}, # Sensor de Intensidad Placas

'Aux1'  : {},    # Sensor Aux1
'Aux2'  : {},    # Sensor Aux2
'Aux3'  : {},    # Sensor Aux3
'Aux4'  : {},    # Sensor Aux4
'Aux5'  : {},    # Sensor Aux5
'Aux6'  : {},    # Sensor Aux6
'Aux7'  : {},    # Sensor Aux7

'Vred' : {},   # Sensor Voltaje de red 
'Ired' : {},   # Sensor Intensidad de red
'EFF'  : {},   # Eficienca Conversion 

'Temp_Bat': {},  #  Sensor Temperatura

# Expresiones calculadas
'Wbat' : {"Ibat * Vbat"}, #  Potencia de/a baterias
'Wplaca' : {"d_['HIBRIDO']['Wplaca']"}, #  Potencia de placas
'Wred' : {"Ired * Vred"},     #  Potencia de/a red
'Wconsumo': {"Wplaca-Wred-Wbat"}, # Consumo

'Temp': {'Equipo':"Temp_Bat"},  #  Temperatura que se guarda en BD y muestra en reloj Web


'Grafica_Aux'  : {"[0,1,Vbat,Iplaca,Ibat]"},  # [Activar, Nmuestras, lista variables....]

}

###### TABLAS / GRAFICAS AUXILIARES
## Permite crear las tablas que se deseen definiendo las variables a guardar
## lo que permitira generar graficos personalizados 
# Se puede usar cualquier variable conocida por fv.py o definida en "sensores"

Graficas_Aux = {

  'TABLA_1': {                               # poner el nombre de la tabla que se quiera crear
       'activo':0,                           # 0 no captura,...1 captura
       'tmuestra':5,                         # tiempo en seg entre capturas
       'variables': "Vbat, Ibat,Vplaca"      # Nombre de las variables a incluir en cada registro
       },
  
  'TABLA_2': {'activo':0, 'tmuestra':1,'variables': ""},
  
  'TABLA_3': {'activo':0, 'tmuestra':1,'variables': ""},
  
   }

# -----------------------------------------------

######################################
###### Parametros Base de Datos ######
######################################
servidor = "localhost"
usuario = "rpi"
clave = "fv"
basedatos = "control_solar"

grabar_datos_s = "False"   # expresion para grabar cada muestra en la tabla datos_s
                           # Ejemplos: 'True'.. 'False'.. 'Vplaca > 10'... 'PWM > 0'

t_muestra_max = 6     # valor para grabar en el log si tarda mas el bucle en ejecutarse

# tuplas de [nombre tabla, dias maximos de antiguedad de registros que se conservan]
# Se gestiona en fv_gestionbd.py que se lanza por comando diario por crontab archivo...PVControl+/etc/cron.d/pvcontrol
limpieza_tablas=[
                ['datos_s',10],
                ['datos',366],
                ['reles_grab',366],
                ['log',30],
                ['datos_aux',366],
                ['datos_celdas',366],
                
                # tablas de datos de equipos...modificar segun equipamiento instalado
                ['hibrido',366],
                ['hibrido1',366],
                ['hibrido2',366],
                
                ['victron',366],
                ['bmv',366],
                ['srne',366],
                
               ]

# Limpieza tablas con campo fecha
tablas_d=[
         ['reles_segundos_on',366],
        ]


# -----------------------------------------------

##################
###### MQTT ######
##################
mqtt_broker  = "localhost"
mqtt_puerto  = 1883
mqtt_usuario = "rpi"
mqtt_clave   = "fv"


##### Subcripciones #####
usar_mqtt_suscripciones = 0  # activa servicio fv_mqtt.py que se suscribe a los topics que se especifiquen en mqtt_suscripciones  
               # guarda lo capturado en la tabla ram 'equipos' ... diccionario=d_['MQTT'] / servicio = fv_mqtt                

mqtt_suscripciones_watchdog = 1800 # Tiempo maximo sin mensajes para reiniciar fv_mqtt.py

mqtt_suscripciones=[] #  lista de topics a los que se suscribe fv_mqtt.py para guardar en tabla equipos.. diccionario=d_['MQTT']


##### Publicaciones #####
usar_mqtt_publicaciones =  0    # 1 = Publica por MQTT los topic definidos en mqtt_publicaciones...... 0= No publica por MQTT  
mqtt_topic_raiz = "PVControl/"  # Raiz del topic a publicar

#  Tuplas [Nombre Topic, Variable, frecuencia en sg (0 deshabilita, por defecto = Tmuestra * Nmuestra)]
mqtt_publicaciones = [["Wplaca","Wplaca"],
                      ["Vbat","Vbat"],
                      ["Ibat","Ibat",10],
                      ["SOC","SOC",15],
                      ["DatosFV","d_['FV']",0]] # publica diccionario d_[FV] en topic PVControl/DatosFV para poder ser usado por Home Assistant

# -----------------------------------------------
###########################################
### Reles 1XX personalizados [[Id_rele1, comando1, comando2,...],[Id_rele1, comando1, comando2,...]]
############################################

reles_personalizados =[
                       
                      ]


# ====================================================================
# ====================================================================
#    2.- SECCION PARAMETRIZACION SEGUN EQUIPAMIENTO INSTALADO        
# ====================================================================
# ====================================================================


################################
###### Parametros Bateria ######
################################
AH = 100.           # Capacidad en Ah de la Bateria a C20 (poner 0 para instalaciones sin Bateria)
CP = 1.              # Indice Peukert
EC = 1.              # Eficiencia Carga
vsis = 4.            # Voltaje sistema - 1=12V  2=24V   4=48V
vflotacion = 13.7   # Valor por defecto de flotacion a 25ºC a 12V (no se usa por ahora)

SOC_incremento_rapido_condicion = 'Ibat>0 and Ibat<0.005*AH and abs(Vbat-Vflot)<0.2'
SOC_incremento_rapido_accion = 'DS += (AH-DS)/50'  # AH es el valor de los Ah nominales de bateria --  DS son los Ah actuales de capacidad

# Acciones a ejecutar en paso de fases de carga
Bulk_Absorcion_accion = []        # ['comando1', 'comando2',...]
Absorcion_Flotacion_accion = []   #['comando1', 'comando2',...]
Flotacion_Bulk_accion = []        #['comando1', 'comando2',...]

Tflot_bulk_tiempo = 10000 # contador de paso a BULK desde Flotacion

# Parametros de Icola
usar_Icola = False        # Activa/desactiva absorció per corrent de cua
Icola_t = 600             # tiempo (s) de Icola valida
Icola_reset_t = 60        # tiempo (s) para resetear el contador de Icola
Icola_t_f = 10            # constante de tiempo de filtrado (s)

usar_Icola_temp = True    # Activar/desactivar compensació per temperatura
Icola_pct_ref = 0.02      # Percentatge de C a 25 °C (2% de la capacitat)
Icola_T_ref = 25.0        # Temperatura de referència (°C)
Icola_pct_TC = -0.0005    # Variació del percentatge per °C (-0.5% C / 10°C)
Icola_min_pct     = 0.01  # Límit mínim del percentatge (1% C)
Icola_max_pct     = 0.03  # Límit màxim del percentatge (3% C)

# -----------------------------------------------

#######################################################
###### Parametros ADS1115  - Permite hasta 4 ADS ######
#######################################################
usar_ADS = [0,0] # activar o no el ADS
nombre_ADS = ['ADS1','ADS4']                                         # Nombre de los ADS
direccion_ADS = [72,75]                                              # direccion I2C del ADS

var_ADS = [['Vbat','Aux1', 'Vplaca','Aux2'],['Ibat','','Iplaca','']] # Nombre de las variables a capturar

tmuestra_ADS = [1,1]                                                 # tiempo en sg entre capturas
rate_ADS = [[250,250,250,250],[250,0,250,0]]                     # datarate de lectura
bucles_ADS = [[10,5,5,5], [5,0,5,0]]                                 # Numero de bucles de lectura

gain_ADS = [[2,2,2,2], [16,0,16,0]]                                # Voltios Fondo escala 1=4,096V - 2=2.048V - 16= 256mV
modo_ADS = [[1,1,1,1], [3,0,3,0]]                                    # 0=desactivado, 1=disparado, 2= Continuo, 3=diferencial, 4=diferencial_continuo
res_ADS = [[47.46,47.46,47.46,47.46],[100/0.075,0,100/0.075,0]]      # ratio lectura ADS - Lectura real

# -----------------------------------------------
#########################
###### Multiplexor ######
#########################
usar_mux = 0   # Poner el numero de celdas a monitorizar (0= desactivar)...diccionario = d_['MUX'] / servicio = fv_mux

t_muestra_mux = 5 # segundos entre capturas del mux
n_muestras_mux = 4        # grabar en BD en tabla permanente cada X capturas 

pin_ADS_mux1 = "A2_2" #A2_1 = entrada A2 del ADS1, #A2_2 = entrada A2 del ADS2
                      #A2_3 = entrada A2 del ADS3, #A2_4 = entrada A2 del ADS4
                      
pin_ADS_mux2 = 'A3_2' #A3_1 = entrada A3 del ADS1, #A3_2 = entrada A3 del ADS2
                      #A3_3 = entrada A3 del ADS3, #A3_4 = entrada A3 del ADS4

captura_mux = "S"  # D = lectura modo diferencial.... S = modo simple
                   # ATENCION si el modo de captura es diferencial se deben usar los 2 MUX y 
                   #   configurar en la PCB las salidas del MUX para usar las entradas A2 y A3 del mismo ADS
             
gain_mux = 1       # Voltios Fondo escala del ADS1115... 1=4,096 - 2=2.048

r_mux = [47] * 32  # Ratio Divisores de Voltaje de cada entrada de los Mux - Ejecutar el programa.. python3 fv_mux_calibracion.py  ... para calibrar los valores medidos
                   # Dicho programa creara en la BD la tabla "parametros1" y un registro donde se incluira la calibracion realizada

celdas_log_dif = 0.5 # diferencia entre la celda mas alta y la mas baja para mandar log

# -----------------------------------------------
#################################################
###### HIBRIDO  -  Permite hasta 9 Equipos ######
#################################################

## ATENCION ser congruente con lo que se ha puesto en el apartado de sensores
## Si algun sensor (Vbat, Vplaca,...)  usa el Hibrido o se quiere guardar en BD en la tabla 'Hibrido'
## se debe poner usar hibrido = 1

usar_hibrido = [0] #1 para leer datos Hibrido ..... 0 para no usar

dev_hibrido = ["/dev/hidraw0"]  # puerto donde reconoce la RPi al Hibrido
usar_crc = [1]                  # 1 para comandos del hibrido con CRC... 0 para no añadir CRC

t_muestra_hibrido = [5]         # Tiempo en segundos entre muestras del Hibrido
publicar_hibrido_mqtt = [1]     # Publica o no por MQTT los datos capturados del Hibrido

grabar_datos_hibrido = [1]      # 1 = Graba la tabla Hibrido... 0 = No graba
n_muestras_hibrido = [1]        # grabar en BD en tabla 'hibrido' cada X capturas del Hibrido 

protocolo_hibrido = [30]        # Nº de Protocolo del Hibrido (30 o 18)

QPIGS2h_enviar = [0]            # Envia QPIGS2h en protocolo 30 ademas de QPIGS para el segundo MPPT 
# -----------------------------------------------

#########################
###### DALY ######
#########################
usar_daly = 0                   # 1 = Se usa 0 = No se usa
t_muestra_daly = 1              # segundos entre capturas para tabla en RAM 
grabar_datos_daly = 1           # 1 = Graba la tabla ... 0 = No graba
leer_soc_daly = 1               # 1 = leer soc ibat vbat .... 0 = NO SE USA
leer_temp_daly = 0              # 1 = leer la temperaturas ... 0 = NO SE USA 
leer_ciclos_daly = 1            # 1 = leer los ciclos el numero de celdas y varias cosas mas que no tengo claro = 0 NO SE USA
leer_V_Max_Min_daly = 1         # 1 = leer el valor max y min de las celdas ... 0 = NO SE USA
n_muestras_daly = 5             # grabar en BD en tabla permanente cada X capturas 
Valor_error_max_daly = 4.5      # no grabar si alguna lectura da este valor
Valor_error_min_daly = 2.8      # no grabar si alguna lectura da este valor
dev_daly = "/dev/ttyUSB0"       # puerto donde reconoce la RPi al Hibrido


# -----------------------------------------------

#####################
###### VICTRON ######
#####################

# ============= victron.py  ===========================================

## valido para un unico equipo por VE.direct ( se mantiene por compatibilidad)

usar_victron = 0              # 1 para leer datos victron ..... 0 para no usar

dev_victron = "/dev/ttyUSB0"  # puerto donde reconoce la RPi al Victron


# ============= fv_victron_vedirect.py  ================================

## valido para N equipos por VE.direct 

VICTRON_VEDIRECT = {
    "VICTRON1": {
        "usar": 0,
        "dev": "/dev/ttyUSB1"
    },
    "VICTRON2": {
        "usar": 0,
        "dev": "/dev/ttyUSB2"
    }
}

# ============= fv_victron_mk2.py  ================================

## valido para N equipos por MK2 y MK3 

VICTRON_MK2 = {
    'MULTIPLUS1': {'usar': 0,
           'dev' : 'dev/ttyUSB0',
           'tiempo_captura': 5,
           'ciclos_grabacion' : 1, # 0 para NO grabar en BD
          },
          
    'MULTIPLUS2': {'usar':0,
            'dev' : 'dev/ttyUSB1',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 5,
          },
    }



# ============= fv_mqtt_venus.py  =====================================

## valido para conexion a CERBO o VENUS OS por MQTT 

mqtt_broker_venus  = "192.168.X.XX"
mqtt_puerto_venus  = 1883
mqtt_usuario_venus = "XXXX"
mqtt_clave_venus   = "YYY"

usar_mqtt_suscripciones_venus = 0
mqtt_suscripciones_venus = [] #  lista de topics a los que se suscribe fv_mqtt_venus.py para guardar en tabla equipos.. diccionario=d_['MQTT_EXT']

usar_mqtt_publicaciones_venus = 0
mqtt_publicaciones_venus = [
                             ["R/XXXX/keepalive", "", 60], #topic, payload, frecuencia
                             ["R/YYYY/keepalive", "", 60]
                           ] 



# -----------------------------------------------
#####################
###### MUST ######
#####################

## ATENCION ser congruente con lo que se ha puesto en el apartado de sensores
## Si algun sensor (Iplaca, Vplaca,...)  usa el MUST o se quiere guardar en BD en la tabla 'must'
## se debe poner usar must= 1

usar_must = 0              # 1 para leer datos victron ..... 0 para no usar
n_equipos_must = 0         #número de inversores en paralelo. Si sólo hay uno, marcar 1.
dev_must = "/dev/ttyUSB0"  # puerto donde reconoce la RPi al Must

grabar_datos_must= 0      # 1 = Graba la tabla Must... 0 = No graba
t_muestra_must = 1         # Tiempo en segundos entre muestras + numero de equipos

iplaca_must_max = 99
iplaca_must_min = 0

# -----------------------------------------------
#################
###### BMV ######
#################

## ATENCION ser congruente con lo que se ha puesto en el apartado de sensores
## Si algun sensor (Iplaca, Vplaca,...)  usa el BMV o se quiere guardar en BD en la tabla 'bmv'
## se debe poner usar bmv = 1

usar_bmv = 0              # 1 para leer datos victron ..... 0 para no usar

dev_bmv = "/dev/serial0"  # puerto donde reconoce la RPi al BMV

grabar_datos_bmv = 0      # 1 = Graba la tabla bmv... 0 = No graba
n_muestra_bmv = 5         # # Numero de muestras para guardar en BD tabla bmv

# -----------------------------------------------
#################
###### SMA ######
#################

## ATENCION ser congruente con lo que se ha puesto en el apartado de sensores

usar_SI = 0               # 1 para leer datos del SI ..... 0 para no usar
usar_SB1 = 0              # 1 para leer datos del SB1 ..... 0 para no usar
usar_SB2 = 0              # 1 para leer datos del SB2 ..... 0 para no usar
usar_smameter = 0        # 1 para leer datos del meter SMA ..... 0 para no usar

IP_SI = "192.168.0.24"    # IP del SI
IP_SB1 = "192.168.1.154"  # IP del SB1
IP_SB2 = "192.168.0.252"  # IP del SB2

t_muestra_SB1 = 5 # tiempo en segundos entre capturas del SB1
t_muestra_SB2 = 5 # tiempo en segundos entre capturas del SB2


# -----------------------------------------------
#################
#### FRONIUS ####
#################

## Se admiten varios equipos fronius... incluir separado por comas los distintos parametros....
## por ejemplo para 2 equipos....
##    usar_fronius = [1,1]....IP_FRONIUS = ["192.168.1.101","192.168.1.102"] ...etc
 
## ATENCION ser congruente con lo que se ha puesto en el apartado de sensores
## Si algun sensor (Iplaca, Vplaca,...)  usa fronius se debe poner usar fronius = [1]

usar_fronius = [0]          	 # 1 para leer datos del fronius..... 0 para no usar
usar_meter_fronius = [0]         # 1 para activar lectura de contador de Fronius
IP_FRONIUS = ["192.168.0.24"]    # IP del FRONIUS
t_muestra_fronius = [5]          # Tiempo en segundos entre capturas 
# -----------------------------------------------
#################
####  HUAWEI ####
#################

## ATENCION ser congruente con lo que se ha puesto en el apartado de sensores
## Si algun sensor (Iplaca, Vplaca,...)  usa fronius se debe poner usar huawei = 1

usar_huawei = 0                # 1 para leer datos del huawei..... 0 para no usar
IP_HUAWEI = "192.168.200.1"    # IP del huawei
puerto_huawei = 6607           # puerto comunicaciones 502 ... 6607
t_muestra_huawei = 5           # Tiempo entre capturas
# -----------------------------------------------
#################
####  GOODWE ####
#################

## ATENCION ser congruente con lo que se ha puesto en el apartado de sensores
## Si algun sensor (Iplaca, Vplaca,...)  usa fronius se debe poner usar goodwe = 1

usar_goodwe = 0                 # 1 para leer datos del goodwe..... 0 para no usar
IP_GOODWE = "192.168.0.100"     # IP del goodwe
t_muestra_goodwe = 5
usar_batgoodwe = 0              # 1 para usar batería y 0 para no usar

# -----------------------------------------------
##################
###### SRNE ######
##################

SRNE = {
      'SRNE1': {'usar':0,
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


#####################
###### SDM120C ######
#####################

## ATENCION ser congruente con lo que se ha puesto en el apartado de sensores
## Si algun sensor usa sdm120c se debe poner usar_sdm120c = 1

usar_sdm120c = [0] 
dev_sdm120c = ["/dev/ttyUSB0"]  # puerto donde reconoce la RPi al equipo
t_muestra_sdm120c = [5]         # Tiempo en segundos entre muestras
publicar_sdm120c_mqtt = [0]     # Publica o no por MQTT los datos capturados (no implementado aun)
grabar_datos_sdm120c = [1]      # 1 = Graba la tabla Hibrido... 0 = No graba
n_muestras_sdm120c = [1]        # grabar en BD cada nmuestras

#####################
###### SDM230M ######
#####################
usar_sdm230m = [0] 
dev_sdm230m = ["/dev/ttyUSB0"]         
t_muestra_sdm230m = [5]         # Tiempo en segundos entre muestras
# -----------------------------------------------


#####################
###### EASTRON ######
#####################

## ATENCION ser congruente con lo que se ha puesto en el apartado de sensores
## Si algun sensor usa el eastron se debe poner usar eastron = 1

usar_eastron = 0       # 1 para leer datos ..... 0 para no usar
dev_eastron = ""       # /dev/ttyUSB0" # USB  

# -----------------------------------------------
######################################
###### DEYE, TURBO ENERGY,...   ######
######################################

usar_deye = [0,0]
nombre_deye = ['DEYE', 'DEYE1']  #Nombre que asignamos a cada equipo  deye1 que es wifi? 

dev_deye = ["/dev/ttyUSB0","192.168.0.195"]  # puerto o IP donde reconoce la RPi al equipo
n_serie_dongle = [0,11111111]                # numero de serie de dongle WiFI si existe o 0 si no existe
mb_slave_id = [0,1]                          # 1 para Master de conexion WiFi

t_muestra_deye = [5,5]                       # Tiempo en segundos entre muestras

# -----------------------------------------------
#####################
###### DiY BMS ######
#####################
# activar servicio fv_diy
usar_diybms = 0       # Poner el numero de celdas a monitorizar (0= desactivar)...diccionario = d_['BMS_DIY'] / servicio = diy_BMS

# -----------------------------------------------
##########################
### PYLONTECH_CONSOLA ####
##########################
usar_pylontech_consola = 0
baudrate_pylontech_consola = 115200
port_pylontech_consola ='/dev/ttyUSB0'
timeout_pylontech_consola = 1
n_pylontech = 4 # Número de baterías pylontech que forman el banco
t_muestra_pylontech_consola = 5
# -----------------------------------------------
#####################
###### EVSE  ########
#####################
# Indicar si se tiene instalado un cargador de coche EVSE
usar_evse = 0          # 1 para leer datos ..... 0 para no usar
usar_diario2 = 0       # 1 para guardar consumos parciales en diario2 ..... 0 para no usar
#40,45,80
SOC_cut_off = 35 #por debajo de este valor indicaremos al inversor que cargue la batería vía RED.
SOC_warning = 40 #por debajo de este valor, si estamos en periodo valle, cargaremos batería
SOC_cut_on = 70 #por encima de este valor indicaremos al inversor que cargue unicamente usando SOLAR.
SOC_export = 84 #por encima de este valor indicaremos al inversor que podemos volcar a la RED.
Voltage_cut_off = 50.0 #por debajo de este voltage, indicaremos al inversor que cargue vía RED.


# -----------------------------------------------
##################
### BROADLINK ####
##################

## Indicar si se tiene instalado algún equipo de broadlink para uso AA


array_IP = ['192.168.1.234','192.168.1.235']  # Indicar IP´s de equipos Broadlnk
array_reles = [271,281]     #Indicar relés en el mismo orden que las IPs anteriores a asignar a los relés.

###########################
###### Pantalla OLED ######
###########################

"""
#### Pantalla predefinidas:
   0 ... Logo PVControl+
   1 ... Resumen1 Bateria/Placas/Reles
   2 ... Resumen2 Bateria/Placas/Reles
   3 ... Detalles Reles
   4 ... SOC en grande
   5 ... Estado PVControl+
   El resto de pantallas que se quieran se deben definir en 'PANTALLAS' (se pone como ejemplo JK1 y JK2)
   
"""
OLED = {
  'OLED1' : {'tipo':'ssd1306',         # SSD1306 o SH1106
             'i2c_direccion' : 0x3C,   # Direccion I2C de la pantalla
             'salida':[0,1,2,3,4,5]},    # secuencia de pantallazos cada 5 sg
  
  'OLED2' : {'tipo':'ssd1306',
             'i2c_direccion' : 0x3D,
             'salida':['JK1', 'JK2']},

  'PANTALLAS' :{
        'JK1' : ["draw.rectangle((0, 0, 127, 20), outline=255, fill=0)",
                 "draw.text((8, 0), 'JK1'+' - '+str(d_['BMS_JK1']['SOC'])+'%', font=font16, fill=255)",
                 "draw.rectangle((0, 20, 127, 63), outline=255, fill=0)",
                 "draw.text((4, 22), 'Vbat='+str(d_['BMS_JK1']['Vbat'])+'V' +' / '+'Ibat='+str(d_['BMS_JK1']['Ibat'])+'A', font=font, fill=255)",
                 "draw.text((4, 34), str(max(d_['BMS_JK1']['Vceldas']))+' - '+str(min(d_['BMS_JK1']['Vceldas']))+' = '+str(int((round((max(d_['BMS_JK1']['Vceldas']))-(min(d_['BMS_JK1']['Vceldas'])),3))*1000))+'mV', font=font, fill=255)",
                 "draw.text((4, 46), 'AH = '+str(d_['BMS_JK1']['AH_p'])+' - '+str(d_['BMS_JK1']['AH_n'])+' = '+str((d_['BMS_JK1']['AH_p'])-(d_['BMS_JK1']['AH_n'])), font=font, fill=255)",
                ],
        
        'JK2' : ["draw.rectangle((0, 0, 127, 20), outline=255, fill=0)",
                 "draw.text((8, 0), 'JK2'+' - '+str(d_['BMS_JK2']['SOC'])+'%', font=font16, fill=255)",
                 "draw.rectangle((0, 20, 127, 63), outline=255, fill=0)",
                 "draw.text((4, 22), 'Vbat='+str(d_['BMS_JK2']['Vbat'])+'V' +' / '+'Ibat='+str(d_['BMS_JK2']['Ibat'])+'A', font=font, fill=255)",
                 "draw.text((4, 34), str(max(d_['BMS_JK2']['Vceldas']))+' - '+str(min(d_['BMS_JK2']['Vceldas']))+' = '+str(int((round((max(d_['BMS_JK2']['Vceldas']))-(min(d_['BMS_JK2']['Vceldas'])),3))*1000))+'mV', font=font, fill=255)",
                 "draw.text((4, 46), 'AH = '+str(d_['BMS_JK2']['AH_p'])+' - '+str(d_['BMS_JK2']['AH_n'])+' = '+str((d_['BMS_JK2']['AH_p'])-(d_['BMS_JK2']['AH_n'])), font=font, fill=255)",
                ],
      }
}




# -----------------------------------------------
##################
### DERIVA_DC ####
##################
usar_deriva_dc = 0
#rele_deriva_dc = 209  # Ya no se usa...se suscribe directamente a los reles del 202 al 213

baudrate_deriva_dc = 9600
parity_deriva_dc = 'N'
port_deriva_dc ='/dev/ttyACM0'
timeout_deriva_dc = 1

simular_deriva_dc = 0    

# -----------------------------------------------
##################
#### SOFAR  ######
##################

usar_sofar = [0,0] 

dir_modbus_sofar = [1,2]          # Direccion en la red MODBUS de cada equipo
t_muestra_sofar = [5,5]           # Tiempo en segundos entre muestras
#grabar_datos_sofar = [0,0]       # 1 = Graba la tabla sofar... 0 = No graba  (no implementado aun)
n_muestras_sofar = [1,1]          # grabar en BD cada nmuestras
                                      
dev_sofar = ["/dev/ttyUSB0","/dev/ttyUSB0"]    # puerto donde reconoce la RPi a cada equipo                                      


# -----------------------------------------------
##################
#### PYLONTECH ###
##################

usar_pylontech = 0
dbcfile="/home/pi/PVControl+/pylontech_US2000B_Plus_PVControl.dbc"
caninterface="can0"
id_equipo = 'PYLON'

# -----------------------------------------------
###############################
#### BMS JK pot BlueTooth #####
###############################
BMS_JK = {
    'JK1': {'usar':0,
            'MAC': 'C8:47:80:01:D8:CC',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 3,
          },
          
    'JK2': {'usar':0,
            'MAC': 'C8:47:80:01:D9:0B',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 3,
          },
    }

###############################
###### BMS JK pot RS485 #######
###############################

BMS_JK_RS485 = {
    'JK1': {'usar':0,
            'dev': '/dev/ttyUSB0',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 3,
          },
          
    'JK2': {'usar':0,
            'dev': '/dev/ttyUSB1',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 3,
          },
           
    'COMANDOS' : {
        ## R
        0x79:{'Captura': True, 'Nombre':'Vceldas', 'Nbytes': 99, 'Estructura':{'Nbytes': 1, 'Nceldas':1, 'Vcelda':2} },
        0x80:{'Captura': True, 'Nombre':'Temp_tube', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0x81:{'Captura': True, 'Nombre':'Temp_bat_box', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0x82:{'Captura': True, 'Nombre':'Temp_bat', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0x83:{'Captura': True, 'Nombre':'Vbat', 'Nbytes': 2, 'Adaptar':'round(x/100,2)'},
        0x84:{'Captura': True, 'Nombre':'Ibat', 'Nbytes': 2, 'Adaptar':'-round(x/100,2) if x < 32768 else round((x-32768)/100,2)'},
        0x85:{'Captura': True, 'Nombre':'SOC', 'Nbytes': 1, 'Adaptar':'x'},
        0x86:{'Captura': False, 'Nombre':'Nsondas_temp', 'Nbytes': 1, 'Adaptar':'x'},
        0x87:{'Captura': True, 'Nombre':'T_uso', 'Nbytes': 2, 'Adaptar':'x'},
        0x89:{'Captura': True, 'Nombre':'AH_ciclados', 'Nbytes': 4, 'Adaptar':'x'},
        0x8a:{'Captura': True, 'Nombre':'Nceldas', 'Nbytes': 2, 'Adaptar':'x'},
        0x8b:{'Captura': True, 'Nombre':'Alarma_bat', 'Nbytes': 2, 'Adaptar':'f"{x:016b}"'},
        0x8c:{'Captura': True, 'Nombre':'Status_bat', 'Nbytes': 2, 'Adaptar':'f"{x:04b}"'},
        
        ## RW
        0x8e:{'Captura': True, 'Nombre':'V_total_max', 'Nbytes': 2, 'Adaptar':'round(x/100,2)'},
        0x8f:{'Captura': True, 'Nombre':'V_total_min', 'Nbytes': 2, 'Adaptar':'round(x/100,2)'},
        0x90:{'Captura': True, 'Nombre':'Vcelda_max', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x91:{'Captura': True, 'Nombre':'Vcelda_max_rec', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x92:{'Captura': True, 'Nombre':'T_Vcelda_max', 'Nbytes': 2, 'Adaptar':'x'},
        0x93:{'Captura': True, 'Nombre':'Vcelda_min', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x94:{'Captura': True, 'Nombre':'Vcelda_min_rec', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x95:{'Captura': True, 'Nombre':'T_Vcelda_min', 'Nbytes': 2, 'Adaptar':'x'},
        0x96:{'Captura': True, 'Nombre':'Vdiff_max', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x97:{'Captura': True, 'Nombre':'Imax_descarga', 'Nbytes': 2, 'Adaptar':'x'},
        0x98:{'Captura': True, 'Nombre':'T_Imax_descarga', 'Nbytes': 2, 'Adaptar':'x'},
        0x99:{'Captura': True, 'Nombre':'Imax_carga', 'Nbytes': 2, 'Adaptar':'x'},
        0x9a:{'Captura': True, 'Nombre':'T_Imax_carga', 'Nbytes': 2, 'Adaptar':'x'},
        0x9b:{'Captura': True, 'Nombre':'Vbalance', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x9c:{'Captura': True, 'Nombre':'Vbalance_ini', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x9d:{'Captura': True, 'Nombre':'Rbalance', 'Nbytes': 1, 'Adaptar':'x'},
        0x9e:{'Captura': True, 'Nombre':'Temp_mos_protec', 'Nbytes': 2, 'Adaptar':'x'},
        0x9f:{'Captura': True, 'Nombre':'Temp_mos_protec_rec', 'Nbytes': 2, 'Adaptar':'x'},
        0xa0:{'Captura': True, 'Nombre':'Temp_bat_protec', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0xa1:{'Captura': True, 'Nombre':'Temp_bat_protec_rec', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0xa2:{'Captura': True, 'Nombre':'Temp_bat_protec_diff', 'Nbytes': 2, 'Adaptar':'x'},
        0xa3:{'Captura': True, 'Nombre':'Temp_bat_max_protec_carga', 'Nbytes': 2, 'Adaptar':'x'},
        0xa4:{'Captura': True, 'Nombre':'Temp_bat_max_protec_descarga', 'Nbytes': 2, 'Adaptar':'x'},
        0xa5:{'Captura': True, 'Nombre':'Temp_bat_min_protec_carga', 'Nbytes': 2, 'Adaptar':'x if x<32768 else x-65536'},
        0xa6:{'Captura': True, 'Nombre':'Temp_bat_min_protec_carga_rec', 'Nbytes': 2, 'Adaptar':'x if x<32768 else x-65536'},
        0xa7:{'Captura': True, 'Nombre':'Temp_bat_min_protec_descarga', 'Nbytes': 2, 'Adaptar':'x if x<32768 else x-65536'},
        0xa8:{'Captura': True, 'Nombre':'Temp_bat_min_protec_descarga_rec', 'Nbytes': 2, 'Adaptar':'x if x<32768 else x-65536'},
        0xa9:{'Captura': True, 'Nombre':'Bat_count', 'Nbytes': 1, 'Adaptar':'x'},
        0xaa:{'Captura': True, 'Nombre':'AH_Bat', 'Nbytes': 4, 'Adaptar':'x'},
        0xab:{'Captura': True, 'Nombre':'Mos_Carga', 'Nbytes': 1, 'Adaptar':'x'},
        0xac:{'Captura': True, 'Nombre':'Mos_descarga', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xad:{'Captura': True, 'Nombre':'Icalibracion', 'Nbytes': 2, 'Adaptar':'x'}, 
        0xae:{'Captura': True, 'Nombre':'Direccion', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xaf:{'Captura': True, 'Nombre':'Bat_tipo', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xb0:{'Captura': True, 'Nombre':'Tiempo_dormir', 'Nbytes': 2, 'Adaptar':'x'}, 
        0xb1:{'Captura': True, 'Nombre':'SOC_alarma', 'Nbytes': 1, 'Adaptar':'x'},
        0xb2:{'Captura': True, 'Nombre':'Pass', 'Nbytes': 10, 'Adaptar':'d[p:p+nb].decode().split("\\x00", 1)[0]'}, 
        0xb3:{'Captura': True, 'Nombre':'Mos_especial', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xb4:{'Captura': True, 'Nombre':'ID_equipo', 'Nbytes': 8, 'Adaptar':'d[p:p+nb].decode()'}, 
        0xb5:{'Captura': True, 'Nombre':'Fecha_equipo', 'Nbytes': 4, 'Adaptar':'d[p:p+nb].decode()'}, 
        0xb6:{'Captura': True, 'Nombre':'Tiempo_activo', 'Nbytes': 4, 'Adaptar':'x'}, 
        0xb7:{'Captura': True, 'Nombre':'SW_version', 'Nbytes': 15, 'Adaptar':'d[p:p+nb].decode()'}, #solo R
        0xb8:{'Captura': True, 'Nombre':'Calibracion', 'Nbytes': 1, 'Adaptar':'x'},
        0xb9:{'Captura': True, 'Nombre':'AH_actual', 'Nbytes': 4, 'Adaptar':'x'}, 
        0xba:{'Captura': True, 'Nombre':'ID_fab', 'Nbytes': 24, 'Adaptar':'d[p:p+nb].decode().split("\\x00", 1)[0][12:]'}, 
        
        0xbb:{'Captura': True, 'Nombre':'Restart', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xbc:{'Captura': True, 'Nombre':'Reset', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xbd:{'Captura': True, 'Nombre':'Upgrade', 'Nbytes': 1, 'Adaptar':'x'},
        0xbe:{'Captura': True, 'Nombre':'Voff', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'}, 
        
        0xc0:{'Captura': True, 'Nombre':'Nversion', 'Nbytes': 1, 'Adaptar':'x'}, 
    
     }
   
   }





######################
#### MPPT EASUN ######
######################

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


##########################
#### HIBRIDO ANENJI ######
##########################

# ANENJI 6.2Kw
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

# ANENJI 11Kw
ANENJI11 = {
    'ANENJI11': {'usar':0,
                'dev': '/dev/ttyUSB0',
                'id_modbus': 1,
                'tiempo_captura': 5,
          },
          
    'ANENJI12': {'usar':0,
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


###########################################
#### DONGLE WIFI - ANENJI, ISOLAR,.. ######
###########################################

# permite configurar distintos modelos de equipos
#  - 'ANENJI6K2'   Probado OK
#  - 'ANENJI11K'   Probado OK
#  - 'POWMR10K2'   NO Probado


# script  fv_rs232_wifi.py

RS232_WIFI = {
    'ANENJI1': {                      # Nombre del registro que aparecera en tabla equipos
        'usar': 0,                    # 0: Desactivado - - 1: Activado
        'modelo': 'ANENJI6K2',        # Definir el modelo de equipo entre los modelos disponibles
        'IP': '',                     # IP del dongle WiFi, si '' se asignara segun scan de dongles en LAN
        'tiempo_captura': 5,          # Tiempo entra cada captura
    },
    
    'ANENJI2': {
        'usar': 0, 
        'modelo': 'ANENJI11K',
        'IP': '',
        'tiempo_captura': 5,
    },
    
    'MODELOS_EQUIPOS': {
        
        'ANENJI6K2': {  
            'COMANDOS': {
                'ayuda': ['h','?','i', 'info',''],
                
                'lectura_multiple': {
                    'usar': 1,  # Lectura registro a registro
                    'rangos': [[201, 234], [300, 337], [406, 420]]
                },
            },
            
            'REGISTROS': {
                'WM': {
                    'reg': 201,
                    'tipo': 'adaptar',
                    'adaptar': [
                        "if d == 0: resultado = '0-Power On'",
                        "elif d == 1: resultado = '1-Standby'", 
                        "elif d == 2: resultado = '2-Mains'",
                        "elif d == 3: resultado = '3-Off-Grid'",
                        "elif d == 4: resultado = '4-Bypass'",
                        "elif d == 5: resultado = '5-Charging'",
                        "elif d == 6: resultado = '6-Fault'",
                    ]
                },
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
                
                'Out_modo': {
                    'reg': 300,
                    'rango': [0, 4],
                    'tipo': 'adaptar',
                    'adaptar': [
                        "if d == 0: resultado = '0-Single'",
                        "elif d == 1: resultado = '1-Paralelo'",
                        "elif d == 2: resultado = '2-Fase1'",
                        "elif d == 3: resultado = '3-Fase2'",
                        "elif d == 4: resultado = '4-Fase3'"
                    ]
                },
                
                'Out_prio': {
                    'reg': 301,
                    'tipo': 'adaptar',
                    'escritura': True,
                    'rango': [0, 2],
                    'adaptar': [
                        "if d == 0: resultado = '0-Util_PV_Bat'",
                        "elif d == 1: resultado = '1-PV_Util_Bat'",
                        "elif d == 2: resultado = '2-PV_Bat_Util'"
                    ]
                },

                'Input_range': {'reg':302, 'rango':[0,1], 'escritura': True, 'parametro': 3},
                'Buzzer_mode_range': {'reg':303, 'rango':[0,2], 'escritura': True, 'parametro': 18},
                'LCD_light': {'reg':305, 'rango':[0,1], 'escritura': True, 'parametro': 20},
                'LCD_return': {'reg':306, 'rango':[0,1], 'escritura': True, 'parametro': 19},
                'Over_load_return': {'reg':308, 'rango':[0,1], 'escritura': True, 'parametro': 6},
                'Over_Temp_return': {'reg':309, 'rango':[0,1], 'escritura': True, 'parametro': 7},
                'Over_load_bypass': {'reg':310, 'rango':[0,1], 'escritura': True, 'parametro': 6},
              
                'Vbat_max'   : {'reg':323, 'dec': 1, 'rango':[55,66], 'escritura': True},
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
            },
        },
        
        'ANENJI11K': {  
            'COMANDOS': {
                'ayuda': ['h','?','i', 'info',''],
                   
                'lectura_multiple': {
                    'usar': 1,  # Lectura registro a registro
                    'rangos':[[201,290],[301,391],[600,650],[702,702]]
                },
            },
            
            'REGISTROS': {
                'WM'       :  {'reg':201,         # Working Mode
                             'tipo':'adaptar',
                             'adaptar':[
                                     "if d == 0: resultado = '0-Power On'",
                                     "elif d == 1: resultado = '1-Standby'",
                                     "elif d == 2: resultado = '2-Mains'",
                                     "elif d == 3: resultado = '3-Off-Grid'",
                                     "elif d == 4: resultado = '4-Bypass'",
                                     "elif d == 5: resultado = '5-Charging'",
                                     "elif d == 6: resultado = '6-Fault'",
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
                                     "if d == 0: resultado = '0-Single'",
                                     "elif d == 1: resultado = '1-Paralelo'",
                                     "elif d == 2: resultado = '2-Fase1'",
                                     "elif d == 3: resultado = '3-Fase2'",
                                     "elif d == 4: resultado = '4-Fase3'"
                                     ]
                            },
              
                'Out_prio' : {'reg':601,
                             'tipo':'adaptar',
                             'rango':[1,3],
                             'escritura': True,
                             'adaptar':[
                                     "if d == 0: resultado = '0-???Util_PV_Bat'",
                                     "elif d == 1: resultado = '1-SUB'",
                                     "elif d == 2: resultado = '2-SBU'",
                                     "elif d == 3: resultado = '3-SUF'"                                     
                                     ]
                            },
                'Tipo_Bat' : {'reg':630,
                             'tipo':'adaptar',
                             'rango':[0,8],
                             'escritura': True,
                             'adaptar':[
                                     "if d == 0: resultado = '0-AGM'",
                                     "elif d == 1: resultado = '1-FLD'",
                                     "elif d == 2: resultado = '2-USER'",
                                     "elif d == 4: resultado = '4-Li2'",
                                     "elif d == 6: resultado = '6-Li4'",
                                     "elif d == 8: resultado = '8-LiB'"                                     
                                     ]
                            },
                'Prioridad_carga' : {'reg':632,
                                   'tipo':'adaptar',
                                   'rango':[0,4],
                                   'escritura': True,
                                   'adaptar':[
                                     "if d == 1: resultado = '1-SOF'",
                                     "elif d == 2: resultado = '2-SNU'",
                                     "elif d == 3: resultado = '3-OSO'",
                                     "elif d == 4: resultado = '4-SOR'",
                                     "elif d == 0: resultado = '0 ??'"
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

            },

        },

        'POWMR10K2': {  
            'COMANDOS': {
                'ayuda': ['h','?','i', 'info',''],
                   
                'lectura_multiple': {
                    'usar': 1,  # Lectura registro a registro
                    'rangos':[[4501,4564]]
                },
            },
            
            'REGISTROS': {
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

        },


    },   
}



##########################
#### MPPT EPEVER    ######
##########################

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
              
              'Vplaca'    : {'reg':0x3100, 'dec':2, 'fc': 4},   # Voltaje Placas
              'Wplaca'    : {'reg':0x3102, 'dec':2, 'fc': 4},   # Watios Placas ...registro bajo
               
              'Vbat'      : {'reg':0x331A, 'dec':2, 'fc': 4},   # Voltaje baterias
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



##########################
#######  GROWATT    ######
##########################

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


##########################
#####  POWMR 10.2Kw ######
##########################

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


###################################
#####  CENTRAL METEO ECOWITT ######
###################################

ECOWITT = {
    'ECOWITT': {
        'usar': 0,
        'APPLICATION_KEY': 'XXXXXXXXXXXXXXX',
        'API_KEY' : 'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy',
        'MAC' :  'ZZ:ZZ:ZZ:ZZ:ZZ:ZZ',
        't_muestra' : 60 # tiempo entre capturas
    }
}

###################################
##########  RELES TUYA ############
###################################

# SCAN: Si no se incluye o esta a False  solo se capturan los reles definidos.... 
#       .....con True se añaden a EQUIPOS todos los dispositivos que se detecten en el scan de la LAN

# TABLA : False implica que NO se guardan los datos historicos en la tabla TUYA
# CREAR_RELE : False implica que NO se creara el rele correspondiente en la tabla reles
# MODO: Por defecto el rele se creara con modo "MAN" salvo que se especifique otro modo (ON. OFF,....)
# tmuestra: tiempo entre capturas (15sg por defecto)

TUYA = {
    'usar': 0,
    
    'tmuestra': 15,
    
    'SCAN': True,
    
    'RELES':{
        801 : {'Nombre': 'Rele 801', 'ID': 'XXXX1', 'KEY': 'YYYY1'},
        802 : {'Nombre': 'Rele 802', 'ID': 'XXXX2', 'KEY': 'YYYY2', 'TABLA': False, 'CREAR_RELE': False},
        
    }
}


# ====================================================================
# ====================================================================
#    3.- SECCION PARAMETRIZACION SERVICIOS ADICIONALES 
# ====================================================================
# ====================================================================

###############################
###### Telegram & MOTION ######
###############################
usar_telegram = 0 # 1 para usar  ..... 0 para no usar
TOKEN ='XXXXXX:YYYYYYYYYY......'# bot Telegram...cambiar por el que cada uno de de alta

# ID de Usuarios autorizados a mandar mensajes, los msg periodicos se mandan al primer declarado
Aut = [111111,22222] # Lista de ID de Telegram autorizados

cid_alarma = 1111111 # # Id Telegram a donde se enviara la foto/video de alarma

msg_periodico_telegram = 0 # 1 = Manda un mensaje resumen por Telegram cada Hora -- 0 = No manda mensaje

# Configuracion mensaje Telegram

#  --- IMAGEN ---
region_captura_pantalla = [0, 0, 0, 0, 0] #(Activar envio imagen, X, Y, Ancho, Alto) manda la captura de la region de pantalla
acciones_mouse = [''] # lista de comandos para gestionar el mouse, teclas etc... .por ejemplo pyautogui.moveTo(900,800) moveria el puntero del raton al punto (900,800)

#  --- TEXTO ----
#   Se puede incluir...  {cualquier campo de la tabla equipos}, texto, unicodes,....
#   Tambien existen algunas variables propias definidas 
#      {L_celdas}         Linea con valor max y min de las celdas
#      {L_reles}          Una unica linea con informacion resumida de los reles
#      {L_reles_unicode}  Una linea por cada rele
#      {L_temp}           Una linea con temperaturas CPU y DS18b20 
#      {temperaturas}     Una linea con temperaturas DS18b20 
#      {L_ip_local}       IP LAN local
#      {L_ip}             IP WAN

#unicodes para categorizar reles  ....primera dupla= ('texto que no exista en reles', 'unicode por defecto')
unicode_reles_telegram = [('ñññ###','\U0001F6A6'),('luz','\U0001F526'),('cale','\U0001F525')] # duplas (texto, unicode) para primer simbolo de {L_reles_unicode}

msg_telegram = ["\U0001F50B <b><u>Batería</u></b>: (<code>{d_['FV']['Mod_bat']}</code>)",
				"     SOC: <b>{d_['FV']['SOC']:.1f}</b>%     \U000024CB <b>{d_['FV']['Vbat']:.1f}</b>V     \U000024BE <b>{d_['FV']['Ibat']:.1f}</b>A",
				#"     \U0001F4CA {L_celdas}",

                "\U0001F31E <b><u>Placas</u></b>:",
                "     \U000024C5 <b>{d_['FV']['Wplaca']:.0f}</b>W     \U000024BE <b>{d_['FV']['Iplaca']:.1f}</b>A     \U000024CB <b>{d_['FV']['Vplaca']:.0f}</b>V",

                "\U0001F4A1 <b><u>Consumo</u></b>:",
                "     \U000024C5 <b>{d_['FV']['Wconsumo']:.0f}</b>W     \U000024BE <b>{d_['FV']['Iplaca']-d_['FV']['Ibat']:.1f}</b>A     PWM: <b>{d_['FV']['PWM']:.0f}</b>",
                
                "\U00002753 <b><u>Relés</u></b>:",
                "<b>{L_reles_unicode}</b>",
                
                #"\U0001F50C <b><u>Red</u></b>:",
                #"     \U000024C5 <b>{d_['FV']['Wred']:.0f}</b>W     \U000024BE <b>{d_['FV']['Ired']:.1f}</b>A     \U000024CB <b>{d_['FV']['Vred']:.0f}</b>V",

                "\U0001F4C6 <b><u>Diario (KWh)</u></b>:",
                "     \U0001F31E <b>{d_['FV']['Wh_placa']/1000:.1f}</b> \U0001F50B <i>{d_['FV']['Whp_bat']/1000:.1f}-{d_['FV']['Whn_bat']/1000:.1f}</i> = <b>{(d_['FV']['Whp_bat']-d_['FV']['Whn_bat'])/1000:.1f}</b> \U0001F4A1 <b>{(d_['FV']['Wh_consumo'])/1000:.1f}</b>",
                #"     \U0001F50C <b>{(d_['FV']['Wh_red'])/1000:.1f}</b>",

                "\U0001F321 <b><u>Temperaturas (ºC)</u></b>:",
                "     Bat: <b>{d_['FV']['Temp']}</b> / CPU: <b>{d_['TEMP']['Temp_cpu']:.1f}</b>",

                "\U0001F4BB <b><u>Conexión (IP)</u></b>:",
                "     \U0001F3E0 {L_ip_local}  \U0001F30D <span class='tg-spoiler'>{L_ip}</span>",
                ]

# Botones personalizados que aparecen con opcion /C
# El comando puede incluir una descripcion tras  el caracter :
cmd_telegram = [
'#i : Informacion',
]

botones_visibles_una_vez = False # Se mantienen desplegados o no los botones personalizados

# -----------------------------------------------

#########################
###### PV_OUTPUT ########
#########################
usar_pvoutput = 0 # 1 para usar  ..... 0 para no usar

pvoutput_key = "xxxxxxxx" # Key PVoutput
pvoutput_id = "1233455"
# -----------------------------------------------

#########################################################
###### Vigilancia por Camara con Motion y Clarifai ######
#########################################################

usar_motioneye = 0 # activa servicio motioneye

motion_telegram = 0 # 1 = Envia foto deteccion a Telegram

motion_clarifai = 0 # activa reconocimiento por Clarifai
api_key = 'xxxxxxxxxxxx' # Key Clarifai
workflow_id = 'yyyyyyyy' # Nombre del Workflow creado en Clarifai

# fconfiguración horaria para motion
# dias de la semana 1-7. Horas 24 bits 0=no grabar 1=si
horario_alarma = {
    1:'111111110000000000000000',
    2:'111111110000000000000000',
    3:'111111110000000000000000',
    4:'111111110000000000000000',
    5:'111111110000000000000000',
    6:'111111111000000000000000',
    7:'111111111000000000000000'}

# -----------------------------------------------
#########################################################
################  AEMET ###############################
#########################################################

localidad = ''  # Numero de Localidad segun AEMET

variables = 'ctl' # c= cielo   t = temperatura   l = lluvia

# Estimacion Kwh por estado del cielo y franja horaria
Cielo_Kwh = {"Despejado":{"06-12": 0,"12-18": 0},
       "Poco nuboso": {"06-12": 0,"12-18": 0},
       "Nubes altas": {"06-12": 0,"12-18": 0},
       "Intervalos nubosos": {"06-12": 0,"12-18": 0},
       "Nuboso": {"06-12": 0,"12-18": 0},
       "Muy Nuboso": {"06-12": 0,"12-18": 0},
       "Cubierto": {"06-12": 0,"12-18": 0}
       }


#########################################################
############  TUTIEMPO IRRADIACION ######################
#########################################################

irradiacion = {
    'url': "https://www.tutiempo.net/radiacion-solar/titulcia.html"
}


crontab = {
    # TELEGRAM
    'mensaje_telegram': {'activo': 1,
                         'comando': ['python', 'fvbot_msg.py'],
                         'horas': ['01:00','02:00','03:00','04:00','05:00','06:00',
                                   '07:00','08:00','09:00','10:00','11:00','12:00',
                                   '13:00','14:00','15:00','16:00','17:00','18:00',
                                   '19:00','20:00','21:00','22:00','23:00','23:59',],
                         'periodo': 0, # cada X minutos
                         'log': 0
                        },
                        
    # PROCESOS BD                    
    'comprimir_bd':     {'activo': 1,
                         'comando': ['python', 'fv_comprimir_BD.py'],
                         'horas': [],
                         'periodo': 10,
                         'log': 0 
                        },
    'gestion_bd':       {'activo': 1,
                         'comando': ['python', 'fv_gestionbd.py','-v','-c','-b'],
                         'horas': ['05:32'],
                         'periodo': 0, 
                         'log': 1
                        },
    'diario':           {'activo': 1,
                         'comando': ['python', 'diario.py'],
                         'horas': [],
                         'periodo': 30,
                         'log': 0 
                        },
                        
     'diario_back':     {'activo': 1,
                         'comando': ['python', 'diario.py','-ini0', '-fin7'],
                         'horas': ['00:10'],
                         'periodo': 0,
                         'log': 0 
                        },
     'SOH':             {'activo': 1,
                         'comando': ['python', 'fv_soh.py'],
                         'horas': ['01:03'],
                         'periodo': 0,
                         'log': 0 
                        },
                        
    # Reinicio Servicios
    'fv_temp':          {'activo': 1,
                         'comando': ['sudo','systemctl','restart', 'fv_temp'],
                         'horas': [],
                         'periodo': 60,
                         'log': 0
                        },
    'fv_oled':          {'activo': 1,
                         'comando': ['sudo','systemctl','restart', 'fv_oled'],
                         'horas': [],
                         'periodo': 60,
                         'log': 0
                        },
    'fvbot':            {'activo': 0,
                         'comando': ['sudo','systemctl','restart', 'fvbot'],
                         'horas': [],
                         'periodo': 60,
                         'log': 0
                        },
                                                               
    # DESCARGA DATOS AEMET                      
    'AEMET':            {'activo': 0,
                         'comando': ['python', 'aemet.py'],
                         'horas': ['01:03'],
                         'periodo': 0,
                         'log': 0 
                        },

    # DESCARGA DATOS IRRADIACION SOLAR                      
    'IRRADIACION':      {'activo': 0,
                         'comando': ['python', 'fv_irradiacion.py'],
                         'horas': ['00:30','08:03','20:12'],
                         'periodo': 0,
                         'log': 1 
                        },
                        
    # DESCARGA a PVOutput.org                      
    'PVOutput':         {'activo': 0,
                         'comando': ['python', 'pvoutput_live.py'],
                         'horas': [],
                         'periodo': 5, 
                         'log': 0
                        },
    # EJEMPLOS de uso de crontab para mandar comandos al Hibrido
    'Hibrido_Inicio_dia':{'activo': 0,
                         'comando': ['python', 'fvbot_msg_hibrido.py','PCVV29.2','PCVV29.2','PBFT29.2'],
                         'horas': ['09:10'],
                         'periodo': 0,
                         'log': 1 
                        },
     
          }
