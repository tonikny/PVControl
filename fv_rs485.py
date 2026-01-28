# -*- coding: utf-8 -*-

# Versión 2024-05-26
#############################################
##  Libreria generica de captura RS485 RTU ##
#############################################

# Se llama desde el programa principal en donde se define el equipo, puerto etc junto con los registros a capturar

##################################################################

EQUIPO = eval(NEQUIPO)

try: 
    if orden_bytes == 1: orden_bytes = 1 #en hibrido Powmr inverten el ordes de los bytes 
except:
    orden_bytes = 0 
    
try:
    comandos = EQUIPO['COMANDOS']
    del EQUIPO['COMANDOS']
except:
    pass
    
import sys, time, datetime
import MySQLdb,json
import subprocess

import paho.mqtt.client as mqtt # MQTT
import telebot # Librería de la API del bot.
import timeout_decorator

import minimalmodbus

# Import new helper modules
from modbus_utils import convert_u16, convert_s16, convert_u32, apply_byte_order
from db_manager import DatabaseManager
from mqtt_handler import MQTTHandler
from telegram_notifier import TelegramNotifier
    
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0])

#Comprobacion argumentos en comando
simular_datos = DEBUG = 0
narg = len(sys.argv)
if '-p' in sys.argv: DEBUG = 1 # para desarrollo permite print en distintos sitios
if '-s' in sys.argv: simular_datos = 1 # para desarrollo permite print en distintos sitios

comando_mqtt = {} # 'equipo', 'comando'   para uso de comandos Telegram o MQTT (legacy, replaced by mqtt_handler)
if DEBUG > 0:
    print()
    print (Fore.CYAN+ '------- Parametros -------')
    print(EQUIPO)
    print('-' * 40)

# Initialize Telegram notifier (auto-imports from Parametros_FV.py globals)
telegram_notifier = None
cid = None  # Initialize cid for backward compatibility
if usar_telegram == 1:
    try:
        cid = Aut[0]  # Set cid from Aut list
        # Parameters auto-imported from globals (TOKEN, Aut, usar_telegram)
        telegram_notifier = TelegramNotifier()
        telegram_notifier.send_startup_message(NEQUIPO)
    except Exception as e:
        print(f'Error inicializando Telegram notifier: {e}')
        telegram_notifier = None
        cid = None

# Legacy bot_enviar_mensaje function for backward compatibility
@timeout_decorator.timeout(20, use_signals=False)
def bot_enviar_mensaje(cid, msg):
    if telegram_notifier and telegram_notifier.is_enabled():
        telegram_notifier.send_message(msg, chat_id=cid)
    else:
        print(f'[Telegram disabled] Would send: {msg}')


 ##### MQTT ###########################################
# MQTT message callback for legacy compatibility
def on_message_received(equipo, comando):
    global comando_mqtt
    if DEBUG == 1:
        print(Fore.CYAN + f'MQTT .... Comando {comando} en equipo {equipo} recibido')
    comando_mqtt = {'equipo': equipo, 'comando': comando}

# Initialize MQTT handler (auto-imports from Parametros_FV.py globals)
mqtt_handler = None
try:
    # Parameters auto-imported from globals (mqtt_broker, mqtt_puerto, mqtt_usuario, mqtt_clave)
    mqtt_handler = MQTTHandler(
        on_message_callback=on_message_received,
        debug=(DEBUG > 0)
    )
    
    # Subscribe to equipment topics
    equipos_list = [e for e in EQUIPO if e != 'COMANDOS']
    mqtt_handler.subscribe_equipment(equipos_list)
    
    # Connect to broker
    mqtt_handler.connect()
    
except Exception as e:
    print(f'Error inicializando MQTT handler: {e}')
    mqtt_handler = None

# Legacy MQTT client callbacks (kept for reference, but not used with mqtt_handler)
def on_connect(client, userdata, flags, rc):
    for e in EQUIPO:
        client.subscribe(f"PVControl/{e}")
        if DEBUG > 0: print(f'{e}....MQTT Conectado.... Topic =  PVControl/{e}')
    
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print (f"Desconexion MQTT de {NEQUIPO}... intentando reconexion")
    else:
        client.loop_stop()
        client.disconnect()

def on_message(client, userdata, msg):
    global comando_mqtt
    topic = msg.topic.upper()[10:]
    mensaje = msg.payload.decode().strip()
    if DEBUG == 1:
        print (Fore.CYAN + f'MQTT .... Comando {mensaje} en equipo {topic} recibido')
    comando_mqtt = {'equipo': topic, 'comando': mensaje}
    return

def listar_parametros(equipo):
    
    #if MENSAJE in comandos['ayuda']: # Comando AYUDA
    if True:
        #print(f'Lista Parametros de {topic}...')
        msg = f'\U0001F4DF   <b>LISTA PARAMETROS {equipo}</b>\n'
        msg += ' =============================\n'
        nlineas = 0
        for c in comandos:
            nlineas += 1
            comandos1 = comandos[c].copy()
            if 'adaptar' in comandos1: del comandos1['adaptar']
            #if 'lectura_multiple' in comandos1: del comandos1['lectura_multiple']
                                
            msg += f'\U0001F6A6<b>{c}</b> : {comandos1}\n'
            if c in ['ayuda','lectura_multiple'] : 
                msg += f"\n"
                continue
            try:
                #print(f'lectura registro {equipo} {c}....', end='')
                d = leer_registro(equipo, c)
                
                tipo = comandos[c]['tipo'] if 'tipo' in comandos[c] else 'u16'    
                
                if tipo == 'adaptar':  
                    datos = {}                    
                    ejecutar = '\n'.join(comandos[c]['adaptar'])
                    exec(ejecutar)
                    d = datos[c]
                    
                msg += f"    ..... Valor Actual de <b>{c}={d}</b>\n\n"
                #print (d)
                time.sleep(0.05)
            except:
                print(f'Error en leer_registro({equipo},{c}) ')
                time.sleep(1)
                msg += f'<b>...error lectura de {c}</b>\n'
            
            if usar_telegram == 1 and nlineas % 20 == 0:
                #print('-' * 80)
                #print(msg)
                #print('-' * 80)
                bot_enviar_mensaje(cid, msg)
                msg = ''
                
        
        
        if usar_telegram == 1:
            msg += ' =============================\n'
            #print('*' * 80)
            #print(msg)
            #print('*' * 80)
            bot_enviar_mensaje(cid, msg)
    
        #flag_lectura[topic] = 0
        
    return
        
    
def escribir_registro(equipo, mensaje):

    MENSAJE = mensaje.upper()
    for c in comandos: 
        ee = 30
        f = MENSAJE.find(c.upper())
        
        if f != -1: # se encuentra la cadena
            ee = 40
            variable = mensaje[f:len(c)]
            
            try:
                d = leer_registro(equipo, c)
                
                valor = mensaje[len(c):].strip()
                ee = 50
                if len(valor) > 0:
                    if valor[0] == '=': valor = valor[1:]
                    valor_n = float(valor)
                    escritura = True
                else:
                    escritura = False
                    
                ee = 60
                registro = comandos[c]['reg']
                msg = f'Valor registro {registro}...{variable}= {d} '
                if DEBUG == 1: print(msg)
                ee = 70
                
                if not comandos[c]['escritura']:
                    escritura = False
                    msg += f'\n Error {variable} no admite escritura'
                elif escritura:
                    if 'rango' not in comandos[c]: comandos[c]['rango'] = [0,65535]
                    if valor_n < comandos[c]['rango'][0] or  valor_n > comandos[c]['rango'][1]:
                        escritura = False
                        msg += f'\n Error en valor {valor_n} fuera de rango admitido'
                        if DEBUG == 1: print(msg)
                        
                ee = 80
                if escritura:
                    decimales = comandos[c]['dec'] if 'dec' in comandos[c] else 0
                    modbus[equipo].write_register(registro, valor_n, decimales)  # Registro, nº decimales
                     
                    msg += f'\nNuevo Valor-->{registro}...{variable}= {valor_n} '
                    if DEBUG == 1: print(msg)
                
                ee = 90
                if usar_telegram == 1: bot_enviar_mensaje(cid, msg)
            except:
                print(f'Error {ee} en comando MQTT')
            #time.sleep(1)
            #flag_lectura[equipo] = 0
    
            return
        
    ee = 100
    
    try:
        msg = f'Comando {mensaje} no encontrado'
        ee = 110
        if usar_telegram == 1: bot_enviar_mensaje(cid, msg)
    except:
        print(f'Error {ee} en comando MQTT')
    
    #flag_lectura[topic] = 0

# Legacy MQTT client initialization (commented out, replaced by mqtt_handler)
# client = mqtt.Client(f"{NEQUIPO}")
# client.on_connect = on_connect
# client.on_disconnect = on_disconnect
# client.on_message = on_message
# client.reconnect_delay_set(3,15)
# client.username_pw_set(mqtt_usuario, password=mqtt_clave)
# try:
#     client.connect(mqtt_broker, mqtt_puerto)
# except:
#     print(f'Error de conexion al servidor MQTT en {NEQUIPO}')
# time.sleep(.2)
# client.loop_start()
#######################################################

def leer_registros(equipo):
    """
    Lee varios registros de un equipo usando la funcionalidad de lectura múltiple.
    Devuelve un diccionario comando: valor
    """
    global n_fallos_captura
    ee = 1000
    lectura = {}  # diccionario registro: valor..... ejemplo... {102: 5655, 103: 200}
    datos = {}    # diccionario comando: valor..... ejemplo... {'Vbat': 5655, 'Ibat': 200}
    
    try:
        for reg_ini, reg_fin in comandos['lectura_multiple']['rangos']:
            ee = 1010
            #print (f'rango = {reg_ini},{reg_fin}')
            ee = 1015
            nreg = reg_fin - reg_ini + 1
            registros = list(range(reg_ini, reg_fin + 1)) # lista de numeros de registros

            try:
                ee = 1020
                # Lectura de todos los registros del rango
                if simular_datos: d = [9999] * nreg
                else: d = modbus[equipo].read_registers(reg_ini, nreg, 3)
                
                # Construir diccionario raw lectura {registro: valor}
                lectura.update({registros[i]: d[i] for i in range(nreg)})

            except Exception as e:
                ee = 1030
                print(f'Error lectura múltiple {equipo} reg_ini:{reg_ini} reg_fin:{reg_fin} -> {e}')
                raise
            time.sleep(0.1)

        # Interpretar cada registro leído
        for reg, valor in lectura.items():
            if reg not in reg_to_comando:
                continue

            comando = reg_to_comando[reg]
            params = get_command_params(comando)
            if not params['grabar']:
                continue

            try:
                # Manejo de orden de bytes
                if orden_bytes == 1:
                    valor = apply_byte_order(valor, orden_bytes)

                tipo = params['tipo']
                dec = params['dec']
                offset = params['offset']

                if tipo == 'u16':
                    d = convert_u16(valor, dec, offset)
                elif tipo == 's16':
                    d = convert_s16(valor, dec, offset)
                elif tipo == 'u32':
                    valor_alto = lectura.get(reg + 1, 0)
                    d = convert_u32(valor, valor_alto, dec, offset)
                elif tipo == 'adaptar' and params['adaptar']:
                    ee = 1050
                    d = valor
                    ejecutar = '\n'.join(params['adaptar'])
                    ee = 1060
                    exec(ejecutar)
                    # 'adaptar' commands usually write directly to datos inside exec
                    continue
                else:
                    ee = 1070
                    d = -9999

                datos[comando] = d

            except Exception as e:
                print(f"Error {ee} en leer_registros({equipo}) comando={comando} -> {type(e).__name__}: {e}")
                datos[comando] = -9999
                raise

    except Exception as e:
        print(f"Error general en leer_registros({equipo}): {e}")
        raise

    return datos

def leer_registro(equipo, comando, datos=None):
    """
    Lee un registro de un equipo según la configuración de comandos.
    Retorna None si la lectura falla.
    """
    params = get_command_params(comando)
    reg = params['reg']
    dec = params['dec']
    tipo = params['tipo']
    offset = params['offset']
    fc = params['fc']

    if datos is None:
        datos = {}

    d = -9999

    try:
        # Lectura de Modbus
        if tipo in ('u16', 's16', 'u32', 'adaptar'):
            d = modbus[equipo].read_register(reg, dec if tipo != 'u16' else 0, fc,
                                            signed=(tipo == 's16'))

        # Interpretación según tipo
        if tipo == 'u16':
            if orden_bytes == 1:
                d = apply_byte_order(d, orden_bytes)
            d = convert_u16(d, dec, offset)

        elif tipo == 's16':
            d = convert_s16(d, dec, offset)

        elif tipo == 'u32':
            valor_alto = modbus[equipo].read_register(reg + 1, 0, fc)
            d = convert_u32(d, valor_alto, dec, offset)

        elif tipo == 'adaptar' and params.get('adaptar'):
            ee = 110
            for line in params['adaptar']:
                exec(line, {}, {"datos": datos, "d": d})
            return None

        return d

    except Exception as e:
        print(f"Error leyendo {comando} en {equipo}: {type(e).__name__} - {e}")
        return None  # Signal failure to caller


    
def leer_equipo(equipo):
    global n_fallos_captura
    t0 = time.time()
    nombre_equipo = equipo.upper()
    datos = {}
    read_failed = False  # Track any failed read

    try:
        ee = 100
        lectura_multiple = comandos.get('lectura_multiple', {}).get('usar', 0)

        if lectura_multiple:
            # lectura múltiple: if any read fails, mark read_failed
            datos = leer_registros(equipo)
            if any(v == -9999 for v in datos.values()):
                read_failed = True
        else:
            for c in comandos:
                if c == 'ayuda' : continue
                if c in ('ayuda', 'lectura_multiple'):
                    continue
                params = get_command_params(c)
                if not params['grabar']:
                    continue

                ee = 120
                valor = leer_registro(equipo, c, datos)
                if params['tipo'] != 'adaptar':
                    if valor is None:  # read failed
                        read_failed = True
                        datos[c] = -9999
                    else:
                        datos[c] = valor

        datos['tcaptura'] = round(time.time() - t0, 2)

    except Exception as e:
        n_fallos_captura[equipo] += 1
        print(f"Error general leyendo equipo {equipo} Fallos: {n_fallos_captura[equipo]}: {type(e).__name__} - {e}")
        read_failed = True

    t2= time.time()
    ee = 200

    # Logging en debug
    # if DEBUG:
    #     color = {
    #         '1': Style.BRIGHT + Fore.GREEN,
    #         '2': Style.BRIGHT + Fore.YELLOW,
    #         '3': Style.BRIGHT + Fore.MAGENTA
    #     }.get(equipo[-1], Fore.RESET)
    #     print(Fore.RESET + time.strftime("%Y-%m-%d %H:%M:%S") + color + f" -- {equipo}: {datos}")
    #     print("-" * 70)

    _log_debug(equipo, datos)

    # Guardar en BD solo si todas las lecturas fueron correctas
    ee = 300
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    if not read_failed:
        ee = 302
        try:
            datos['Nfallos'] = n_fallos_captura[equipo]
            salida = json.dumps(datos)
            ee = 304
            # Use parameterized query via db_manager to prevent SQL injection
            db_manager.save_equipment_data(nombre_equipo, tiempo, salida)
            if DEBUG == 100: print(f"{nombre_equipo} - Guardado: {salida} 👌")
            if DEBUG == 0:
                print(f"{nombre_equipo[-1]}", end="", flush=True)
            
        except Exception as e:
            print(Fore.RED + f"Error {ee} guardando datos en BD para {nombre_equipo}: {type(e).__name__} - {e}")
        ee = 330
    else:
        print(f"{tiempo} - Error {ee} {nombre_equipo} - Lectura fallida, no se guardan datos en BD.")

    return datos



def get_command_params(c):
    cmd = comandos[c]
    return {
        'reg': cmd['reg'],
        'dec': cmd.get('dec', 0),
        'tipo': cmd.get('tipo', 'u16'),
        'offset': cmd.get('offset', 0),
        'fc': cmd.get('fc', 3),
        'grabar': cmd.get('grabar', True),
        'adaptar': cmd.get('adaptar', None)
    }

def build_reg_to_comando_map():
    """Build mapping from register number to command name."""
    reg_map = {}
    for cmd_name in comandos:
        if cmd_name in ('ayuda', 'lectura_multiple'):
            continue
        if 'reg' in comandos[cmd_name]:
            reg_map[comandos[cmd_name]['reg']] = cmd_name
    return reg_map

# Build the register to command mapping
reg_to_comando = build_reg_to_comando_map()

def _log_debug(equipo, datos):
    if DEBUG:
        color = {
            '1': Fore.GREEN + Style.BRIGHT,
            '2': Fore.YELLOW + Style.BRIGHT,
            '3': Fore.MAGENTA + Style.BRIGHT
        }.get(equipo[-1], Fore.RESET)
        print(Fore.RESET + time.strftime("%Y-%m-%d %H:%M:%S") + color + f' -- {equipo}: {datos}')
        print('-'*70)

def _grabar_en_bd(equipo, datos, error):
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        if not error:
            datos['Nfallos'] = n_fallos_captura[equipo]
            salida = json.dumps(datos)
            # Use parameterized query via db_manager to prevent SQL injection
            db_manager.save_equipment_data(equipo.upper(), tiempo, salida)
            if DEBUG == 0: print(f'{equipo[-1]}', end='', flush=True)
        else:
            print(f'{tiempo} - Error en captura equipo {equipo.upper()}')
    except Exception as e:
        print(Fore.RED + f'Error grabando en BD equipo {equipo.upper()}: {e}')

    
# Bucle para llamada a funcion leer_equipo

dia = time.strftime("%Y-%m-%d")

t_recarga_parametros = time.time()
t_ultima_captura = {} # marca temporal de la ultima captura de datos de cada equipo
n_fallos_captura = {} # numero de fallos diario en la captura de datos de cada equipo
wh_placa = {}     # sin uso actualmente
wh_consumo = {}   # sin uso actualmente
flag_lectura = {} # Flag de lectura para evitar conflicto con lectura desde Telegram

# Conexion BD (auto-imports from Parametros_FV.py globals)
try:
    ee = '1'
    # Initialize DatabaseManager with parameterized queries
    # Parameters auto-imported from globals (servidor, usuario, clave, basedatos)
    db_manager = DatabaseManager()
    
    # Keep legacy db and cursor for backward compatibility with existing code
    db = db_manager.connection
    cursor = db_manager.cursor
except Exception as e:
    print(Fore.RED, f'ERROR - inicializando BD RAM: {e}')
    sys.exit()


#Apertura Puertos y control registro
modbus={}
      
######### BUCLE PRINCIPAL ############### 
 
while True:
    ee = '10a'
    if time.time() - t_recarga_parametros > 300: # cada XX sg
        t_recarga_parametros = time.time()
        if DEBUG == 1: print(Fore.RED + 'recarga Parametros')
        try:
            exec(open(parametros_FV_DIST).read(),globals()) #cargo Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
            exec(open(parametros_FV).read(),globals()) #cargo Parametros_FV.py
        except:
            print(Fore.RED + 'ERROR en recarga Parametros')
            
    ee = '10b'
    dia_anterior = dia
    dia = time.strftime("%Y-%m-%d")

    if dia_anterior != dia: #cambio de dia
        n_fallos_captura = {}
        wh_placa = {} # Ya veremos si se usa
        wh_consumo = {} # Ya veremos si se usa
    
    ee = '10c'    
    try:
        for e in EQUIPO:
            ee = '10d'
            if EQUIPO[e]['usar'] == 1 and e != 'COMANDOS':
                ee = '10e'
                if e not in modbus:
                    if DEBUG >= 1 : print(f"Abriendo conexion Modbus en {EQUIPO[e]['dev']} con id : {EQUIPO[e]['id_modbus']}", end='')
                    modbus[e] = minimalmodbus.Instrument(EQUIPO[e]['dev'], EQUIPO[e]['id_modbus'])
                    modbus[e].serial.baudrate = EQUIPO[e]['baudrate'] if 'baudrate' in EQUIPO[e] else 9600
                    modbus[e].serial.bytesize = 8
                    modbus[e].serial.parity = minimalmodbus.serial.PARITY_NONE
                    modbus[e].serial.stopbits = 1
                    modbus[e].serial.timeout = 3
                    modbus[e].debug = False
                    modbus[e].mode = minimalmodbus.MODE_RTU
                    if DEBUG >= 1 : print('.... OK')
                n_fallos_captura[e] = n_fallos_captura[e] if e in n_fallos_captura else 0
                
                #flag_lectura[e] = 0 if e not in flag_lectura else flag_lectura[e]
                ee = '10e_10'
                #for c_mqtt in comando_mqtt:
                if comando_mqtt != {}:
                    c_mqtt = comando_mqtt.copy()
                    ee = '10e_20'
                    if c_mqtt['comando'] in comandos['ayuda']: # Comando AYUDA  
                        ee = '10e_30'
                        if DEBUG >= 1: print(f"Ejecutando Listar Parametros de equipo {c_mqtt['equipo']}")
                        listar_parametros(c_mqtt['equipo'])
                    else:
                        ee = '10e_40'
                        if DEBUG >= 1: print(f"Ejecutando Lectura/Escritura {c_mqtt['comando']} en equipo {c_mqtt['equipo']}")
                        escribir_registro(c_mqtt['equipo'], c_mqtt['comando']) #comando de lectura o escritura de un registro                 
                    
                    comando_mqtt = {} # ya vere si se hace para N
                
                ee = '10e_50'    
                if e in t_ultima_captura.keys():
                    if time.time() - t_ultima_captura[e] > EQUIPO[e]['tiempo_captura']:# and flag_lectura[e] == 0:
                        ee = '10f'
                        try:
                            leer_equipo(e)
                            t_ultima_captura[e] = time.time()
                        except Exception as error:
                            print(Fore.RED + f"Error {ee} en Bucle Principal... equipo {e} :", type(error).__name__, "–", error) 
                            time.sleep(1)
                            continue
                else:
                    t_ultima_captura[e] = time.time()
                    
                    # comprobacion que existe registro en tabla equipos
                    ee = '10g'
                    
                    try: 
                        ee = '10h'
                        nombre_equipo = e.upper()
                        
                        # Use db_manager to insert equipment if missing
                        db_manager.insert_equipment_if_missing(nombre_equipo)
                    except:
                        pass    
                   
    except Exception as error1:
        print(f"Error {ee} en bucle principal", type(error1).__name__, "-", error1) 
        print ('.... se reinicia')
        cursor.close()
        db.close()
    
        sys.exit()
    
    time.sleep(0.1)
