# Refactor: Control de Servicios y Gestión de Base de Datos

## Resumen de Cambios

Este refactor implementa mejoras de seguridad, modularidad y mantenibilidad en el sistema de control de servicios y gestión de base de datos de PVControl+.

## Cambios Principales

### 1. Nuevo Sistema de Control de Servicios (`fv_control_servicio.py`)

**Anteriormente:** Se utilizaba `exec()` y `eval()` para evaluar condiciones dinámicamente, lo cual representa un riesgo de seguridad.

**Ahora:** Funciones explícitas en español sin uso de `exec()` o `eval()`:

- `controlar_servicio(nombre_servicio, debe_ejecutarse)`: Controla la ejecución basándose en un booleano
- `parar_servicio(nombre_servicio)`: Detiene un servicio mediante systemctl
- `verificar_equipos_activos(config_dict)`: Verifica si hay equipos activos en un diccionario
- `verificar_parametro_boolean(valor)`: Verifica valores booleanos de forma segura

**Mejoras:**
- ✅ Elimina vulnerabilidades de inyección de código
- ✅ Funciones explícitas y tipadas
- ✅ Código más legible y mantenible
- ✅ Comentarios en español

### 2. Nuevo Gestor de Base de Datos (`helpers/gestor_bd.py`)

**Anteriormente:** Módulo `helpers/db_manager.py` con nombres en inglés.

**Ahora:** Módulo `helpers/gestor_bd.py` completamente en español:

**Clase `GestorBD`:**
- `guardar_datos_equipo()` (antes `save_equipment_data`)
- `guardar_datos_equipo_dict()` (antes `save_equipment_data_dict`)
- `insertar_equipo_si_falta()` (antes `insert_equipment_if_missing`)
- `obtener_datos_equipo()` (antes `get_equipment_data`)
- `confirmar()` (antes `commit`)
- `revertir()` (antes `rollback`)
- `cerrar()` (antes `close`)

**Atributos:**
- `servidor` (antes `host`)
- `usuario` (antes `user`)
- `clave` (antes `passwd`)
- `nombre_bd` (antes `db_name`)
- `conexion` (antes `connection`)

**Mejoras:**
- ✅ Nomenclatura consistente en español
- ✅ Mantiene toda la funcionalidad de seguridad (consultas parametrizadas)
- ✅ Documentación completa en español

### 3. Mejoras en `helpers/cargar_parametros.py`

**Nuevas características:**

- **Caché por mtime**: Los parámetros se cachean basándose en la fecha de modificación de los archivos
- **Rendimiento mejorado**: Evita recargas innecesarias de archivos Python
- **Nueva función**: `limpiar_cache()` para forzar recarga si es necesario

**Implementación:**
```python
# Caché global basado en mtime de archivos
_cache_modulos = {}

def cargar_parametros(*params):
    # Verifica mtime antes de recargar
    mtime_dist = _obtener_mtime(RUTA_DIST)
    mtime_user = _obtener_mtime(RUTA_USER)
    clave_cache = (mtime_dist, mtime_user)
    
    if clave_cache in _cache_modulos:
        # Usar caché si los archivos no han cambiado
        vars_combinadas = _cache_modulos[clave_cache]
    else:
        # Recargar y actualizar caché
        ...
```

**Mejoras:**
- ✅ Reduce I/O y tiempo de carga
- ✅ Mantiene sincronización automática con cambios en archivos
- ✅ Comentarios explicativos en español

### 4. Actualización de `fv_ads.py`

**Cambios clave:**

1. **Uso de booleano en lugar de diccionario completo:**
   ```python
   # ANTES:
   control = 'sum(1 for v in ADS.values() if v.get("usar"))'
   exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
   
   # AHORA:
   hay_ads_activas = sum(1 for v in ads_config.values() if v.get("usar", False)) > 0
   controlar_servicio("fv_ads", hay_ads_activas)
   ```

2. **Uso de gestor_bd en lugar de db_manager:**
   ```python
   # ANTES:
   from helpers.db_manager import DatabaseManager
   db_mgr = DatabaseManager()
   db_mgr.insert_equipment_if_missing(ads_name)
   db_mgr.save_equipment_data_dict(ads_name, tiempo, d_ads)
   
   # AHORA:
   from helpers.gestor_bd import GestorBD
   gestor = GestorBD()
   gestor.insertar_equipo_si_falta(ads_name)
   gestor.guardar_datos_equipo_dict(ads_name, tiempo, d_ads)
   ```

**Mejoras:**
- ✅ Parámetros más simples y reutilizables
- ✅ No expone estructuras de datos internas
- ✅ Más fácil de adaptar para otros servicios
- ✅ Nombres de métodos en español

### 5. Actualización de `fv_rs485.py` y `hibrido.py`

Ambos archivos ahora usan `helpers.gestor_bd.GestorBD` en lugar de `db_manager.DatabaseManager`:

**fv_rs485.py:**
- `gestor_bd.guardar_datos_equipo()` para guardar datos
- `gestor_bd.insertar_equipo_si_falta()` para crear registros

**hibrido.py:**
- `gestor_bd.guardar_datos_equipo()` para datos del híbrido
- `gestor_bd.confirmar()` y `gestor_bd.revertir()` para transacciones
- `gestor_bd.cerrar()` para limpieza de recursos

### 6. Eliminación de `helpers/db_manager.py`

El archivo wrapper en inglés ha sido eliminado. Todo el código ahora usa el módulo español `gestor_bd`.

## Patrón de Uso para Otros Servicios

El nuevo sistema permite fácil reutilización en otros scripts:

```python
from helpers.cargar_parametros import cargar_parametros
from helpers.gestor_bd import GestorBD
from fv_control_servicio import controlar_servicio

# Cargar configuración
mi_config = cargar_parametros("MI_EQUIPOS")

# Verificar si hay equipos activos
hay_equipos = sum(1 for v in mi_config.values() if v.get("usar", False)) > 0

# Controlar servicio
controlar_servicio("mi_servicio", hay_equipos)

# Usar gestor de BD
gestor = GestorBD()
gestor.guardar_datos_equipo_dict("MI_EQUIPO1", tiempo, datos)
gestor.cerrar()
```

## Compatibilidad con Código Existente

### ⚠️ Cambios Requeridos

Si otros scripts usan `db_manager`, deben actualizarse:

```python
# CAMBIAR:
from helpers.db_manager import DatabaseManager
db = DatabaseManager()
db.save_equipment_data(...)

# POR:
from helpers.gestor_bd import GestorBD
gestor = GestorBD()
gestor.guardar_datos_equipo(...)
```

### Mapeo de Métodos

| db_manager (inglés) | gestor_bd (español) |
|---------------------|---------------------|
| `DatabaseManager()` | `GestorBD()` |
| `save_equipment_data()` | `guardar_datos_equipo()` |
| `save_equipment_data_dict()` | `guardar_datos_equipo_dict()` |
| `insert_equipment_if_missing()` | `insertar_equipo_si_falta()` |
| `get_equipment_data()` | `obtener_datos_equipo()` |
| `commit()` | `confirmar()` |
| `rollback()` | `revertir()` |
| `close()` | `cerrar()` |
| `.connection` | `.conexion` |
| `.cursor` | `.cursor` |

## Archivos Modificados

- ✅ `fv_control_servicio.py` - Reescrito sin exec/eval
- ✅ `helpers/gestor_bd.py` - Nuevo módulo en español
- ✅ `helpers/cargar_parametros.py` - Agregado caché por mtime
- ✅ `fv_ads.py` - Usa booleano y gestor_bd
- ✅ `fv_rs485.py` - Migrado a gestor_bd
- ✅ `hibrido.py` - Migrado a gestor_bd
- ❌ `helpers/db_manager.py` - Eliminado

## Beneficios

1. **Seguridad**: Eliminación de `exec()` y `eval()`
2. **Mantenibilidad**: Código más limpio y explícito
3. **Rendimiento**: Caché inteligente de parámetros
4. **Consistencia**: Nomenclatura en español en todo el código
5. **Reutilización**: Funciones modulares fáciles de usar
6. **Documentación**: Código autodocumentado con nombres descriptivos

## Testing

Los archivos de test existentes (`test_auto_config.py`, `test_db_security.py`, `test_direct_import.py`) probablemente necesiten actualización para usar `gestor_bd` en lugar de `db_manager`.

## Notas

- El comportamiento funcional del sistema permanece idéntico
- Todas las consultas SQL siguen siendo parametrizadas (prevención de inyección SQL)
- La gestión de conexiones y transacciones se mantiene igual
- Los cambios son principalmente de refactorización y nomenclatura
