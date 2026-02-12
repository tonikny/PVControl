# Resumen de Refactorización: servicios/fv_rs485.py

## Objetivo
Refactorizar `servicios/fv_rs485.py` para usar los módulos helpers (gestor_parametros, gestor_bd, gestor_logs, gestor_mqtt, gestor_telegram, control_servicio) manteniendo el comportamiento actual de adaptar/exec intacto.

**IMPORTANTE**: Este archivo es una **librería** que se carga vía `exec()` desde scripts como `fv_srne.py`, no un programa ejecutable.

## Cambios Realizados

### 1. Estructura General
- ✅ Mantiene estructura de librería cargable vía `exec()`
- ✅ NO tiene función `main()` ni `if __name__ == "__main__"`
- ✅ Ejecuta código al nivel de módulo cuando se carga
- ✅ Espera que `NEQUIPO` esté definido en el contexto del llamante

### 2. Logging (GestorLogs)
- ✅ Reemplazado `print` con `log.debug/info/warning/error`
- ✅ Niveles de debug configurables mediante argumentos:
  - `-p`: DEBUG
  - `-p2`: INFO
  - `-p1`: WARNING
  - (default): ERROR
- ✅ Mantenido indicador de progreso `print(f'{nombre_equipo[-1]}')` solo cuando no está en modo debug
- ✅ `log.manual()` para mensajes importantes con formato especial

### 3. Parámetros (GestorParametros)
- ✅ `GestorParametros(check_interval=300)` para carga automática
- ✅ Carga inicial: `EQUIPO = eval(NEQUIPO)` (NEQUIPO debe estar en globals)
- ✅ Recarga automática cada 300 segundos usando `gp.leer_parametros(NEQUIPO)`
- ✅ Detección de cambios de versión con `gp.version()`
- ✅ `NEQUIPO` se define en scripts como `fv_srne.py`, `fv_anenji.py`, etc.

### 4. Base de Datos (GestorBD)
- ✅ `gestor_bd = GestorBD()` para conexión automática
- ✅ `gestor_bd.guardar_datos_equipo_dict(nombre_equipo, tiempo, datos)` en lugar de SQL manual
- ✅ `gestor_bd.insertar_equipo_si_falta(nombre_equipo)` para inicializar equipos
- ✅ Eliminado uso directo de `MySQLdb` y consultas SQL vulnerables

### 5. MQTT (GestorMQTT)
- ✅ `gestor_mqtt = GestorMQTT(depurar=(DEBUG == 1))` para conexión
- ✅ `gestor_mqtt.suscribir_equipos(equipos_activos)` en lugar de suscripciones manuales
- ✅ `gestor_mqtt.conectar()` para iniciar conexión
- ✅ `gestor_mqtt.obtener_comando_pendiente()` en lugar de `comando_mqtt` global
- ✅ Eliminadas funciones `on_connect`, `on_disconnect`, `on_message` manuales

### 6. Telegram (GestorTelegram)
- ✅ `gestor_telegram = GestorTelegram()` para inicialización
- ✅ `gestor_telegram.enviar_mensaje_inicio(NEQUIPO)` al arrancar
- ✅ `gestor_telegram.enviar_mensaje_seguro(msg)` en `listar_parametros` y `escribir_registro`
- ✅ `gestor_telegram.esta_habilitado()` para verificar disponibilidad
- ✅ Eliminados `telebot` y `timeout_decorator` directos

### 7. Control de Servicio (control_servicio)
- ✅ `controlar_servicio("fv_rs485", hay_activos)` para detener servicio si no hay equipos activos
- ✅ Cálculo de equipos activos: `equipos_activos = [e for e in EQUIPO if EQUIPO[e].get('usar', 0) == 1 and e != 'COMANDOS']`

### 8. Lógica adaptar/exec - MANTENIDA SIN CAMBIOS
- ✅ `leer_registro()`: sin cambios en lógica de conversión
- ✅ `leer_registros()`: `exec(ejecutar)` intacto en línea 177
- ✅ `listar_parametros()`: `exec(ejecutar)` intacto en línea 223
- ✅ `leer_equipo()`: `exec(ejecutar)` intacto en línea 352
- ✅ Diccionario `datos` construido exactamente igual
- ✅ Variable `d` usada igual que en el original

### 9. Comentarios en Español
- ✅ Todos los comentarios en español
- ✅ Docstrings en español
- ✅ Mensajes de error y logging en español

## Cómo Se Usa (Patrón Original)

### Desde scripts como fv_srne.py:
```python
# 1. Definir configuración del equipo en Parametros_FV.py
SRNE = {
    'SRNE1': {'usar':1, 'dev': '/dev/ttyUSB0', ...},
    'COMANDOS': {...}
}

# 2. Definir NEQUIPO en el script
NEQUIPO = 'SRNE'

# 3. Cargar la librería vía exec
exec(open("/home/pi/PVControl+/servicios/fv_rs485.py").read(), globals())
```

### Ejemplo completo (fv_srne.py):
```python
# -*- coding: utf-8 -*-

# Definir configuración del equipo
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
        # ... más comandos
    }
}

# Ejecutar control de servicio
servicio = 'fv_srne'
NEQUIPO = 'SRNE'

# Cargar librería fv_rs485 vía exec
exec(open("/home/pi/PVControl+/servicios/fv_rs485.py").read(), globals())
```

## Argumentos de Línea de Comandos

Los argumentos se pasan al script que llama a fv_rs485.py (ej. fv_srne.py):

```bash
python3 fv_srne.py -p    # DEBUG level
python3 fv_srne.py -p2   # INFO level
python3 fv_srne.py -p1   # WARNING level
python3 fv_srne.py -s    # Simular datos
```

## Funciones Disponibles

Cuando se carga vía `exec()`, estas funciones quedan disponibles en el namespace:

- `leer_registro(equipo, comando)`: Lectura de comando individual
- `leer_registros(equipo)`: Lectura múltiple usando rangos
- `listar_parametros(equipo)`: Lista parámetros vía Telegram
- `escribir_registro(equipo, mensaje)`: Escribe registro
- `leer_equipo(equipo)`: Bucle principal de lectura

## Compatibilidad

- ✅ Mantiene compatibilidad con archivos de configuración existentes (Parametros_FV.py)
- ✅ Mantiene compatibilidad con adaptar/exec de equipos existentes
- ✅ Mantiene estructura de diccionario EQUIPO y COMANDOS
- ✅ Mantiene lógica de modbus/RS485 sin cambios
- ✅ Mantiene lógica de orden de bytes (orden_bytes)
- ✅ Mantiene lógica de simulación (simular_datos)
- ✅ Mantiene patrón de carga vía `exec()` como el original

## Mejoras de Seguridad

- ✅ Eliminadas vulnerabilidades de inyección SQL (usando consultas parametrizadas)
- ✅ Mejor manejo de errores con try/except en todos los gestores
- ✅ Timeout controlado en Telegram
- ✅ Reintento automático de conexión MQTT y BD

## Mejoras de Mantenibilidad

- ✅ Código modular y reutilizable usando helpers
- ✅ Separación de preocupaciones (logging, BD, MQTT, Telegram)
- ✅ Auto-recarga de configuración sin reiniciar servicio
- ✅ Mejor documentación y comentarios en español
- ✅ Tipos de datos explícitos en funciones de helpers

## Diferencias con Versión Ejecutable

A diferencia de una versión con `main()`, esta versión:

1. **NO tiene función main()**: Ejecuta código directamente al cargar
2. **NO usa if __name__ == "__main__"**: No está diseñada para ejecución directa
3. **Depende de NEQUIPO**: Espera que la variable `NEQUIPO` esté definida en el contexto del llamante
4. **Mantiene el bucle while True**: El bucle principal se ejecuta inmediatamente al cargar

Esto es intencional para mantener compatibilidad con el patrón original de `exec()`.

## Pruebas Realizadas

- ✅ Sintaxis Python correcta (py_compile exitoso)
- ✅ Estructura de librería cargable vía exec()
- ✅ Verificación de que no tiene main() ni guardias de ejecución
- ✅ Verificación de lógica adaptar/exec intacta
- ✅ Compatibilidad con scripts existentes (fv_srne.py, fv_anenji.py)
