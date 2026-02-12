# Resumen de Refactorización: servicios/fv_rs485.py

## Objetivo
Refactorizar `servicios/fv_rs485.py` para usar los módulos helpers (gestor_parametros, gestor_bd, gestor_logs, gestor_mqtt, gestor_telegram, control_servicio) manteniendo el comportamiento actual de adaptar/exec intacto.

## Cambios Realizados

### 1. Estructura General
- ✅ Convertido a módulo con función `main()` ejecutable
- ✅ Agregado `if __name__ == "__main__": main()` al final
- ✅ Variables globales organizadas y documentadas

### 2. Logging (GestorLogs)
- ✅ Reemplazado `print` con `log.debug/info/warning/error`
- ✅ Niveles de debug configurables mediante argumentos:
  - `-p`: DEBUG
  - `-p2`: INFO
  - `-p1`: WARNING
  - (default): ERROR
- ✅ Mantenido indicador de progreso `print(f'{nombre_equipo[-1]}')` solo cuando no está en modo debug

### 3. Parámetros (GestorParametros)
- ✅ `GestorParametros(check_interval=300)` para carga automática
- ✅ Carga de configuración: `EQUIPO = gp.leer_parametros(nombre_equipo_rs485)`
- ✅ Recarga automática cada 300 segundos en el bucle principal
- ✅ Detección de cambios de versión con `gp.version()`
- ✅ Argumento `-NEQUIPO=<nombre>` para especificar tipo de equipo

### 4. Base de Datos (GestorBD)
- ✅ `gestor_bd = GestorBD()` para conexión automática
- ✅ `gestor_bd.guardar_datos_equipo_dict(nombre_equipo, tiempo, datos)` en lugar de SQL manual
- ✅ `gestor_bd.insertar_equipo_si_falta(nombre_equipo)` para inicializar equipos
- ✅ Eliminado uso directo de `MySQLdb` y consultas SQL vulnerables

### 5. MQTT (GestorMQTT)
- ✅ `gestor_mqtt = GestorMQTT(depurar=log.es_debug())` para conexión
- ✅ `gestor_mqtt.suscribir_equipos(equipos_activos)` en lugar de suscripciones manuales
- ✅ `gestor_mqtt.conectar()` para iniciar conexión
- ✅ `gestor_mqtt.obtener_comando_pendiente()` en lugar de `comando_mqtt` global
- ✅ Eliminadas funciones `on_connect`, `on_disconnect`, `on_message` manuales

### 6. Telegram (GestorTelegram)
- ✅ `gestor_telegram = GestorTelegram()` para inicialización
- ✅ `gestor_telegram.enviar_mensaje_inicio(nombre_equipo_rs485)` al arrancar
- ✅ `gestor_telegram.enviar_mensaje_seguro(msg)` en `listar_parametros` y `escribir_registro`
- ✅ `gestor_telegram.esta_habilitado()` para verificar disponibilidad
- ✅ Eliminados `telebot` y `timeout_decorator` directos

### 7. Control de Servicio (control_servicio)
- ✅ `controlar_servicio("fv_rs485", hay_activos)` para detener servicio si no hay equipos activos
- ✅ Cálculo de equipos activos: `equipos_activos = [e for e in EQUIPO if EQUIPO[e].get('usar', 0) == 1]`

### 8. Lógica adaptar/exec - MANTENIDA SIN CAMBIOS
- ✅ `leer_registro()`: sin cambios en lógica de conversión
- ✅ `leer_registros()`: `exec(ejecutar)` intacto en línea 146
- ✅ `listar_parametros()`: `exec(ejecutar)` intacto en línea 186
- ✅ `leer_equipo()`: `exec(ejecutar)` intacto en línea 319
- ✅ Diccionario `datos` construido exactamente igual
- ✅ Variable `d` usada igual que en el original

### 9. Comentarios en Español
- ✅ Todos los comentarios en español
- ✅ Docstrings en español
- ✅ Mensajes de error y logging en español

## Uso del Servicio Refactorizado

### Ejecución Básica
```bash
python3 servicios/fv_rs485.py -NEQUIPO=ANENJI
python3 servicios/fv_rs485.py -NEQUIPO=SRNE
python3 servicios/fv_rs485.py -NEQUIPO=EPEVER
```

### Con Debugging
```bash
python3 servicios/fv_rs485.py -NEQUIPO=ANENJI -p    # DEBUG level
python3 servicios/fv_rs485.py -NEQUIPO=ANENJI -p2   # INFO level
python3 servicios/fv_rs485.py -NEQUIPO=ANENJI -p1   # WARNING level
```

### Simulación de Datos
```bash
python3 servicios/fv_rs485.py -NEQUIPO=ANENJI -s    # Simular datos
```

## Funciones Principales (Exportadas)
- `leer_registro(equipo, comando)`: Lectura de comando individual
- `leer_registros(equipo)`: Lectura múltiple usando rangos
- `listar_parametros(equipo)`: Lista parámetros vía Telegram
- `escribir_registro(equipo, mensaje)`: Escribe registro
- `leer_equipo(equipo)`: Bucle principal de lectura
- `main()`: Función principal del servicio

## Compatibilidad
- ✅ Mantiene compatibilidad con archivos de configuración existentes (Parametros_FV.py)
- ✅ Mantiene compatibilidad con adaptar/exec de equipos existentes
- ✅ Mantiene estructura de diccionario EQUIPO y COMANDOS
- ✅ Mantiene lógica de modbus/RS485 sin cambios
- ✅ Mantiene lógica de orden de bytes (orden_bytes)
- ✅ Mantiene lógica de simulación (simular_datos)

## Mejoras de Seguridad
- ✅ Eliminadas vulnerabilidades de inyección SQL (usando consultas parametrizadas)
- ✅ Mejor manejo de errores con try/except en todos los gestores
- ✅ Timeout controlado en Telegram
- ✅ Reintento automático de conexión MQTT y BD

## Mejoras de Mantenibilidad
- ✅ Código modular y reutilizable
- ✅ Separación de preocupaciones (logging, BD, MQTT, Telegram)
- ✅ Auto-recarga de configuración sin reiniciar servicio
- ✅ Mejor documentación y comentarios en español
- ✅ Tipos de datos explícitos en funciones de helpers

## Pruebas Realizadas
- ✅ Sintaxis Python correcta (py_compile exitoso)
- ✅ Importación de módulos helpers exitosa
- ✅ Verificación de estructura de código
- ✅ Verificación de lógica adaptar/exec intacta
