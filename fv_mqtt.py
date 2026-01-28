# -*- coding: utf-8 -*-

# Versión 2025-11-19 - Con sistema de WATCHDOG_THREAD

import time
import sys
import signal
import threading
from datetime import datetime

parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"

# #################### Control Ejecucion Servicio ########################################
servicio = 'fv_mqtt'
control = 'usar_mqtt_suscripciones'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

# Variables globales para control de salud
HORA_ULTIMO_MENSAJE = time.time()
INTERVALO_SIN_MENSAJES = mqtt_suscripciones_watchdog  # Definido por usuario en Parametros_FV.py o por defecto en Parametros_FV_DIST.py(1800sg)
WATCHDOG_THREAD = None
SHUTDOWN_EVENT = threading.Event()
MQTT_RECONECTAR = False

import MySQLdb
import json
import paho.mqtt.client as mqtt
import telebot
import colorama
from colorama import Fore, Back, Style
colorama.init()

def signal_handler(signum, frame):
    """Manejar señales de terminación"""
    print(f"{Fore.YELLOW}Recibida señal {signum}. Cerrando limpiamente...{Style.RESET_ALL}")
    SHUTDOWN_EVENT.set()
    sys.exit(0)

# Registrar manejadores de señales
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def watchdog_monitor():
    """Monitor que verifica la salud del servicio"""
    global HORA_ULTIMO_MENSAJE, MQTT_RECONECTAR
    
    while not SHUTDOWN_EVENT.is_set():
        current_time = time.time()
        time_since_last_message = current_time - HORA_ULTIMO_MENSAJE
        
        if time_since_last_message > INTERVALO_SIN_MENSAJES and not MQTT_RECONECTAR:
            print(f"{Fore.RED}ALERTA: No hay mensajes desde hace {time_since_last_message:.0f} segundos")
            print(f"{Fore.YELLOW}Reiniciando conexión MQTT...{Style.RESET_ALL}")
            
            MQTT_RECONECTAR = True
            try:
                # Detener y reiniciar completamente el cliente MQTT
                client.loop_stop()
                time.sleep(2)
                client.disconnect()
                time.sleep(2)
                
                # Reconectar
                client.connect(mqtt_broker, mqtt_puerto)
                client.loop_start()
                
                # Esperar a que se establezca la conexión
                time.sleep(5)
                
                # Resuscribir a todos los topics
                suscribir_topics()
                
                HORA_ULTIMO_MENSAJE = time.time()  # Reset timer
                MQTT_RECONECTAR = False
                print(f"{Fore.GREEN}Conexión MQTT reiniciada exitosamente{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}Error en reconexión: {e}{Style.RESET_ALL}")
                MQTT_RECONECTAR = False
                # Intentar reconectar en el próximo ciclo
                try:
                    client.loop_start()
                except:
                    pass
        
        SHUTDOWN_EVENT.wait(30)  # Verificar cada 30 segundos

def suscribir_topics():
    """Resuscribir a todos los topics definidos en mqtt_suscripciones"""
    try:
        # Recargar parámetros por si han cambiado
        exec(open(parametros_FV).read(), globals())
        
        print(f"{Fore.CYAN}Resuscribiendo a {len(mqtt_suscripciones)} topics...{Style.RESET_ALL}")
        for topic in mqtt_suscripciones:
            try:
                result, mid = client.subscribe(topic)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    print(f"{Fore.GREEN}  ✓ Suscrito a: {topic}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}  ✗ Error suscribiendo a: {topic} (código: {result}){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Excepción suscribiendo a {topic}: {e}{Style.RESET_ALL}")
                
    except Exception as e:
        print(f"{Fore.RED}Error al resuscribir topics: {e}{Style.RESET_ALL}")

def safe_db_operation(operation, *args, max_retries=3):
    """Ejecutar operaciones de BD con reintentos"""
    for intento in range(max_retries):
        try:
            return operation(*args)
        except MySQLdb.OperationalError as e:
            if intento < max_retries - 1:
                print(f"{Fore.YELLOW}Error BD (intento {intento + 1}): {e}. Reintentando...{Style.RESET_ALL}")
                time.sleep(2)
                continue
            else:
                print(f"{Fore.RED}Error BD después de {max_retries} intentos: {e}{Style.RESET_ALL}")
                raise
        except Exception as e:
            print(f"{Fore.RED}Error inesperado en BD: {e}{Style.RESET_ALL}")
            raise

print(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' fv_mqtt')

# Comprobacion argumentos en comando 
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 100
else:
    DEBUG = 0
print(Fore.RED + 'DEBUG=', DEBUG)

# Inicialización con reintentos
def inicializar_bd():
    """Inicializar base de datos con reintentos"""
    for intento in range(3):
        try:
            db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
            cursor = db.cursor()
            
            try:
                cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                              ('MQTT','{}'))
                db.commit()
                print(f"{Fore.GREEN}Registro MQTT inicializado en BD{Style.RESET_ALL}")
            except Exception as e:
                if DEBUG:
                    print(f"{Fore.YELLOW}Registro MQTT ya existe o error: {e}{Style.RESET_ALL}")
                pass
            
            cursor.close()
            db.close()
            return True
        except Exception as e:
            print(f"{Fore.RED}Error inicializando BD (intento {intento + 1}): {e}{Style.RESET_ALL}")
            if intento < 2:
                time.sleep(5)
            else:
                return False
    
    return False

if not inicializar_bd():
    print(f"{Fore.RED}ERROR: No se pudo inicializar BD. Saliendo...{Style.RESET_ALL}")
    sys.exit(1)

# -----------------------MQTT MOSQUITTO ------------------------
Nmensajes = 0
DATOS_MQTT = {} # Diccionario de los datos recibidos por MQTT
Rele_Dict = {}  # Diccionario para tabla reles

def on_connect(client, userdata, flags, rc):
    global HORA_ULTIMO_MENSAJE, MQTT_RECONECTAR
    if rc == 0:
        print(f"{Fore.GREEN}Conexión MQTT establecida correctamente{Style.RESET_ALL}")
        # Suscribir a todos los topics al conectar
        suscribir_topics()
        HORA_ULTIMO_MENSAJE = time.time()
        MQTT_RECONECTAR = False
    else:
        print(f"{Fore.RED}Error de conexión MQTT. Código: {rc}{Style.RESET_ALL}")
        MQTT_RECONECTAR = False

def on_disconnect(client, userdata, rc):
    global HORA_ULTIMO_MENSAJE
    print(f"{Fore.YELLOW}Desconexión MQTT. Código: {rc}{Style.RESET_ALL}")
    if rc != 0:
        print(f"{Fore.YELLOW}Conexión perdida, intentando reconexión automática...{Style.RESET_ALL}")
        HORA_ULTIMO_MENSAJE = time.time()

def on_subscribe(client, userdata, mid, granted_qos):
    """Callback cuando se realiza una suscripción"""
    if DEBUG == 100:
        print(f"{Fore.CYAN}Suscripción confirmada - MID: {mid}, QOS: {granted_qos}{Style.RESET_ALL}")

def on_message(client, userdata, msg):
    global DATOS_MQTT, Nmensajes, HORA_ULTIMO_MENSAJE
    
    HORA_ULTIMO_MENSAJE = time.time()  # Actualizar tiempo del último mensaje
    Nmensajes += 1
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    
    topic = msg.topic
    mensaje = msg.payload.decode()
    
    if DEBUG == 100:
        print(Fore.RESET + '=' * 80)
        print(time.strftime("%Y-%m-%d %H:%M:%S") + Fore.YELLOW + ' - Nuevo Mensaje en Topic' + 
              Fore.RED + f' {msg.topic} ' + Fore.YELLOW + '..... DATOS_MQTT=')
    
    try:
        DATOS_MQTT[msg.topic] = json.loads(msg.payload)
    except:
        DATOS_MQTT[msg.topic] = mensaje
        if DEBUG == 100:
            print(f"{Fore.YELLOW}Mensaje no JSON: {mensaje}{Style.RESET_ALL}")
    
    if DEBUG == 100:
        for mq in DATOS_MQTT:
            color = Fore.CYAN if msg.topic == mq else Fore.BLUE
            print(color + mq + ':', Fore.RESET, DATOS_MQTT[mq])
    
    # Procesamiento en hilo separado para no bloquear la recepción MQTT
    threading.Thread(target=process_message, args=(msg, tiempo), daemon=True).start()

def process_message(msg, tiempo):
    """Procesar mensaje en hilo separado"""
    try:
        # Actualizar BD
        def update_db():
            salida = json.dumps(DATOS_MQTT)
            db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
            cursor = db.cursor()
            
            sql = f"UPDATE equipos SET `tiempo` = '{tiempo}', sensores = '{salida}' WHERE id_equipo = 'MQTT'"
            cursor.execute(sql)
            
            # Procesamiento específico del mensaje
            process_specific_message(msg, cursor)
            
            db.commit()
            cursor.close()
            db.close()
        
        safe_db_operation(update_db)
        
    except Exception as e:
        print(f"{Fore.RED}Error procesando mensaje: {e}{Style.RESET_ALL}")

def process_specific_message(msg, cursor):
    """Procesar tipos específicos de mensajes """
    global Rele_Dict
    
    try:
        # Lógica para POWER
        if 'POWER' in DATOS_MQTT[msg.topic] and msg.topic[-5:] =='STATE':
            id_rele = int(msg.topic[-8:-6]) # Falta para varios reles ON/OFF en el mismo topic

            if DATOS_MQTT[msg.topic]['POWER'] == 'ON': 
                estado = 100
            else: 
                estado = 0

            cursor.execute(f"UPDATE reles SET estado={estado} WHERE id_rele LIKE {id_rele}")
            if DEBUG == 100:
                print(f"{Fore.GREEN}Actualizado rele {id_rele} a estado {estado}{Style.RESET_ALL}")
                
    except Exception as e:
        if DEBUG:
            print(f"{Fore.YELLOW}Error procesando POWER: {e}{Style.RESET_ALL}")

    try:
        # Lógica para PWM
        if 'PWM' in DATOS_MQTT[msg.topic] and msg.topic[-5:] =='STATE':
            if DEBUG == 100:
                print(f'{Fore.CYAN}Hay PWM en {msg.topic}{Style.RESET_ALL}')

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
                        x1, y1 = ssr[i-1][0], ssr[i-1][1] # puntos de la recta
                        x2, y2 = ssr[i][0], ssr[i][1]

                        estado = (x1 + (x2-x1)/(y2-y1)*(estado_ori-y1)) # ecuacion recta
                except Exception as e:
                    if DEBUG:
                        print(f'{Fore.YELLOW}Error des-calibracion: {e}{Style.RESET_ALL}')
                    estado = estado_ori
                  
                if DEBUG == 100: 
                    print(f"{Fore.CYAN}Hay PWM1 con valor {PWM} ({estado_ori:.1f}/{estado:.1f}) en {msg.topic}['PWM']{Style.RESET_ALL}")

                cursor.execute(f"UPDATE reles SET estado={estado} WHERE id_rele = {id_rele}")
        
    except Exception as e:
        if DEBUG:
            print(f"{Fore.YELLOW}Error procesando PWM: {e}{Style.RESET_ALL}")
        
    try:
        # Lógica original para HOMEASSISTANT
        if 'HOMEASSISTANT' in msg.topic.upper(): # si se recibe un topic con HOMEASSISTANT
            if DEBUG == 100: 
                print(f'{Fore.CYAN}Mensaje de HA ....topic:{msg.topic}  payload:{msg.payload.decode()}{Style.RESET_ALL}')
            
            if 'RELE' in msg.topic.upper(): # comprobamos que el topic incluye "rele"
                id_rele = msg.payload.decode()[0:3] # se asigna los 3 primers caracteres del mensaje tipo 611PRG.... 611 
                modo = msg.payload.decode()[3:] # se asigna los caracteres del mensaje a partir del 4   ..... PRG
                print(f'{Fore.GREEN}rele {id_rele} --- modo {modo}{Style.RESET_ALL}')
                cursor.execute(f"UPDATE reles SET modo= '{modo}' WHERE id_rele = {id_rele}")  # se ejecuta la SQL
             
            elif 'TELEGRAM' in msg.topic.upper(): # comprobamos que el topic incluye "telegram"
                if bot is not None:
                    bot.send_message(Aut[0], msg.payload.decode())# mensaje al ID de telegram definido en Parametros_FV.py
                    if DEBUG:
                        print(f"{Fore.GREEN}Mensaje enviado a Telegram{Style.RESET_ALL}")
                
            # dejamos preparado para otros temas de HA 
            
    except Exception as e:
        if DEBUG:
            print(f'{Fore.YELLOW}Error procesando HOMEASSISTANT: {e}{Style.RESET_ALL}')

# Configuración MQTT con manejo robusto de conexión
def setup_mqtt_client():
    client = mqtt.Client("fv_mqtt")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.reconnect_delay_set(3, 15)
    client.username_pw_set(mqtt_usuario, password=mqtt_clave)
    
    # Configuración adicional para robustez
    client.max_queued_messages_set(100)  # Limitar cola de mensajes
    client.max_inflight_messages_set(20)  # Limitar mensajes en vuelo
    
    return client

def connect_mqtt_with_retry(client, max_retries=5):
    """Conectar MQTT con reintentos"""
    for intento in range(max_retries):
        try:
            client.connect(mqtt_broker, mqtt_puerto)
            print(f"{Fore.GREEN}Conexión MQTT establecida (intento {intento + 1}){Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}Error conexión MQTT (intento {intento + 1}): {e}{Style.RESET_ALL}")
            if intento < max_retries - 1:
                wait_time = 10 * (intento + 1)  # Backoff exponencial
                print(f"{Fore.YELLOW}Reintentando en {wait_time} segundos...{Style.RESET_ALL}")
                time.sleep(wait_time)
            else:
                return False
    return False

# Inicializar cliente MQTT
client = setup_mqtt_client()

if not connect_mqtt_with_retry(client):
    print(f"{Fore.RED}ERROR: No se pudo conectar al broker MQTT. Saliendo...{Style.RESET_ALL}")
    sys.exit(1)

client.loop_start()

# TELEGRAM
try:
    bot = telebot.TeleBot(TOKEN)
    bot.skip_pending = True
    print(f"{Fore.GREEN}Bot Telegram inicializado correctamente{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.YELLOW}Advertencia: No se pudo inicializar Telegram: {e}{Style.RESET_ALL}")
    bot = None

# Iniciar watchdog
WATCHDOG_THREAD = threading.Thread(target=watchdog_monitor, daemon=True)
WATCHDOG_THREAD.start()

print(f"{Fore.GREEN}Servicio MQTT iniciado correctamente. Monitor de salud activo.{Style.RESET_ALL}")

# ==========================================================
#----------------- BUCLE PRINCIPAL MEJORADO ---------------
# ==========================================================

dia = time.strftime("%Y-%m-%d")
main_loop_failures = 0
MAX_LOOP_FAILURES = 5

while not SHUTDOWN_EVENT.is_set():
    try:
        if DEBUG > 0:
            time_since_last = time.time() - HORA_ULTIMO_MENSAJE
            status_color = Fore.GREEN if time_since_last < 60 else Fore.YELLOW if time_since_last < 120 else Fore.RED
            print(Fore.GREEN + time.strftime("%Y-%m-%d %H:%M:%S") + 
                  f' - Mensajes={Nmensajes} - Último hace: {status_color}{time_since_last:.0f}s{Fore.GREEN} - MQTT_RECONECTAR: {MQTT_RECONECTAR}{Style.RESET_ALL}')
        
        # Recargar parámetros
        exec(open(parametros_FV).read(), globals())
        
        # Actualizar tabla reles
        def update_reles_table():
            db1 = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
            cursor1 = db1.cursor()
            cursor1.execute('SELECT * FROM reles')
            
            columns = [column[0] for column in cursor1.description]
            rele_dict = {}
            for row in cursor1.fetchall():
                if DEBUG == 100:
                    print(f"Rele {row}")
                rele_dict[row[0]] = dict(zip(columns, row))
            
            cursor1.close()
            db1.close()
            return rele_dict
        
        Rele_Dict = safe_db_operation(update_reles_table)
        
        # Renovar suscripciones periódicamente (solo si no estamos en proceso de reconexión)
        if not MQTT_RECONECTAR:
            for i in mqtt_suscripciones:
                try:
                    client.subscribe(i)
                    if DEBUG == 100:
                        print(f'{Fore.CYAN}Renovada suscripción a: {i}{Style.RESET_ALL}')
                except Exception as e:
                    if DEBUG:
                        print(f'{Fore.YELLOW}Error renovando suscripción a {i}: {e}{Style.RESET_ALL}')
        
        main_loop_failures = 0  # Reset counter on successful iteration
        
        # Espera con posibilidad de interrupción
        for _ in range(60):  # Dividir en segmentos de 1 segundo para mejor respuesta
            if SHUTDOWN_EVENT.is_set():
                break
            time.sleep(1)
        
    except Exception as e:
        main_loop_failures += 1
        print(f"{Fore.RED}Error en bucle principal (fallo {main_loop_failures}): {e}{Style.RESET_ALL}")
        
        if main_loop_failures >= MAX_LOOP_FAILURES:
            print(f"{Fore.RED}Demasiados errores consecutivos. Reiniciando servicio...{Style.RESET_ALL}")
            break
        
        # Espera antes de reintentar
        for _ in range(10):
            if SHUTDOWN_EVENT.is_set():
                break
            time.sleep(1)

# Limpieza final
print(f"{Fore.YELLOW}Cerrando servicio MQTT...{Style.RESET_ALL}")
SHUTDOWN_EVENT.set()

try:
    client.loop_stop()
    client.disconnect()
    print(f"{Fore.GREEN}Conexión MQTT cerrada correctamente.{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.YELLOW}Error cerrando conexión MQTT: {e}{Style.RESET_ALL}")

print(f"{Fore.GREEN}Servicio MQTT cerrado correctamente.{Style.RESET_ALL}")