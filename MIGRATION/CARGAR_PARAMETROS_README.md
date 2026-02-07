# Manual: cargar_parametros.py

## Descripción
El módulo `cargar_parametros.py` gestiona la carga de configuración de PVControl+, combinando valores por defecto (`Parametros_FV_DIST.py`) con personalizaciones del usuario (`Parametros_FV.py`).

## Funciones Principales

### `cargar_parametros(*params, recargar=False)`
Obtiene uno o varios parámetros. 
- **Auto-recarga**: Comprueba automáticamente si `Parametros_FV.py` ha cambiado en el disco y recarga si es necesario.
- `params`: Nombres de las variables deseadas.
- `recargar`: Si es `True`, fuerza la relectura de los archivos desde el disco ignorando si han cambiado o no.

### `han_cambiado_parametros()`
Devuelve `True` si el archivo de parámetros del usuario ha sido modificado desde la última vez que se cargaron. Útil para disparar lógica adicional tras una recarga.

### `recargar_parametros()`
Fuerza la recarga de todos los parámetros en el caché interno, actualiza el mtime de referencia y devuelve el diccionario completo.

### `obtener_mtime_user()`
Devuelve el tiempo de última modificación de `Parametros_FV.py` en el disco.

## Ejemplos de Uso

### Carga básica (con auto-recarga automática)
```python
from helpers.cargar_parametros import cargar_parametros

# En cada llamada, cargar_parametros comprueba si hay cambios en el archivo
# y se actualiza solo si es necesario.
servidor = cargar_parametros("servidor")
```

### Detección de cambios para lógica adicional
Si necesitas ejecutar código especial cuando los parámetros cambian (como reiniciar un hardware):

```python
from helpers.cargar_parametros import cargar_parametros, han_cambiado_parametros

primera_vez = True
while True:
    if han_cambiado_parametros() or primera_vez:
        primera_vez = False
        config = cargar_parametros("ADS")
        # ... lógica de reinicialización ...
```

## Prioridad de Carga
1. Se cargan los valores de `Parametros_FV_DIST.py`.
2. Si existe `Parametros_FV.py`, se cargan sus valores y estos **sobreescriben** a los anteriores.
3. Se filtran las variables internas de Python (aquellas que empiezan por `__`).
