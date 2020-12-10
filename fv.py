#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-11-24


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
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' PVControl') #+Style.RESET_ALL)

#Parametros Instalacion FV
from Parametros_FV import *

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
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p2':
    DEBUG = 2
elif str(sys.argv[narg-1]) == '-p3':
    DEBUG = 3
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 100
else:
    DEBUG = 0
print (Fore.RED + 'DEBUG=',DEBUG)

if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]

#if (Vbat_sensor + Vplaca_sensor + Aux1_sensor+ Aux2_sensor + Ibat_sensor + Iplaca_sensor).find ('ADS') >=0 : 
bus = SMBus(1) # Activo Bus I2C

if (Vbat_sensor + Vplaca_sensor + Aux1_sensor+ Aux2_sensor).find ('ADS') >=0 : 
    # Alta ADS1115_1 - pin addr a 3V3
    # A0=Vbat // A1=Aux1 // A2= Vplaca// A3= Aux2
    adc1 = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1) 

if (Ibat_sensor + Iplaca_sensor).find ('ADS') >=0:
    # Alta ADS1115_4 - pin addr a GND
    # A0=Ibat // A1=Ibat // // A2=Iplaca // A3=Iplaca
    adc = Adafruit_ADS1x15.ADS1115(address=0x4b, busnum=1)

#---------------------------------------------------------------
DatosFV = {} #Creamos diccionario para los datos FV

OP = {'id_rele':0,'nombre':1,'modo':2,'estado':3,'grabacion':4,'salto':5,'prioridad':6,
      'id_rele2':7,'operacion':8,'parametro':9,'condicion':10,'valor':11}
OPH = {'id_rele':0,'nombre':1,'modo':2,'estado':3,'grabacion':4,'salto':5,'prioridad':6,
       'id_rele2':7,'parametro_h':8,'valor_h_ON':9,'valor_h_OFF':10}
#NDIA = {'D':0,'L':1,'M':2,'X':3,'J':4,'V':5,'S':6}
NDIA = {'0':'D','1':'L','2':'M','3':'X','4':'J','5':'V','6':'S'}

#Inicializando las variables del programa
Grabar = 1 # Contador ciclo grabacion en BD

T_ejecucion_max = 0.0
 
hora_m = time.time() #para calcular tiempo entre muestras real
dia = time.strftime("%Y-%m-%d") # para cambio de dia y reinicializar Wh
tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

t_muestra = 5 # Inicializo Tiempo entre muestra real...idealmente TP[2]
t_muestra_1 = t_muestra_2 = t_muestra_3 = t_muestra_4 = t_muestra_5 = t_muestra_6 = 0 # muestras t ejecucion intermedias
T_ejecucion = 0

Ibat = 0.0      # Intensidad Bateria
Vbat = vsis*12.0     # Voltaje Bateria inicial
Mod_bat =''

Iplaca = Vplaca = 0.0   #  Voltaje e Intensidad de Placas(valor intensidad tras el regulador)

Aux1 = Aux2 = 0.0   # Valores de captura auxiliares (salida regulador, Iplaca2, etc)
Temp = 0.0      # temperatura baterias
Mtemp = 60      # Numero de segundos para leer temperatura

Ctemp = 0       # Contador del numero de muestra para leer temperatura
Vflot = Vabs = Vecu = 0.0   # Voltaje asociado a estado de flotacion/Absorcion/Ecu
Tflot = Tabs = Tecu = 0.0   # Tiempo asociado a estado de flotacion/Absorcion/Ecu
Tflot_bulk = Tbulk = 0.0    # Tiempo asociado al paso de FLOT a BULK 
SOC_max = SOC_min = 0     #Variable para guardar SOC maximo y minimo diario
Vbat_max = Vbat_min = 0    # Variable para guardar Vbat maximo  y minimo diario

flag_Abs= flag_Flot = 0

Coef_Temp = 0.0             # Coeficiente de compensacion de temperatura para Vflot/Vabs 

Nlog = Nlog_max = 30 # Contador Numero de log maximos cada minuto
minuto = time.strftime("%H:%M")

n_refresco_rele = 0 #utilizado en secuenciacion escritura de refresco en reles

CD1 = CD2 = CD3 = CD4 = CD5 = 0.0 # contadores que se ponen a cero cada dia
C1 = C2 = C3 = C4 = C5 = 0.0      # contadores que NO se ponen a cero cada dia

#---Variables calculo SOC --------------------------------
Ip = Ip1 = Ip2 = DS = 0.0

Puerto = estado = 0
Wh_bat = Whp_bat = Whn_bat = 0.0
Wh_placa = Wh_consumo = 0.0

N = 5  # numero de muestras para control PID
Lista_errores_PID = [0.0 for i in range(5)]
PWM = IPWM_P = IPWM_I = IPWM_D = 0.0


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

def act_rele(adr,out) : # Activar Reles
   
    if simular_reles == 0:
        if int(adr/100) == 2: #Rele WIFI
            try:
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

        elif int(adr/100) == 4: # Rele GPIO
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
            #print("Rele Sonoff")
            if out == 100: out = "ON"
            else:          out = "OFF"
            
            try:
                client.publish("cmnd/PVControl/Reles/"+str(adr)+"/POWER",str(out))  # via MQTT
                #print("cmnd/PVControl/Reles/"+str(adr)+"/POWER",str(out))
            except:
                logBD('Error rele sonoff '+str(adr)+'='+ str(out)) 




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
    except:
        traceback.print_exc()
        print ('Error en sensor ', n_sensor, sensor)
        y = anterior
        logBD('-ERROR MEDIDA -'+n_sensor+ '='+sensor)    

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
    
    Objetivo_PID= TP[5]   # Variable sensora de PID
    Diver = Calcular_PID (TP[6],Objetivo_PID,TP[7],TP[8],TP[9]) # 'sensor', objetivo, P,I,D 
    
    Diver_Max = 200 # Ya veremos si lo pongo en Parametros_FV.py
    if Diver > Diver_Max: Diver = Diver_Max
    elif Diver < -Diver_Max : Diver=-Diver_Max
    
    PWM += Diver
    
    if PWM >= PWM_Max: PWM = PWM_Max
    if PWM <= 0: PWM = 0

    #print ('Vbat={0:>5}'.format(Vbat) ,TP[6]+'={0:>5}'.format(round(eval(TP[6]),1)),
    #       ' -- PWM={0:>3} -- Incr={1:>4} -- Ibat={2:>6}'.format(round(PWM,0),round(Diver,1), round(Ibat,1)))
    return PWM

## RECUPERAR DE LA BD ALGUNOS DATOS ##
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql="""SELECT DS, DATE(Tiempo),Whp_bat,Whn_bat,Wh_placa, SOC, Vbat
         FROM datos ORDER BY id DESC limit 1"""
    cursor.execute(sql)
    var=cursor.fetchone()
    DS=float(var[0])
    HOY=str(var[1])
    SOC_min = SOC_max =float(var[5])
    Vbat_min = Vbat_max = float(var[6])
    
    if HOY == time.strftime("%Y-%m-%d"): #Comprueba que es el mismo dia
        Whp_bat=float(var[2])
        Whn_bat=float(var[3])
        Wh_placa=float(var[4])
        
        sql='SELECT min(SOC), max(SOC), min(Vbat), max(Vbat) FROM datos WHERE Tiempo >= CURDATE()'
        cursor.execute(sql)
        var=cursor.fetchone()
        SOC_min = float(var[0])
        SOC_max = float(var[1])
        Vbat_min = float(var[2])
        Vbat_max = float (var[3])        
    else:
         Whp_bat = Whn_bat = Wh_placa = 0.0

except Exception as e:
    print ("Sin registros en la tabla datos")

## Definir diccionarios Rele y Rele_Ant
Rele = {}        # Situacion actual de los reles
Rele_Ant = {}    # Situacion anterior de los reles
Rele_H = {}      # Situacion condiciones horario
Rele_Tiempo = {} # Tiempo activo en segundos de cada rele en el dia


##  ------ inicializamos reles apagandolos  ------------------------
sql = 'SELECT * FROM reles'
nreles = cursor.execute(sql)
nreles = int(nreles)  # = numero de reles
TR = cursor.fetchall()

Rele_SSR = [ ]
NGPIO =0 # Num Reles GPIO

for I in range(nreles): #apagado fisico 
    Rele_Ant[TR[I][0]] = Rele[TR[I][0]] = Rele_H[TR[I][0]] = 0
    
    tipo_rele = int(TR[I][0]/100)
    
    act_rele(TR[I][0],0)

    if tipo_rele == 4: # Inicializo Rele SSR en GPIO
        NGPIO_PIN = TR[I][0] % 100
        #print (NGPIO_PIN , TR[I][0] % 100)
  
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

try:
    if simular != 1 and Vbat_sensor == 'ADS':
        Vbat, Vbat_err = leer_sensor('Vbat',Vbat_sensor,vsis*12.0,vbat_min,vbat_max)
    else:
        Vbat = vsis * 12.0
except:
    # TODO: reformular esto, hay cambio de parametros
    pass

    
log=''
if Vbat > 11 and Vbat < 15.5 : vsis = 1
elif Vbat > 22 and Vbat < 31 : vsis = 2
elif Vbat > 44 and Vbat < 62 : vsis = 4
else : log='Error: Imposible reconocer el voltaje del sistema'

Vflot = 13.7 * vsis
Vabs = 14.4 * vsis
Objetivo_PID = 15.2 * vsis #pongo un valor alto no alcanzable

print(Fore.RED+'Pulsa Ctrl-C para salir...'+Fore.RESET)

log = ' Arrancando programa fv.py \nBateria = ' + str(Vbat) + 'v' + log
logBD(log) # incluyo mensaje en el log
if usar_telegram == 1:
    try:        
        pass
        #bot.send_message( cid, log)
    except:
        logBD("Error en Msg Telegram") # incluyo mensaje en el log


# Inicializo lista reles diver
Reles_D = [ ] 
for P in range(nreles):
    if TR[P][2] == 'PRG' and TR[P][6]!= 0:
       Reles_D.append([TR[P][0],TR[P][6],TR[P][5]]) #id_rele, prioridad, salto
Reles_D_Ord = sorted(Reles_D, key=lambda rr: rr[1])
Nreles_Diver = len(Reles_D_Ord) # Nº de reles Diver a considerar para reparto excedentes
PWM_Max = Nreles_Diver * 100

if DEBUG >= 100: print ('PWM_Max=',PWM_Max)

#########################################################################################
# -------------------------------- BUCLE PRINCIPAL --------------------------------------
#########################################################################################

#nbucle = consumo = 0
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
            TP=cursor.fetchone()
            
            Mod_bat = TP[10]
            Vflot = float(TP[11])
            Vabs = float(TP[12])
            Tabs_max = float(TP[13])
            Vequ = float(TP[14])
            Tequ_max = float(TP[15])
            
            sql='SELECT * FROM reles'
            nreles=cursor.execute(sql)
            nreles=int(nreles)  # = numero de reles
            TR=cursor.fetchall()
            
            for I in range(nreles): # actualizar diccionarios por si se han creado nuevos reles
                Rele[TR[I][0]] = TR[I][3] # actualizamos diccionario Reles_Out con valor en BD
                Rele_H[TR[I][0]] = 0 # inicializamos a cero el diccionario para control horario
           

            sql='SELECT * FROM reles INNER JOIN reles_c ON reles.id_rele = reles_c.id_rele'
            fvcon=cursor.execute(sql)
            fvcon=int(fvcon)  # = numero de condiciones
            R=cursor.fetchall()


            sql='SELECT * FROM reles INNER JOIN reles_h ON reles.id_rele = reles_h.id_rele'
            hcon=cursor.execute(sql)
            hcon=int(hcon)  # = numero de condiciones horarias
            H=cursor.fetchall()

            sql='SELECT * FROM condiciones WHERE activado is True ORDER BY id_condicion'
            ncon=cursor.execute(sql)
            ncon=int(ncon)  # = numero de condiciones
            TC=cursor.fetchall()
            
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
        i=-1 
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
            Ibat = random.choice([0,12,22,33,46,56,65,78,101,
                                -10,-20,-30,-40,-50,-60,-70,-80,-90])
            Iplaca = random.choice([0,10,20,30,45,57,67,77,88,99,102,110])
            Vbat = random.choice([22.5,23.7,24.0,24.4,25.5,26.3,27,27.5,28.2,29.1])
            Vplaca = random.choice([60,59.4,61,59.9,52,60.1,61.6,58.7,62,57.3])
            Wplaca = random.choice([600,590.40,610,590.90,520,600.10,610.60,580.70,620,570.30])
            Diver = random.choice([10,-10,11,20,-7,5,8,-8])  
            Temp = random.choice([10,12,14,16,18,20,22,24,26,28,30,32,34])
            Aux1 = random.choice([0,10,12,14,16,18,20,22,24,26,28,30,32,34])
            Aux2 = random.choice([0,10,12,14,16,18,20,22,24,26,28,30,32,34])
            Consumo = Vbat * (Iplaca-Ibat)
            
        else:
            ## Capturando valores desde xxxxx.pkl
            ee=30.1
            if usar_hibrido == 1:
                archivo_ram='/run/shm/datos_hibrido.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_hibrido = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue

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
                    
            if usar_fronius == 1:
                archivo_ram='/run/shm/datos_fronius.pkl'
                try:
                    with open(archivo_ram, 'rb') as f:
                        d_fronius = pickle.load(f)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue       
                    

            ee=30.5
            if usar_srne == 1:
                d_srne = Srne.get_datos()
                if d_srne is None:
                    logBD('error lectura archivo ram SRNE')
                    continue
            
            ee=30.6
            if usar_mux > 0:
                archivo_ram='/run/shm/datos_mux.json'
                try:
                    with open(archivo_ram, 'r') as f:
                        d_mux = json.load(f)
                        #print(d_mux)
                except:
                    logBD('error lectura '+archivo_ram)
                    continue
                
            ee=34
            Ibat, Ibat_err = leer_sensor('Ibat',Ibat_sensor,Ibat,ibat_min,ibat_max)            
            Vbat, Vbat_err = leer_sensor('Vbat',Vbat_sensor,Vbat,vbat_min,vbat_max)
            
            Iplaca, Iplaca_err = leer_sensor('Iplaca',Iplaca_sensor,Iplaca,iplaca_min,iplaca_max)
            if abs(Iplaca) < iplaca_error: Iplaca =0 
            
            Vplaca, Vplaca_err = leer_sensor('Vplaca',Vplaca_sensor,Vplaca,vplaca_min,vplaca_max)
            Aux1, Aux1_err = leer_sensor('Aux1',Aux1_sensor,Aux1,aux1_min,aux1_max)
            Aux2, Aux2_err = leer_sensor('Aux2',Aux2_sensor,Aux2,aux2_min,aux2_max)
        
            try:
                # evalua las expresiones definidas en Parametros_FV.py
                Consumo = float(eval (Consumo_sensor)) 
                Wplaca = float(eval(Wplaca_sensor))
            except:
                Consumo = 0
                Wplaca = 0

            if Temperatura_sensor != '' and Ctemp <= 0:
                if True: #usar_ds18b20 == 1:
                    archivo_ram='/run/shm/datos_ds18b20.pkl'
                    try:
                        with open(archivo_ram, 'rb') as f:
                            d_ds18b20 = pickle.load(f)
                    except:
                        logBD('error lectura '+archivo_ram)
                        continue
                Temp, Temp_err = leer_sensor('Temp',Temperatura_sensor,Temp,temp_min,temp_max)
                Ctemp=Mtemp # reinicio contador
                client.publish("PVControl/DatosFV/Temp",Temp)
                if DEBUG >= 100: print(Fore.BLUE +'Temp=',Temp,Fore.RESET,end='')
            else:
                Ctemp -= t_muestra # resto t_muestra

      ### ------------------ Control Excedentes...Cálculo salida PWM ----------
        ee=36
        PWM = Calcular_PWM(PWM)
        
        ##################################################################
        t_muestra_1=(time.time()-hora_m) * 1000

        ### CALCULO Wh_BAT y Wh_PLACA
        
        dia_anterior = dia
        dia = time.strftime("%Y-%m-%d")

        if dia_anterior != dia: #cambio de dia
            Wh_bat = Whp_bat = Whn_bat = Wh_placa = 0.0
            CD1 = CD2 = CD3 = CD4 = CD5 = 0.0
            Tbulk = Tflot = Tabs = Tflot_bulk= 0  #Tecu ??
            SOC_min = SOC_max = SOC
            Vbat_max = Vbat_min = Vbat
            Rele_Tiempo = {} # inicializo diccionaro tiempo de reles 
            
        else:
            if Ibat < 0: Whn_bat = round(Whn_bat - (Ibat * Vbat * t_muestra/3600),2)
            else:        Whp_bat = round(Whp_bat + (Ibat * Vbat * t_muestra/3600),2)

            Wh_placa = round(Wh_placa + (Wplaca * t_muestra/3600),2)

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

        if TP[4] != 0: # Actualizo SOC si en la BD es distinto de 0
            DS = AH*TP[4]/100
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
                    if TP[6] == 'Vbat':
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
                    if TP[6] == 'Vbat':
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
            
        
        ee=40
        if Grabar == 1: #publico cada t_muestra*N_muestras
            client.publish("PVControl/DatosFV/Ibat",Ibat)
            client.publish("PVControl/DatosFV/Iplaca",Iplaca)
            client.publish("PVControl/DatosFV/Vbat",Vbat)
            client.publish("PVControl/DatosFV/Vplaca",Vplaca)
            client.publish("PVControl/DatosFV/Wplaca",Wplaca)
            client.publish("PVControl/DatosFV/Aux1",Aux1)
            client.publish("PVControl/DatosFV/Aux2",Aux2)
            client.publish("PVControl/Reles/PWM", PWM)  # publico salida PWM
            client.publish("PVControl/DatosFV/SOC",SOC)
        
        t_muestra_2=(time.time()-hora_m) * 1000
        
        #------------- Asignamos valores al diccionario para parametros condiciones ...
        DatosFV['Vbat'] = Vbat
        DatosFV['Ibat'] = Ibat
        DatosFV['SOC'] = SOC
        DatosFV['Iplaca'] = Iplaca
        DatosFV['Aux1'] = Aux1
        DatosFV['Aux2'] = Aux2
        DatosFV['Temp'] = Temp
        DatosFV['Vplaca'] = Vplaca
        DatosFV['Wplaca'] = Wplaca
        DatosFV['PWM'] = PWM
        DatosFV['Consumo'] = Consumo
                
        # ------------------ Calculo del SOCmax, SOCmin, Vbat_max, Vbat_min ------------------
        if SOC > SOC_max:   SOC_max = SOC
        elif SOC < SOC_min: SOC_min = SOC
        
        if Vbat > Vbat_max:   Vbat_max = Vbat
        elif Vbat < Vbat_min: Vbat_min = Vbat

                
      ## ------------------ ALGORITMO CONDICIONES RELES -----------------------------
        ee=50
        #### Cargamos los valores actuales de los reles  en Rele_Ant####
        
        for I in range(nreles): # Calculo Numero reles wifi y actualizo Rele_Ant
            Rele_Ant[TR[I][0]] = Rele[TR[I][0]] # ponemos estado en BD del rele
            Rele_H[TR[I][0]] = 0 # inicializamos a cero el diccionario para control horario
        
            
        #### Encendemos virtualmente y apagamos SI condiciones FV o HORARIAS no se cumplen####
        
        ee=52
        for I in range(fvcon): # enciendo reles con condiciones FV
            if R[I][6] == 0: # no actuo en reles de excedentes
                Rele[R[I][0]] = R[I][5] # pongo valor del salto
                #print ('enciendo condiciones FV - Rele',R[I][0],'=',Rele[R[I][0]])
                # no me gusta... deberia ser al valor ant + salto y ver si no me paso de 100

        ee=54
        for I in range(hcon): # enciendo reles con condiciones horario
            if H[I][6] == 0: # no actuo en reles de excedentes
                Rele[H[I][0]] = H[I][5] # pongo valor del salto
                #print ('enciendo condiciones Horario - Rele',H[I][0],'=',Rele[H[I][6])
                
                # no me gusta... deberia ser al valor ant + salto y ver si no me paso de 100

        # -------------------- Bucle de condiciones de horario --------------------------
        ee=56

        for I in range(hcon):
            id_rele = H[I][0]
            
            diaok = 0 # variables de control para ver si esta dentro de horario
            horaok = 0
            dias_activos=H[I][OPH['parametro_h']].upper()
            
            if  dias_activos == 'T': #Todos los dias de la semana
                diaok = 1
            elif NDIA[diasemana] in dias_activos:
                diaok = 1

            if str(H[I][OPH['valor_h_ON']]).zfill(8) > str(H[I][OPH['valor_h_OFF']]).zfill(8): #True si periodo pasa por 0:00
                if (hora >= str(H[I][OPH['valor_h_ON']]).zfill(8) and hora <= "23:59:59"): 
                    horaok = 1                                                       
                if (hora >= "00:00:00" and hora <= str(H[I][OPH['valor_h_OFF']]).zfill(8)): 
                    horaok = 1

            elif (hora >= str(H[I][OPH['valor_h_ON']]).zfill(8) and hora <= str(H[I][OPH['valor_h_OFF']]).zfill(8)):
                horaok = 1

            if diaok == 1 and horaok == 1:
                Rele_H[id_rele] += 1

        for I in range(hcon):
            id_rele = H[I][0]
            
            if Rele_H[id_rele] == 0:
                Rele[id_rele] = 0 #apago rele
                # deberia ser quitar salto y ver que no me paso de 0
                
                Rele_H[id_rele] = -1 # para quitar posibilidad de ser rele Diver en el ciclo

        """
        for I in range(nreles): # ver reles tras Condiciones Hora 
            id_rele = TR[I][0]
            #print ('Despues Condiciones Hora- Rele',id_rele,'=',Rele[id_rele], 'Out_H=',Rele_H[id_rele])
        """

        # -------------------- Bucle de condiciones de parametros FV --------------------------
        ee=58
        for I in range(fvcon):
            id_rele = R[I][0]
            
            if R[I][OP['condicion']] == '<':
                if R[I][OP['operacion']] == 'ON' and DatosFV[R[I][OP['parametro']]] > R[I][OP['valor']] and Rele_Ant[id_rele] == 0 :
                    Rele[id_rele] = 0
                    # deberia ser quitar salto y ver que no me paso de 0
                    
                if R[I][OP['operacion']] == 'OFF' and DatosFV[R[I][OP['parametro']]] <= R[I][OP['valor']] :
                    Rele[id_rele] = 0

            if R[I][OP['condicion']] == '>':
                if R[I][OP['operacion']] == 'ON' and DatosFV[R[I][OP['parametro']]] < R[I][OP['valor']] and Rele_Ant[id_rele] == 0 :
                    Rele[id_rele] = 0
                if R[I][OP['operacion']] == 'OFF' and DatosFV[R[I][OP['parametro']]] >= R[I][OP['valor']] :
                    Rele[id_rele] = 0

        # -------------------- Bucle de condiciones  --------------------------
        ee=60
        for I in range(ncon):
            try:
                TC1 = TC[I][1]
                TC2 = TC[I][2]
                #print(TC1],TC2) 
                if TC1 in ('', ' ','1'): TC1 = 'True'          
                if TC2 in ('', ' ','1'): TC2 = 'True'
                if (eval(TC1) and eval(TC2)): exec(TC[I][3]) 
            except:
                print ('Error Condicion ',str(TC[I][5]))
                logBD('Error en id_condicion='+str(TC[I][5]))

        #-------------------- Bucle encendido/apagado reles ------------------------------------
        ee=62
        Flag_Rele_Encendido = 0
        for I in range(nreles):
            id_rele = TR[I][0]
            
            ### forzado ON/OFF
            if TR[I][OP['modo']] == 'ON' :
                Rele[id_rele] = 100
                
            if TR[I][OP['modo']] == 'OFF' :
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
                if TR[I][6]== 0: Flag_Rele_Encendido = 1 # activo flag solo para reles que no son de excedentes
            
            ### apagar rele
            if Rele[id_rele] == 0 and Rele_Ant[id_rele]>0: # and TR[I][6]== 0:
                print (tiempo,' - Apago rele ',id_rele)
                act_rele(id_rele,0) #apagar rele
        
            
            """
            if Rele[id_rele] != TR[I][3]:
                sql = "UPDATE reles SET estado =" +str(Rele[id_rele])+ " WHERE id_rele = " + str(id_rele)
                cursor.execute(sql)
            """
            
      ## --------- BUCLE DIVER + ACTIVACION RELES CONTROL DE EXCEDENTES -------------
        t_muestra_3=(time.time()-hora_m) * 1000
        ee=90
        Reles_D = [ ] # inicializo lista reles diver
        for P in range(nreles):
            id_rele = TR[P][0]
            
            if TR[P][2] == 'PRG' and TR[P][6]!= 0 and Rele_H[id_rele] != -1 and Flag_Rele_Encendido != 1:
               Reles_D.append([TR[P][0],TR[P][6],TR[P][5]]) #id_rele, prioridad, salto

        Reles_D_Ord = sorted(Reles_D, key=lambda rr: rr[1]) # Ordeno lista reles por prioridad
        
        Nreles_Diver = len(Reles_D_Ord) # Nº de reles Diver a considerar para reparto excedentes
        PWM_Max= Nreles_Diver * 100
    
        ee=100
        if PWM >=0 : # situacion normal
            #print ('Reles diver=',Nreles_Diver)
            #print (Reles_D_Ord)
            if Nreles_Diver > 0:
                # Repartimos PWM entre los reles
                PWM_R = PWM
                for P in range(Nreles_Diver):
                    id_rele = Reles_D_Ord[P][0]
                    
                    valor = min(100,PWM_R)
                    salto = Reles_D_Ord[P][2]
                    
                    Rele[id_rele] =  int(salto * round(valor/salto))
                    
                    if Rele[id_rele] != Rele_Ant[id_rele]:
                        act_rele(id_rele,Rele[id_rele])
                        #Rele_Ant[id_rele] = Rele[id_rele]
                    
                    PWM_R -= Rele[id_rele]
                    PWM_R = max(0,PWM_R)
                    #print('Rele',id_rele,Rele[id_rele],int(PWM_R))
                #print('.....................')
                    
        else: #salida manual de reles de excedentes
            for P in range(Nreles_Diver):
                id_rele = Reles_D_Ord[P][0]
                
                if Rele[id_rele] != Rele_Ant[id_rele]:
                    act_rele(id_rele,Rele[id_rele])
                    Rele_Ant[id_rele]=Rele[id_rele]
            

      ## --------- Escribir en la BD Tabla Reles el Estado RELES -------------------------
        t_muestra_4=(time.time()-hora_m) * 1000
        ee=200

        if Grabar == 1: # actualizo BD cada N bucles
            
            for I in range(nreles):
                id_rele = TR[I][0]
                if Rele[id_rele] != TR[I][3]:
                    sql = "UPDATE reles SET estado =" +str(Rele[id_rele])+ " WHERE id_rele = " + str(id_rele)
                    cursor.execute(sql)
        
                ### refrescar estado rele (uno por ciclo)
                if I == n_refresco_rele:
                    #print (tiempo,I,'Refrescando valor Rele(', id_rele, ')=' ,Rele[id_rele])
                    act_rele(id_rele, Rele[id_rele])
            
            n_refresco_rele += 1
            if n_refresco_rele >= nreles: n_refresco_rele = 0
            
                 
                    
        if TP[1] == "S" and Grabar == 1 and nreles > 0:
            for I in range(nreles):
                id_rele = TR[I][0]
                estado = Rele[id_rele]
                sql = ('SELECT id_rele,segundos_on,nconmutaciones FROM reles_segundos_on WHERE fecha='+
                      '"'+time.strftime("%Y-%m-%d")+'" and id_rele =' + str(id_rele))
                
                segundos_on = 0
                try:
                    nreles_on = cursor.execute(sql)
                    nreles_on = int(nreles_on)
                    if estado > 0 :
                        segundos_on = float(TP[2] * TP[3])
                        nconmutaciones = 1

                        if nreles_on >= 1:
                            TS = cursor.fetchall()
                            
                            segundos_on = TS[0][1] + round((t_muestra*TP[3]*estado/100),2)  # calculo funcionamiento real reles PWM
                            if TR[I][3] == 0:
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
                    
                if TP[1] == "S" and Grabar == 1 and TR[I][4] == "S" and Rele[id_rele] != TR[I][3]:
                    try:
                        cursor.execute("""INSERT INTO reles_grab (Tiempo,id_rele,valor_rele)
                                       VALUES(%s,%s,%s)""",(tiempo,id_rele,estado))
                        #db.commit()
                    except:
                        db.rollback()
                        logBD('tabla reles_grab NO grabados por fallo')


        #------------------------Escribir en la tabla valores FV  ---------------------------
        
        if TP[0] == "S" and Grabar == 1:
            if DEBUG >=2: print (Fore.RED+'G'+Fore.RESET,end='')
            try:
                cursor.execute("""INSERT INTO datos (Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,Mod_bat) 
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,Mod_bat))
                #db.commit()
            except:
                db.rollback()
                logBD('Registro DATOS no grabado')
        
        if TP[0] == "S" and eval(grabar_datos_s): #grabar datos_s 
            if DEBUG >=2: print ('S',end='')
            try:
                cursor.execute("""INSERT INTO datos_s (Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,
                   Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,
                   IPWM_P,IPWM_I,IPWM_D,Kp, Ki,Kd) 
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (tiempo_us,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,
                   Wplaca,Wh_placa,Temp,PWM,IPWM_P,IPWM_I,IPWM_D,TP[7],TP[8],TP[9]))
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
        datos= [round(tiempo_sg,2), time.strftime("%d-%B-%Y -- %H:%M:%S"),
               Ibat,Vbat,SOC,round(DS,2),Aux1,Aux2,
               int(Whp_bat),int(Whn_bat),Iplaca,Vplaca,round(Wplaca),round(Wh_placa,1),
               Temp,int(PWM),round(Consumo,0),Mod_bat,int(Tabs),int(Tflot),
               int(Tflot_bulk),SOC_min,SOC_max,Vbat_min,Vbat_max]        
        
        with open('/run/shm/datos_fv.json', 'w') as f:
            json.dump(datos, f)
        
        ee=310
        with open('/run/shm/datos_reles.json', mode='w') as f:
            TRR=[]
            for I in range(nreles):
                TRR.append ([TR[I][1]+'('+TR[I][2]+'-P'+str(TR[I][6])+')',Rele[TR[I][0]]])
            json.dump(TRR,f)
        
        Grabar += 1
        if Grabar >= TP[3] + 1: Grabar = 1

        ###### ajuste fino tiempo bucle
        T_ejecucion = round(time.time() - hora1,2)

        if T_ejecucion_max < T_ejecucion: T_ejecucion_max = T_ejecucion
        
        ee=320
        if DEBUG >= 1:
            #print (tiempo,'-',end='')
            print(' {0:4}ms - Sensor={1}={2:.2f}'.format(int(T_ejecucion*1000),TP[6],TP[5]),end='')
            print (Fore.CYAN+'/{0:.2f}'.format(eval(TP[6])),end='')
            print (Fore.MAGENTA+' / Vbat={0:.2f}- Iplaca={1:.2f}- Ibat={2:.2f}- Wcon={3:.2f}- PWM={4:.0f}'.format(Vbat,Iplaca,Ibat,Consumo,PWM),Fore.RESET)

        # Repetir bucle cada X segundos
        espera = TP[2] - T_ejecucion #-0.1
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
