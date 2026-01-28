from concurrent.futures import ThreadPoolExecutor
import time
import paho.mqtt.client as mqtt
import MySQLdb,json

import sys, subprocess

##################################################################
##### NO TOCAR ESTA PARTE----- PERSONALIZAR EN Parametros_fv.py
##################################################################

# SCAN: Si no se incluye o esta a False  solo se capturan los reles definidos.... 
#       .....con True se añaden a EQUIPOS todos los dispositivos que se detecten en el scan de la LAN

# TABLA : False implica que NO se guardan los datos historicos en la tabla TUYA
# CREAR_RELE : False implica que NO se creara el rele correspondiente en la tabla reles
# MODO: Por defecto el rele se creara con modo "MAN" salvo que se especifique otro modo (ON. OFF,....)
# tmuestra: tiempo entre capturas

TUYA = {
    'usar': 0,
    
    'SCAN': True,
    
    'tmuestra': 15,
    
    'RELES':{
        801 : {'Nombre': 'Rele 801', 'ID': 'XXXX1', 'KEY': 'YYYY1'},
        802 : {'Nombre': 'Rele 802', 'ID': 'XXXX2', 'KEY': 'YYYY2', 'TABLA': False, 'CREAR_RELE': False, },
        
    }
}
############### FIN Parametrizacion #################

# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'TUYA'
servicio = 'fv_tuya'
control = f"TUYA['usar']"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
"""
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Style: DIM, NORMAL, BRIGHT, RESET_ALL
"""
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_tuya') #+Style.RESET_ALL)

# Intenta importar la librería
try:
    import tinytuya 
except ImportError:
    try:
        # Instala tinytuya usando pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tinytuya"])
    except Exception as e:
        sys.exit(1)  # Termina el script si no se puede instalar

import tinytuya
   

DEBUG = False
if '-p' in sys.argv: DEBUG= True 

# -----------------------MQTT MOSQUITTO ------------------------
def on_connect(cli, userdata, flags, rc):
    cli.subscribe("PVControl/Reles/TUYA")
    cli.subscribe("PVControl/TUYA")
    if sys.stdout.isatty():
        print('Suscripcion a PVControl/Reles/TUYA')
        print('Suscripcion a PVControl/TUYA')
            
def on_disconnect(cli, userdata, rc):
    if rc != 0:
        print (f'{time.strftime("%H:%M:%S")} Desconexion MQTT.... intentando reconectar (asegure que NO esta corriendo a la vez el servicio fv_tuya y fv_tuya.py')
    else:
        cli.loop_stop()
        cli.disconnect()

def on_message(client, userdata, msg):
    global device
    
    print(msg.topic+" "+str(msg.payload))
    if  msg.topic in ("PVControl/Reles/TUYA", "PVControl/TUYA") :
        comando = msg.payload.decode('utf-8')
        print(f'comando recibido: {comando}')  
        
        # comando tipo 806ON
        if comando[:1] == '8':
            id_rele = int(comando[:3])
            orden = comando[3:]
            if orden == 'ON':
                device[id_rele].turn_on()
                print(f'rele {id_rele} a ON')
            elif orden == 'OFF':
                device[id_rele].turn_off()
                print(f'rele {id_rele} a OFF')
            else: 
                print(f'Orden {orden} en rele {id_rele} no rreconocida')    

        
            
        """
        try:
            db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor1 = db1.cursor()
            
            comando = msg.payload.decode('utf-8')
            if DEBUG == 1: print(f'comando recibido: {comando}')
            id_rele = comando[0:3]
            modo = comando[3:]
            sql = f'UPDATE reles SET modo="{modo}" WHERE id_rele={id_rele}'
            cursor1.execute(sql)
            db1.commit()
        except:
            db1.rollback()
        try:
            cursor1.close()
            db1.close()
        except:
            pass
        """
               
client = mqtt.Client("tuya") #crear nueva instancia
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


# Función para capturar el estado de un dispositivo
def capturar_status(id_rele, dispositivo):
    global datos
    try:
        ee = 10
        # Obtener el estado del dispositivo
        if 'tiempo' in datos[id_rele]:
            t_ant = datos[id_rele]['tiempo']
        else:
            t_ant = time.time()
        
        t_captura = round(time.time(),1)
            
        t_muestra = time.time() - t_ant
        status = dispositivo.status()
        ee = 20
        if DEBUG:
            print()
            print('=' * 5, id_rele, dispositivo.address, Fore.YELLOW+datos[id_rele]['Nombre']+Fore.RESET, '=' * 40)
            print("status", status)
            print(status.items())
            print()
        
        if 'dps' in status:
            ee = 22
            # Extraer los campos relevantes
            
            lectura = status.get('dps', None)
            ee = 23
            
            if lectura is not None:
                for l in lectura:
                    #print(l, lectura[l])
                    ee = 25
            
                    if l == '1':
                        ee = 25.1
                        captura = lectura[l]
                        estado = 100 if captura else 0 # Estado de encendido/apagado
                        if DEBUG: print(f"Estado: {estado}")
                        
                        if estado == 100:
                            if dia == dia_anterior:
                                datos[id_rele]['T_on'] = round(datos[id_rele]['T_on'] +  t_muestra,1) 
                            else:
                                datos[id_rele]['T_on'] = 0
                                                         
                        if estado != datos[id_rele]['Estado']:
                            if sys.stdout.isatty(): print(f'{Fore.YELLOW}Cambio de estado en rele {id_rele} a {estado}{Fore.RESET}')
                            
                            datos[id_rele]['Estado'] = estado
                            sql = """
                                  UPDATE reles
                                  SET estado = %s
                                  WHERE id_rele = %s;
                                  """
                            valores = (estado, id_rele)
                            ee = 27
                            # Ejecutar la consulta
                            cursor.execute(sql, valores)

                            # Confirmar los cambios en la base de datos
                            db.commit()
                            
                    elif l == '18':
                        ee = 25.2
                        captura = lectura[l]
                        current = captura
                        
                    elif l == '19':
                        ee = 25.3
                        captura = lectura[l]
                        datos[id_rele]['Wac'] = captura / 10 # Potencia en W
                        
                        if 'Wh' not in datos[id_rele]: datos[id_rele]['Wh'] = 0 # Inicializar Wh
                        if 'Wmax' not in datos[id_rele]: datos[id_rele]['Wmax'] = 0 # Inicializar Wmax
                        
                        if dia == dia_anterior:
                            datos[id_rele]['Wmax'] = max(datos[id_rele]['Wac'], datos[id_rele]['Wmax'])
                            datos[id_rele]['Wh'] = round(datos[id_rele]['Wh'] + datos[id_rele]['Wac'] * t_muestra/3600,3) 
                        else:
                            datos[id_rele]['Wmax'] = 0
                            datos[id_rele]['Wh_ayer'] = datos[id_rele]['Wh']
                            datos[id_rele]['Wh']= 0
                       
                        if DEBUG: print(f"Potencia: {datos[id_rele]['Wac']} W")
                    elif l == '20':
                        ee = 25.4
                        captura = lectura[l]
                        datos[id_rele]['Vac'] = captura / 10 # Voltaje en V
                        if DEBUG: print(f"Voltaje: {datos[id_rele]['Vac']} V")
                    elif l == '39':
                        ee = 25.5
                        captura = lectura[l]
                        Overcharge_switch = captura 
                        if DEBUG: print(f"Overcharge_switch {Overcharge_switch}")
                    elif l == '41':
                        ee = 25.6
                        captura = lectura[l]
                        Child_lock = captura
                        if DEBUG: print(f"Child_lock: {Child_lock}")                       
                
                    ee = 28
            
                #datos[id_rele]['tiempo'] = round(time.time(),1)
            
                #print('----  ', datos[id_rele])
                
        else:
            ee = 30
            print(f"{Fore.MAGENTA}{id_rele}-{datos[id_rele]['Nombre']} -> status: {status}")
            print()
    
        datos[id_rele]['tiempo'] = t_captura
        
    except Exception as e:
        print(f"{Fore.RED}Error {ee} al capturar el estado de {id_rele}: {e}")
        try:
            print(Fore.YELLOW, status, Fore.RESET)
        except:
            print(Fore.RESET)


# Función para actualizar la tabla TUYA_DIARIO
def actualizar_diario():
    for id_rele, valores in datos.items():
        # Obtener los valores, usando 0 si no existen
        wac = valores.get('Wac', 0)
        estado = valores.get('Estado', 0)
        wh = valores.get('Wh', 0)
        wmax = valores.get('Wmax', 0)
        t_on = valores.get('T_on', 0)

        # Insertar o actualizar el registro del día
        cursor.execute('''
        INSERT INTO TUYA_DIARIO (Fecha, id_rele, Wh, Wmax, T_on)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Wh = VALUES(Wh),
        Wmax = VALUES(Wmax),
        T_on = VALUES(T_on)
        ''', (dia, id_rele, wh, wmax, t_on))
    db.commit()


################################################
#### OPERACIONES PREVIAS EN BD #################
################################################

# Conexión a la base de datos
db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
cursor = db.cursor()

dia = time.strftime("%Y-%m-%d")

if sys.stdout.isatty():print (Fore.CYAN, ' Chequeando tabla TUYA_DIARIO....', end='')
# Creación de la tabla TUYA_DIARIO si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS TUYA_DIARIO (
    Fecha DATE NOT NULL,
    id_rele VARCHAR(10) NOT NULL,
    Wh FLOAT NOT NULL,
    Wmax FLOAT NOT NULL,
    T_on FLOAT NOT NULL,
    PRIMARY KEY (Fecha, id_rele))
''')

if sys.stdout.isatty():print ('OK')


# Verificar si la tabla "TUYA_HISTORICO" existe

if sys.stdout.isatty():print (Fore.CYAN, ' Chequeando tabla TUYA_HISTORICO....', end='')

cursor.execute("SHOW TABLES LIKE 'TUYA_HISTORICO'")
tabla_existe = cursor.fetchone()

if not tabla_existe:
    crear_tabla_TUYA = """
    CREATE TABLE TUYA_HISTORICO (
        id_registro INT AUTO_INCREMENT PRIMARY KEY,
        id_rele VARCHAR(10) NOT NULL,
        tiempo DATETIME NOT NULL,
        estado TINYINT UNSIGNED NOT NULL,
        wac FLOAT,
        vac FLOAT,
        wh FLOAT
    )
    """
    cursor.execute(crear_tabla_TUYA)
    print("Tabla 'TUYA_HISTORICO' creada exitosamente.")
else:
    if sys.stdout.isatty():print ('OK')

# Verificar si la tabla "TUYA_DISPOSITIVOS" existe
if sys.stdout.isatty():print (Fore.CYAN, ' Chequeando tabla TUYA_DISPOSITIVOS....', end='')

cursor.execute("SHOW TABLES LIKE 'TUYA_DISPOSITIVOS'")
tabla_existe = cursor.fetchone()

# Si la tabla no existe, crearla
if not tabla_existe:
    crear_tabla_TUYA = """
    CREATE TABLE TUYA_DISPOSITIVOS (
        id_dispositivo VARCHAR(50) PRIMARY KEY,
        id_rele VARCHAR(10) NOT NULL,
        nombre VARCHAR(50) NOT NULL,
        clave_local VARCHAR(50) NOT NULL,
        version VARCHAR(10) NOT NULL,
        ip VARCHAR(15) NOT NULL        
    )
    """
    cursor.execute(crear_tabla_TUYA)
    print("Tabla 'TUYA_DISPOSITIVOS' creada exitosamente.")
else:
    if sys.stdout.isatty():print ('OK')


# Ver si el campo "sensores" esta como VARCHAR(10000) en tabla equipos
cursor.execute("SHOW COLUMNS FROM equipos LIKE 'sensores'")
resultado = cursor.fetchone()

if resultado:
    tipo_campo = resultado[1]  # Ejemplo: 'varchar(5000)'
    if DEBUG: print(f"El campo sensores de tabla equipos tiene actualmente el tipo: {tipo_campo}")

    # 2. Verificar si el campo tiene el tamaño deseado (VARCHAR(10000))
    if not tipo_campo.lower().startswith('varchar(10000)'):
        print()
        print(f"{Fore.RED}El campo 'sensores' no está definido como VARCHAR(10000). Actualizando...")

        # 3. Ejecutar ALTER TABLE para actualizar el campo
        try:
            cursor.execute(f"ALTER TABLE equipos MODIFY sensores VARCHAR(10000);")
            db.commit()
            print(f"{Fore.GREEN}El campo 'sensores' ha sido actualizado a VARCHAR(10000).")
        except MySQLdb.Error as e:
            print(f"¡¡¡¡ Error al actualizar el campo sensores: {e} !!!!")
    else:
        if DEBUG: print(f"{Fore.GREEN}El campo 'sensores' ya está definido como VARCHAR(10000). No se requiere actualización.")
else:
    print()
    print ('=' * 80)
    print(f"{Fore.RED}El campo 'sensores' no existe en la tabla 'equipos'.")
    print ('=' * 80)
    print()

# Recorrer el diccionario TUYA['RELES'] para actualizar tabla reles

if sys.stdout.isatty():print()
for id_rele, datos_rele in TUYA['RELES'].items():
    # Verificar si la clave 'CREAR_RELE' no existe o es True
    if 'CREAR_RELE' not in datos_rele or datos_rele['CREAR_RELE']:
        nombre = datos_rele['Nombre']
        modo = datos_rele.get('MODO', 'MAN')  # Usar 'MAN' por defecto, a menos que exista la clave 'MODO'
        calibracion = ''
        
        if sys.stdout.isatty(): print(f'{Fore.GREEN} Creando/Actualizando rele {Fore.YELLOW}{id_rele} {nombre}{Fore.GREEN} a modo {Fore.YELLOW}{modo}{Fore.RESET} ')
        
        # Consulta SQL para insertar o actualizar el registro
        query = """
        INSERT INTO reles (id_rele, nombre, modo, calibracion)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE nombre = %s, modo = %s, calibracion = %s
        """
        valores = (id_rele, nombre, modo, calibracion, nombre, modo, calibracion)

        # Ejecutar la consulta
        cursor.execute(query, valores)

db.commit()


# Inicializar los campos IP y VERSION con 0
for device_data in TUYA['RELES'].values():
    device_data['IP'] = device_data.get('IP',0)
    device_data['VERSION'] = device_data.get('VERSION',0)

    
# Escanear dispositivos en la red
if sys.stdout.isatty(): print ( Fore.CYAN,'  Escaneando dispositivos en la LAN.....')
TUYA_scan = tinytuya.deviceScan()
if DEBUG:
    for d in TUYA_scan:
        print(TUYA_scan[d])
        print()
    print ( '=' * 80)
    print()
    #time.sleep(10)

# Recorrer los dispositivos escaneados para añadir IP y VERSION
for ip, device_info in TUYA_scan.items():
    device_id = device_info['gwId']  # ID del dispositivo escaneado
    version = device_info['version']  # Versión del protocolo

    # Buscar si el dispositivo escaneado está en el diccionario 'TUYA'
    found = False
    for name, data in TUYA['RELES'].items():
        if data['ID'] == device_id:
            # Actualizar la IP y la VERSION en el diccionario
            data['IP'] = ip
            data['VERSION'] = version
            found = True
            break

    # Si el dispositivo escaneado no está en el diccionario TUYA, añadirlo si TUYA['SCAN'] esta a True
    if not found and TUYA['SCAN']:
        # Crear un nombre predeterminado 
        new_name = f"8_{device_id[-4:]}"  # Usamos los últimos 4 caracteres del ID
        TUYA['RELES'][new_name] = {
            'ID': device_id,
            'KEY': 0,  # Sin Clave KEY
            'IP': ip,
            'VERSION': version,
            'Nombre': f"Rele_{device_id[-4:]}",
            'TABLA': False
        }

# Mostrar el diccionario actualizado
if DEBUG:
    print("Dispositivos actualizados:")
    for d in TUYA['RELES']: print(f"{d}-> {TUYA['RELES'][d]}")


# Bucle para insertar o actualizar los datos
for id_rele, dispositivo in TUYA['RELES'].items():
    query = """
    INSERT INTO TUYA_DISPOSITIVOS (id_dispositivo, id_rele, nombre, clave_local, version, ip)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    id_rele = VALUES(id_rele),
    nombre = VALUES(nombre),
    clave_local = VALUES(clave_local),
    version = VALUES(version),
    ip = VALUES(ip)
    """
    values = (
        dispositivo['ID'],
        id_rele,  # El id_rele es la clave del diccionario TUYA['RELES'] 
        dispositivo['Nombre'],
        dispositivo['KEY'],
        dispositivo['VERSION'],
        dispositivo['IP']
    )
    
    cursor.execute(query, values)



# Crear los objetos de los dispositivos e inicializar datos
device = {}
datos =  {}

for d in TUYA['RELES']:
    datos[d] = {}
    datos[d]['Estado'] = 0
    datos[d]['Nombre'] = TUYA['RELES'][d]['Nombre']
    datos[d]['T_on'] = 0
    
    #datos[d]['Nfallos'] = 0

   
    # Obtener el último valor de Wh, Wmax y T_on de la base de datos
    try:
        sql_hoy = """
        SELECT Wh, Wmax, T_on 
        FROM TUYA_DIARIO 
        WHERE id_rele = %s AND Fecha = CURDATE()
        """
        cursor.execute(sql_hoy, (d,))  # d es el id_rele (801, 802, etc.)
        resultado = cursor.fetchone()
        if resultado:
            datos[d]['Wh'] = resultado[0]  
            datos[d]['Wmax'] = resultado[1]
            datos[d]['T_on'] = resultado[2]
   
    except Exception as e:
        print(f"Error al obtener el último valor de Wmax y T_on para el dispositivo {d}: {e}")

    # Obtener el último valor de Wh_ayer de la base de datos
    try:
        sql_ayer = """
        SELECT Wh 
        FROM TUYA_DIARIO 
        WHERE id_rele = %s AND Fecha = CURDATE() - INTERVAL 1 DAY
        """
        cursor.execute(sql_ayer, (d,))  
        resultado = cursor.fetchone()
        if resultado:
            datos[d]['Wh_ayer'] = resultado[0]  
            
    except Exception as e:
        print(f"Error al obtener el último valor de Wh_ayer para el dispositivo {d}: {e}")



    if TUYA['RELES'][d]['IP'] != 0 and TUYA['RELES'][d]['KEY'] != 0 and TUYA['RELES'][d]['VERSION'] != 0:  
    
        device[d] = tinytuya.OutletDevice(TUYA['RELES'][d]['ID'],
                                          TUYA['RELES'][d]['IP'],
                                          TUYA['RELES'][d]['KEY'],
                                          connection_timeout= 1,
                                          connection_retry_limit=2,
                                          connection_retry_delay=1,
                                          persist=True)
        device[d].set_version(float(TUYA['RELES'][d]['VERSION']))
    else:
        datos[d]['Error'] = f"{TUYA['RELES'][d]['IP']} - {TUYA['RELES'][d]['Nombre']}"

if DEBUG:
    print('-' * 80)
    for d in device: print(d, device[d])
    print('-' * 80)


# Bucle principal con ThreadPoolExecutor
if sys.stdout.isatty():
    print(Fore.YELLOW)
    print('=' * 80)    
    print('            Comenzando captura datos.....')
    print('=' * 80)

diario_actualizacion = time.time()

tmuestra = TUYA.get('tmuestra',15) # Tiempo entre capturas ...por defecto 15 segundos


with ThreadPoolExecutor(max_workers=5) as executor:  # Limitar a 5 hilos simultáneos
    while True:
        t0 = time.time()
        dia_anterior = dia
        dia = time.strftime("%Y-%m-%d")

        # Enviar tareas al pool de hilos
        futures = [executor.submit(capturar_status, name, dispositivo) for name, dispositivo in device.items()]

        # Esperar a que todas las tareas terminen
        for future in futures: future.result()
        
        t1= time.time()
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
               
        if sys.stdout.isatty(): # solo se ejecuta si se esta corriendo en ventana de terminal
            print()
            print(Fore.GREEN + '----',tiempo, '----', f"{(t1- t0):.3f}sg")
            for d in datos:
                print(f"{Fore.YELLOW}{d} {datos[d]['Nombre']:<12} -> ", end='')
                try:
                    print(f"{Fore.GREEN if datos[d]['Estado'] == 0 else Fore.RED}{datos[d]['Estado']:3.0f} => ", end='')
                except:
                    print(Fore.MAGENTA + 'None=> ', end='')
                try:
                    print(f"Wac: {datos[d]['Wac']:5.1f} - Wh: {datos[d]['Wh']:5.1f} - Vac: {datos[d]['Vac']:5.1f}")
                except:
                    print()
                
            print(Fore.RESET)
            #print(datos)
        
        # Consulta SQL para insertar o actualizar el registro
        sql = """
        INSERT INTO equipos (id_equipo, tiempo, sensores)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        tiempo = VALUES(tiempo),
        sensores = VALUES(sensores);
        """
        # Ejecutar la consulta con los datos del diccionario
        salida = json.dumps(datos)
        cursor.execute(sql, ('TUYA', tiempo, salida))
    
        for d in TUYA['RELES']:
            grabar = TUYA['RELES'][d].get('TABLA', True)
            if grabar != False: 
                id_rele = d
                Estado = int(datos[d]['Estado'])
                Wac = datos[d].get('Wac',0.0)
                Vac = datos[d].get('Vac',0.0)
                Wh = datos[d].get('Wh',0.0)
                   
                if DEBUG: print('Grabando....', id_rele, Estado, Wac, Vac, Wh)
        
                # Insertar un nuevo registro
                insert_sql = """
                INSERT INTO TUYA_HISTORICO (id_rele, tiempo, estado, wac, vac, wh)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (id_rele, tiempo, Estado, Wac, Vac, Wh))

        db.commit()

        
        # Actualización de la tabla TUYA_DIARIO cada 5 minutos
        if time.time() - diario_actualizacion >= 300:  # 300 segundos = 5 minutos
            if sys.stdout.isatty(): print(f'{tiempo} - Actualizacion diario')
            actualizar_diario()
            diario_actualizacion = time.time()

        t1= time.time()
        
        # Esperar para bucle de tmuestra segundos antes de la siguiente captura
        time.sleep(max(tmuestra - t1+ t0, 0))
