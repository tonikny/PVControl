# Manual: cargar_parametros.py

## Descripción
El módulo `cargar_parametros.py` gestiona la carga de configuración de PVControl+, combinando valores por defecto (`Parametros_FV_DIST.py`) con personalizaciones del usuario (`Parametros_FV.py`).

## Funciones Principales

### `cargar_parametros(*params, recargar=False)`
Obtiene uno o varios parámetros.
- `params`: Nombres de las variables deseadas.
- `recargar`: Si es `True`, fuerza la relectura de los archivos desde el disco.

### `recargar_parametros()`
Fuerza la recarga de todos los parámetros en el caché interno y devuelve el diccionario completo.

### `obtener_mtime_user()`
Devuelve el tiempo de última modificación de `Parametros_FV.py`. Útil para detectar cambios externos.

### `obtener_ruta_user()`
Devuelve la ruta absoluta al archivo de parámetros de usuario.

## Ejemplos de Uso

### Carga básica
```python
from helpers.cargar_parametros import cargar_parametros

# Un solo valor
servidor = cargar_parametros("servidor")

# Múltiples valores
usuario, clave = cargar_parametros("usuario", "clave")
```

### Detección de cambios y recarga
```python
from helpers.cargar_parametros import cargar_parametros, obtener_mtime_user

mtime_anterior = obtener_mtime_user()

# ... más tarde en un bucle ...
if obtener_mtime_user() != mtime_anterior:
    # Algo ha cambiado, recargamos
    ADS = cargar_parametros("ADS", recargar=True)
    mtime_anterior = obtener_mtime_user()
```

## Prioridad de Carga
1. Se cargan los valores de `Parametros_FV_DIST.py`.
2. Si existe `Parametros_FV.py`, se cargan sus valores y estos **sobreescriben** a los anteriores.
3. Se filtran las variables internas de Python (aquellas que empiezan por `__`).
