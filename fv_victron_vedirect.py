#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import serial
import json
import subprocess
import MySQLdb
import colorama
from colorama import Fore, Back, Style
colorama.init()
from threading import Thread, Event
import logging
import glob

###### Configuración ###########################################################
# Configuración de equipos (debería estar en Parametros_FV.py)

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


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        #logging.FileHandler('victron_vedirect.log'),
        logging.StreamHandler()
    ]
)

###############################################################################

# Importar configuraciones
try:
    from Parametros_FV_DIST import *
    from Parametros_FV import *
except ImportError as e:
    logging.error(f"Error importando configuraciones: {e}")
    sys.exit(1)

# Verificar configuración
try:
    equipos_activos = {n: c for n, c in VICTRON_VEDIRECT.items() if c.get('usar', 0) == 1}
    if not equipos_activos:
        logging.info("No hay equipos configurados para monitorear")
        subprocess.run(['sudo', 'systemctl', 'stop', 'fv_victron_vedirect'], check=True)
        sys.exit(0)
except NameError:
    logging.error("Configuración VICTRON_VEDIRECT no encontrada")
    sys.exit(1)

# Mostrar puertos disponibles
puertos_disponibles = glob.glob('/dev/ttyUSB*')
logging.info(f"Puertos serie detectados: {puertos_disponibles}")

# Configuración de debug
DEBUG = 1 if '-p' in sys.argv else 0

def procesar_dato(data, dct):
    """Procesa los datos recibidos del dispositivo Victron"""
    try:
        if len(data) == 2:
            key, value = data[0], data[1]
            
            # Conversión de valores
            conversions = {
                b'V': ('Vbat', 1/1000),
                b'VPV': ('Vplaca', 1/1000),
                b'PPV': ('Wplaca', 1),
                b'I': ('Ibat', 1/1000),
                b'VM': ('Vm', 1/1000),
                b'T': ('Temp', 1),
                b'SOC': ('SOC', 1/10)
            }
            
            if key in conversions:
                name, factor = conversions[key]
                dct[name] = float(value) * factor
            elif key.startswith(b'H'):
                dct[key.decode('utf-8')] = float(value)
            elif key == b'CS':
                estados = {0: 'OFF', 2: 'FALLO', 3: 'BULK', 4: 'ABS', 5: 'FLOT'}
                dct['CS'] = estados.get(int(value), 'DESCONOCIDO')
            elif key != b'Checksum':
                dct[key.decode('utf-8')] = value.decode('utf-8')
                
            return key == b'Checksum'
    except Exception as e:
        logging.error(f"Error procesando dato: {e}")
    return False

def worker(nombre, config, stop_event):
    """Hilo de trabajo para cada dispositivo Victron"""
    retry_delay = 1
    max_delay = 30
    serial_conn = None
    
    while not stop_event.is_set():
        try:
            # Configuración de conexión serie robusta
            serial_conn = serial.Serial(
                port=config['dev'],
                baudrate=19200,
                timeout=5,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            logging.info(f"{nombre}: Conexión establecida con {config['dev']}")
            retry_delay = 1  # Resetear delay tras conexión exitosa
            
            # Conexión a BD por worker
            db_conn = MySQLdb.connect(
                host=servidor,
                user=usuario,
                passwd=clave,
                db=basedatos
            )
            cursor = db_conn.cursor()
            
             # 1. VERIFICAR/CREAR REGISTRO INICIAL
            try:
                cursor.execute(
                    "INSERT INTO equipos (id_equipo, tiempo, sensores) VALUES (%s, %s, %s)"
                    "ON DUPLICATE KEY UPDATE id_equipo=id_equipo",
                    (nombre.upper(), time.strftime("%Y-%m-%d %H:%M:%S"), '{}')
                )
                db_conn.commit()
                logging.info(f"Registro para {nombre} verificado/creado")
            except Exception as e:
                logging.error(f"Error inicializando registro para {nombre}: {e}")
                db_conn.rollback()
                    
            # Variables de estado
            suma = 0
            nfallos = 0
            dct = {}
            ultimo_registro = time.time()
            
            while not stop_event.is_set():
                try:
                    # Lectura con timeout nativo de PySerial
                    raw_data = serial_conn.readline()
                    if not raw_data:
                        raise serial.SerialTimeoutException("Timeout de lectura")
                    
                    #print(f'raw_data:{raw_data}')
                    
                    # CÁLCULO DE CHECKSUM
                    sum_part = (sum(raw_data) % 256) if sum(raw_data) != 23 else 0
                    suma = (suma + sum_part) % 256
                    
                    #print(f'sum_part:{sum_part} --->  suma:{suma}')
                    
                    # Procesamiento del dato
                    data = raw_data.strip(b'\r\n').split(b'\t')
                    
                    #print(f'data:{data}')
                    
                    registro_completo = procesar_dato(data, dct)
                    
                                       
                    #print(f'completo:{registro_completo} - suma:{suma} ---> dct:{dct}')
                    
                    if registro_completo:
                        if DEBUG:
                            print()
                            print(Fore.GREEN, nombre.upper(), dct)                    
                            print('=' * 80)
                            print (f'suma:{suma}')
                            print()
                            
                        if suma == 0:
                            # Campos calculados
                            try:
                                dct['Iplaca'] = round(dct['Wplaca'] / dct['Vbat'], 2)
                                dct['Nfallos'] = nfallos
                            except KeyError:
                                pass
                            
                            # Guardar en BD
                            try:
                                tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
                                cursor.execute(
                                    "UPDATE equipos SET tiempo=%s, sensores=%s WHERE id_equipo=%s",
                                    (tiempo, json.dumps(dct), nombre.upper())
                                )
                                db_conn.commit()
                                    
                            except Exception as e:
                                logging.error(f"Error {nombre} actualizando BD: {e}")
                            
                            dct = {}  # Resetear para nuevo registro
                            ultimo_registro = time.time()
                        else:
                            suma = 0
                            nfallos += 1
                            if DEBUG: logging.warning(f"{nombre}: Fallo de checksum (total {nfallos})")
                    
                    # Verificar timeout de inactividad
                    if time.time() - ultimo_registro > 30:
                        raise serial.SerialException("Timeout de inactividad")
                        
                except serial.SerialTimeoutException:
                    logging.warning(f"{nombre}: Timeout en lectura")
                    break
                except Exception as e:
                    logging.error(f"Error {nombre} en bucle principal: {e}")
                    break
                    
        except serial.SerialException as e:
            logging.error(f"Error {nombre} en conexión serie: {e}")
        except MySQLdb.Error as e:
            logging.error(f"Error {nombre} en conexión BD: {e}")
        except Exception as e:
            logging.error(f"Error inesperado {nombre}: {e}")
        finally:
            # Limpieza de recursos
            if serial_conn and serial_conn.is_open:
                serial_conn.close()
            if 'db_conn' in locals() and db_conn.open:
                db_conn.close()
            
            # Espera exponencial antes de reintentar
            if not stop_event.is_set():
                logging.info(f"Reintentando {nombre} en {retry_delay} segundos...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)

def main():
    """Función principal"""
    print(Fore.YELLOW + f"\nIniciando monitorización para {len(equipos_activos)} equipos\n")
    
    # Evento para controlar la parada
    stop_event = Event()
    
    # Crear e iniciar hilos
    threads = []
    for nombre, config in equipos_activos.items():
        t = Thread(
            target=worker,
            args=(nombre, config, stop_event),
            daemon=True
        )
        t.start()
        threads.append(t)
    
    # Manejar señal de parada
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "\nDeteniendo todos los hilos...")
        stop_event.set()
        for t in threads:
            t.join(timeout=2)
        print(Fore.GREEN + "Sistema detenido correctamente")

if __name__ == "__main__":
    main()
