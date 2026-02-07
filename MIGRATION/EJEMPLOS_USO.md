# Ejemplos de Uso - Nuevo Sistema

## 1. Control de Servicios

### Uso Básico con Booleano

```python
from fv_control_servicio import controlar_servicio

# Simple: pasar booleano directamente
hay_equipos_activos = True
controlar_servicio("mi_servicio", hay_equipos_activos)
# Si hay_equipos_activos es False, el servicio se detiene automáticamente
```

### Verificar Equipos en Diccionario

```python
from helpers.cargar_parametros import cargar_parametros
from fv_control_servicio import controlar_servicio

# Cargar configuración
ADS = cargar_parametros("ADS")

# Opción 1: Calcular manualmente
hay_ads = sum(1 for v in ADS.values() if v.get("usar", False)) > 0
controlar_servicio("fv_ads", hay_ads)

# Opción 2: Usar función helper
from fv_control_servicio import verificar_equipos_activos
hay_ads = verificar_equipos_activos(ADS, clave_usar="usar")
controlar_servicio("fv_ads", hay_ads)
```

### Verificar Parámetro Boolean

```python
from helpers.cargar_parametros import cargar_parametros
from fv_control_servicio import controlar_servicio, verificar_parametro_boolean

# Cargar parámetro que puede ser bool, int, o str
usar_mqtt = cargar_parametros("usar_mqtt")

# Convertir a booleano de forma segura
debe_ejecutar = verificar_parametro_boolean(usar_mqtt)
controlar_servicio("fv_mqtt", debe_ejecutar)
```

## 2. Gestor de Base de Datos

### Uso Básico

```python
from helpers.gestor_bd import GestorBD
import time

# Crear gestor (auto-importa configuración de Parametros_FV.py)
gestor = GestorBD()

# Guardar datos con diccionario
tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
datos = {
    "Vbat": 48.5,
    "Ibat": -5.2,
    "SOC": 85
}
gestor.guardar_datos_equipo_dict("INVERTER1", tiempo, datos)

# Cerrar cuando termine
gestor.cerrar()
```

### Uso con Context Manager (Recomendado)

```python
from helpers.gestor_bd import GestorBD
import time

tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
datos = {"Vbat": 48.5, "SOC": 85}

# Automáticamente cierra la conexión al salir
with GestorBD() as gestor:
    # Insertar equipo si no existe
    gestor.insertar_equipo_si_falta("INVERTER1")
    
    # Guardar datos
    gestor.guardar_datos_equipo_dict("INVERTER1", tiempo, datos)
```

### Guardar Datos JSON Directamente

```python
from helpers.gestor_bd import GestorBD
import json
import time

with GestorBD() as gestor:
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    datos = {"Ppv": 1200, "Pac": 800}
    
    # Opción 1: Usar método que acepta dict
    gestor.guardar_datos_equipo_dict("INVERTER1", tiempo, datos)
    
    # Opción 2: Serializar manualmente
    json_str = json.dumps(datos)
    gestor.guardar_datos_equipo("INVERTER1", tiempo, json_str)
```

### Recuperar Datos

```python
from helpers.gestor_bd import GestorBD

with GestorBD() as gestor:
    # Obtener datos de equipo
    datos = gestor.obtener_datos_equipo("INVERTER1")
    
    if datos:
        print(f"Tiempo: {datos['tiempo']}")
        print(f"Sensores: {datos['sensores']}")
        print(f"Vbat: {datos['sensores'].get('Vbat')}")
    else:
        print("Equipo no encontrado")
```

### Transacciones

```python
from helpers.gestor_bd import GestorBD
import time

with GestorBD() as gestor:
    try:
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Múltiples operaciones
        gestor.guardar_datos_equipo_dict("INV1", tiempo, {"P": 1000})
        gestor.guardar_datos_equipo_dict("INV2", tiempo, {"P": 1200})
        
        # Confirmar todas las operaciones
        gestor.confirmar()
        
    except Exception as e:
        # Revertir en caso de error
        gestor.revertir()
        print(f"Error: {e}")
```

## 3. Cargar Parámetros con Caché

### Uso Básico

```python
from helpers.cargar_parametros import cargar_parametros

# Cargar un parámetro
servidor = cargar_parametros("servidor")
print(f"Servidor: {servidor}")

# Cargar múltiples parámetros
servidor, usuario, clave = cargar_parametros("servidor", "usuario", "clave")

# Cargar diccionario de configuración
ADS = cargar_parametros("ADS")
RS485 = cargar_parametros("RS485")
```

### Forzar Recarga (Limpiar Caché)

```python
from helpers.cargar_parametros import cargar_parametros, limpiar_cache

# Primera carga (lee archivos)
config1 = cargar_parametros("ADS")

# Segunda carga (usa caché si archivos no han cambiado)
config2 = cargar_parametros("ADS")

# Modificar archivo Parametros_FV.py externamente...

# Forzar recarga aunque el mtime no haya cambiado
limpiar_cache()
config3 = cargar_parametros("ADS")  # Recarga desde disco
```

### Manejo de Parámetros Faltantes

```python
from helpers.cargar_parametros import cargar_parametros

# Si el parámetro no existe, devuelve None
parametro_inexistente = cargar_parametros("NO_EXISTE")

if parametro_inexistente is None:
    print("Parámetro no encontrado, usando valor por defecto")
    parametro_inexistente = "valor_por_defecto"
```

## 4. Script Completo de Ejemplo

### Servicio Genérico de Captura

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de servicio genérico usando el nuevo sistema
"""

import time
import sys
from helpers.cargar_parametros import cargar_parametros
from helpers.gestor_bd import GestorBD
from fv_control_servicio import controlar_servicio

# Nombre del servicio
NOMBRE_SERVICIO = "mi_servicio"

# Cargar configuración
config = cargar_parametros("MI_EQUIPOS")

# Verificar si hay equipos activos
equipos_activos = [
    nombre for nombre, cfg in config.items() 
    if cfg.get("usar", False)
]

# Controlar ejecución del servicio
debe_ejecutar = len(equipos_activos) > 0
controlar_servicio(NOMBRE_SERVICIO, debe_ejecutar)

# Si llegamos aquí, el servicio debe ejecutarse
print(f"Iniciando {NOMBRE_SERVICIO}...")
print(f"Equipos activos: {equipos_activos}")

# Crear gestor de BD
with GestorBD() as gestor:
    # Crear registros de equipos
    for equipo in equipos_activos:
        gestor.insertar_equipo_si_falta(equipo)
    
    # Bucle principal
    while True:
        try:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            
            for equipo in equipos_activos:
                # Capturar datos (ejemplo simulado)
                datos = {
                    "valor1": 100,
                    "valor2": 200,
                    "timestamp": tiempo
                }
                
                # Guardar en BD
                gestor.guardar_datos_equipo_dict(equipo, tiempo, datos)
                print(f"{equipo}: {datos}")
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print(f"\nFinalizando {NOMBRE_SERVICIO}...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
```

### Migrar Script Existente

```python
# ANTES (usando db_manager):
from helpers.db_manager import DatabaseManager

db = DatabaseManager()
db.insert_equipment_if_missing("EQUIPO1")
db.save_equipment_data_dict("EQUIPO1", tiempo, datos)
db.commit()
db.close()

# DESPUÉS (usando gestor_bd):
from helpers.gestor_bd import GestorBD

with GestorBD() as gestor:
    gestor.insertar_equipo_si_falta("EQUIPO1")
    gestor.guardar_datos_equipo_dict("EQUIPO1", tiempo, datos)
    gestor.confirmar()
    # El cierre es automático con el context manager
```

## 5. Patrones Comunes

### Patrón: Captura Periódica con Control

```python
from helpers.cargar_parametros import cargar_parametros
from helpers.gestor_bd import GestorBD
from fv_control_servicio import controlar_servicio
import time

# Configuración
CONFIG_KEY = "MIS_SENSORES"
SERVICIO = "fv_sensores"
INTERVALO = 5  # segundos

# Verificar y controlar
config = cargar_parametros(CONFIG_KEY)
debe_ejecutar = any(v.get("usar") for v in config.values())
controlar_servicio(SERVICIO, debe_ejecutar)

# Captura
with GestorBD() as gestor:
    while True:
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        for nombre, cfg in config.items():
            if cfg.get("usar"):
                datos = capturar_datos(cfg)  # Tu función de captura
                gestor.guardar_datos_equipo_dict(nombre, tiempo, datos)
        time.sleep(INTERVALO)
```

### Patrón: Múltiples Procesos

```python
import multiprocessing
from helpers.gestor_bd import GestorBD
import time

def proceso_captura(nombre_equipo, config):
    """Cada equipo en su propio proceso"""
    with GestorBD() as gestor:
        gestor.insertar_equipo_si_falta(nombre_equipo)
        
        while True:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            datos = capturar_datos(config)
            gestor.guardar_datos_equipo_dict(nombre_equipo, tiempo, datos)
            time.sleep(config["intervalo"])

# Iniciar procesos
equipos_activos = [("EQ1", cfg1), ("EQ2", cfg2)]
for nombre, config in equipos_activos:
    p = multiprocessing.Process(
        target=proceso_captura, 
        args=(nombre, config)
    )
    p.start()
```

## 6. Consejos y Mejores Prácticas

### ✅ Siempre usar Context Manager
```python
# BIEN ✅
with GestorBD() as gestor:
    gestor.guardar_datos_equipo_dict(...)

# EVITAR ❌ (fácil olvidar cerrar)
gestor = GestorBD()
gestor.guardar_datos_equipo_dict(...)
gestor.cerrar()  # Fácil de olvidar
```

### ✅ Verificar Booleanos de Forma Segura
```python
from fv_control_servicio import verificar_parametro_boolean

# BIEN ✅ - Maneja diferentes tipos
valor = verificar_parametro_boolean(config.get("usar"))

# MENOS ROBUSTO ❌
valor = bool(config.get("usar"))  # No maneja strings "true", etc.
```

### ✅ Usar Caché Automático
```python
# El caché funciona automáticamente
# No necesitas hacer nada especial

# Solo si modificas archivos desde el programa:
import os
os.utime(ruta_parametros, None)  # Actualiza mtime
# La próxima llamada a cargar_parametros() recargará
```

### ✅ Manejo de Errores
```python
from helpers.gestor_bd import GestorBD
import MySQLdb

try:
    with GestorBD() as gestor:
        gestor.guardar_datos_equipo_dict(...)
except MySQLdb.Error as e:
    print(f"Error de BD: {e}")
except Exception as e:
    print(f"Error general: {e}")
```
