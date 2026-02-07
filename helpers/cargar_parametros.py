import importlib.util
from pathlib import Path
import os

# Rutas por defecto en la Raspberry Pi
BASE_PATH = '/home/pi/PVControl+'
RUTA_DIST = os.path.join(BASE_PATH, 'Parametros_FV_DIST.py')
RUTA_USER = os.path.join(BASE_PATH, 'Parametros_FV.py')

# Diccionario para almacenar los parámetros cargados (caché en memoria)
_parametros_cache = {}
# mtime por proceso (PID) para asegurar que cada proceso detecte el cambio de forma independiente
_mtime_cache_por_pid = {}
# Seguimiento de si el proceso ha obtenido los parámetros con el flag solo_si_cambio
_visto_con_cambio_por_pid = set()

def cargar_parametros(*params, recargar=False, solo_si_cambio=False):
    """
    Carga los parámetros desde los archivos DIST y USER.
    Si el archivo USER ha cambiado en el disco, se recarga automáticamente.
    
    Args:
        *params: Nombres de los parámetros a obtener.
        recargar: Si es True, fuerza la recarga desde los archivos ignorando el mtime.
        solo_si_cambio: Si es True, solo devuelve valores si se ha producido una recarga
                        O si es la primera vez que se solicita con este flag en el proceso actual.
                        En caso contrario devuelve None.
        
    Returns:
        Si solo_si_cambio=True y no hay cambios/no es la primera vez: None.
        Si se pide un solo parámetro: su valor.
        Si se piden varios: una tupla con los valores.
        Si no se piden parámetros: el diccionario completo.
    """
    pid = os.getpid()
    ha_recaragado = False
    
    # Comprobar si hay que recargar
    if not _parametros_cache or han_cambiado_parametros() or recargar:
        recargar_parametros()
        ha_recaragado = True
        # Si hay recarga, reseteamos el visto para todos los procesos que heredaron
        # (aunque en la práctica esto solo afectará al proceso actual ya que el set no es compartido)
        if ha_recaragado and pid in _visto_con_cambio_por_pid:
            _visto_con_cambio_por_pid.remove(pid)
        
    if solo_si_cambio:
        if ha_recaragado or pid not in _visto_con_cambio_por_pid:
            _visto_con_cambio_por_pid.add(pid)
        else:
            return None

    if not params:
        return _parametros_cache
        
    resultado = [_parametros_cache.get(p) for p in params]
    
    if len(params) == 1:
        return resultado[0]
    return tuple(resultado)

def han_cambiado_parametros():
    """
    Comprueba si el archivo de parámetros del usuario ha cambiado desde la última carga
    para el proceso actual.
    """
    pid = os.getpid()
    return obtener_mtime_user() != _mtime_cache_por_pid.get(pid, -1)

def recargar_parametros():
    """
    Lee los archivos de parámetros y devuelve un diccionario con la combinación de ambos.
    También puede ser llamada externamente para forzar la actualización.
    Actualiza el mtime_cache para el proceso actual.
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
    
    # Sincronizar mtime para este proceso
    pid = os.getpid()
    _mtime_cache_por_pid[pid] = obtener_mtime_user()
    
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
