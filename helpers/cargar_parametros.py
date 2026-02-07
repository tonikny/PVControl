import importlib.util
from pathlib import Path
import os

# Rutas por defecto en la Raspberry Pi
BASE_PATH = '/home/pi/PVControl+'
RUTA_DIST = os.path.join(BASE_PATH, 'Parametros_FV_DIST.py')
RUTA_USER = os.path.join(BASE_PATH, 'Parametros_FV.py')

# Diccionario para almacenar los parámetros cargados (caché en memoria)
_parametros_cache = {}

def cargar_parametros(*params, recargar=False):
    """
    Carga los parámetros desde los archivos DIST y USER.
    
    Args:
        *params: Nombres de los parámetros a obtener.
        recargar: Si es True, fuerza la recarga desde los archivos.
        
    Returns:
        Si se pide un solo parámetro, su valor.
        Si se piden varios, una tupla con los valores.
        Si no se piden parámetros, el diccionario completo.
    """
    global _parametros_cache
    
    if not _parametros_cache or recargar:
        _parametros_cache = recargar_parametros()
        
    if not params:
        return _parametros_cache
        
    resultado = [_parametros_cache.get(p) for p in params]
    
    if len(params) == 1:
        return resultado[0]
    return tuple(resultado)

def recargar_parametros():
    """
    Lee los archivos de parámetros y devuelve un diccionario con la combinación de ambos.
    También puede ser llamada externamente para forzar la actualización.
    """
    global _parametros_cache
    
    # Cargar DIST (valores por defecto)
    dist_vars = _cargar_archivo_py(RUTA_DIST)
    
    # Cargar USER si existe (valores de usuario que sobreescriben DIST)
    user_vars = {}
    if os.path.exists(RUTA_USER):
        user_vars = _cargar_archivo_py(RUTA_USER)
    
    # Combinar (USER prevalece sobre DIST)
    # Filtramos para no incluir variables internas de Python
    combinados = {k: v for k, v in dist_vars.items() if not k.startswith('__')}
    combinados.update({k: v for k, v in user_vars.items() if not k.startswith('__')})
    
    _parametros_cache = combinados
    return _parametros_cache

def _cargar_archivo_py(ruta):
    """Carga un archivo Python dinámicamente y devuelve sus variables."""
    try:
        spec = importlib.util.spec_from_file_location(Path(ruta).stem, ruta)
        if spec is None or spec.loader is None:
            return {}
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        return vars(modulo)
    except Exception as e:
        print(f"Error cargando archivo de parámetros {ruta}: {e}")
        return {}

def obtener_mtime_user():
    """
    Obtiene la fecha de modificación del archivo de parámetros de usuario.
    Permite a los scripts externos decidir cuándo recargar.
    """
    try:
        return os.path.getmtime(RUTA_USER)
    except OSError:
        return 0

def obtener_ruta_user():
    """Devuelve la ruta al archivo de parámetros del usuario."""
    return RUTA_USER
