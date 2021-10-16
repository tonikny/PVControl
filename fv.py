#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-09-26

import time,sys
import traceback
import datetime
import MySQLdb 
import random # para simulacion usando random.choice

from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.
import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token
import paho.mqtt.client as mqtt

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

import RPi.GPIO as GPIO # reles 4XX via GPIO
GPIO.setmode(GPIO.BOARD) #para reles SSR en pines RPi
#GPIO.setmode(GPIO.BCM) #para reles SSR en pines RPi
GPIO_PINES_PCB = [11,12,13,15,16,18,22,29] # Numero de pines que presenta la PCB

import pickle,json
from Srne import Srne # Libreria reguladores SRNE

import locale
locale.setlocale(locale.LC_ALL, ("es_ES", "UTF-8")) #nombre mes en Castellano

basepath = '/home/pi/PVControl+/'

"""
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Style: DIM, NORMAL, BRIGHT, RESET_ALL
"""
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' PVControl+') #+Style.RESET_ALL)

#Parametros Instalacion FV
from Parametros_FV import *

#aseguro que los valores introducidos en Parametros_FV.py son float
AH = float(AH)
CP = float(CP)
EC = float(EC)  
vflotacion = float(vflotacion)
SHUNT1 = float(SHUNT1)
SHUNT2 = float(SHUNT2)
RES0 = float(RES0)
RES1 = float(RES1)
RES2 = float(RES2)
RES3 = float(RES3)
RES0_gain = float(RES0_gain)
RES1_gain = float(RES1_gain)
RES2_gain = float(RES2_gain)
RES3_gain = float(RES3_gain)

#Comprobacion argumentos en comando de fv.py
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p2':  DEBUG = 2
elif str(sys.argv[narg-1]) == '-p3':  DEBUG = 3
elif str(sys.argv[narg-1]) == '-p':   DEBUG = 100
else:    DEBUG = 0

print (Fore.RED + 'DEBUG=',DEBUG)

if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]
try:
    bus = SMBus(1) # Activo Bus I2C para ADS o PCF
except:
    pass

if (Vbat_sensor + Vplaca_sensor + Aux1_sensor+ Aux2_sensor).find ('ADS') >=0 : 
    # Alta ADS1115_1 - pin addr a 3V3
    # A0=Vbat // A1=Aux1 // A2= Vplaca// A3= Aux2
    adc1 = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1) 

if (Ibat_sensor + Iplaca_sensor).find ('ADS') >=0:
    # Alta ADS1115_4 - pin addr a GND
    # A0=Ibat // A1=Ibat // // A2=Iplaca // A3=Iplaca
    adc = Adafruit_ADS1x15.ADS1115(address=0x4b, busnum=1)


#Inicializando las variables del programa
#---------------------------------------------------------------
DatosFV = {} #Creamos diccionario para los datos FV

NDIA = {'0':'D','1':'L','2':'M','3':'X','4':'J','5':'V','6':'S'} # Condiciones de dia de la semana

Grabar = 1 # Contador ciclo grabacion en BD

hora_m = time.time() #para calcular tiempo entre muestras real
dia = time.strftime("%Y-%m-%d") # para cambio de dia y reinicializar Wh
tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
minuto = time.strftime("%H:%M")

t_muestra = 5 # Inicializo Tiempo entre muestra real...idealmente TP['t_muestra']
t_muestra_1 = t_muestra_2 = t_muestra_3 = t_muestra_4 = t_muestra_5 = t_muestra_6 = 0 # muestras t ejecucion intermedias
T_ejecucion = T_ejecucion_max = 0.0

#---Variables Bateria --------------------------------
Ibat = 0.0                  # Intensidad Bateria
Vbat = vsis * 12.0          # Voltaje Bateria inicial
DS = SOC = 0                # control SOC bateria
Mod_bat =''
Vflot = Vabs = Vecu = 0.0   # Voltaje asociado a estado de flotacion/Absorcion/Ecu
Tflot = Tabs = Tecu = 0.0   # Tiempo asociado a estado de flotacion/Absorcion/Ecu
Tflot_bulk = Tbulk = 0.0    # Tiempo asociado al paso de FLOT a BULK 
SOC_max = SOC_min = 0       # Variable para guardar SOC maximo y minimo diario
Vbat_max = Vbat_min = 0     # Variable para guardar Vbat maximo  y minimo diario
flag_Abs= flag_Flot = 0     # Flags de Absorcion y Flotacion
Vabs = Vflot = 0            # Valores de Absorcion y Flotacion
Wh_bat = Whp_bat = Whn_bat = 0.0

#---Variables calculo SOC --------------------------------
Ip = Ip1 = Ip2 = DS = 0.0

#---Variables Placas --------------------------------
Wplaca = Iplaca = Vplaca = 0.0   # w, V e Intensidad de Placas(valor intensidad tras el regulador)
Wh_placa = Wh_consumo = 0.0

#---Variables Auxiliares --------------------------------
Aux1 = Aux2 = 0.0       # Valores de captura auxiliares (salida regulador, Iplaca2, etc)
CD1 = CD2 = CD3 = CD4 = CD5 = 0.0 # contadores que se ponen a cero cada dia
C1 = C2 = C3 = C4 = C5 = 0.0      # contadores que NO se ponen a cero cada dia
Nlog = Nlog_max = 30 # Contador Numero de log maximos cada minuto
log=''               # Valor del log 

#---Variables Red Comercial / Generador---------------------------
Wred = Ired = Vred = EFF = 0.0     # Valores de red AC
Vred_max = 0  
Vred_min = 10000                   # Variables para guardar Vred maximo  y minimo diario
Wh_red = Whp_red = Whn_red = 0.0   # Variables para guardar Wh inyectados o consumidos de red
EFF_max = 0
EFF_min = 100                      #Variables para guardar Eficiencia DC/AC maxima y minima diaria

#---Variables temperatura --------------------------------
Temp = 0.0         # temperatura baterias
Coef_Temp = 0.0    # Coeficiente de compensacion de temperatura para Vflot/Vabs 

#---Variables reles --------------------------------
t_refresco_rele = time.time() #utilizado en secuenciacion escritura de refresco en reles
Puerto = estado = 0

## Definir diccionarios Rele y Rele_Ant
Rele = {}        # Situacion actual de los reles
Rele_Dict = {}   # Diccionario completo de la tabla de Reles

Rele_Ant = {}    # Situacion anterior de los reles
Rele_H = {}      # Situacion condiciones horario
Rele_Tiempo = {} # Tiempo activo en segundos de cada rele en el dia


#---Variables PID --------------------------------
N = 5  # numero de muestras para control PID
Lista_errores_PID = [0.0 for i in range(5)]
PWM = IPWM_P = IPWM_I = IPWM_D = 0.0


# Creacion tabla RAM equipos en BD si no existe
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    # Comprobacion si tabla equipos existe y si no se crea
    sql_create = """ CREATE TABLE IF NOT EXISTS `equipos` (
                  `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
                  `tiempo` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha Actualizacion',
                  `sensores` varchar(1000) COLLATE latin1_spanish_ci NOT NULL,
                   PRIMARY KEY (`id_equipo`)
                 ) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""

    import warnings # quitamos el warning que da si existe la tabla equipos
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cursor.execute(sql_create)
        
    try: #inicializamos registros en BD RAM
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('FV','"en espera"'))
        db.commit()              
    except:
        pass
    try: 
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('RELES','"en espera"'))
        db.commit()
    except:
        pass    
        
except:
    print (Fore.RED,'ERROR inicializando tabla equipos')
    sys.exit()



# -----------------------MQTT MOSQUITTO ------------------------

def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))
    client.subscribe("PVControl/Log")
    client.subscribe("PVControl/Opcion")
    
     
def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Unexpected MQTT disconnection. Will auto-reconnect")
        else:
            client.loop_stop()
            client.disconnect()

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
        out1 = out #estado original
        ssr = json.loads(Rele_Dict[adr]['calibracion'])
        if len(ssr) > 0: # solo si existe calibracion
            for i in range(len(ssr)):
                if ssr[i][0] > out : break
            x1, y1 =  ssr[i-1][0], ssr[i-1][1] # puntos de la recta
            x2, y2 =  ssr[i][0], ssr[i][1]
            out = int(y1 + (y2-y1)/(x2-x1)*(out-x1)) # ecuacion recta
    except:
        pass 
    #print ('ssr=',ssr)
    #print (adr,' Potencia=',out1, 'PWM=',out)
    return out

def act_rele(adr,out) : # Activar Reles
   
    if simular_reles == 0:
        if int(adr/100) == 2: #Rele WIFI por MQTT
            try:
                out = calibracion_rele(adr,out)
                client.publish("PVControl/Reles/"+str(adr),int(out))  # via MQTT
                #print("PVControl/Reles/"+str(adr),int(out))
            except:
                if simular != 1:
                    logBD('Error rele wifi'+str(adr)+'='+ str(out))   

        elif int(adr/100) == 3: # Rele I2C
            #print ('act_rele=',adr,out)
            adr_pcf=int(adr/10)
            puerto= adr%adr_pcf
            try:
                estado = bus.read_byte(adr_pcf)  #devuelve el valor en decimal
                #print('Out=',out, ' estado PCF=',bin(estado)[2:10].zfill(8), end='')
                if out == 100 :
                    i2c_out = estado & (2**(puerto-1) ^ (255))
                else :
                    i2c_out = estado | 2**(puerto-1)
                bus.write_byte(adr_pcf,i2c_out)
                #print(' adr_pcf=',adr_pcf, ' i2c_out=',bin(i2c_out)[2:10].zfill(8))
                
            except:
                if simular != 1:
                    logBD('Error bus I2C '+str(adr)+ '='+ str(out))

        elif int(adr/100) == 4: # Rele GPIO .. esta por regulacion SC
            try:
                #if DEBUG >= 2: print('rele GPIO=',adr, int(out))
                for I in range (NGPIO):
                    if Rele_SSR[I][1] == adr % 100:
                        out=int(out) #por ahora resolucion maxima de 1 
                        
                        #print('rele GPIO=',adr, 'duty=',int(out))
                        
                        Rele_SSR[I][0].ChangeDutyCycle(out)
                        if out == 0 or out == 100:
                            pass
                            #Rele_SSR[I][0].ChangeFrequency(5)
                        elif out <= 50:
                            #print (' frec=',out)
                            Rele_SSR[I][0].ChangeFrequency(out)
                        else:
                            Rele_SSR[I][0].ChangeFrequency(100-out)
                            #print (' frec=',100-out)
                        break
            except:
                print ('Error rele GPIO')
                print (I, Rele_SSR[I][0],Rele_SSR[I][1], adr,out)         

        elif int(adr/100) == 5: #Rele Sonoff (tasmota)
            try:
                if int(adr/10) >= 58: # Dejo 58X y 59X para reles ON/OFF, resto PWM
                    if out == 100: out = "ON"
                    else:          out = "OFF"
                    client.publish("cmnd/PVControl/Reles/"+str(adr)+"/POWER",str(out))  # via MQTT
                else:
                    out = calibracion_rele(adr,out)
                    client.publish("cmnd/PVControl/Reles/"+str(adr)[0:2]+"/Channel"+str(adr)[-1],str(out))  # PWM via MQTT  
                      
            except:
                logBD('Error rele TASMOTA '+str(adr)+'='+ str(out)) 


    return

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

def leer_sensor(n_sensor,sensor,anterior,minimo,maximo) :  # leer sensor
    try:
        y_err = 0.0 # error en lectura multiple
        if sensor=='ADS':
            Suma = 0; Max=-40000; Min=-Max
            if n_sensor == 'Ibat':
                N = 5
                for i in range(N):
                    l = adc.read_adc_difference(0, gain=16, data_rate=250)
                    Suma += l
                    Max = max(Max,l)
                    Min = min(Min,l)
                ADS = Suma/N
                y = round(0.0078127 * ADS * SHUNT1,2)
                y_err = round((Max-Min) * 0.0078127 * SHUNT1 ,2)
            
            elif n_sensor == 'Iplaca':
                N = 2
                for i in range(N):
                    l = adc.read_adc_difference(3, gain=16, data_rate=250)
                    Suma += l
                    Max = max(Max,l)
                    Min = min(Min,l)
                ADS = Suma/N
                y = round(0.0078127 * ADS * SHUNT2,2)
                y_err = round((Max-Min) * 0.0078127 * SHUNT2 ,2)
            elif n_sensor == 'Vbat':
                N = 5
                for i in range(N):
                    l = adc1.read_adc(0, gain=RES0_gain,data_rate=250)
                    Suma += l
                    Max = max(Max,l)
                    Min = min(Min,l)
                ADS = Suma/N
                y = round(ADS * 0.000125/RES0_gain * RES0,2) # A0   4,096V/32767=0.000125
                y_err = round((Max-Min) * 0.000125/RES0_gain * RES0,2)
            elif n_sensor == 'Aux1':
                y = round(adc1.read_adc(1, gain=RES1_gain,data_rate=128) * 0.000125/RES1_gain * RES1, 2)  # A1   4,096V/32767=0.000125 
                y_err = 0.0
            elif n_sensor == 'Vplaca':
                y = round(adc1.read_adc(2, gain=RES2_gain,data_rate=128) * 0.000125/RES2_gain * RES2, 2)  # A2   4,096V/32767=0.000125 
            elif n_sensor == 'Aux2':
                y = round(adc1.read_adc(3, gain=RES3_gain,data_rate=128) * 0.000125/RES3_gain * RES3, 2)  # A3   4,096V/32767=0.000125 
        
        
        elif sensor =='':
            return anterior, y_err
        else:
            y = float(eval(sensor))
            """
            pp1=[idx for idx, x in enumerate(sensor) if x=='_']    # indices de todos los '_'
            pp2=[idx for idx, x in enumerate(sensor) if x=='[']    # indices de todos los '['

            k=len(pp1)
            dif=0
            if k>0:
                for i in range(k):
                    #print('Caso pp1=',i,'--',sensor[pp1[i]-1:pp2[i]])
                    dif += (time.time() - eval("float("+sensor[pp1[i]-1:pp2[i]]+"['Tiempo_sg'])"))/k
            else:
                dif += time.time() - eval("float("+sensor[:pp2[0]]+"['Tiempo_sg'])")
                #print('Caso pp2=',sensor[pp2[0]])
               
            if dif < 10: y = float(eval(sensor))
            elif dif <20: y = float(anterior)
            else: y = 0.0
            """ 
    except:
        traceback.print_exc()
        print ('Error en sensor ', n_sensor, sensor)
        y = anterior
        logBD('-ERROR MEDIDA -'+n_sensor+ '='+sensor)
        time.sleep(5)

    if y < minimo or y > maximo:
        logBD('lectura incoherente '+n_sensor+'='+str(y))
        print ('Error min/max sensor ', n_sensor)
        
        y = anterior

    return y,y_err

def Calcular_PID (sensor,objetivo,P,I,D):
    global Lista_errores_PID, IPWM_P, IPWM_I, IPWM_D
    
    valor = eval(sensor)
    
    # Desplazamos un elemento en la Lista de errores
    Lista_errores_PID = Lista_errores_PID[-1:] + Lista_errores_PID[:-1] 
    
    # Calculo Termino Proporcional PID
    error_actual = Lista_errores_PID[0] = valor - objetivo
    """
    if objetivo >= 0:
        error_actual = Lista_errores_PID[0] = valor - objetivo
    else:
        error_actual = Lista_errores_PID[0] = objetivo - valor
    """
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
    global Diver #,PWM
    
    Objetivo_PID= TP['objetivo_PID']   # Variable sensora de PID
    Diver = Calcular_PID (TP['sensor_PID'],Objetivo_PID,TP['Kp'],TP['Ki'],TP['Kd']) # 'sensor', objetivo, P,I,D 
    
    Diver_Max = 200 # Ya veremos si lo pongo en Parametros_FV.py
    if Diver > Diver_Max: Diver = Diver_Max
    elif Diver < -Diver_Max : Diver=-Diver_Max
    
    PWM += Diver
    
    if PWM >= PWM_Max: PWM = PWM_Max
    if PWM <= 0: PWM = 0

    #print ('Vbat={0:>5}'.format(Vbat) ,TP['sensor_PID']+'={0:>5}'.format(round(eval(TP['sensor_PID']),1)),
    #       ' -- PWM={0:>3} -- Incr={1:>4} -- Ibat={2:>6}'.format(round(PWM,0),round(Diver,1), round(Ibat,1)))
    return PWM

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

##  ------ inicializamos reles apagandolos  ------------------------
sql = 'SELECT * FROM reles'
nreles = cursor.execute(sql)
nreles = int(nreles)  # = numero de reles
columns = [column[0] for column in cursor.description] # creacion diccionario Tabla Reles
TR=[] 
for row in cursor.fetchall(): TR.append(dict(zip(columns, row)))
TR_refresco = TR[:] # lista copia de tabla reles para ir refrescando 1 valor por ciclo en los reles

Rele_SSR = [ ]
NGPIO =0 # Num Reles GPIO

for r in TR:
    Rele[r['id_rele']] = Rele_Ant[r['id_rele']] = Rele_H[r['id_rele']] = 0
    tipo_rele = int(r['id_rele']/100)
    
    act_rele(r['id_rele'],0)

    if tipo_rele == 4: # Inicializo Rele SSR en GPIO
        NGPIO_PIN = r['id_rele'] % 100
        #print (NGPIO_PIN , TR[I]['id_rele'] % 100)
  
        GPIO.setup(NGPIO_PIN, GPIO.OUT)
        Rele_SSR.append ([GPIO.PWM(NGPIO_PIN, 5),NGPIO_PIN])# 5hz
        
        #print  ('NGPIO=',NGPIO, '- NGPIO_PIN=',NGPIO_PIN)
        Rele_SSR[NGPIO][0].start(0)
        NGPIO +=1

if nreles > 0 : # apagado reles en BD
    sql = "UPDATE reles SET estado = 0"
    cursor.execute(sql)

## ------------------------------------------------------------
### Calcular voltaje sistema (12,24 o 48)
#print ('ERROR LECTURA VOLTAJE BATERIA.....SISTEMA POR DEFECTO a 24V')
if AH > 1:
    try:
        if simular != 1 and Vbat_sensor == 'ADS':
            Vbat, Vbat_err = leer_sensor('Vbat',Vbat_sensor,vsis*12.0,vbat_min,vbat_max)
        else:
            Vbat = vsis * 12.0
    except:
        # TODO: reformular esto, hay cambio de parametros
        pass

    if Vbat > 11 and Vbat < 15.5 : vsis = 1
    elif Vbat > 22 and Vbat < 31 : vsis = 2
    elif Vbat > 44 and Vbat < 62 : vsis = 4
    else : log='Error: Imposible reconocer el voltaje del sistema'

    Vflot = 13.7 * vsis
    Vabs = 14.4 * vsis
    Objetivo_PID = 17.2 * vsis #pongo un valor alto no alcanzable

print(Fore.RED+'Pulsa Ctrl-C para salir...'+Fore.RESET)

log = ' Arrancando programa fv.py \nBateria\Red = ' + str(Vbat) + 'v' + log
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

#nbucle = Wconsumo = 0
try:
    while True:
        #print (time.strftime("%Y-%m-%d %H:%M:%S"),' Bucle',)
        """
        cursor.close()
        db.close()
        
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        """
        ee=10

        t_muestra_7=(time.time()-hora_m) * 1000

        hora1=time.time()
        
        if Grabar == 1: #leer BD cada t_muestra * N_muestras
            ### B1 ---------- Cargar tablas parametros, reles , reles_c, reles_h ---------------------
            #print ('Grabar = 1')
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

            sql='SELECT * FROM reles'
            nreles=cursor.execute(sql)
            nreles=int(nreles)  # = numero de reles

            columns = [column[0] for column in cursor.description] # creacion diccionario Tabla Reles
            TR=[] 
            for row in cursor.fetchall(): TR.append(dict(zip(columns, row)))
                        
            for r in TR: # actualizar diccionarios por si se han creado nuevos reles
                Rele[r['id_rele']] = r['estado'] # actualizamos diccionario Reles con valor en BD
                Rele_H[r['id_rele']] = 0 # inicializamos a cero el diccionario para control horario
                Rele_Dict[r['id_rele']] = r # guado todo los campos de la tabla Reles en BD
                
                
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
            
        ee=20
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
        
        if t_muestra > t_muestra_max:
            logBD('TmuestraX='+str(int(t_muestra_1))+'/'+str(int(t_muestra_2))+'/'+str(int(t_muestra_3))+'/'+str(int(t_muestra_4))+'/'+str(int(t_muestra_5))+'/'+str(int(t_muestra_6))+'/'+str(int(t_muestra_7))+'/'+str(int(t_muestra_8)))
       
        if DEBUG >= 2:
            print(Style.BRIGHT + Fore.YELLOW,end='')
            print('{:<28}'.format('T='+str(int(t_muestra_1))+'/'+str(int(t_muestra_2))+
              '/'+str(int(t_muestra_3))+'/'+str(int(t_muestra_4))+'/'+
              str(int(t_muestra_5))+'/'+str(int(t_muestra_6))+'/'+
              str(int(t_muestra_7))+'/'+str(int(t_muestra_8))),end='')  
            print(Fore.RESET,end='')
            
        if pub_time == 1:
            client.publish("PVControl/Opcion/Time",str(int(t_muestra_1))+'/'+str(int(t_muestra_2))+'/'+str(int(t_muestra_3))+'/'+str(int(t_muestra_4))+'/'+str(int(t_muestra_5))+'/'+str(int(t_muestra_6))+'/'+str(int(t_muestra_7))+'/'+str(int(t_muestra_8)))
            
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
            
        else:
            ## Capturando valores desde BD en tabla equipos
            ee=30.1
            sql = 'SELECT * FROM equipos'
            nequipos = int(cursor.execute(sql))

            d_={}
            for row in cursor.fetchall(): d_[row[0]] = json.loads(row[2])
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
            if usar_sma == 1:
                archivo_ram='/run/shm/datos_sma.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_sma = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue
            
            if usar_smameter == 1:
                archivo_ram='/run/shm/datos_smameter.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_smameter = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue
            
            ee=30.41              
            if usar_fronius == 1:
                archivo_ram='/run/shm/datos_fronius.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_fronius = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue   

            ee=30.42        
            if usar_huawei == 1:
                archivo_ram='/run/shm/datos_huawei.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_huawei = pickle.load(f)
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
            
            ee=34            
            Ibat, Ibat_err = leer_sensor('Ibat',Ibat_sensor,Ibat,Ibat_min_log,Ibat_max_log)            
            Vbat, Vbat_err = leer_sensor('Vbat',Vbat_sensor,Vbat,Vbat_min_log,Vbat_max_log)
            Wbat = Vbat * Ibat # W instantaneos a bateria
            
            Ired, Ired_err = leer_sensor('Ired',Ired_sensor,Ired,Ired_min_log,Ired_max_log)            
            Vred, Vred_err = leer_sensor('Vred',Vred_sensor,Vred,Vred_min_log,Vred_max_log)            
            EFF, EFF_err = leer_sensor('EFF',EFF_sensor,EFF,EFF_min_log,EFF_max_log)
            Wred = Vred * Ired # W instantaneos a red
                
            Iplaca, Iplaca_err = leer_sensor('Iplaca',Iplaca_sensor,Iplaca,Iplaca_min_log,Iplaca_max_log)
            if abs(Iplaca) < Iplaca_error: Iplaca =0 
            
            Vplaca, Vplaca_err = leer_sensor('Vplaca',Vplaca_sensor,Vplaca,Vplaca_min_log,Vplaca_max_log)
             
            Aux1, Aux1_err = leer_sensor('Aux1',Aux1_sensor,Aux1,Aux1_min_log,Aux1_max_log)
            Aux2, Aux2_err = leer_sensor('Aux2',Aux2_sensor,Aux2,Aux2_min_log,Aux2_max_log)
        
            Temp, Temp_err = leer_sensor('Temp',Temperatura_sensor,Temp,Temp_min_log,Temp_max_log)
                
            # evalua las expresiones definidas en Parametros_FV.py
            try:    Wconsumo = float(eval (Consumo_sensor)) 
            except: Wconsumo = 0
            try:    Wplaca = float(eval(Wplaca_sensor))
            except: Wplaca = 0
            
      ### ------------------ Control Excedentes...Cálculo salida PWM ----------
        ee=36
        PWM = Calcular_PWM(PWM)
        
        ##################################################################
        t_muestra_1=(time.time()-hora_m) * 1000

        ### CALCULO Wh_BAT y Wh_PLACA
        
        dia_anterior = dia
        dia = time.strftime("%Y-%m-%d")

        if dia_anterior != dia: #cambio de dia
            Wh_bat = Whp_bat = Whn_bat = Wh_placa = Whp_red = Whn_red = 0.0
            CD1 = CD2 = CD3 = CD4 = CD5 = 0.0
            Tbulk = Tflot = Tabs = Tflot_bulk= 0  #Tecu ??
            SOC_min = SOC_max = SOC
            Vbat_max = Vbat_min = Vbat
            Vred_max = Vred_min = Vred
            EFF_max = EFF_min = EFF
                  
            Rele_Tiempo = {} # inicializo diccionaro tiempo de reles 
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
            
        ee=40
            
        t_muestra_2=(time.time()-hora_m) * 1000
        
        #------------- Asignamos valores al diccionario para parametros condiciones ...
        DatosFV['Temp'] = Temp                 # Tempertura (Baterias, ...)
        DatosFV['Vplaca'] = Vplaca             # Voltaje en placas
        DatosFV['Iplaca'] = Iplaca             # Intensidad de placas (referenciada a bateria si existe)
        DatosFV['Wplaca'] = Wplaca             # Watios generaos por placas
        DatosFV['PWM'] = PWM                   # Señal PWM de salida PID
        DatosFV['Wconsumo'] = Wconsumo         # Watios consumo
        
        DatosFV['Vbat'] = Vbat                 # Voltaje Bateria
        DatosFV['Ibat'] = Ibat                 # Intensidad a Bateria
        DatosFV['SOC'] = SOC                   # Estado Carga de Bateria
        DatosFV['Whn_bat'] = Whn_bat           # Wh descargados de bateria
        DatosFV['Whp_bat'] = Whp_bat           # Wh cargados a bateria
        DatosFV['Wh_bat'] = Whp_bat - Whn_bat  # Wh balance (cargados - descargados) bateria
        DatosFV['Wbat'] = Wbat                 # Wbateria = Vbat * Ibat
        
        DatosFV['Vred'] = Vred                 # Voltaje Red AC
        DatosFV['Ired'] = Ired                 # Intensidad a Red AC
        DatosFV['EFF'] = EFF                   # Eficiencia conversion DC/AC
        DatosFV['Whn_red'] = Whn_red           # Wh consumidos de red
        DatosFV['Whp_red'] = Whp_red           # Wh inyectados a red
        DatosFV['Wh_red'] = Whp_red - Whn_red  # Wh balance (inyectados - consumidos) red
        DatosFV['Wred'] = Wred                 # Wred =  Vred * Ired
        
        DatosFV['Aux1'] = Aux1                 # Campo auxiliar1
        DatosFV['Aux2'] = Aux2                 # Campo auxiliar2
        
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
        ee=50
        #### Cargamos los valores actuales de los reles  en Rele_Ant####
        
        Rele_Ant = Rele.copy() # ponemos estado del rele en el estado anterior
        for r in TR: Rele_H[r['id_rele']] = 0 # inicializamos a cero el diccionario para control horario
        
        #### Encendemos virtualmente y apagamos SI condiciones FV o HORARIAS no se cumplen####
        ee=52
        for r in TCFV: # enciendo reles con condiciones FV
            if r['prioridad'] == 0: # no actuo en reles de excedentes (prioridad > 0) 
                Rele[r['id_rele']] = r['salto'] # pongo valor del salto
                # no me gusta... deberia ser al valor ant + salto y ver si no me paso de 100

        ee=54
        for r in TCH: # enciendo reles con condiciones horario
            if r['prioridad'] == 0: # no actuo en reles de excedentes
                Rele[r['id_rele']] = r['salto'] # pongo valor del salto
                # no me gusta... deberia ser al valor ant + salto y ver si no me paso de 100

        # -------------------- Bucle de condiciones de horario --------------------------
        ee=56

        for r in TCH:
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

        for r in TCH:
            id_rele = r['id_rele']
            
            if Rele_H[id_rele] == 0:
                Rele[id_rele] = 0 #apago rele
                # deberia ser quitar salto y ver que no me paso de 0
                
                Rele_H[id_rele] = -1 # para quitar posibilidad de ser rele Diver en el ciclo

        # -------------------- Bucle de condiciones de parametros FV --------------------------
        ee=58
        for r in TCFV:
            id_rele = r['id_rele']
            
            if r['condicion'] == '<':
                if r['operacion'] == 'ON' and DatosFV[r['parametro']] > r['valor'] and Rele_Ant[id_rele] == 0 :
                    Rele[id_rele] = 0
                    # deberia ser quitar salto y ver que no me paso de 0
                    
                if r['operacion'] == 'OFF' and DatosFV[r['parametro']] <= r['valor'] :
                    Rele[id_rele] = 0

            elif r['condicion'] == '>':
                if r['operacion'] == 'ON' and DatosFV[r['parametro']] < r['valor'] and Rele_Ant[id_rele] == 0 :
                    Rele[id_rele] = 0
                if r['operacion'] == 'OFF' and DatosFV[r['parametro']] >= r['valor'] :
                    Rele[id_rele] = 0

        # -------------------- Bucle de condiciones  --------------------------
        ee=60
        for r in TC:
            try:
                TC1 = r['condicion1']
                TC2 = r['condicion2']
                #print(TC1],TC2) 
                if TC1 in ('', ' ','1'): TC1 = 'True'          
                if TC2 in ('', ' ','1'): TC2 = 'True'
                if (eval(TC1) and eval(TC2)): exec(r['accion']) 
            except:
                print ('Error Condicion ',str(r['id_condicion']))
                logBD('Error en id_condicion='+str(r['id_condicion']))

        #-------------------- Bucle encendido/apagado reles ------------------------------------
        ee=62
        Flag_Rele_Encendido = 0
        for r in TR:
            id_rele = r['id_rele']
            
            ### forzado ON/OFF
            if r['modo'] == 'ON' :
                Rele[id_rele] = 100
                
            if r['modo'] == 'OFF' :
                Rele[id_rele] = 0

            #print ('Despues Condiciones FV - Rele',id_rele,'=',Rele[id_rele], 'Ant=',Rele_Ant[id_rele], ' Flag=',Flag_Rele_Encendido)

            ### dejar rele como esta     
            if Rele[id_rele] == 100 and Rele_Ant[id_rele] < 100 and Flag_Rele_Encendido == 1 : 
                #print ('Dejo el rele ', id_rele, ' para encender en otro ciclo por flag ', Rele[id_rele] ,'/', Rele_Ant[id_rele] )
                Rele[id_rele] = Rele_Ant[id_rele]      #dejar rele en el estado anterior
                
            ### encender rele
            #print (id_rele,Rele[id_rele],Rele_Ant[id_rele])
            #if Rele[id_rele] != Rele_Ant[id_rele] and Flag_Rele_Encendido == 0 :
            if Rele[id_rele] == 100 and Flag_Rele_Encendido == 0 and Rele_Ant[id_rele] < 100 :
                print (tiempo,' - Enciendo rele ',id_rele)
                act_rele(id_rele,100)
                if r['prioridad']== 0: Flag_Rele_Encendido = 1 # activo flag solo para reles que no son de excedentes
            
            ### apagar rele
            if Rele[id_rele] == 0 and Rele_Ant[id_rele]>0: # and r['prioridad']== 0:
                print (tiempo,' - Apago rele ',id_rele)
                act_rele(id_rele,0) #apagar rele
        
      ## --------- BUCLE DIVER + ACTIVACION RELES CONTROL DE EXCEDENTES -------------
        t_muestra_3=(time.time()-hora_m) * 1000
        ee=90
        reles_exc_prio = {}  # inicializacion dict reles excedentes por prioridad
        PWM_max = 0
        for r in TR:
            if r['modo'] == 'PRG' and r['prioridad']!= 0 and Rele_H[r['id_rele']] != -1 and Flag_Rele_Encendido != 1:
                if r['prioridad'] not in reles_exc_prio.keys():
                    reles_exc_prio [r['prioridad']] = []
                reles_exc_prio[r['prioridad']].append({'id_rele': r['id_rele'], 'salto': r['salto']})
            PWM_max += 100

        ee=100
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
                        valor = min(100,round(PWM_R/nreles_prio))
                        salto = rele_prio['salto']
                        nivel_rele =  int(salto * round(valor/salto))
                        Rele[id_rele] = (min(PWM_R, nivel_rele) // salto) * salto

                        if Rele[id_rele] != Rele_Ant[id_rele]:
                            act_rele(id_rele, Rele[id_rele])

                        PWM_R -= Rele[id_rele]
                        PWM_R = max(0,PWM_R)
                        nreles_prio -= 1
                        if DEBUG >= 100: print('Reles PWM: ', id_rele, '->', Rele[id_rele], '(salto=',salto,'PWM_R=', PWM_R,')')
                    
        else: #salida manual de reles de excedentes por si se manipulan en condiciones
            for prio in reles_exc_prio.keys():
                for rele_prio in reles_exc_prio[prio]:
                    id_rele = rele_prio['id_rele']
                    if Rele[id_rele] != Rele_Ant[id_rele]:
                        act_rele(id_rele,Rele[id_rele])
                        Rele_Ant[id_rele]=Rele[id_rele]
            
      ## --------- Escribir en la BD Tabla Reles el Estado RELES -------------------------
        t_muestra_4=(time.time()-hora_m) * 1000
        ee=200
        if Grabar == 1: # actualizo BD cada N bucles
            
            for I in range(nreles):
                id_rele = TR[I]['id_rele']
                if Rele[id_rele] != TR[I]['estado']:
                    sql = "UPDATE reles SET estado =" +str(Rele[id_rele])+ " WHERE id_rele = " + str(id_rele)
                    cursor.execute(sql)
        
        # Refresco valor de rele 
        if time.time()-t_refresco_rele > 2: # refrescar 1 rele cada max(t_muestra, 2sg)  
            t_refresco_rele = time.time()
            if len(TR_refresco) > 0:
                act_rele(TR_refresco[0]['id_rele'], Rele[TR_refresco[0]['id_rele']])
                #print ('refrescando rele',TR_refresco[0])
                TR_refresco.pop(0)
            else:
                TR_refresco = TR[:]
                    
        if TP['grabar_reles'] == "S" and Grabar == 1 and nreles > 0: # Grabar en BD actividad reles
            for I in range(nreles):
                id_rele = TR[I]['id_rele']
                estado = Rele[id_rele]
                sql = ('SELECT id_rele,segundos_on,nconmutaciones FROM reles_segundos_on WHERE fecha='+
                      '"'+time.strftime("%Y-%m-%d")+'" and id_rele =' + str(id_rele))
                
                segundos_on = 0
                try:
                    nreles_on = cursor.execute(sql)
                    nreles_on = int(nreles_on)
                    if estado > 0 :
                        segundos_on = float(TP['t_muestra'] * TP['n_muestras_grab'])
                        nconmutaciones = 1

                        if nreles_on >= 1:
                            TS = cursor.fetchall()
                            
                            segundos_on = TS[0][1] + round((t_muestra*TP['n_muestras_grab']*estado/100),2)  # calculo funcionamiento real reles PWM
                            if TR[I]['estado'] == 0:
                                nconmutaciones = TS[0][2] + 1
                            else:
                                nconmutaciones = TS[0][2]
                            sql = ("UPDATE reles_segundos_on SET segundos_on =" +str(segundos_on)+
                                   ",nconmutaciones =" + str(nconmutaciones)+ " WHERE id_rele = " +
                                   str(id_rele) + ' and fecha = "' + time.strftime("%Y-%m-%d") +'"')
                            cursor.execute(sql)
                        else :
                            cursor.execute("""INSERT INTO reles_segundos_on
                                            (id_rele,fecha,segundos_on,nconmutaciones)
                                            VALUES (%s,%s,%s,%s)""",
                                            (id_rele,time.strftime("%Y-%m-%d"),segundos_on,1))
                        
                        Rele_Tiempo[id_rele] = segundos_on
                    
                    if not(id_rele in Rele_Tiempo): Rele_Tiempo[id_rele] = 0  #aseguramos que el diccionario contiene todos los reles

                    
                        
                except:
                    db.rollback()
                    print ('Error grabacion Reles_segundos_on',ee)
                    logBD('Error grabacion Reles_segundos_on')
                    
                if TP['grabar_reles'] == "S" and Grabar == 1 and TR[I]['grabacion'] == "S" and Rele[id_rele] != TR[I]['estado']:
                    try:
                        cursor.execute("""INSERT INTO reles_grab (Tiempo,id_rele,valor_rele)
                                       VALUES(%s,%s,%s)""",(tiempo,id_rele,estado))
                        #db.commit()
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
        
        if TP['grabar_datos'] == "S" and eval(grabar_datos_s): #grabar datos_s 
            if DEBUG >=2: print ('S',end='')
            try:
                cursor.execute("""INSERT INTO datos_s (Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,
                   Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,
                   IPWM_P,IPWM_I,IPWM_D,Kp, Ki,Kd,Vred,Wred,Whn_red,Whp_red) 
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (tiempo_us,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,
                   IPWM_P,IPWM_I,IPWM_D,TP['Kp'],TP['Ki'],TP['Kd'],Vred,Wred,Whn_red,Whp_red))
                db.commit()
            except:
                db.rollback()
                logBD('Registro datos_s no grabado')
        else :
            db.commit()

        ## ------------------------------------------------
        t_muestra_5=(time.time()-hora_m) * 1000
        
        # ----------------- Guardamos datos_fv.json ------
        ee=300
        datos_FV =  {'Vbat':Vbat,'Ibat':Ibat,'Wbat':round(Wbat),'Whp_bat':int(Whp_bat),'Whn_bat':int(Whn_bat),
                     'Vbat_min':Vbat_min,'Vbat_max':Vbat_max,
                     'DS':round(DS,2),'SOC':SOC,'SOC_min':SOC_min,'SOC_max':SOC_max,
                     'Mod_bat':Mod_bat,'Tabs':int(Tabs),'Tflot':int(Tflot),'Tflot_bulk':int(Tflot_bulk),
                     'Vplaca':Vplaca,'Iplaca':Iplaca,'Wplaca':round(Wplaca),'Wh_placa':round(Wh_placa),
                     'Vred':Vred,'Wred':Wred,'Whp_red':int(Whp_red),'Whn_red':int(Whn_red),
                     'Vred_min':Vred_min,'Vred_max':Vred_max,'EFF':EFF,'EFF_min':EFF_min,'EFF_max':EFF_max,
                     'Wconsumo':round(Wconsumo),'Wh_consumo': round(Wh_consumo),
                     'Temp':Temp,'PWM':int(PWM),
                     'Aux1':Aux1,'Aux2':Aux2
                     }
        
        salida_FV = json.dumps(datos_FV)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida_FV}' WHERE id_equipo = 'FV'") # grabacion en BD RAM
        cursor.execute(sql)
                    
        ee=310
        salida_RELES = json.dumps(Rele_Dict)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida_RELES}' WHERE id_equipo = 'RELES'") # grabacion en BD RAM
        cursor.execute(sql)
        
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
        
        ee=320
        if DEBUG >= 1:
            #print (tiempo,'-',end='')
            print(' {0:4}ms - Sensor={1}={2:.2f}'.format(int(T_ejecucion*1000),TP['sensor_PID'],TP['objetivo_PID']),end='')
            print (Fore.CYAN+'/{0:.2f}'.format(eval(TP['sensor_PID'])),end='')
            if AH > 0:
                print (Fore.MAGENTA+' / Vbat={0:.2f}- Iplaca={1:.2f}- Ibat={2:.2f}- Wcon={3:.2f}- PWM={4:.0f}'.format(Vbat,Iplaca,Ibat,Wconsumo,PWM),Fore.RESET)
            else:
                print (Fore.MAGENTA+' / Vred={0:.2f}- Iplaca={1:.2f}- Ired={2:.2f}- Wcon={3:.2f}- PWM={4:.0f}'.format(Vred,Iplaca,Ired,Wconsumo,PWM),Fore.RESET)
                
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
