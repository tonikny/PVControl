# Refactor: Control de Servicios y Gestión de Parámetros

Este documento detalla los cambios realizados en la arquitectura de control de servicios y carga de parámetros en PVControl+.

## 1. Carga de Parámetros (`helpers/cargar_parametros.py`)

Se ha rediseñado el módulo para centralizar la lógica de rutas y permitir recargas controladas.

### Cambios principales:
- **Rutas centralizadas**: El módulo conoce la ubicación de `Parametros_FV.py` y `Parametros_FV_DIST.py`.
- **Caché en memoria**: Los parámetros se cargan una vez y se mantienen en memoria dentro del proceso.
- **Recarga explícita**: Para actualizar los parámetros (por ejemplo, tras un cambio en el archivo), se debe llamar a `cargar_parametros(..., recargar=True)`.
- **Verificación de cambios**: Se proporciona `obtener_mtime_user()` para que los procesos de larga duración puedan comprobar si el archivo de parámetros ha sido modificado en el disco.

### Ejemplo de uso en servicios:
```python
from helpers.cargar_parametros import cargar_parametros, obtener_mtime_user

# Carga inicial
config = cargar_parametros("MI_SECCION")
mtime_local = obtener_mtime_user()

# En el bucle principal
while True:
    if obtener_mtime_user() != mtime_local:
        config = cargar_parametros("MI_SECCION", recargar=True)
        mtime_local = obtener_mtime_user()
    ...
```

## 2. Control de Servicios (`fv_control_servicio.py`)

Se ha eliminado el uso de `exec()` y `eval()` para mejorar la seguridad y claridad.

### Funciones disponibles:
- `controlar_servicio(nombre_servicio, debe_ejecutarse)`: Recibe un booleano. Si es `False`, detiene el servicio y finaliza el script.
- `verificar_equipos_activos(config_dict)`: Utilidad para contar cuántos equipos tienen la clave `"usar": True`.

### Ejemplo:
```python
ads_config = cargar_parametros("ADS")
hay_activos = sum(1 for v in ads_config.values() if v.get("usar", False)) > 0
controlar_servicio("fv_ads", hay_activos)
```

## 3. Gestión de Base de Datos (`helpers/gestor_bd.py`)

Sustituye al antiguo `db_manager.py`, ofreciendo una interfaz en español y segura.

### Mapeo de métodos (Transición):
- `save_equipment_data` -> `guardar_datos_equipo`
- `save_equipment_data_dict` -> `guardar_datos_equipo_dict`
- `insert_equipment_if_missing` -> `insertar_equipo_si_falta`
- `commit` -> `confirmar`
- `close` -> `cerrar`

## 4. Beneficios del Refactor
1. **Seguridad**: Prevención de inyección de código.
2. **Eficiencia**: Los parámetros no se leen del disco en cada iteración a menos que cambien.
3. **Consistencia**: Nomenclatura uniforme en español.
4. **Mantenibilidad**: Código modular y bien documentado.
