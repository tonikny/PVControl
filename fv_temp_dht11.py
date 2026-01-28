#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión Modernizada 2026
# Compatible con estructura existente, sin archivos adicionales

import time
import glob
import sys
import json
import os
from datetime import datetime, date
import MySQLdb

# ============================================================================
# CONFIGURACIÓN - Estos parámetros se moverán a Parametros_FV.py
# ============================================================================

# Configuración de sensores DHT (Temperatura/Humedad)
# Formato: {'nombre_sensor': {'pin': GPIO_PIN, 'type': 'DHT11'|'DHT22'}}
DHT_CONFIG = {
    # Ejemplo: 'DHT_Salon': {'pin': 4, 'type': 'DHT22'},
    # Ejemplo: 'DHT_Exterior': {'pin': 17, 'type': 'DHT22'},
    # Ejemplo: 'DHT_Invernadero': {'pin': 27, 'type': 'DHT11'},
}

# ============================================================================
# FIN CONFIGURACIÓN
# ============================================================================

# Librerias y Parametros PVControl+
basepath = '/home/pi/PVControl+/'
parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"
parametros_FV_DIST = "/home/pi/PVControl+/Parametros_FV_DIST.py"

exec(open(parametros_FV_DIST).read(), globals())
exec(open(parametros_FV).read(), globals())

# Comprobacion argumentos en comando
DEBUG = 0
if len(sys.argv) > 1:
    arg = sys.argv[-1]
    if arg == '-p1':
        DEBUG = 1
    elif arg == '-p2':
        DEBUG = 2
    elif arg == '-p3':
        DEBUG = 3
    elif arg == '-p':
        DEBUG = 100

# Variable global para estadísticas diarias
daily_stats = {}
current_date = date.today()

def init_daily_stats():
    """Inicializar estadísticas diarias desde la BD"""
    global daily_stats, current_date
    
    try:
        db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
        cursor = db.cursor()
        cursor.execute("SELECT sensores FROM equipos WHERE id_equipo = 'TEMP'")
        result = cursor.fetchone()
        
        if result and result[0]:
            data = json.loads(result[0])
            if 'daily_stats' in data:
                # Verificar si las estadísticas son del día actual
                stats_date_str = data.get('stats_date', '')
                try:
                    stats_date = datetime.strptime(stats_date_str, '%Y-%m-%d').date()
                    if stats_date == current_date:
                        daily_stats = data['daily_stats']
                        if DEBUG >= 2:
                            print(f"Estadísticas cargadas del día {stats_date_str}")
                    else:
                        daily_stats = {}
                        if DEBUG >= 1:
                            print(f"Nuevo día: {current_date}, reiniciando estadísticas")
                except:
                    daily_stats = {}
        
        cursor.close()
        db.close()
        
    except Exception as e:
        if DEBUG >= 1:
            print(f"Error cargando estadísticas: {e}")
        daily_stats = {}

def update_daily_stats(sensor_type, sensor_id, temperature, humidity=None):
    """Actualizar estadísticas diarias para un sensor"""
    global daily_stats
    
    sensor_key = f"{sensor_type}_{sensor_id}"
    
    if sensor_key not in daily_stats:
        daily_stats[sensor_key] = {
            'min_temp': temperature,
            'max_temp': temperature,
            'min_humidity': humidity,
            'max_humidity': humidity,
            'readings': 1
        }
    else:
        stats = daily_stats[sensor_key]
        
        # Actualizar temperatura
        if temperature < stats['min_temp']:
            stats['min_temp'] = temperature
        if temperature > stats['max_temp']:
            stats['max_temp'] = temperature
        
        # Actualizar humedad si existe
        if humidity is not None:
            if stats['min_humidity'] is None:
                stats['min_humidity'] = humidity
                stats['max_humidity'] = humidity
            else:
                if humidity < stats['min_humidity']:
                    stats['min_humidity'] = humidity
                if humidity > stats['max_humidity']:
                    stats['max_humidity'] = humidity
        
        stats['readings'] += 1

def read_ds18b20_sensors():
    """Leer sensores DS18B20"""
    temp_data = {}
    sensors = glob.glob("/sys/bus/w1/devices/28*/w1_slave")
    
    if sensors:
        temp_data['Ds18b20'] = {}
        Ctemp = 0
        
        for sensor in sensors:
            try:
                with open(sensor, 'r') as tfile:
                    texto = tfile.read()
                
                # Buscar línea con t=xxxxx (temperatura)
                for line in texto.split('\n'):
                    if 't=' in line:
                        temp_str = line.split('t=')[1]
                        temp = round(float(temp_str) / 1000, 2)
                        break
                else:
                    continue  # No se encontró temperatura
                
                sensor_id = os.path.basename(os.path.dirname(sensor))
                temp_data['Ds18b20'][f'Temp{Ctemp}'] = temp
                
                # Actualizar estadísticas
                update_daily_stats('DS18B20', sensor_id, temp)
                
                Ctemp += 1
                
                if DEBUG >= 2:
                    print(f"DS18B20 {sensor_id}: {temp}°C")
                
                time.sleep(0.1)
                
            except Exception as e:
                if DEBUG >= 1:
                    print(f"Error leyendo DS18B20 {sensor}: {e}")
                continue
    
    return temp_data

def read_dht_sensors():
    """Leer sensores DHT11/DHT22 usando la librería moderna"""
    temp_data = {}
    
    if not DHT_CONFIG:
        return temp_data
    
    # Intentar importar la librería moderna
    try:
        import adafruit_dht
        import board
    except ImportError:
        if DEBUG >= 1:
            print("adafruit_dht no instalado. Omite sensores DHT.")
            print("Instalar: sudo pip3 install adafruit-circuitpython-dht")
            print("También necesitas: sudo apt-get install libgpiod2")
        return temp_data
    
    # Mapeo de pines GPIO a pines de la librería board
    pin_mapping = {
        4: board.D4,
        17: board.D17,
        18: board.D18,
        22: board.D22,
        23: board.D23,
        24: board.D24,
        25: board.D25,
        27: board.D27
    }
    
    for sensor_name, config in DHT_CONFIG.items():
        try:
            pin = config['pin']
            sensor_type = config['type']
            
            # Verificar si el pin está mapeado
            if pin not in pin_mapping:
                if DEBUG >= 1:
                    print(f"Pin GPIO {pin} no soportado para DHT")
                continue
            
            board_pin = pin_mapping[pin]
            
            # Crear objeto sensor según el tipo
            if sensor_type == 'DHT11':
                sensor = adafruit_dht.DHT11(board_pin, use_pulseio=False)
            elif sensor_type == 'DHT22':
                sensor = adafruit_dht.DHT22(board_pin, use_pulseio=False)
            else:
                if DEBUG >= 1:
                    print(f"Tipo DHT no válido: {sensor_type}")
                continue
            
            # Leer sensor con reintentos
            for attempt in range(3):
                try:
                    temperature = sensor.temperature
                    humidity = sensor.humidity
                    
                    if temperature is not None and humidity is not None:
                        # Crear entrada para este tipo de sensor si no existe
                        sensor_type_key = f"DHT_{sensor_type}"
                        if sensor_type_key not in temp_data:
                            temp_data[sensor_type_key] = {}
                        
                        temp_data[sensor_type_key][sensor_name] = {
                            'temperature': round(temperature, 2),
                            'humidity': round(humidity, 2)
                        }
                        
                        # Actualizar estadísticas
                        update_daily_stats(sensor_type_key, sensor_name, temperature, humidity)
                        
                        if DEBUG >= 2:
                            print(f"{sensor_name} ({sensor_type}): {temperature}°C, {humidity}%")
                        
                        break  # Salir del bucle de reintentos
                    
                except RuntimeError as e:
                    if DEBUG >= 2:
                        print(f"Intento {attempt+1} fallado para {sensor_name}: {e}")
                    time.sleep(1)
                except Exception as e:
                    if DEBUG >= 1:
                        print(f"Error inesperado con {sensor_name}: {e}")
                    break
            
            # Limpiar sensor
            try:
                sensor.exit()
            except:
                pass
            
            time.sleep(2)  # Los DHT necesitan tiempo entre lecturas
            
        except Exception as e:
            if DEBUG >= 1:
                print(f"Error configurando DHT {sensor_name}: {e}")
            continue
    
    return temp_data

def read_cpu_temperature():
    """Leer temperatura de la CPU"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_cpu = round(float(f.read()) / 1000, 2)
        
        # Actualizar estadísticas
        update_daily_stats('CPU', 'CPU', temp_cpu)
        
        if DEBUG >= 2:
            print(f"CPU: {temp_cpu}°C")
        
        return {'Temp_cpu': temp_cpu}
        
    except Exception as e:
        if DEBUG >= 1:
            print(f"Error leyendo temperatura CPU: {e}")
        return {}

def save_to_database(temp_data):
    """Guardar datos en la base de datos"""
    try:
        db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
        cursor = db.cursor()
        
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Preparar datos para JSON
        all_data = temp_data.copy()
        
        # Agregar estadísticas diarias si existen
        if daily_stats:
            all_data['daily_stats'] = daily_stats
            all_data['stats_date'] = str(current_date)
        
        salida = json.dumps(all_data)
        
        # Actualizar registro en BD
        sql = "UPDATE equipos SET tiempo = %s, sensores = %s WHERE id_equipo = 'TEMP'"
        cursor.execute(sql, (tiempo, salida))
        db.commit()
        
        cursor.close()
        db.close()
        
        if DEBUG >= 3:
            print(f"BD actualizada: {tiempo}")
        
        return True
        
    except Exception as e:
        if DEBUG >= 1:
            print(f'Error grabacion BD tabla equipos: {e}')
        return False

def main():
    """Función principal"""
    global current_date, daily_stats
    
    # Inicializar BD si no existe registro TEMP
    try:
        db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM equipos WHERE id_equipo = 'TEMP'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO equipos (id_equipo, sensores) VALUES ('TEMP', '{}')")
            db.commit()
            if DEBUG >= 1:
                print("Registro TEMP creado en BD")
        cursor.close()
        db.close()
    except:
        pass
    
    # Inicializar estadísticas desde BD
    init_daily_stats()
    
    if DEBUG >= 1:
        print(f"Iniciando servicio - DEBUG={DEBUG}")
        if DHT_CONFIG:
            print(f"Configurados {len(DHT_CONFIG)} sensores DHT")
        else:
            print("No hay sensores DHT configurados")
    
    while True:
        try:
            # Verificar si es nuevo día
            today = date.today()
            if today != current_date:
                if DEBUG >= 1:
                    print(f"Nuevo día: {today}, reiniciando estadísticas")
                current_date = today
                daily_stats = {}
            
            # Leer todos los sensores
            temp_data = {}
            
            # 1. Sensores DS18B20
            ds18b20_data = read_ds18b20_sensors()
            temp_data.update(ds18b20_data)
            
            # 2. Sensores DHT
            dht_data = read_dht_sensors()
            temp_data.update(dht_data)
            
            # 3. Temperatura CPU
            cpu_data = read_cpu_temperature()
            temp_data.update(cpu_data)
            
            # Mostrar datos en modo debug
            if DEBUG >= 1 and temp_data:
                print("=" * 40)
                print(f"Datos leídos ({time.strftime('%H:%M:%S')}):")
                for key, value in temp_data.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, dict):
                                print(f"    {subkey}: Temp={subvalue.get('temperature', 'N/A')}°C, Hum={subvalue.get('humidity', 'N/A')}%")
                            else:
                                print(f"    {subkey}: {subvalue}°C")
                    else:
                        print(f"  {key}: {value}°C")
                
                if daily_stats:
                    print("\n  Estadísticas diarias:")
                    for sensor_key, stats in daily_stats.items():
                        print(f"    {sensor_key}:")
                        print(f"      Temp: Min={stats['min_temp']}°C, Max={stats['max_temp']}°C")
                        if stats['min_humidity'] is not None:
                            print(f"      Hum: Min={stats['min_humidity']}%, Max={stats['max_humidity']}%")
                        print(f"      Lecturas: {stats['readings']}")
                print("=" * 40)
            
            # Guardar en BD
            if temp_data:
                save_to_database(temp_data)
            
            # Esperar entre lecturas
            time.sleep(10)
            
        except KeyboardInterrupt:
            if DEBUG >= 1:
                print("\nServicio detenido por usuario")
            break
            
        except Exception as e:
            if DEBUG >= 1:
                print(f"Error en bucle principal: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()