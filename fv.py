#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-12-30

import time,sys
import traceback
import datetime
import MySQLdb 
import random # para simulacion usando random.choice
import pickle,json

from smbus import SMBus

import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token
import paho.mqtt.client as mqtt

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
"""
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Style: DIM, NORMAL, BRIGHT, RESET_ALL
"""
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' PVControl+') #+Style.RESET_ALL)

import RPi.GPIO as GPIO # reles 4XX via GPIO
GPIO.setmode(GPIO.BOARD) #para reles SSR en pines RPi
#GPIO.setmode(GPIO.BCM) #para reles SSR en pines RPi
GPIO_PINES_PCB = [11,12,13,15,16,18,22,29] # Numero de pines que presenta la PCB

import locale
locale.setlocale(locale.LC_ALL, ("es_ES", "UTF-8")) #nombre mes en Castellano

import subprocess
import click # para DEBUG parando ejecucion donde se quiera

basepath = '/home/pi/PVControl+/'
parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"

try:
    #Parametros Instalacion FV
    from Parametros_FV import *

    from Srne import Srne # Libreria reguladores SRNE

    #aseguro que los valores introducidos en Parametros_FV.py son float
    AH = float(AH)
    CP = float(CP)
    EC = float(EC)  
    vflotacion = float(vflotacion)
    
    if usar_telegram == 1:
        bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
        bot.skip_pending = True # Skip the pending messages
        cid = Aut[0]
    try:
        bus = SMBus(1) # Activo Bus I2C para PCF
    except:
        pass

except:
    print ('Error irrecuperable en Parametros_FV.py')
    
    
#Comprobacion argumentos en comando de fv.py
narg = len(sys.argv)
DEBUG= 0
DEBUG1 = ''
if '-p1' in sys.argv: DEBUG= 1 
elif '-p2' in sys.argv: DEBUG= 2 
elif '-p3' in sys.argv: DEBUG= 3
elif '-p4' in sys.argv: DEBUG= 50
elif '-p' in sys.argv: DEBUG= 100
if '-r' in sys.argv: DEBUG1= 'RELES'
elif '-t' in sys.argv: DEBUG1= 'TEST'
 
print (Fore.RED + f'DEBUG={DEBUG} - DEBUG1={DEBUG1}')
#########################################################################################
#              Inicializando las variables del programa
#########################################################################################

NDIA = {'0':'D','1':'L','2':'M','3':'X','4':'J','5':'V','6':'S'} # Condiciones de dia de la semana

Grabar = 1 # Contador ciclo grabacion en BD

hora_m = time.time() #para calcular tiempo entre muestras real
dia = time.strftime("%Y-%m-%d") # para cambio de dia y reinicializar Wh
tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
minuto = time.strftime("%H:%M")

t_muestra = 5.0 # Inicializo Tiempo entre muestra real...idealmente TP['t_muestra']
t_muestra_1 = t_muestra_2 = t_muestra_3 = t_muestra_4 = t_muestra_5 = t_muestra_6 = 0.0 # muestras t ejecucion intermedias
T_ejecucion = T_ejecucion_max = 0.0

#---Variables Bateria --------------------------------
Ibat = 0.0                  # Intensidad Bateria
Vbat = vsis * 12.0          # Voltaje Bateria inicial
DS = SOC = 0.0              # control SOC bateria
Mod_bat =''
Vflot = Vabs = Vequ = 0.0   # Voltaje asociado a estado de flotacion/Absorcion/Ecu
Tflot = Tabs = Tequ = 0.0   # Tiempo asociado a estado de flotacion/Absorcion/Ecu
Tflot_bulk = Tbulk = 0.0    # Tiempo asociado al paso de FLOT a BULK 
SOC_max = SOC_min = 0.0     # Variable para guardar SOC maximo y minimo diario
Vbat_max = Vbat_min = 0.0   # Variable para guardar Vbat maximo  y minimo diario
flag_Abs= flag_Flot = 0     # Flags de Absorcion y Flotacion
Vabs = Vflot = 0.0          # Valores de Absorcion y Flotacion
Wh_bat = Whp_bat = Whn_bat = 0.0
Wbat = 0.0

#---Variables calculo SOC --------------------------------
Ip = Ip1 = Ip2 = 0.0

#---Variables Watios --------------------------------
Wplaca = Iplaca = Vplaca = 0.0   # w, V e Intensidad de Placas(valor intensidad tras el regulador)
Wh_placa = Wh_consumo = 0.0
Wconsumo = 0.0

#---Variables Auxiliares --------------------------------
Aux1 = Aux2 = 0.0       # Valores de captura auxiliares (salida regulador, Iplaca2, etc)
CD1 = CD2 = CD3 = CD4 = CD5 = 0.0 # contadores que se ponen a cero cada dia
C1 = C2 = C3 = C4 = C5 = 0.0      # contadores que NO se ponen a cero cada dia
Nlog = Nlog_max = 30 # Contador Numero de log maximos cada minuto
log=''               # Valor del log 

#---Variables Red Comercial / Generador---------------------------
Wred = Ired = Vred = EFF = 0.0     # Valores de red AC
Vred_max = 0.0  
Vred_min = 10000.0                   # Variables para guardar Vred maximo  y minimo diario
Wh_red = Whp_red = Whn_red = 0.0   # Variables para guardar Wh inyectados o consumidos de red
EFF_max = 0.0
EFF_min = 100.0                      #Variables para guardar Eficiencia DC/AC maxima y minima diaria

#---Variables temperatura --------------------------------
Temp_Bat = 0.0     # temperatura baterias
Coef_Temp = 0.0    # Coeficiente de compensacion de temperatura para Vflot/Vabs 
Vbat_temp = 0.0    # Compensacion de temperatura en valor Vbat

#---Variables reles --------------------------------
t_refresco_rele = time.time() #utilizado en secuenciacion escritura de refresco en reles
Puerto = estado = 0

## Definir diccionarios Rele y Rele_Ant
Rele: dict = {}        # Situacion actual de los reles
Rele_Dict: dict = {}   # Diccionario completo de la tabla de Reles
Rele_Dict_Aux: dict = {}   # Diccionario completo de la tabla de Reles--copia para actualizacion/borrado

Rele_Ant: dict = {}    # Situacion anterior de los reles
Rele_H: dict = {}      # Situacion condiciones horario
Rele_Tiempo: dict = {} # Tiempo activo en segundos de cada rele en el dia

datos_FV: dict = {}  # datos que se publican en tabla equipos y se usan en pagina web inicio
d_: dict ={}         # diccionario de captura de equipos
Estado : dict ={}    # diccionario del estado de funcionamiento de fv.py 

#---Variables PID --------------------------------
N = 5  # numero de muestras para control PID
Lista_errores_PID = [0.0 for i in range(5)]
PWM = IPWM_P = IPWM_I = IPWM_D = PWM_ant = 0.0


#########################################################################################
# Creacion tabla RAM equipos en BD si no existe
#########################################################################################
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    # Comprobacion si tabla equipos existe y si no se crea
    sql_create = """ CREATE TABLE IF NOT EXISTS `equipos` (
                  `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
                  `tiempo` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha Actualizacion',
                  `sensores` varchar(5000) COLLATE latin1_spanish_ci NOT NULL,
                   PRIMARY KEY (`id_equipo`)
                 ) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""

    import warnings # quitamos el warning que da si existe la tabla equipos
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cursor.execute(sql_create)
        
    try: #inicializamos registros en BD RAM
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('FV','{}'))
        db.commit()              
    except:
        pass
    try: 
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('RELES','{}'))
        db.commit()
    except:
        pass    
    try:
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('_PVControl+','{}'))
        db.commit()              
    except:
        pass
    

    try:
        sql = 'SELECT * FROM equipos'
        nequipos = int(cursor.execute(sql))
        for row in cursor.fetchall(): d_[row[0]] = json.loads(row[2])

    except:
        print (Fore.RED+'Error lectura tabla equipos')


except:
    print (Fore.RED,'ERROR inicializando tabla equipos... abortando PVControl+')
    sys.exit()


#########################################################################################
#                 DEFINICION DE FUNCIONES
#########################################################################################

# -----------------------MQTT MOSQUITTO ------------------------

def on_connect(cli, userdata, flags, rc):
    #print("Connected with result code "+str(rc))
    cli.subscribe("PVControl/Log")
    cli.subscribe("PVControl/Opcion")
     
def on_disconnect(cli, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")
    else:
        cli.loop_stop()
        cli.disconnect()

def on_message(client, userdata, msg):
    global pub_time
    
    #print(msg.topic+" "+str(msg.payload))
    if msg.topic== "PVControl/Log":
        try:
            db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor1 = db1.cursor()
            cursor1.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo, str(msg.payload)))
            db1.commit()
        except:
            db1.rollback()
        try:
            cursor1.close()
            db1.close()
        except:
            pass
    elif msg.topic== "PVControl/Opcion":
        pub_orden=str(msg.payload)
        print (pub_orden)
        
        if pub_orden == "PUB_TIME_ON":
            pub_time=1
        elif pub_orden == "PUB_TIME_OFF":
            pub_time=0

             
client = mqtt.Client("fv") #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
try:
    client.connect(mqtt_broker, mqtt_puerto) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.2)
client.loop_start()

# --------------------- DEFINICION DE FUNCIONES --------------
def calibracion_rele(adr,out): # linealiza la respuesta del SSR por cada rele segun campo calibracion en tabla reles
    try: 
        #out1 = out #estado original
        ssr = json.loads(Rele_Dict[adr]['calibracion'])
        if len(ssr) > 0: # solo si existe calibracion
            for i in range(len(ssr)):
                if ssr[i][0] > out : break
            x1, y1 =  ssr[i-1][0], ssr[i-1][1] # puntos de la recta
            x2, y2 =  ssr[i][0], ssr[i][1]
            out = (y1 + (y2-y1)/(x2-x1)*(out-x1)) # ecuacion recta
    except:
        pass 
    #print ('ssr=',ssr)
    #print (adr,' Potencia=',out1, 'PWM=',out)
    return out

def act_rele(adr,out,tipo) :
    # Activar Reles
    #tipo = 0 funcionamiento normal ...se actualiza marca temporal
    #tipo = 1 Fuerzo actualizacion ... marca temporal a 0
    #tipo = 2 Refresco ... no actualiza marca temporal
    try:
        cambio = Rele_Dict[adr]['cambio']
        
        if tipo == 0: # modo normal de actuacion
            if out == Rele_Ant[adr]:
                return Rele[adr], cambio # no se actua sobre los reles ni marca temporal por tener misma salida
            else:
                if time.time() < Rele_Dict[adr]['retardo'] + Rele_Dict[adr]['cambio']:
                    if DEBUG == 50:
                        print (Fore.GREEN + time.strftime("%H:%M:%S"),
                               f"Cambio...T{time.time():.1f} - R{Rele_Dict[adr]['retardo']} - C{Rele_Dict[adr]['cambio']:.1f} sg "+
                               f'- Orden {out} - Dejando Rele {adr} con valor {Rele_Ant[adr]} ')     
                    return Rele_Ant[adr], cambio
                            
            if DEBUG == 50:
                print (Fore.RED + time.strftime("%H:%M:%S"),f'- Activando rele {adr} con valor {out}',
                       f"Cambio...T{time.time():.1f} - R{Rele_Dict[adr]['retardo']} - C{Rele_Dict[adr]['cambio']:.1f} sg",
                       f"= T{time.time()- Rele_Dict[adr]['retardo'] - Rele_Dict[adr]['cambio']:.1f} sg")
            cambio = round(time.time(),1)
        
        elif tipo == 1: # ON/OFF forzado
            if DEBUG == 50: print (Fore.RED + time.strftime("%H:%M:%S"),f'- Forzado rele {adr} con valor {out}')
            cambio = 0
            
        elif tipo == 2: # Refresco
            if DEBUG == 100: print(Fore.BLUE+f'Refresco rele {adr}')   
        
        # ----- Activacion real de Reles -----------    
        if simular_reles == 0:
            if int(adr/100) == 2: #Rele WIFI por MQTT
                try:
                    out1 = calibracion_rele(adr,out)
                    client.publish(f'PVControl/Reles/{adr}',int(out1))  # via MQTT
                    
                except:
                    if simular != 1:
                        logBD(f'Error rele wifi {adr}= {out1}')   

            elif int(adr/100) == 3: # Rele I2C
                adr_pcf=int(adr/10)
                puerto= adr%adr_pcf
                try:
                    estado = bus.read_byte(adr_pcf)  #devuelve el valor en decimal
                    if out == 100 :
                        i2c_out = estado & (2**(puerto-1) ^ (255))
                    else :
                        i2c_out = estado | 2**(puerto-1)
                    bus.write_byte(adr_pcf,i2c_out)
                    
                except:
                    if simular != 1:
                        logBD(f'Error bus I2C {adr}= {out}')

            elif int(adr/100) == 4: # Rele GPIO .. esta por regulacion SC
                try:
                    #if DEBUG >= 2: print('rele GPIO=',adr, int(out))
                    for I in range (NGPIO):
                        if Rele_SSR[I][1] == adr % 100:
                            out1=int(out) #por ahora resolucion maxima de 1 
                            
                            #print('rele GPIO=',adr, 'duty=',int(out1))
                            
                            Rele_SSR[I][0].ChangeDutyCycle(out1)
                            if out1 == 0 or out1 == 100:
                                pass
                                #Rele_SSR[I][0].ChangeFrequency(5)
                            elif out1 <= 50:
                                #print (' frec=',out)
                                Rele_SSR[I][0].ChangeFrequency(out1)
                            else:
                                Rele_SSR[I][0].ChangeFrequency(100-out1)
                                #print (' frec=',100-out1)
                            break
                except:
                    print ('Error rele GPIO')
                    print (I, Rele_SSR[I][0],Rele_SSR[I][1], adr,out1)         

            elif int(adr/100) == 5: #Rele Sonoff (tasmota)
                try:
                    if out == 100: out1 = "ON"
                    else:          out1 = "OFF"
                    client.publish(f"cmnd/PVControl/Reles/{str(adr)[0:2]}/POWER",str(out1))  # via MQTT
                except:
                    logBD(f'Error TASMOTA ON/OFF {adr}={out} - ´{out1}')
            
            elif int(adr/100) == 6: #Rele TASMOTA
                try:
                    out1 = calibracion_rele(adr,out)
                    duty = int(out1 *10.23)
                    #if out < 50: Freq = out 
                    #else: Freq= 100 - out
                    #client.publish("cmnd/PVControl/Reles/"+str(adr)[0:2]+"/PwmFrequency",str(Freq))  # Freq via MQTT 
                    client.publish("cmnd/PVControl/Reles/"+str(adr)[0:2]+"/PWM"+str(adr)[-1],str(duty))  # Logica positiva PWM via MQTT 
                    
                except:
                    logBD(f'Error TASMOTA AF / SC {adr}={out}') 
    except:
        log = f'Error no reconocido en activacion rele={adr} valor={out}  tipo={tipo}'
        print (log)
        logBD(log)        
         
    return out, cambio

def logBD(texto) : # Incluir en tabla de Log
    global Nlog, minuto

    Nlog -=1
    if time.strftime("%H:%M") != minuto:
        minuto = time.strftime("%H:%M")
        Nlog = Nlog_max

    if Nlog > 0:
        try: 
            cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,texto))
            #print (tiempo,' ', texto)
            db.commit()
        except:
            db.rollback()

    return

def leer_sensor(variable, sensor) :  # leer sensor
    try:
        try:
            anterior = eval(variable)
        except:
            anterior = 0.0
            
        y_err = 0 # error en lectura 0= No error....1= Error lectura.....2= Error limites max/min
        y = round(float(eval(sensor['Equipo'])),3)
    
    except:
        #traceback.print_exc()
        
        print (Fore.RED+f'Error en sensor..{variable } ..valor anterior = {anterior}   - ',flush=True, end='')
        y = anterior
        y_err = 1
    
    if 'Min' in sensor.keys() : 
        if y < sensor['Min']:
            print (Fore.RED+f"Error:{variable}={y}/Min={sensor['Min']}. Valor anterior={anterior}..", flush=True,end='')     
            logBD(f'lectura incoherente {variable}={y}')
            y = anterior
            y_err = 2 
    
    if 'Max' in sensor.keys() : 
        if y > sensor['Max']:
            print (Fore.RED+f"Error:{variable}={y}/Max={sensor['Max']}. Valor anterior={anterior}.. ", flush=True,end='')     
            logBD(f'lectura incoherente {variable}={y}')
            y = anterior
            y_err = 2 

    return y,y_err

def Calcular_PID (sensor,objetivo,P,I,D):
    global Lista_errores_PID, IPWM_P, IPWM_I, IPWM_D
    
    valor = eval(sensor)
    
    # Desplazamos un elemento en la Lista de errores
    Lista_errores_PID = Lista_errores_PID[-1:] + Lista_errores_PID[:-1] 
    
    # Calculo Termino Proporcional PID
    error_actual = Lista_errores_PID[0] = valor - objetivo
    
    # Calculo Termino Integral PID
    error_integral = 0
    for i in range(N-1):
        error_integral += (Lista_errores_PID[i]+Lista_errores_PID[i+1])/2/N
 
    # Calculo Termino Diferencial PID
    error_diferencial = Lista_errores_PID[0]-Lista_errores_PID[1]

    IPWM_P = P * error_actual
    IPWM_I = I * error_integral
    IPWM_D = D * error_diferencial

    #IPWM = P * error_actual + I * error_integral + D * error_diferencial
    IPWM = IPWM_P + IPWM_I + IPWM_D
    
    return IPWM
       
def Calcular_PWM(PWM):
    #global Diver #,PWM
    
    Objetivo_PID= TP['objetivo_PID']
    if TP['sensor_PID']== 'Vbat':  Objetivo_PID += Vbat_temp # añade compensacion temperatura
    
    Diver = Calcular_PID (TP['sensor_PID'],Objetivo_PID,TP['Kp'],TP['Ki'],TP['Kd']) # 'sensor', objetivo, P,I,D 
    
    Diver_Max = 200 # Ya veremos si lo pongo en Parametros_FV.py
    if Diver > Diver_Max: Diver = Diver_Max
    elif Diver < -Diver_Max : Diver=-Diver_Max
    
    PWM += Diver
    
    if PWM >= PWM_Max: PWM = PWM_Max
    if PWM <= 0: PWM = 0

    return PWM


#########################################################################################
#    INICIALIZACION PVControl+
#########################################################################################

## RECUPERAR DE LA BD ALGUNOS DATOS ##
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql="""SELECT DS, DATE(Tiempo),Whp_bat,Whn_bat,Wh_placa, SOC, Vbat,Whp_red,Whn_red
         FROM datos ORDER BY id DESC limit 1"""
                 
    cursor.execute(sql)
    var=cursor.fetchone()
    DS=float(var[0])
    HOY=str(var[1])
    SOC_min = SOC_max =float(var[5])
    Vbat_min = Vbat_max = float(var[6])
    
    if HOY == time.strftime("%Y-%m-%d"): #Comprueba que es el mismo dia
        Whp_bat = float(var[2])
        Whn_bat = float(var[3])
        Wh_placa = float(var[4])
        Whp_red = float(var[7])
        Whn_red = float(var[8])
            
        sql='SELECT min(SOC), max(SOC), min(Vbat), max(Vbat) FROM datos WHERE Tiempo >= CURDATE()'
        cursor.execute(sql)
        var=cursor.fetchone()
        SOC_min = float(var[0])
        SOC_max = float(var[1])
        Vbat_min = float(var[2])
        Vbat_max = float (var[3])        
    else:
        Whp_bat = Whn_bat = Wh_placa = Whp_red = Whn_red = 0.0

except Exception as e:
    print ("Sin registros en la tabla datos")


# inicializando variables definidas en Parametros_FV.py

while True:
    errores = 0
    Estado['PVControl+'] = 'OK'
    Estado['PVControl+_error'] = ''
    print()
    print (Fore.GREEN+'#' *80)
    print (Fore.CYAN+'Captura inicial de los sensores')
    try:
        for sensor in sensores:
            print (Fore.RESET+f"{sensor}"+Fore.MAGENTA+f" = {sensores[sensor]}", end=' = ')
            try:
                if type(sensores[sensor]) is dict:
                    if 'Equipo' in sensores[sensor].keys():
                        exec(f'{sensor}, {sensor}_err =leer_sensor("{sensor}",{sensores[sensor]})' )
                        print (Fore.GREEN,end='')
                        if eval(f'{sensor}_err') == 1:
                            errores += 1
                            #Estado['Sensor_error'] = errores
                            Estado['PVControl+'] = 'ERROR'
                            
                    else:
                        print (Fore.RED+'Variable sin sensor definido = ',end='')
                        exec (f'{sensor}= 0.0')
                elif type(sensores[sensor]) is set:
                    l = list (sensores[sensor])
                    try:
                        exec (f'{sensor}= {l[0]}')
                    except:
                        exec (f'{sensor}= 0.0')
                        Estado['PVControl+'] = 'ERROR'
                
                elif type(sensores[sensor]) in (int,float,str):
                    try:
                        exec (f'{sensor}= {sensores[sensor]}')
                    except:
                        exec (f'{sensor}= 0.0')
                    
                    
            except:
                print('Error no conocido en sensores')
                    
            print ( f'{eval(sensor)}')
    except:
        print (Fore.RED,'ERROR no conocido en definicion sensores en Parametros_FV.py')
        #sys.exit()

    print (Fore.GREEN+'#' *80)
    if DEBUG1 != 'TEST': break
    else: 
        print (Fore.RED+f'  Nº errores en definicion de sensores = {errores}')
        salir = click.prompt(Fore.CYAN + '     pulse 0 para salir... 1 para otro bucle de test ..... ', type=int, default=0)
        if salir == 0: break
        else: exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios

        
print()

##  ------ inicializamos reles ------------------------
sql = 'SELECT * FROM reles'
nreles = cursor.execute(sql)
nreles = int(nreles)  # = numero de reles
columns = [column[0] for column in cursor.description] # creacion diccionario Tabla Reles
TR=[] 
for row in cursor.fetchall(): TR.append(dict(zip(columns, row)))
TR_refresco = TR[:] # lista copia de tabla reles para ir refrescando 1 valor por ciclo en los reles

Rele_SSR = [ ]
NGPIO =0 # Num Reles GPIO

for r in TR: # inicializando reles
    id_rele = r['id_rele']
    Rele[id_rele] = Rele_Ant[id_rele] = Rele_H[id_rele] =  0
    tipo_rele = int(id_rele/100)
    Rele_Dict[id_rele] = r.copy() # guardo todo los campos de la tabla Reles en BD            
    Rele_Dict[id_rele]['cambio'] = 0 # inicializo a 0 la marca temporal para permitir cambio al iniciar programa
    Rele_Dict[id_rele]['nconmutaciones']= 0  # inicializo a 0 el numero de conmutaciones del dia
    Rele_Dict[id_rele]['segundos_on']= Rele_Tiempo[id_rele] = 0  # inicializo a 0 el tiempo en funcionamiento del dia
    
    try: # aseguro que existe el registro diario de actividad del rele
        cursor.execute("INSERT INTO reles_segundos_on (id_rele,fecha,segundos_on,nconmutaciones) VALUES (%s,%s,%s,%s)",
                       (id_rele,time.strftime("%Y-%m-%d"),0,0))
    except:
        #print ('Ya existe registro del rele en tabla reles_segundos_on')
        pass    
    
    if r['modo'] == 'PRG': # apago todos los reles en modo PRG por defecto
        Rele[id_rele], i = act_rele(id_rele,0,2) # No actualizo la marca temporal de cambio

    if tipo_rele == 4: # Inicializo Rele SSR en GPIO
        NGPIO_PIN = id_rele % 100
  
        GPIO.setup(NGPIO_PIN, GPIO.OUT)
        Rele_SSR.append ([GPIO.PWM(NGPIO_PIN, 5),NGPIO_PIN])# 5hz
        
        Rele_SSR[NGPIO][0].start(0)
        NGPIO +=1
        
# Actualizar valores de  numero conmutaciones y tiempo activo del dia actual
sql = 'SELECT id_rele,segundos_on,nconmutaciones FROM reles_segundos_on WHERE fecha="'+time.strftime("%Y-%m-%d")+'"'                
try:
    nreles_on = cursor.execute(sql)
    nreles_on = int(nreles)  # = numero de reles con conmutaciones o tiempo activo en el dia actual
    columns = [column[0] for column in cursor.description] # creacion diccionario Tabla Reles
    TS=[] 
    for row in cursor.fetchall(): TS.append(dict(zip(columns, row)))
    
    for r in TS:
        id_rele = r['id_rele']
        try:
            Rele_Dict[id_rele]['nconmutaciones']= r['nconmutaciones']
            Rele_Dict[id_rele]['segundos_on']= Rele_Tiempo[id_rele] = r['segundos_on']
        except:
            pass
except:
    db.rollback()
    print ('Error lectura tabla reles_segundos_on')
    logBD('Error lectura tabla reles_segundos_on')

if nreles > 0 : # apagado reles en BD
    sql = "UPDATE reles SET estado = 0 WHERE modo = 'PRG'"
    cursor.execute(sql)
    db.commit()
    
## ------------------------------------------------------------
### Calcular voltaje sistema (12,24 o 48)
#print ('ERROR LECTURA VOLTAJE BATERIA.....SISTEMA POR DEFECTO a 24V')
if AH > 1:
    try:
        if simular != 1 and len(sensores['Vbat'])>0:
            Vbat, Vbat_err = leer_sensor('Vbat',sensores['Vbat'])
        else:
            Vbat = vsis * 12.0
    except:
        time.sleep(5) # espero 5sg por si los programas se estan iniciando 
        pass

    if Vbat > 11 and Vbat < 15.5 : vsis = 1
    elif Vbat > 22 and Vbat < 31 : vsis = 2
    elif Vbat > 44 and Vbat < 62 : vsis = 4
    else : print(f'Vbat = {Vbat}: Imposible reconocer el voltaje del sistema')

    Vflot = 13.7 * vsis
    Vabs = 14.4 * vsis
    Objetivo_PID = 17.2 * vsis #pongo un valor alto no alcanzable

print(Fore.RED+'Pulsa Ctrl-C para salir...'+Fore.RESET)

log = f' Arrancando programa fv.py ....{Vbat}V  {log}'
logBD(log) # incluyo mensaje en el log
if usar_telegram == 1:
    try:        
        pass
        #bot.send_message( cid, log)
    except:
        logBD("Error en Msg Telegram") # incluyo mensaje en el log

# Inicializo lista reles diver
Reles_D = [ ] 
for r in TR:
    if r['modo'] == 'PRG' and r['prioridad']!= 0:
        Reles_D.append([r['id_rele'],r['prioridad'],r['salto']]) #id_rele, prioridad, salto
Reles_D_Ord = sorted(Reles_D, key=lambda rr: rr[1])
Nreles_Diver = len(Reles_D_Ord) # Nº de reles Diver a considerar para reparto excedentes
PWM_Max = Nreles_Diver * 100
print ('Reles para excedentes = Reles_D_Ord[Id_rele, salto, prioridad] =',Reles_D_Ord)

if DEBUG >= 100: print ('PWM_Max=',PWM_Max)

#########################################################################################
# -------------------------------- BUCLE PRINCIPAL --------------------------------------
#########################################################################################

try:
    while True:
        #print (time.strftime("%Y-%m-%d %H:%M:%S"),' Bucle',)
        """
        cursor.close()
        db.close()
        
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        """
        ee=10.0

        t_muestra_7=(time.time()-hora_m) * 1000

        hora1=time.time()
        
        if 'ERROR' in Estado['PVControl+']:  print (Estado['PVControl+'],Estado['PVControl+_error'])
            
        if 'ERROR CRITICO' in Estado['PVControl+']:
            Estado['PVControl+'] = 'ERROR CRITICO EN Parametros_FV.py'
            Estado['PVControl+_error'] = 'No es posible leer correctamente Parametros_FV.py...corrija el archivo'   
        else:
            Estado['PVControl+'] = 'OK'
            Estado['PVControl+_error'] = ''
       
        if Grabar == 1: #leer BD cada t_muestra * N_muestras
            if int(time.time()%100) < 10: # cada 100 sg
                try:
                    exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios
                    Estado['PVControl+'] = 'OK'
                    Estado['PVControl+_error'] = ''              
             
                except:
                    Estado['PVControl+'] = 'ERROR CRITICO EN Parametros_FV.py'
                    Estado['PVControl+_error'] = 'No es posible leer correctamente Parametros_FV.py...corrija el archivo'                        
            
            ### B1 ---------- Cargar tablas parametros, reles , reles_c, reles_h ---------------------
            sql='SELECT * FROM parametros'
            nparametros=cursor.execute(sql)
            nparametros=int(nparametros)  # = numero de filas de parametros.---- debe ser 1
            
            columns = [column[0] for column in cursor.description]
            TP1 = []
            for row in cursor.fetchall(): TP1.append(dict(zip(columns, row)))
            TP = TP1[0] # solo la primera fila

            Mod_bat = TP['Mod_bat']
            Vflot = float(TP['Vflot'])
            Vabs = float(TP['Vabs'])
            Tabs_max = float(TP['Tabs'])
            Vequ = float(TP['Vequ'])
            Tequ_max = float(TP['Tequ'])
            Coef_Temp = float(TP['coef_temp'])

            sql='SELECT * FROM reles'
            nreles=cursor.execute(sql)
            nreles=int(nreles)  # = numero de reles

            columns = [column[0] for column in cursor.description] # creacion diccionario Tabla Reles
            TR=[] 
            Reles_D = []
            for row in cursor.fetchall(): TR.append(dict(zip(columns, row)))
            
            #print (Rele_Dict)
            Rele_Dict_Aux = {}
            for r in TR: # actualizar diccionarios por si se han creado/borrado nuevos reles o modificado campos (salvo estado)
                id_rele = r['id_rele']
              
                if r['modo'] == 'PRG' and r['prioridad']!= 0:
                    Reles_D.append([r['id_rele'],r['prioridad'],r['salto']]) #id_rele, prioridad, salto
                    Reles_D_Ord = sorted(Reles_D, key=lambda rr: rr[1])
                    Nreles_Diver = len(Reles_D_Ord) # Nº de reles Diver a considerar para reparto excedentes
                    PWM_Max = Nreles_Diver * 100  
                
                if id_rele in Rele: # mantengo valores que gestiona fv.py
                    if r['estado'] != Rele[id_rele]:
                        r['estado'] = Rele[id_rele]
                        sql = f"UPDATE reles SET estado ={Rele[id_rele]} WHERE id_rele = {id_rele}"
                        cursor.execute(sql)
                        
                    r['cambio'] = Rele_Dict[id_rele]['cambio']
                    r['nconmutaciones'] = Rele_Dict[id_rele]['nconmutaciones']  
                    r['segundos_on'] = Rele_Dict[id_rele]['segundos_on']  
                else:
                    r['cambio'] = 0 # marca temporal de cambio a 0 
                    r['nconmutaciones'] = 0 # numero de conmutaciones a 0 
                    r['segundos_on'] = 0 
                    Rele[id_rele] = Rele_Ant[id_rele] = r['estado'] # actualizamos diccionario Reles con valor en BD
                    Rele_H[id_rele] = Rele_Tiempo[id_rele] = 0 # inicializamos a cero los diccionarios para control horario y tiempo rele
                    
                    try: # aseguro que existe el registro diario de actividad del rele
                        cursor.execute("INSERT INTO reles_segundos_on (id_rele,fecha,segundos_on,nconmutaciones) VALUES (%s,%s,%s,%s)",
                                      (id_rele,time.strftime("%Y-%m-%d"),0,0))
                    except:
                        pass    
                       
                Rele_Dict_Aux[r['id_rele']] = r.copy() # genero diccionario tabla Reles
            
            Rele_Dict = Rele_Dict_Aux.copy() # copio el nuevo diccionario creado con las actualizaciones
            
            sql='SELECT * FROM reles INNER JOIN reles_c ON reles.id_rele = reles_c.id_rele'
            fvcon=cursor.execute(sql)
            fvcon=int(fvcon)  # = numero de condiciones
            columns = [column[0] for column in cursor.description] # diccionario condiciones FV
            TCFV = []
            for row in cursor.fetchall(): TCFV.append(dict(zip(columns, row)))
            
            sql='SELECT * FROM reles INNER JOIN reles_h ON reles.id_rele = reles_h.id_rele'
            hcon=cursor.execute(sql)
            hcon=int(hcon)  # = numero de condiciones horarias
            columns = [column[0] for column in cursor.description] # diccionario condiciones Horarias
            TCH = []
            for row in cursor.fetchall(): TCH.append(dict(zip(columns, row)))
            
            sql='SELECT * FROM condiciones WHERE activado is True ORDER BY id_condicion'
            ncon=cursor.execute(sql)
            ncon=int(ncon)  # = numero de condiciones
            columns = [column[0] for column in cursor.description] # diccionario condiciones
            TC = []
            for row in cursor.fetchall(): TC.append(dict(zip(columns, row)))
            
        ee=20.0
        t_muestra_8= (time.time()-hora_m)* 1000
      
      ### B2---------------------- LECTURA FECHA / HORA ----------------------
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        tiempo_sg = time.time()
        tiempo_us = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        diasemana = time.strftime("%w")
        hora = time.strftime("%H:%M:%S") #No necesario .zfill() ya pone los ceros a la izquierda
        
      ### ------------------------ CAPTURA PARAMETROS FV----------------------

        t_muestra_ant=t_muestra
        t_muestra=time.time()-hora_m
        hora_m=time.time()
        
        log = f'{t_muestra_1:.0f}/{t_muestra_2:.0f}/{t_muestra_3:.0f}/{t_muestra_4:.0f}/{t_muestra_5:.0f}/{t_muestra_6:.0f}/{t_muestra_7:.0f}/{t_muestra_8:.0f}'
        if t_muestra > t_muestra_max: logBD('TmuestraX='+ log)
        if DEBUG >= 2: print(Style.BRIGHT + Fore.YELLOW+ f'T={log:<26}',Fore.RESET,end='')
        if pub_time == 1: client.publish("PVControl/Opcion/Time", log)
            
        if simular == 1:
            Ibat = random.choice([0,12,22,33,46,56,65,78,101,-10,-20,-30,-40,-50,-60,-70,-80,-90])
            Iplaca = random.choice([0,10,20,30,45,57,67,77,88,99,102,110])
            Vbat = random.choice([22.5,23.7,24.0,24.4,25.5,26.3,27,27.5,28.2,29.1])
            Vplaca = random.choice([60,59.4,61,59.9,52,60.1,61.6,58.7,62,57.3])
            Wplaca = random.choice([600,590,40,610,590,520,600.10,610.60,580.70,620,570])
            Temp = random.choice([10,12,14,16,18,20,22,24,26,28,30,32,34])
            Aux1 = random.choice([0,10,12,14,16,18,20,22,24,26,28,30,32,34])
            Aux2 = random.choice([0,10,12,14,16,18,20,22,24,26,28,30,32,34])
            Vred = random.choice([220,221,222])
            Ired = random.choice([1,2,3,0,-1,-2,-3])
            EFF = random.choice([81,90.95,70.9])
            
            ## Evaluo expresiones genericas
            Wbat = Vbat * Ibat
            Wred = Vred * Ired
            Wconsumo = Wplaca - Wbat - Wred
            
            CD1 += 1
            if DEBUG1 == 'RELES' : 
                print(Fore.GREEN+'datos_FV  =',datos_FV)
                print(Fore.CYAN +'Reles_Dict=',Rele_Dict)
        
            print('Rele=',Rele)
            print ('Rele_Tiempo=',Rele_Tiempo)
            print()
            print ('== ',CD1,'=' * 80)
            if CD1 == 1:   Vbat = 12; Iplaca = 50; Wconsumo = 1000
            elif CD1 == 2: Vbat = 12; Iplaca = 110; Wconsumo = 2000
            elif CD1 == 3: Vbat = 12; Iplaca = 110; Wconsumo = 3100
            elif CD1 == 4: Vbat = 13.8; Iplaca = 90; Wconsumo = 2500
            elif CD1 == 5: Vbat = 13.8; Iplaca = 110; Wconsumo = 2500
            elif CD1 == 6: Vbat = 13.8; Iplaca = 110; Wcomsumo = 2500
            elif CD1 == 7: Vbat = 13.8; Iplaca = 110; Wconsumo = 3100
            elif CD1 == 8: Vbat = 13.8; Iplaca = 90; Wconsumo = 3100
            
            #elif CD1 == 9: Vbat = 13.8; Iplaca = 90; Wconsumo = 2500
            #elif CD1 ==10: Vbat = 13.8; Iplaca = 90; Wconsumo = 2500
            
            else:
                #sys.exit()
                CD1 = 0
            d_={}
            sql = 'SELECT * FROM equipos'
            nequipos = int(cursor.execute(sql))
            for row in cursor.fetchall(): d_[row[0]] = json.loads(row[2])
                        
        else:
            ## Capturando valores desde BD en tabla equipos
            ee=30.1
            sql = 'SELECT * FROM equipos'
            nequipos = int(cursor.execute(sql))

            d_={}
            try:
                for row in cursor.fetchall(): d_[row[0]] = json.loads(row[2])
            except:
                if 'ERROR CRITICO' in Estado['PVControl+']: Estado['PVControl+'] += ' / ERROR'
                else: Estado['PVControl+'] = 'ERROR'
                
                Estado['PVControl+_error'] += f" #### Error lectura tabla equipos clave {d_[row[0]]}"                
                #print ('Error Lectura Tabla equipos')
                #logBD('Error lectura Tabla Equipos')    
                #time.sleep(5)
                
            if DEBUG == 100:
                print ('#'*40)
                print (Fore.BLUE+'Equipos =',d_)
                
            ## Capturando valores desde xxxxx.pkl...esta opcion se ira eliminando dejando solo la tabla de equipos
            
            ee=30.2
            if usar_victron == 1:
                archivo_ram='/run/shm/datos_victron.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_victron = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue

            ee=30.3
            if usar_bmv == 1:
                archivo_ram='/run/shm/datos_bmv.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_bmv = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue

            ee=30.4
            if usar_smameter == 1:
                archivo_ram='/run/shm/datos_smameter.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_smameter = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue
            
            if usar_goodwe == 1:
                archivo_ram='/run/shm/datos_goodwe.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_goodwe = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue 
                          
            ee=30.43             
            if usar_must == 1:
                archivo_ram='/run/shm/datos_must.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_must = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue

            ee=30.5
            if usar_srne == 1:
                d_srne = Srne.get_datos()
                if d_srne is None:
                    logBD('error lectura archivo ram SRNE')
                    continue
            
            # LECTURA SENSORES EQUIPOS
            ee=34
            for sensor in sensores:
                #print (f"{sensor} = {sensores[sensor]}")
                try:
                    if type(sensores[sensor]) is dict:
                        if 'Equipo' in sensores[sensor].keys():    
                            s= f'{sensor}, {sensor}_err =leer_sensor("{sensor}",{sensores[sensor]})' 
                            exec(s)
                            errores = 0
                            if eval(f'{sensor}_err') == 1:
                                errores += 1
                                if 'ERROR CRITICO' in Estado['PVControl+']: Estado['PVControl+'] += ' / ERROR'
                                else: Estado['PVControl+'] = 'ERROR'
                
                                Estado['PVControl+_error'] += f' #### Corrija en Parametros_FV.py definicion sensor {sensor}'
                            if errores > 0: 
                                time.sleep(1) # espero
                        else:
                            exec (f'{sensor}= 0.0')
                            if len (sensores[sensor]) > 0:
                                if 'ERROR CRITICO' in Estado['PVControl+']: Estado['PVControl+'] += ' / ERROR'
                                else: Estado['PVControl+'] = 'ERROR'
                
                                Estado['PVControl+_error'] += f' ### Corrija en Parametros_FV.py definicion sensor {sensor} (se pone a 0.00)'
                                
                    elif type(sensores[sensor]) is set:
                        l = list (sensores[sensor])
                        try:
                            if len(l)>0: exec (f'{sensor}= {l[0]}')
                            else:  exec (f'{sensor}= 0.0')
                        except:
                            exec (f'{sensor}= 0.0')
                            if 'ERROR CRITICO' in Estado['PVControl+']: Estado['PVControl+'] += ' / ERROR'
                            else: Estado['PVControl+'] = 'ERROR'
                            
                            Estado['PVControl+_error'] += f' ## Corrija en Parametros_FV.py definicion sensor {sensor} (se pone a 0.00)'
                            
                    elif type(sensores[sensor]) in (int,float,str):
                        try:
                            if sensores[sensor] != '': exec (f'{sensor}= {sensores[sensor]}')
                            else: exec (f'{sensor}= 0.0')
                        except:
                            exec (f'{sensor}= 0.0')
                            if 'ERROR CRITICO' in Estado['PVControl+']: Estado['PVControl+'] += ' / ERROR'
                            else: Estado['PVControl+'] = 'ERROR'
                           
                            Estado['PVControl+_error'] += f' # Corrija en Parametros_FV.py definicion sensor {sensor} (se pone a 0.00)'
                            
                    else:
                        print('Tipo no tratado en sensores=',type(sensores[sensor]))
                except:
                    if 'ERROR CRITICO' in Estado['PVControl+']: Estado['PVControl+'] += ' / ERROR'
                    else: Estado['PVControl+'] = 'ERROR'
                
                    Estado['PVControl+_error'] += f' ##### Except ... Corrija en Parametros_FV.py definicion sensor {sensor}'
                    
            if 'Temp_Bat' in sensores.keys():
                if 'Equipo' in sensores['Temp_Bat']:
                    if len(sensores['Temp_Bat']['Equipo']) >= 1 : # calculo compensacion temperatura solo cuando existe Temperature_sensor
                        Vbat_temp = Coef_Temp * (min(max(Temp_Bat,0),45) - 25)# Nominal 25ºC - rango maximo admisible (0-45ºC)
                        if Vbat_temp >0:# permito un maximo de variacion de 1V por cada 12V de bateria
                            Vbat_temp = min( Vbat_temp, vsis * 1) 
                        else:
                            Vbat_temp = max( Vbat_temp, -vsis * 1)
                    else:
                        Vbat_temp = 0
                        
      ### ------------------ Control Excedentes...Cálculo salida PWM ----------
        ee=36
        
        PWM_ant = PWM
        PWM_Max = Nreles_Diver * 100 
        PWM = Calcular_PWM(PWM) #  calculo de PWM con PWM_Max segun tabla reles
        
        ##################################################################
        t_muestra_1=(time.time()-hora_m) * 1000

        ### CALCULO Wh_BAT,Wh_PLACA Y Wh_RED
        
        dia_anterior = dia
        dia = time.strftime("%Y-%m-%d")

        if dia_anterior != dia: #cambio de dia
            Wh_bat = Whp_bat = Whn_bat = Wh_placa = Whp_red = Whn_red = 0.0
            CD1 = CD2 = CD3 = CD4 = CD5 = 0.0
            Tbulk = Tflot = Tabs = Tflot_bulk= 0  #Tequ ??
            SOC_min = SOC_max = SOC
            Vbat_max = Vbat_min = Vbat
            Vred_max = Vred_min = Vred
            EFF_max = EFF_min = EFF
            for id_rele in Rele_Dict:
                Rele_Tiempo[id_rele] = Rele_Dict[id_rele]['segundos_on'] = 0 # inicializo tiempo de reles 
                Rele_Dict[id_rele]['nconmutaciones'] = 0 # inicializo numero conmutaciones
                
                try: # aseguro que existe el registro diario de actividad del rele
                    cursor.execute("INSERT INTO reles_segundos_on (id_rele,fecha,segundos_on,nconmutaciones) VALUES (%s,%s,%s,%s)",
                      (id_rele,time.strftime("%Y-%m-%d"),0,0))
                except:
                    print ('Error creacion registros diarios reles_segundos_on')
            db.commit() 
        
        else: # calculo Wh
            if Ibat < 0: Whn_bat = round(Whn_bat - (Wbat * t_muestra/3600),2)
            else:        Whp_bat = round(Whp_bat + (Wbat * t_muestra/3600),2)

            if Ired < 0: Whn_red = round(Whn_red - (Wred * t_muestra/3600),2)
            else:        Whp_red = round(Whp_red + (Wred * t_muestra/3600),2)
            
            Wh_bat = Whp_bat - Whn_bat
            Wh_red = Whp_red - Whn_red
            Wh_placa = round(Wh_placa + (Wplaca * t_muestra/3600),2)
            Wh_consumo = Wh_placa - Wh_red - Wh_bat
        
        if AH > 1:   #Calculo SOC solo si hay batería
            ## -------- CALCULO SOC% A C20 ----------
            if Ibat < 0 :
                Ip1 = -Ibat; Ip1 = Ip1**CP; Ip1 = AH*Ip1
                Ip2 = AH / 20 ; Ip2 = (Ip2**CP)*20
                Ip= -Ip1/Ip2
            else :
                Ip = Ibat * EC

            if (Ibat>0 and Ibat<0.005*AH and abs(Vbat-Vflot)<0.2) : DS = DS + (AH-DS)/50
            else : DS = DS + (Ip * t_muestra/3600)
            
            if DS > AH : DS = AH
            if DS < 0 :  DS = 0

            if TP['nuevo_soc'] != 0: # Actualizo SOC si en la BD es distinto de 0
                DS = AH * TP['nuevo_soc']/100
                cursor.execute("UPDATE parametros SET nuevo_soc=0 WHERE id_parametros=1")
                db.commit()                
            SOC = round(DS/AH*100,2)
            
            ###########   Calculo Algoritmo de carga #############
            ee=38
            try:
                if Mod_bat == 'BULK':
                    ee=38.1
                    if Iplaca > 0: Tbulk += t_muestra
                    
                    if Vbat >= Vabs:# paso de Bulk a Abs
                        cursor.execute("UPDATE parametros SET Mod_bat='ABS'")
                        db.commit()
                        try:
                            if flag_Abs == 0 and usar_telegram == 1:
                                flag_Abs =1
                                logBD('Inicio ABS')
                                bot.send_message( cid, 'Inicio Absorcion')
                        except:
                            pass

                elif Mod_bat == 'FLOT': 
                    ee=38.2
                    if Vbat >= Vflot-0.2: Tflot += t_muestra
                
                    # paso de Flot a Bulk
                    if Vbat <= Vflot-4: Tflot_bulk += 8 * t_muestra
                    elif Vbat <= Vflot-3: Tflot_bulk += 4 * t_muestra
                    elif Vbat <= Vflot-2: Tflot_bulk += 2 * t_muestra
                    elif Vbat <= Vflot-0.1: Tflot_bulk += t_muestra

                    if Tflot_bulk > 10000: # Ver que tiempo se pone o si se pone como parametro
                        Tflot_bulk = Tabs = flag_Abs= 0
                        cursor.execute("UPDATE parametros SET Mod_bat='BULK'")
                        if TP['sensor_PID'] == 'Vbat': # si sensor_PID es Vbat
                            cursor.execute("UPDATE parametros SET objetivo_PID='"+str(Vabs)+"'")
                        db.commit()
                        try:
                            if flag_Flot == 1 and usar_telegram == 1:
                                flag_Flot = 0
                                logBD('Inicio BULK')
                                bot.send_message( cid, 'Inicio BULK')
                        except:
                            pass
                
                elif Mod_bat == 'ABS':
                    ee=38.3
                    if Vbat >= Vabs-0.1:Tabs += t_muestra
                    
                    elif Vbat < Vabs-0.2:# paso de Abs a Bulk
                        cursor.execute("UPDATE parametros SET Mod_bat='BULK'")
                        db.commit() 
                    
                    if Tabs >= Tabs_max: # paso de Abs a Flot
                        cursor.execute("UPDATE parametros SET Mod_bat='FLOT'")
                        if TP['sensor_PID'] == 'Vbat':
                            cursor.execute("UPDATE parametros SET objetivo_PID='"+str(Vflot)+"'")
                        db.commit()
                        try:
                            if flag_Flot == 0 and usar_telegram == 1:
                                flag_Flot = 1
                                logBD('Inicio FLOT')
                                bot.send_message( cid, 'Inicio Flotacion')
                        except:
                            pass

                elif Mod_bat == 'EQU':
                    ee=38.4
                    if Vbat >= Vequ-0.2:
                        Tequ += t_muestra
                    if Tequ >= Tequ_max:    
                        Tequ=0 
                        cursor.execute("UPDATE parametros SET Mod_bat='FLOT'")
                        db.commit() 
                ee=39
                if DEBUG >=3:
                    print(' Tbulk={0:.2f} - Tabs={1:.2f} - Tflot={2:.2f}- Tflot_bulk={3:.2f}'.format(Tbulk,Tabs,Tflot,Tflot_bulk),end='')
                    print (' Carga= {0}'.format(Mod_bat))
            except:
                print (tiempo,' Error algoritomo carga ',ee) 
                print(' Tbulk={0:.2f} - Tabs={1:.2f} - Tflot={2:.2f}- Tflot_bulk={3:.2f}'.format(Tbulk,Tabs,Tflot,Tflot_bulk),end='')
                print (' Carga= {0}'.format(Mod_bat))
                logBD('Err.Alg.Carga='+ str(ee)+ '==' + Mod_bat + '=' + str(Tabs) + '/' + str(Tflot) + '/' + str(Tflot_bulk))            

        if Wred > 0:  Mod_red = 'INYECT'
        else:         Mod_red = 'CONS'
            
        ee=40.0    
        t_muestra_2=(time.time()-hora_m) * 1000
        
        # ------------------ Calculo del SOCmax,min, Vbat_max,min  Vred_max,min EFF_max,min ------------
        SOC_max = max (SOC, SOC_max)
        SOC_min = min (SOC, SOC_min)
        Vbat_max = max (Vbat, Vbat_max)
        Vbat_min = min (Vbat, Vbat_min)
        Vred_max = max (Vred, Vred_max)
        Vred_min = min (Vred, Vred_min)
        EFF_max = max (EFF, EFF_max)
        EFF_min = min (EFF, EFF_min)
        
               
      ## ------------------ ALGORITMO CONDICIONES RELES -----------------------------
        ee=50.0
        #### Cargamos los valores actuales de los reles  en Rele_Ant####
        
        Rele_Ant = Rele.copy() # ponemos estado del rele en el estado anterior
        for r in TR: Rele_H[r['id_rele']] = 0 # inicializamos a cero el diccionario para control horario
        
        # -------------------- Bucle de condiciones de horario --------------------------
        ee=56.0
        for r in TCH:
            try:
                id_rele = r['id_rele']
                
                diaok = 0 # variables de control para ver si esta dentro de horario
                horaok = 0
                dias_activos=r['parametro_h'].upper()
                
                if  dias_activos == 'T': #Todos los dias de la semana
                    diaok = 1
                elif NDIA[diasemana] in dias_activos:
                    diaok = 1

                if str(r['valor_h_ON']).zfill(8) > str(r['valor_h_OFF']).zfill(8): #True si periodo pasa por 0:00
                    if (hora >= str(r['valor_h_ON']).zfill(8) and hora <= "23:59:59"): 
                        horaok = 1                                                       
                    if (hora >= "00:00:00" and hora <= str(r['valor_h_OFF']).zfill(8)): 
                        horaok = 1

                elif (hora >= str(r['valor_h_ON']).zfill(8) and hora <= str(r['valor_h_OFF']).zfill(8)):
                    horaok = 1

                if diaok == 1 and horaok == 1:
                    Rele_H[id_rele] += 1
            except:
                Estado['PVControl+'] = 'ERROR'
                Estado['Reles_h'] = r['id_rele']
                

        for r in TCH:
            id_rele = r['id_rele']
            
            if Rele_H[id_rele] == 0:
                Rele[id_rele]  = 0 #apago rele
                
                Rele_H[id_rele] = -1 # quitar posibilidad de ON o ser rele Diver en el ciclo

        # -------------------- Bucle de condiciones de parametros FV --------------------------
        ee=58.0
        for r in TCFV:
            id_rele = r['id_rele']
            condicion = f"{r['parametro']} {r['condicion']} {r['valor']}"
            #print(Fore.BLUE + f"Rele {id_rele} - condicion {r['operacion']}={condicion}  ", end='')
            if  Rele_H[id_rele] != -1: # mientras cumpla condiciones de horario o se de una condicion de OFF
                try:
                    if eval(condicion):
                        #print (Fore.GREEN+ 'TRUE')
                        if r['operacion'] == 'ON':
                            Rele[id_rele] = 100
                            if r['prioridad'] > 0 : Rele_H[id_rele] = -2 # lo pongo a 100 y quito de Excedentes
                            
                        elif r['operacion'] in ['OFF',0] :
                            Rele[id_rele] = 0
                            Rele_H[id_rele] = -1 # quitar posibilidad de ON o de ser rele excedentes en el ciclo
                        
                        elif eval(r['operacion']) > 0:
                            Rele[id_rele] = eval(r['operacion'])
                            if r['prioridad'] > 0 : Rele_H[id_rele] = -2 # lo pongo a 100 y quito de Excedentes
                            
                        #print (f'Pongo rele {id_rele} a {Rele[id_rele]}')
                    else:
                        pass                
                        #print (Fore.RED+ 'FALSE')
                except:
                    if 'ERROR CRITICO' in Estado['PVControl+']: Estado['PVControl+'] += ' / ERROR'
                    else: Estado['PVControl+'] = 'ERROR'
                
                    Estado['PVControl+_error'] += f' #### Corrija condicion del rele {id_rele}-{condicion} en tabla reles_c'
                
                    #print (f'Error condicion rele {id_rele}-{condicion}')
                    #logBD(f'Error condicion rele {id_rele}-{condicion[:23]}')
                    #db.commit()
            else:
                pass
                #Rele[id_rele] = 0
                #print ( f'no entro en {condicion} por estar ya puesto a 0')
        #print(Fore.CYAN+'tras condiciones=',Rele)
             
        # -------------------- Bucle de condiciones  --------------------------
        ee=60.0
        for r in TC:
            try:
                TC1 = r['condicion1']
                TC2 = r['condicion2']
                #print(TC1],TC2) 
                if TC1 in ('', ' ','1'): TC1 = 'True'          
                if TC2 in ('', ' ','1'): TC2 = 'True'
                if (eval(TC1) and eval(TC2)): exec(r['accion']) 
            except:
                if 'ERROR CRITICO' in Estado['PVControl+']: Estado['PVControl+'] += ' / ERROR'
                else: Estado['PVControl+'] = 'ERROR'
                
                Estado['PVControl+_error'] += f" #### Corrija definicion id_condicion = {r['id_condicion']} en tabla condiciones "
                
                #print (f"Error Condicion {r['id_condicion']}")
                #logBD(f"Error en id_condicion={r['id_condicion']}")
        
        #print ('Antes=',Estado['Condiciones'])
        #Estado['Condiciones'] = Estado['Condiciones'].replace("'", "''")
        #print ('Despues=',Estado['Condiciones'])
        
        
        #-------------------- Bucle encendido/apagado reles ------------------------------------
        ee=62.0
        Flag_Rele_Encendido = 0
        for r in TR:
            id_rele = r['id_rele']
            tipo_act_rele = 0
            
            ### forzado ON/OFF
            if r['modo'] == 'ON' :
                Rele[id_rele] = 100
                tipo_act_rele = 1
                
            elif r['modo'] == 'OFF' :
                Rele[id_rele] = 0
                tipo_act_rele = 1
                   
            ### dejar rele como esta     
            if Rele[id_rele] == 100 and Rele_Ant[id_rele] < 100 and Flag_Rele_Encendido == 1 : 
                #print ('Dejo el rele ', id_rele, ' para encender en otro ciclo por flag ', Rele[id_rele] ,'/', Rele_Ant[id_rele] )
                Rele[id_rele] = Rele_Ant[id_rele]      #dejar rele en el estado anterior
                
            ### encender rele
            if Rele[id_rele] == 100 and Flag_Rele_Encendido == 0 and Rele_Ant[id_rele] < 100 :
                #print (tiempo,' - Enciendo rele ',id_rele)
                Rele[id_rele], Rele_Dict[id_rele]['cambio'] = act_rele(id_rele,100,tipo_act_rele)
                if r['prioridad'] == 0 and Rele[id_rele] == 100: Flag_Rele_Encendido = 1 # activo flag solo para reles que no son de excedentes
            
            ### apagar rele
            if Rele[id_rele] == 0 and Rele_Ant[id_rele]>0: # and r['prioridad']== 0:
                #print (tiempo,' - Apago rele ',id_rele)
                Rele[id_rele], Rele_Dict[id_rele]['cambio'] = act_rele(id_rele,0, tipo_act_rele) #apagar rele
            
            Rele_Dict[id_rele]['estado']= Rele[id_rele]
            Rele_Dict[id_rele]['espera']=  max(0,int(Rele_Dict[id_rele]['cambio'] +  Rele_Dict[id_rele]['retardo'] - time.time())) # sg hasta permitir cambio
            
            
        #print('tras activacion=',Rele)
        #print ('C.excedentes=', Rele_H)
            
      ## --------- ACTIVACION RELES CONTROL DE EXCEDENTES -------------
        t_muestra_3=(time.time()-hora_m) * 1000
        ee=90.0
        reles_exc_prio: dict = {}  # inicializacion dict reles excedentes por prioridad
        PWM_Max_1 = 0
        for r in TR:
            if r['modo'] == 'PRG' and r['prioridad']!= 0 and Rele_H[r['id_rele']] >= 0 : #and Flag_Rele_Encendido != 1:
                if r['prioridad'] not in reles_exc_prio.keys():
                    reles_exc_prio [r['prioridad']] = []
                reles_exc_prio[r['prioridad']].append({'id_rele': r['id_rele'], 'salto': r['salto']})
                PWM_Max_1 += 100
                
        if PWM > PWM_Max_1:
            PWM = PWM_Max_1
            
        #print('Reles para PWM',reles_exc_prio)
        
        ee=100.0
        if PWM >=0 : # situacion normal, se puede anular la entrada aqui poniendo en condiciones PWM = -1
            if reles_exc_prio:
                # Repartimos PWM entre los reles
                PWM_R = PWM

                prios = [*reles_exc_prio]  # lista de prioridades usadas
                prios.sort()
                for prio in prios:
                    nreles_prio = len(reles_exc_prio[prio])
                    reles_exc_prio[prio].sort(key=lambda d:(-d['salto']))  # ordenamos por salto descendente
                    
                    for rele_prio in reles_exc_prio[prio]:
                        id_rele = rele_prio['id_rele']
                        valor = min(100,PWM_R/nreles_prio)
                        salto = rele_prio['salto']
                        if salto == 0: salto = 1 # por si da error mientras se actualiza la BD
                        nivel_rele =  round(salto * (valor // salto),3) # resolucion hasta 0.001
                        Rele[id_rele] = min(PWM_R, nivel_rele)
                        
                        if Rele[id_rele] != Rele_Ant[id_rele]:
                            #print (Rele_Dict)
                            Rele[id_rele], Rele_Dict[id_rele]['cambio'] = act_rele(id_rele, Rele[id_rele],0)
            
                        Rele_Dict[id_rele]['estado']= Rele[id_rele]
            
                        PWM_R -= Rele[id_rele]
                        PWM_R = max(0,PWM_R)
                        nreles_prio -= 1
                        if DEBUG >= 100: print('Reles PWM: ', id_rele, '->', Rele[id_rele], '(salto=',salto,'PWM_R=', PWM_R,')')
                    
        else: #salida manual de reles de excedentes por si se manipulan en condiciones
            for prio in reles_exc_prio.keys():
                for rele_prio in reles_exc_prio[prio]:
                    id_rele = rele_prio['id_rele']
                    if Rele[id_rele] != Rele_Ant[id_rele]:
                        Rele[id_rele], Rele_Dict[id_rele]['cambio'] = act_rele(id_rele,Rele[id_rele],0)
                        Rele_Ant[id_rele]=Rele[id_rele]
                        Rele_Dict[id_rele]['estado']= Rele[id_rele]
        
        t_muestra_4=(time.time()-hora_m) * 1000
        ee=200.0      
  
        # Refresco valor de rele 
        if time.time()-t_refresco_rele > 2: # refrescar 1 rele cada max(t_muestra, 2sg)  
            t_refresco_rele = time.time()
            if len(TR_refresco) > 0:
                id_rele = TR_refresco[0]['id_rele'] 
                Rele[id_rele], i = act_rele(id_rele, Rele[id_rele],2)
                Rele_Dict[id_rele]['estado']= Rele[id_rele]
                TR_refresco.pop(0)
            else:
                TR_refresco = TR[:]
        
        ## --------- Actualizando Tabla Reles y tabla reles_segundos_on -----------------------
        # ---- Actualizacion Nº conmutaciones y tiempo encendido de cada rele -----------------        
        for I in range(nreles):
            id_rele = TR[I]['id_rele']
            if Grabar == 1: # actualizo BD cada N bucles
                # Actualizacion estado Tabla reles
                if Rele[id_rele] != TR[I]['estado']:
                    sql = f"UPDATE reles SET estado ={Rele[id_rele]} WHERE id_rele = {id_rele}"
                    cursor.execute(sql)
                    TR[I]['estado'] = Rele[id_rele]
                
                # Actualizacion Tabla reles_segundos_on               
                if TP['grabar_reles'] == "S":
                    try: # actualizo registro
                        sql = (f"UPDATE reles_segundos_on SET segundos_on = {Rele_Dict[id_rele]['segundos_on']}, nconmutaciones = {Rele_Dict[id_rele]['nconmutaciones']}"+ 
                             f" WHERE id_rele = {id_rele} and fecha ='{time.strftime('%Y-%m-%d')}'")
                        cursor.execute(sql)
                    except : # inicializo registro
                        print ('Error actualizacion reles_segundos_on')
                        
            # calculo encendido reles 
            if Rele[id_rele] > 0:
                Rele_Tiempo[id_rele] += round((t_muestra * Rele[id_rele]/100),2)
                Rele_Dict[id_rele]['segundos_on'] = round(Rele_Tiempo[id_rele],2)
                
            # Calculo nconmutaciones
            if Rele[id_rele] != Rele_Ant[id_rele]:
                Rele_Dict[id_rele]['nconmutaciones'] += 1
                if Rele_Dict[id_rele]['grabacion'] == "S":
                    try:
                        cursor.execute("INSERT INTO reles_grab (Tiempo,id_rele,valor_rele) VALUES(%s,%s,%s)",(tiempo,id_rele,Rele[id_rele]))
                    except:
                        db.rollback()
                        logBD('tabla reles_grab NO grabados por fallo')
                        
        #------------------------Escribir en la tabla valores FV  ---------------------------
        
        if TP['grabar_datos'] == "S" and Grabar == 1:
            if DEBUG >=2: print (Fore.RED+'G'+Fore.RESET,end='')
            try:
                cursor.execute("""INSERT INTO datos (Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,
                    Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,Mod_bat,Vred,Wred,Whn_red,Whp_red) 
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,
                    Temp,PWM,Mod_bat,Vred,Wred,Whn_red,Whp_red))
                #db.commit()
            except:
                db.rollback()
                logBD('Registro DATOS no grabado')
        try:
            if TP['grabar_datos'] == "S" and eval(grabar_datos_s): #grabar datos_s 
                if DEBUG >=2: print ('S',end='')
                
                cursor.execute("""INSERT INTO datos_s (Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,
                   Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,
                   IPWM_P,IPWM_I,IPWM_D,Kp, Ki,Kd,Vred,Wred,Whn_red,Whp_red) 
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (tiempo_us,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,
                   IPWM_P,IPWM_I,IPWM_D,TP['Kp'],TP['Ki'],TP['Kd'],Vred,Wred,Whn_red,Whp_red))
                #db.commit()
            
        except:
            db.rollback()
            logBD('Registro datos_s no grabado')
        ## ------------------------------------------------
        t_muestra_5=(time.time()-hora_m) * 1000
        
        # ----------------- Guardamos datos_fv.json ------
        ee=300.0
        datos_FV =  {'Vbat':Vbat,'Ibat':Ibat,'Wbat':round(Wbat),'Whp_bat':int(Whp_bat),'Whn_bat':int(Whn_bat),
                     'Vbat_min':Vbat_min,'Vbat_max':Vbat_max,
                     'DS':round(DS,2),'SOC':SOC,'SOC_min':SOC_min,'SOC_max':SOC_max,
                     'Mod_bat':Mod_bat,'Tabs':int(Tabs),'Tflot':int(Tflot),'Tflot_bulk':int(Tflot_bulk),
                     'Vplaca':Vplaca,'Iplaca':Iplaca,'Wplaca':round(Wplaca),'Wh_placa':round(Wh_placa),
                     'Vred':Vred,'Wred':Wred,'Whp_red':int(Whp_red),'Whn_red':int(Whn_red),
                     'Vred_min':Vred_min,'Vred_max':Vred_max,'EFF':EFF,'EFF_min':EFF_min,'EFF_max':EFF_max,
                     'Wconsumo':round(Wconsumo),'Wh_consumo': round(Wh_consumo),
                     'Temp':Temp,'PWM':int(PWM),
                     'Aux1':Aux1,'Aux2':Aux2,'Aux3':Aux3,'Aux4':Aux4,'Aux5':Aux5,'Aux6':Aux6,'Aux7':Aux7
                     }
        
        salida_FV = json.dumps(datos_FV)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida_FV}' WHERE id_equipo = 'FV'") # grabacion en BD RAM
        cursor.execute(sql)
                    
        ee=310.0
        salida_RELES = json.dumps(Rele_Dict)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida_RELES}' WHERE id_equipo = 'RELES'") # grabacion en BD RAM
        cursor.execute(sql)
        
        ee=320.0
        if Estado['PVControl+_error'] == '': del Estado['PVControl+_error'] 
        salida_ESTADO = json.dumps(Estado)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida_ESTADO}' WHERE id_equipo = '_PVControl+'") # grabacion en BD RAM
        #print ('sql=',sql)
        cursor.execute(sql)
        
        db.commit()
        
        if DEBUG1 == 'RELES' : 
            print(Fore.GREEN+'datos_FV  =',datos_FV)
            print(Fore.CYAN +'Reles_Dict=',Rele_Dict)
        
        
        ###### PUBLICACION MQTT ##########      
        if Grabar == 1: #publico MQTT cada t_muestra*N_muestras
            client.publish("PVControl/DatosFV/Iplaca",Iplaca)
            client.publish("PVControl/DatosFV/Vplaca",Vplaca)
            client.publish("PVControl/DatosFV/Wplaca",Wplaca)
            client.publish("PVControl/DatosFV/Aux1",Aux1)
            client.publish("PVControl/DatosFV/Aux2",Aux2)
            client.publish("PVControl/Reles/PWM", PWM)  
            if Vbat > 0 :
                client.publish("PVControl/DatosFV/Ibat",Ibat)
                client.publish("PVControl/DatosFV/Vbat",Vbat)
                client.publish("PVControl/DatosFV/SOC",SOC)
            if Vred > 0:
                client.publish("PVControl/DatosFV/Ired",Ired)
                client.publish("PVControl/DatosFV/Vred",Vred)
                client.publish("PVControl/DatosFV/EFF",EFF)
    
            if usar_mqtt_homeassistant == 1: #publica en topic PVControl/DatosFV para poder ser usado por Home Assistant
                client.publish("PVControl/DatosFV",salida_FV)
                client.publish("PVControl/DatosFV/RELES",salida_RELES)
                    
        Grabar += 1
        if Grabar >= TP['n_muestras_grab'] + 1: Grabar = 1

        ###### ajuste fino tiempo bucle
        T_ejecucion = round(time.time() - hora1,2)

        if T_ejecucion_max < T_ejecucion: T_ejecucion_max = T_ejecucion
        
        ee=320.0
        if DEBUG >= 1:
            #print (tiempo,'-',end='')
            print(f"{int(T_ejecucion*1000):4}ms-Sensor={TP['sensor_PID']}={TP['objetivo_PID']:.2f}",end='')
            print (Fore.CYAN+f"/{eval(TP['sensor_PID']):.2f}-Ct={Vbat_temp:.2f}",end='')
            if AH > 0:
                print (Fore.MAGENTA+f'/Vbat={Vbat:>5.2f}-Iplaca={Iplaca:>6.1f}-Ibat={Ibat:>6.1f}-Wcon={Wconsumo:>6.0f}-PWM={PWM:>3.0f}-Temp={Temp:>4.1f}'+Fore.RESET)
            else:
                print (Fore.MAGENTA+f'/Vred={Vred:.2f}-Iplaca={Iplaca:.1f}-Ired={Ibat:.1f}-Wcon={Wconsumo:.0f}-PWM={PWM:.0f}'+Fore.RESET)
                
        # Repetir bucle cada X segundos
        espera = TP['t_muestra'] - T_ejecucion #-0.1
        if espera > 0: time.sleep(espera)
        t_muestra_6=(time.time()-hora_m) * 1000
        
except:
    print()
    print ('Error en bucle fv',ee)
    try:
        cursor.close()
        db.close()
    except:
        pass    
    for I in range (NGPIO):
        print (I)
        Rele_SSR[I][0].stop()
    traceback.print_exc()
finally:
    GPIO.cleanup()    
