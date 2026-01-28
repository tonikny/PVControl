# -*- coding: utf-8 -*-

# Versión 2024-02-02
#

ANENJI = {
    'ANENJI1': {'usar':1,
                'dev': '/dev/ttyUSB0',
                'id_modbus': 1,
                'tiempo_captura': 5,
                'ciclos_grabacion' : 0, # 0 para NO grabar en BD
          },
          
    'ANENJI2': {'usar':0,
                'dev': '/dev/ttyUSB1',
                'id_modbus': 1,
                'tiempo_captura': 3,
                'ciclos_grabacion' : 0,
          },
          
    'COMANDOS':{
              'ayuda' : ['h','?','i', 'info',''],
              
              'Out_prio': {'reg':301, 'dec': 0, 'min':0, 'max':2,'parametro': 1},
              'Input_range': {'reg':302, 'dec': 0, 'min':0, 'max':1,'parametro': 3},
              'Buzzer_mode_range': {'reg':303, 'dec': 0, 'min':0, 'max':2,'parametro': 18},
              
              'LCD_light': {'reg':305, 'dec': 0, 'min':0, 'max':1,'parametro': 20},
              'LCD_return': {'reg':306, 'dec': 0, 'min':0, 'max':1,'parametro': 19},
              
              'Over_load_return': {'reg':308, 'dec': 0, 'min':0, 'max':1,'parametro': 6},
              'Over_Temp_return': {'reg':309, 'dec': 0, 'min':0, 'max':1,'parametro': 7},
              'Over_load_bypass': {'reg':310, 'dec': 0, 'min':0, 'max':1},
              
              
              'Vabs': {'reg':324, 'dec': 1, 'min':48.0, 'max':62.0,'parametro': 26},
              'Vflot': {'reg':325, 'dec': 1, 'min':48.0, 'max':62.0,'parametro': 27},
              'Voff_r_main': {'reg':326, 'dec': 1, 'min':40.0, 'max':48.0},
              'Voff_main': {'reg':327, 'dec': 1, 'min':40.0, 'max':48.0},
              'R328': {'reg':328, 'dec': 0, 'min':0, 'max':10000}, #??
              'Voff': {'reg':329, 'dec': 1, 'min':40.0, 'max':48.0},
              'R330': {'reg':330, 'dec': 0, 'min':0, 'max':10000}, #??
              'Prioridad_carga': {'reg':331, 'dec': 0, 'min':0, 'max':3,'parametro': 16},
              'Icarga_max': {'reg':332, 'dec': 1, 'min':2.0, 'max':80.0,'parametro': 11},
              'Icarga_main': {'reg':333, 'dec': 1, 'min':2.0, 'max':30.0,'parametro': 2},
              'Vequ': {'reg':334, 'dec': 1, 'min':48.0, 'max':62.0,'parametro': 34},
              'Tequ': {'reg':335, 'dec': 0, 'min':0, 'max':900,'parametro': 35},
              'Tequ_timeout': {'reg':336, 'dec': 0, 'min':0, 'max':900,'parametro': 36},
              'Tequ_dias': {'reg':337, 'dec': 0, 'min':0, 'max':90,'parametro': 37},
              
              'Modo_On_Off': {'reg':406, 'dec': 0, 'min':0, 'max':2},
              'Remote_Switch': {'reg':420, 'dec': 0, 'min':0, 'max':1},
             
            }
          
          
    }


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'ANENJI'
servicio = 'fv_anenji'
# ---------------------------
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

EQUIPO = eval(NEQUIPO)
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
    
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0])

#Comprobacion argumentos en comando
simular_datos = DEBUG= 0
narg = len(sys.argv)
if '-p' in sys.argv: DEBUG = 1 # para desarrollo permite print en distintos sitios
if '-s' in sys.argv: simular_datos = 1 # para desarrollo permite print en distintos sitios

if DEBUG > 0:
    print()
    print (Fore.CYAN+ '------- Parametros -------')
    print(EQUIPO)
    print('-' * 40)


@timeout_decorator.timeout(10, use_signals=False)
def bot_enviar_mensaje(cid, msg):
    bot.send_message(cid, msg, parse_mode="HTML")

if usar_telegram == 1:
    try:
        bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
        bot.skip_pending = True # Skip the pending messages
        cid = Aut[0]
        bot_enviar_mensaje(cid, f'Arrancando Programa Control {NEQUIPO}')
    except:
        print ('Error en envio de mensaje Telegram')


##### MQTT ###########################################
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
    
    def leer(reg, dec):
        modbus1 = minimalmodbus.Instrument(EQUIPO[topic]['dev'], EQUIPO[topic]['id_modbus'])
        modbus1.serial.baudrate = 9600
        modbus1.serial.bytesize = 8
        modbus1.serial.parity = minimalmodbus.serial.PARITY_NONE
        modbus1.serial.stopbits = 1
        modbus1.serial.timeout = 3
        modbus1.debug = False
        modbus1.mode = minimalmodbus.MODE_RTU
        lectura = modbus1.read_register(reg, dec)  # Registro, nº decimales
        modbus1.serial.close()
        return lectura
    
    def escribir(reg, x, dec):  
        modbus1 = minimalmodbus.Instrument(EQUIPO[topic]['dev'], EQUIPO[topic]['id_modbus'])
        modbus1.serial.baudrate = 9600
        modbus1.serial.bytesize = 8
        modbus1.serial.parity = minimalmodbus.serial.PARITY_NONE
        modbus1.serial.stopbits = 1
        modbus1.serial.timeout = 3
        modbus1.debug = False
        modbus1.mode = minimalmodbus.MODE_RTU
        
        modbus1.write_register(reg, x, dec)  # Registro, valor, nº decimales
        
        modbus1.serial.close()
        
    print(msg)
    ee = 10
    topic = msg.topic.upper()[10:] # quito PVControl/
    mensaje = msg.payload.decode().strip()
    MENSAJE = mensaje.upper()
    ee = 20
    if DEBUG == 1: print (Fore.CYAN + f'Comando {mensaje} en equipo {topic} recibido')
    
    if MENSAJE in comandos['ayuda']:
        msg = f'\U0001F4DF   <b>LISTA PARAMETROS {topic}</b>\n'
        msg += ' =============================\n'
        for c in comandos:
            msg += f'\U0001F6A6<b>{c}</b> : {comandos[c]}\n'
            try:
                registro = comandos[c]['reg']
                decimales = comandos[c]['dec']
                d = leer(registro, decimales)  # Registro, nº decimales
                msg += f"    ..... Valor Actual de <b>{c}={d}</b>\n\n"
            except:
                msg += '\n'
        if usar_telegram == 1: bot_enviar_mensaje(cid, msg)
        return
        
    for c in comandos:
        ee = 30
        f = MENSAJE.find(c.upper())
        
        if f != -1: # se encuentra la cadena
            ee = 40
            variable = mensaje[f:len(c)]
            registro = comandos[c]['reg']
            decimales = comandos[c]['dec']
            valor = mensaje[len(c):].strip()
            ee = 50
            if len(valor) > 0:
                if valor[0] == '=': valor = valor[1:]
                valor_n = float(valor)
                escritura = True
            else:
                escritura = False
                
            ee = 60
            
            try:
                ee = 100
                d = leer(registro, decimales)  # Registro, nº decimales
                msg = f'Valor registro {registro}...{variable}= {d} '
                if DEBUG == 1: print(msg)
                ee = 120
                if escritura:
                    if valor_n < comandos[c]['min'] or valor_n > comandos[c]['max']:
                        escritura = False
                        msg += f'\n Error en valor {valor_n} fuera de rango admitido'
                        if DEBUG == 1: print(msg)
                        
                ee = 130
                if escritura:
                    escribir(registro, valor_n, decimales)
                    msg += f'\nNuevo Valor-->{registro}...{variable}= {valor_n} '
                    if DEBUG == 1: print(msg)
                bot_enviar_mensaje(cid, msg)
            except:
                print(f'Error {ee} en comando')
            time.sleep(1)
            
client = mqtt.Client(f"{NEQUIPO}")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
try:
    client.connect(mqtt_broker, mqtt_puerto) #conectar al broker: url, puerto
except:
    print(f'Error de conexion al servidor MQTT en {NEQUIPO}')
time.sleep(.2)

client.loop_start()  
#######################################################

def leer_equipo(equipo): # bucle de lectura de cada equipo
    global n_fallos_captura
    
    t0= time.time()
    
    # creamos que registro en tabla equipos si no existe
    try:
        ee = '100'
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
    except:
        print (Fore.RED,f'ERROR {ee} - inicializando BD RAM en equipo {equipo}')
        return

    # Conexion al equipo
    if simular_datos == 0:
        modbus = minimalmodbus.Instrument(EQUIPO[equipo]['dev'], EQUIPO[equipo]['id_modbus'])
        modbus.serial.baudrate = 9600
        modbus.serial.bytesize = 8
        modbus.serial.parity = minimalmodbus.serial.PARITY_NONE
        modbus.serial.stopbits = 1
        modbus.serial.timeout = 3
        modbus.debug = False
        modbus.mode = minimalmodbus.MODE_RTU
        
    #Captura 
    t1= time.time()
    
    datos= {} # inicializo diccionario
    error = False
    
    try:
        ee = 100
        reg_ini = 201
        reg_fin = 234
        nreg = reg_fin - reg_ini + 1
       
        try:
            d = modbus.read_registers(reg_ini, nreg, 3) if simular_datos == 0 else [9999] * nreg 
        except:
            error = True
            n_fallos_captura[equipo] += 1
                
        if not error:
            ee = 110
             
            #####################################
            #    interpretacion captura
            #####################################
            x = d[201-reg_ini] # Working Mode
            if   x == 0: datos['WM'] = '0-Power On'
            elif x == 1: datos['WM'] = '1-Standby'
            elif x == 2: datos['WM'] = '2-Mains'
            elif x == 3: datos['WM'] = '3-Off-Grid'
            elif x == 4: datos['WM'] = '4-Bypass'
            elif x == 5: datos['WM'] = '5-Charging'
            elif x == 6: datos['WM'] = '6-Fault'

            datos['Vred'] = round(d[202 - reg_ini] / 10,2)  # Voltaje red AC entrada
            datos['Fred'] = round(d[203 - reg_ini] / 100,2) # Frecuencia red AC entrada
            datos['Wred'] = d[204 - reg_ini]  # W de red AC.... ver  signo ??
            datos['Vred_aff'] = round(d[205 - reg_ini] / 10,2)  # Voltaje Affectivo red AC entrada
            datos['Ired_aff'] = round(d[206 - reg_ini] / 10,2)  # Intensidad Affectiva red AC entrada
            datos['Finv'] = round(d[207 - reg_ini] / 100,2) # Frecuencia Hibrido
            
            x = d[208 - reg_ini]
            datos['Winv'] = x if x < 32768 else x-65535  # W del inversor
            datos['Winv_bat'] = d[209 - reg_ini]  #  Watios de AC entrada a bateria
            datos['Vout'] = round(d[210 - reg_ini] / 10,2)  #  Salida Voltaje efectivo
            datos['Iout'] = round(d[211 - reg_ini] / 10,2)  #  Salida Intensidad efectiva
            datos['Fout'] = round(d[212 - reg_ini] / 100,2) #  Salida Frecuencia
            
            x = d[213 - reg_ini]
            datos['Wout'] = x if x < 32768 else x-65535  # Output active power
        
            datos['VAout'] = d[214 - reg_ini]  #  Output VA power
            datos['Vbat'] = round(d[215 - reg_ini] / 10,2)  # Voltaje bateria
            x = d[216 - reg_ini]
            datos['Ibat'] = round(x/10, 2) if x < 32768 else round((x-65535)/10 ,2)  # Intensidad bateria con signo
            
            x = d[232 - reg_ini]
            datos['Ibat1'] = round(x/10, 2) if x < 32768 else round((x-65535)/10 ,2)  # Intensidad bateria con signo
            
            datos['Vplaca'] = round(d[219 - reg_ini] / 10,2)  # Voltaje placa
            datos['Iplaca'] = round(d[220 - reg_ini] / 10,2)  # Intensidad placa
            
            datos['Wplaca'] = d[223 - reg_ini]  # Watios Placa  
            datos['Wplaca_bat'] = d[224 - reg_ini]  # Watios de Placa a bateria
            datos['Carga%'] = d[225 - reg_ini]  # % carga
            datos['Temp_dc'] = d[226 - reg_ini]  # Temperatura DC-DC
            datos['Temp_inv'] = d[227 - reg_ini]  # Temperatura Inversor
            datos['SOC'] = d[229 - reg_ini]  # % bateria
        
            x = d[233 - reg_ini]
            datos['Icarga'] = round(x/10, 2) if x < 32768 else round((x-65535)/10 ,2)  # Intensidad bateria con signo
            x = d[234 - reg_ini]
            datos['Icarga_placas'] = round(x/10, 2) if x < 32768 else round((x-65535)/10 ,2)  # Intensidad bateria con signo
            
            
        ####### 
        reg_ini = 300
        reg_fin = 337
        nreg = reg_fin - reg_ini + 1
       
        try:
            d = modbus.read_registers(reg_ini, nreg, 3) if simular_datos == 0 else [9999] * nreg 
        except:
            error = True
            n_fallos_captura[equipo] += 1
                
        if not error:
            ee = 210
            
            x = d[300-reg_ini] #Modo salida
            if   x == 0: datos['Out_modo'] = '0-Single'
            elif x == 1: datos['Out_modo'] = '1-Paralelo'
            elif x == 2: datos['Out_modo'] = '2-Fase1'
            elif x == 3: datos['Out_modo'] = '3-Fase2'
            elif x == 4: datos['Out_modo'] = '4-Fase3'
            
            x = d[301-reg_ini] # Working Mode
            if   x == 0: datos['Out_prio'] = '0-Util_PV_Bat'
            elif x == 1: datos['Out_prio'] = '1-PV_Util_Bat'
            elif x == 2: datos['Out_prio'] = '1-PV_Bat_Util'
            
            
            datos['Vabs'] = round(d[324 - reg_ini] / 10,1)  # Vabs  
            datos['Vflot'] =  round(d[325 - reg_ini] / 10,1)  # Vflot              
            
    except Exception as error1:
        print(f"Error {ee} en leer_equipo({e}) ", type(error1).__name__, "–", error1) 
        error = True
        
    t2= time.time()
    
    if DEBUG == 1:
        #print(equipo, equipo[-1])
        if equipo[-1] == '1': color = Style.BRIGHT + Fore.GREEN
        elif equipo[-1] == '2': color = Style.BRIGHT + Fore.YELLOW
        else: color = Fore.RESET
        
        print(Fore.RESET+time.strftime("%Y-%m-%d %H:%M:%S")+ color + f' -- {e}: {datos}') # print del diccionario que estoy creando
        print('-' * 70)
    
    try:####  ARCHIVOS RAM en BD ############ 
        ee = '300'
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        if not error:
            datos['Nfallos'] = n_fallos_captura[equipo]
            
            salida = json.dumps(datos)
            nombre_equipo = equipo.upper()
            sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{equipo}'") # grabacion en BD RAM
            #print (Fore.RED+sql)
            cursor.execute(sql)
            ee = 310
            db.commit()
            if DEBUG == 0:
                print('G', flush= True, end='')
        else:
            print(f'{tiempo} - Error {ee} en captura equipo {equipo}')
            
            
    except:
        print(Fore.RED+f'error {ee}, Grabacion tabla RAM equipos en {equipo}')
    
    cursor.close()
    db.close()
    
    
    
# Bucle para llamada a funcion leer_equipo

dia = time.strftime("%Y-%m-%d")

t_recarga_parametros = time.time()
t_ultima_captura = {} # marca temporal de la ultima captura de datos de cada equipo
n_fallos_captura = {} # numero de fallos diario en la captura de datos de cada equipo
wh_placa = {}
wh_consumo = {}


Nbucles = 0
while True:
    Nbucles += 1
    ee = '10a'
    if time.time() - t_recarga_parametros > 300: # cada XX sg
        t_recarga_parametros = time.time()
        if DEBUG == 1: print(Fore.RED + 'recarga Parametros')
        try:
            exec(open(parametros_FV_DIST).read(),globals()) #cargo Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
            exec(open(parametros_FV).read(),globals()) #cargo Parametros_FV.py
            EQUIPO = eval(NEQUIPO)
            comandos = EQUIPO['COMANDOS']
            del EQUIPO['COMANDOS']
        except:
            print(Fore.RED + 'ERROR en recarga Parametros')
            
    ee = '10b'
    dia_anterior = dia
    dia = time.strftime("%Y-%m-%d")

    if dia_anterior != dia: #cambio de dia
        n_fallos_captura = {}
        wh_placa = {}
        wh_consumo = {}
    
    ee = '10c'    
    try:
        for e in EQUIPO:
            ee = '10d'
            if EQUIPO[e]['usar'] == 1:
                ee = '10e'
                n_fallos_captura[e] = 0
                if e in t_ultima_captura.keys():
                    if time.time() - t_ultima_captura[e] > EQUIPO[e]['tiempo_captura']:
                        ee = '10f'
                        try:
                            if DEBUG > 0: print(Nbucles)
                            leer_equipo(e)
                            t_ultima_captura[e] = time.time()
                            Nbucles = 0
                        except Exception as error:
                            print(Fore.RED + f"Error {ee} en Bucle Principal... equipo {e} :", type(error).__name__, "–", error) 
                            time.sleep(10)
                            continue  
                    else:
                        time.sleep(0.1)
                else:
                    t_ultima_captura[e] = time.time()
                    
                    # comprobacion que existe registro en tabla equipos
                    ee = '10g'
                    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                    cursor = db.cursor()
                    
                    try: 
                        ee = '10h'
                        nombre_equipo = e.upper()
                        
                        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                                      (nombre_equipo,'{}'))   
                        db.commit()
                    except:
                        pass    
                    cursor.close()
                    db.close()
            
    except Exception as error1:
        print(f"Error {ee} en bucle principal", type(error1).__name__, "–", error1) 
        print ('.... se reinicia')
        cursor.close()
        db.close()
        
        sys.exit()
    
    time.sleep(0.1)
