#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2022-08-22

parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"

# #################### Control Ejecucion Servicio ########################################
servicio = 'fv_mqtt'
control = 'usar_mqtt_suscripciones'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


import MySQLdb,json,time
import paho.mqtt.client as mqtt
import json

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_mqtt') #+Style.RESET_ALL)


#Comprobacion argumentos en comando 
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 100
else:
    DEBUG = 0
print (Fore.RED + 'DEBUG=',DEBUG)

# Comprobacion que la tabla en BD tiene los campos necesarios
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    try: #inicializamos registro en BD RAM
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('MQTT','{}'))
        db.commit()
    except:
        pass
except:
    print (Fore.RED,'ERROR inicializando BD')
    sys.exit()

# -----------------------MQTT MOSQUITTO ------------------------
Nmensajes= 0
DATOS_MQTT = {} # Diccionario de los datos recibidos por MQTT

def on_connect(client, userdata, flags, rc):
    for i in mqtt_suscripciones:
        print ('Topic =',i)
        client.subscribe(i)
    
     
def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Desconexion MQTT - Intentando reconexion")
        else:
            client.loop_stop()
            client.disconnect()

def on_message(client, userdata, msg):
    global DATOS_MQTT, Nmensajes
    
    #print(msg.topic+" "+str(msg.payload))
    Nmensajes += 1
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    #print (Fore.BLUE,tiempo, ' - Mensajes=',Nmensajes)
    
    try:
        DATOS_MQTT[msg.topic] = json.loads(msg.payload)
    except:
        pass
    
    if DEBUG == 100:
        print (Fore.RESET + '=' * 80 )
        print (time.strftime("%Y-%m-%d %H:%M:%S")+ Fore.YELLOW +' - Nuevo Mensaje en Topic'+Fore.RED+f' {msg.topic} ' + Fore.YELLOW + '..... DATOS_MQTT=')
        for mq in DATOS_MQTT:
            if msg.topic == mq:
                print (Fore.CYAN+mq+':',Fore.RESET,DATOS_MQTT[mq])
            else:
                print (Fore.BLUE+mq+':',Fore.RESET,DATOS_MQTT[mq])
                
    ####  ARCHIVOS RAM en BD ############ 
    try:            
        salida = json.dumps(DATOS_MQTT)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'MQTT'") # grabacion en BD RAM
        cursor.execute(sql)
        
                  
    except:
        print(Fore.RED+'error, Grabacion tabla RAM equipos')
 
    try:
    
      if 'POWER' in DATOS_MQTT[msg.topic] and msg.topic[-5:] =='STATE':
          id_rele = int(msg.topic[-8:-6]) # Falta para varios reles ON/OFF en el mismo topic
          
          if DATOS_MQTT[msg.topic]['POWER'] == 'ON': estado = 100
          else: estado = 0
        
          cursor.execute(f"UPDATE reles SET estado={estado} WHERE id_rele LIKE {id_rele}")


      if 'PWM' in DATOS_MQTT[msg.topic] and msg.topic[-5:] =='STATE':
          #print (f'Hay PWM en {msg.topic}')
          
          if 'PWM1' in DATOS_MQTT[msg.topic]['PWM']:
              id_rele = int(msg.topic[-8:-6]+'1')
              PWM = DATOS_MQTT[msg.topic]['PWM']['PWM1']
              estado_ori = PWM/10.23
              
              # Adaptacion calibracion inversa
              try: 
                  ssr = json.loads(Rele_Dict[id_rele]['calibracion'])
                  if len(ssr) > 0: # solo si existe calibracion
                      for i in range(len(ssr)):
                          if ssr[i][1] > estado_ori : break
                      x1, y1 =  ssr[i-1][0], ssr[i-1][1] # puntos de la recta
                      x2, y2 =  ssr[i][0], ssr[i][1]

                      estado = (x1 + (x2-x1)/(y2-y1)*(estado_ori-y1)) # ecuacion recta
              except:
                  print ('Error des-calibracion')
                  pass
                  
              if DEBUG == 100: print (f"Hay PWM1 con valor {PWM} ({estado_ori}/{estado}) en {msg.topic}['PWM']")
              
              cursor.execute(f"UPDATE reles SET estado={estado} WHERE id_rele = {id_rele}")
   
   
    except:
        pass 
        
    db.commit()
        
client = mqtt.Client("fv_mqtt") #crear nueva instancia
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


dia = time.strftime("%Y-%m-%d")

# ==========================================================
#----------------- BUCLE -----------------------------------
# ==========================================================



while True:
    print (Fore.GREEN,time.strftime("%Y-%m-%d %H:%M:%S"), ' - Mensajes=',Nmensajes)

    exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios
    for i in mqtt_suscripciones:
        #print ('Topic =',i)
        client.subscribe(i)
    
    
    ####### LECTURA TABLA RELES ##############
    try:
        Rele_Dict={} 
        nreles=cursor.execute('SELECT * FROM reles')
        columns = [column[0] for column in cursor.description] # creacion diccionario Tabla Reles
        for row in cursor.fetchall(): Rele_Dict[row[0]] = dict(zip(columns, row))
    except:
        print (Fore.RED + 'Error lectura tabla reles')
    
    time.sleep(60)  
