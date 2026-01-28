#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2025-04-10

parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"

#####################################

mqtt_broker_venus  = "192.168.X.XX"
mqtt_puerto_venus  = 1883
mqtt_usuario_venus = "XXXX"
mqtt_clave_venus   = "YYY"

usar_mqtt_suscripciones_venus = 1
mqtt_suscripciones_venus = [] #  lista de topics a los que se suscribe fv_mqtt_venus.py para guardar en tabla equipos.. diccionario=d_['MQTT_EXT']

usar_mqtt_publicaciones_venus = 0
mqtt_publicaciones_venus = [
                             ["R/XXXX/keepalive", "", 60], #topic, payload, frecuencia
                             ["R/YYYY/keepalive", "", 60]
                           ] 



#####################################

# #################### Control Ejecucion Servicio ########################################
servicio = 'fv_mqtt_venus'
control = 'usar_mqtt_suscripciones_venus'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


import MySQLdb,json,time
import paho.mqtt.client as mqtt
import json
import telebot # Librería de la API del bot.

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_mqtt_venus') #+Style.RESET_ALL)


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
                      ('MQTT_VENUS','{}'))
        db.commit()
    except:
        pass
    cursor.close()
    db.close()    

except:
    print (Fore.RED,'ERROR inicializando BD')
    sys.exit()

# -----------------------MQTT MOSQUITTO ------------------------
Nmensajes= 0
DATOS_MQTT = {} # Diccionario de los datos recibidos por MQTT

def on_connect(client, userdata, flags, rc):
    for i in mqtt_suscripciones_venus:
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
    
   
    topic = msg.topic
    mensaje = msg.payload.decode()
    
    #print(topic+" --"+ mensaje)
    
    Nmensajes += 1
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    #print (Fore.BLUE,tiempo, ' - Mensajes=',Nmensajes)
    
    try:
        DATOS_MQTT[msg.topic] = json.loads(msg.payload)

        if isinstance(DATOS_MQTT[msg.topic], dict):
            if "value" in DATOS_MQTT[msg.topic]:
                DATOS_MQTT[msg.topic]["value"] = round(DATOS_MQTT[msg.topic]["value"], 2)
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
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'MQTT_VENUS'") # grabacion en BD RAM
        cursor.execute(sql)
        
                  
    except:
        print(Fore.RED+f'error, Grabacion tabla RAM equipos -- {DATOS_MQTT}')
        sys.exit()
    
    db.commit()
    cursor.close()
    db.close()
    
    time.sleep(0.25)

## MOSQUITTO
client = mqtt.Client("fv_mqtt_venus") #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario_venus, password=mqtt_clave_venus)
try:
    client.connect(mqtt_broker_venus, mqtt_puerto_venus) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.2)
client.loop_start()



dia = time.strftime("%Y-%m-%d")

# ==========================================================
#----------------- BUCLE -----------------------------------
# ==========================================================
cd_debug = 0

# Diccionario para almacenar el último tiempo de publicación de cada topic
ultima_publicacion = {i: 0 for i in range(len(mqtt_publicaciones_venus))}

while True:
    
    if usar_mqtt_publicaciones_venus == 1:
        tiempo_actual = time.time()  # Timestamp actual
        
        # Iterar sobre cada publicación configurada
        for i, (topic, payload, frecuencia) in enumerate(mqtt_publicaciones_venus):
            # Verificar si es momento de publicar (frecuencia en segundos)
            
            if tiempo_actual - ultima_publicacion[i] >= frecuencia:
                client.publish(topic, payload)
                ultima_publicacion[i] = tiempo_actual  # Actualizar el timestamp
                
                if DEBUG > 0:
                    print(f"{Fore.YELLOW}[PUB] {time.strftime('%Y-%m-%d %H:%M:%S')} Topic: {topic} | Payload: {payload}")
        
    if DEBUG > 0 and cd_debug >= 60:
        print (Fore.GREEN,time.strftime("%Y-%m-%d %H:%M:%S"), ' - Mensajes=',Nmensajes)
        cd_debug = 0
    
    
    time.sleep(1)  
