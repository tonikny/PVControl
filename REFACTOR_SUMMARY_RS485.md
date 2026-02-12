# Resumen de Refactorización: servicios/fv_rs485.py

## Objetivo
Refactorizar `servicios/fv_rs485.py` para usar los módulos helpers (gestor_parametros, gestor_bd, gestor_logs, gestor_mqtt, gestor_telegram, control_servicio) manteniendo el comportamiento actual de adaptar/exec intacto.

**IMPORTANTE**: Este archivo es una **librería** que se importa como módulo Python normal, con llamadas a funciones. NO usa `exec()` ni `eval()`.

## Cambios Realizados

### 1. Estructura Orientada a Objetos - Clase CapturadorRS485
- ✅ Convertido a clase orientada a objetos `CapturadorRS485`
- ✅ NO tiene función `main()` ni `if __name__ == "__main__"`
- ✅ Se instancia con `capturador = CapturadorRS485(nombre_equipo, debug=False)`
- ✅ Función de conveniencia `iniciar_captura(nombre_equipo, debug=False)` para uso simplificado
- ✅ Método `ejecutar()` que contiene el bucle principal `while True`

### 2. Carga de Configuración - SIN eval() ni exec()
- ✅ `self.EQUIPO = self.gp.leer_parametros(self.nombre_equipo)` usando GestorParametros
- ✅ NO se usa `eval(NEQUIPO)` en ningún lugar
- ✅ NO se usa `exec()` para cargar la librería
- ✅ Carga inicial en `__init__`: `self.cargar_configuracion()`
- ✅ Recarga automática cada 300 segundos: `self.recargar_configuracion()`
- ✅ GestorParametros maneja archivos Parametros_FV.py y Parametros_FV_DIST.py automáticamente

### 3. Logging (GestorLogs)
- ✅ Reemplazado `print` con `self.log.debug/info/warning/error/manual`
- ✅ Niveles de debug configurables mediante argumento `debug` o `-p` en línea de comandos
- ✅ Mantenido indicador de progreso `print(f'{nombre_equipo[-1]}')` solo cuando no está en modo debug

### 4. Base de Datos (GestorBD)
- ✅ `self.gestor_bd = GestorBD()` para conexión automática
- ✅ `self.gestor_bd.guardar_datos_equipo_dict(nombre_equipo, tiempo, datos)` en lugar de SQL manual
- ✅ `self.gestor_bd.insertar_equipo_si_falta(nombre_equipo)` para inicializar equipos
- ✅ Eliminado uso directo de `MySQLdb` y consultas SQL vulnerables

### 5. MQTT (GestorMQTT)
- ✅ `self.gestor_mqtt = GestorMQTT(depurar=debug)` para conexión
- ✅ `self.gestor_mqtt.suscribir_equipos(equipos_activos)` en lugar de suscripciones manuales
- ✅ `self.gestor_mqtt.conectar()` para iniciar conexión
- ✅ `self.gestor_mqtt.obtener_comando_pendiente()` en lugar de `comando_mqtt` global
- ✅ Eliminadas funciones `on_connect`, `on_disconnect`, `on_message` manuales

### 6. Telegram (GestorTelegram)
- ✅ `self.gestor_telegram = GestorTelegram()` para inicialización
- ✅ `self.gestor_telegram.enviar_mensaje_inicio(nombre_equipo)` al arrancar
- ✅ `self.gestor_telegram.enviar_mensaje_seguro(msg)` en `listar_parametros` y `escribir_registro`
- ✅ `self.gestor_telegram.esta_habilitado()` para verificar disponibilidad
- ✅ Eliminados `telebot` y `timeout_decorator` directos

### 7. Control de Servicio (control_servicio)
- ✅ `controlar_servicio(f"fv_rs485_{nombre_equipo}", hay_activos)` para detener servicio si no hay equipos activos
- ✅ Cálculo de equipos activos: `equipos_activos = [e for e in self.EQUIPO if self.EQUIPO[e].get('usar', 0) == 1 and e != 'COMANDOS']`

### 8. Lógica adaptar/exec - MANTENIDA SIN CAMBIOS
- ✅ `leer_registro()`: sin cambios en lógica de conversión
- ✅ `leer_registros()`: `exec(ejecutar)` intacto (necesario para interpretación dinámica)
- ✅ `listar_parametros()`: `exec(ejecutar)` intacto
- ✅ `leer_equipo()`: `exec(ejecutar)` intacto
- ✅ Diccionario `datos` construido exactamente igual
- ✅ Variable `d` usada igual que en el original

**Nota**: Se mantiene `exec()` para la lógica de `adaptar` porque es necesario para interpretar dinámicamente las reglas de conversión definidas en los archivos de parámetros. Este es el único uso de `exec()` y es parte esencial de la funcionalidad.

### 9. Comentarios en Español
- ✅ Todos los comentarios en español
- ✅ Docstrings en español
- ✅ Mensajes de error y logging en español

## Cómo Se Usa (Patrón de Módulo)

### Desde scripts como fv_srne.py:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Añadir directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from servicios.fv_rs485 import iniciar_captura

if __name__ == "__main__":
    # Iniciar captura para el equipo SRNE
    iniciar_captura('SRNE', debug=('-p' in sys.argv))
```

### Ejemplo de configuración en Parametros_FV.py:
```python
# Configuración para equipo SRNE
SRNE = {
    'SRNE1': {
        'usar': 1,
        'dev': '/dev/ttyUSB0',
        'baudrate': 9600,
        'id_modbus': 1,
        'tiempo_captura': 5,
    },
    'COMANDOS': {
        'SOC': {'reg': 0x0100},
        'Vbat': {'reg': 0x0101, 'dec': 1},
        'Iplaca': {'reg': 0x0102, 'dec': 2},
        # ... más comandos
    }
}
```

### Uso avanzado con la clase directamente:
```python
from servicios.fv_rs485 import CapturadorRS485

# Crear instancia del capturador
capturador = CapturadorRS485('SRNE', debug=True)

# Ejecutar bucle principal (se mantiene en while True)
capturador.ejecutar()
```

## Argumentos de Línea de Comandos

Los argumentos se pasan al script que llama a fv_rs485.py (ej. fv_srne.py):

```bash
python3 fv_srne.py        # Ejecución normal
python3 fv_srne.py -p     # Modo debug
```

## Funciones Disponibles

### Función de conveniencia:
- `iniciar_captura(nombre_equipo, debug=False)`: Función simplificada para iniciar captura

### Métodos de la clase CapturadorRS485:
- `__init__(nombre_equipo, debug=False)`: Constructor que inicializa el capturador
- `cargar_configuracion()`: Carga configuración inicial desde Parametros_FV.py
- `recargar_configuracion()`: Recarga configuración periódicamente
- `leer_registro(equipo, comando)`: Lectura de comando individual
- `leer_registros(equipo)`: Lectura múltiple usando rangos
- `listar_parametros(equipo)`: Lista parámetros vía Telegram
- `escribir_registro(equipo, mensaje)`: Escribe registro
- `leer_equipo(equipo)`: Bucle principal de lectura
- `ejecutar()`: Ejecuta el bucle principal del capturador

## Compatibilidad

- ✅ Mantiene compatibilidad con archivos de configuración existentes (Parametros_FV.py)
- ✅ Mantiene compatibilidad con adaptar/exec de equipos existentes
- ✅ Mantiene estructura de diccionario EQUIPO y COMANDOS
- ✅ Mantiene lógica de modbus/RS485 sin cambios
- ✅ Mantiene lógica de orden de bytes (orden_bytes)
- ✅ Mantiene lógica de simulación (simular_datos)
- ✅ **NO usa exec() para cargar el módulo** - se importa como módulo Python normal
- ✅ **NO usa eval()** - se usa GestorParametros para cargar configuración

## Mejoras de Seguridad

- ✅ Eliminadas vulnerabilidades de inyección SQL (usando consultas parametrizadas)
- ✅ Eliminado uso de `eval()` para cargar configuración
- ✅ Eliminado uso de `exec()` para cargar módulos
- ✅ Mejor manejo de errores con try/except en todos los gestores
- ✅ Timeout controlado en Telegram
- ✅ Reintento automático de conexión MQTT y BD

## Mejoras de Mantenibilidad

- ✅ Código modular y reutilizable usando helpers
- ✅ Separación de preocupaciones (logging, BD, MQTT, Telegram)
- ✅ Auto-recarga de configuración sin reiniciar servicio
- ✅ Mejor documentación y comentarios en español
- ✅ Tipos de datos explícitos en funciones de helpers
- ✅ Estructura orientada a objetos para mejor encapsulación
- ✅ Fácil de probar y mantener

## Diferencias con Versión Anterior

A diferencia de la versión anterior que usaba `exec()` para cargar el módulo:

1. **Importación como módulo normal**: `from servicios.fv_rs485 import iniciar_captura`
2. **NO eval(NEQUIPO)**: Se usa `GestorParametros.leer_parametros(nombre_equipo)`
3. **Función de conveniencia**: `iniciar_captura()` simplifica el uso
4. **Clase encapsulada**: Toda la lógica está en la clase `CapturadorRS485`
5. **Métodos públicos**: Funcionalidad expuesta a través de métodos, no variables globales

## Único Uso de exec()

El único uso de `exec()` en el código es para la lógica de `adaptar` en los comandos de equipos:

```python
# En leer_registros(), listar_parametros(), y leer_equipo():
if tipo == 'adaptar':
    ejecutar = '\n'.join(self.comandos[comando]['adaptar'])
    exec(ejecutar)
```

Esto es **necesario** porque las reglas de adaptación se definen como cadenas de código Python en los archivos de parámetros (Parametros_FV.py) para permitir conversiones personalizadas por cada equipo. Este `exec()` es seguro porque:
1. El código a ejecutar proviene del archivo de configuración controlado por el usuario
2. Solo se ejecuta en contexto de interpretación de datos, no para cargar módulos
3. Es parte esencial de la funcionalidad del sistema

## Pruebas Realizadas

- ✅ Sintaxis Python correcta (py_compile exitoso)
- ✅ Verificación de que NO usa eval() para cargar configuración
- ✅ Verificación de que NO usa exec() para cargar módulo
- ✅ Verificación de que se puede importar como módulo normal
- ✅ Verificación de lógica adaptar/exec intacta (solo para datos)
- ✅ Estructura orientada a objetos correcta
