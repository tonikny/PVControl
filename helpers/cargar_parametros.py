import importlib.util
from pathlib import Path
import os

# Rutas por defecto en la Raspberry Pi
RUTA_DIST = '/home/pi/PVControl+/Parametros_FV_DIST.py'
RUTA_USER = '/home/pi/PVControl+/Parametros_FV.py'

# Caché global: guarda el módulo y el mtime de los archivos
_cache_modulos = {}

def cargar_parametros(*params):
    """
    Carga DIST primero, luego USER (sobreescribe) y devuelve las variables solicitadas.
    
    Implementa caché basado en mtime (modification time) para evitar recargas innecesarias.
    Si los archivos no han cambiado desde la última carga, se devuelven los valores
    del caché en lugar de recargar los archivos.

    Args:
        *params: Las variables que se solicitan.

    Returns:
        El valor de la variable (si es una) o una tupla con los valores. 
        Si se solicita una variable que no existe, devuelve None.
    """
    global _cache_modulos
    
    # Obtener mtime de los archivos
    mtime_dist = _obtener_mtime(RUTA_DIST)
    mtime_user = _obtener_mtime(RUTA_USER)
    
    # Clave de caché basada en los mtime
    clave_cache = (mtime_dist, mtime_user)
    
    # Verificar si el caché está actualizado
    if clave_cache in _cache_modulos:
        vars_combinadas = _cache_modulos[clave_cache]
    else:
        # Cargar DIST y convertir a diccionario de variables
        dist_vars = vars(_cargar_archivo(RUTA_DIST))
        
        # Cargar USER si existe (opcional)
        user_vars = {}
        try:
            user_vars = vars(_cargar_archivo(RUTA_USER))
        except (FileNotFoundError, ImportError):
            print(f"Archivo usuario {RUTA_USER} no encontrado, usando solo defaults")
        
        # Combinar variables: USER prevalece sobre DIST
        # Filtrar variables privadas (que empiezan con _)
        vars_combinadas = {
            k: v for k, v in dist_vars.items() 
            if not k.startswith('_')
        }
        vars_combinadas.update({
            k: v for k, v in user_vars.items() 
            if not k.startswith('_')
        })
        
        # Guardar en caché
        _cache_modulos[clave_cache] = vars_combinadas
    
    # Crear el diccionario con los parámetros solicitados
    # PRIORIDAD: El valor de USER (user_vars) prevalece sobre DIST (dist_vars)
    resultado = {param: vars_combinadas.get(param, None) for param in params}
    
    # Si se pide solo un parámetro, devolver el valor directamente
    if len(params) == 1:
        return list(resultado.values())[0]
        
    # Si se piden varios, devolver la tupla
    return tuple(resultado.values())

def _obtener_mtime(ruta):
    """
    Obtiene el mtime (modification time) de un archivo.
    
    Args:
        ruta: Ruta del archivo
        
    Returns:
        El mtime del archivo, o 0 si el archivo no existe
    """
    try:
        return os.path.getmtime(ruta)
    except (FileNotFoundError, OSError):
        return 0
    
def _cargar_archivo(ruta):
    """
    Carga un archivo .py dinámicamente como un módulo.
    
    Args:
        ruta: Ruta del archivo .py a cargar
        
    Returns:
        El módulo cargado
        
    Raises:
        FileNotFoundError: Si el archivo no existe
    """
    if not Path(ruta).exists():
        raise FileNotFoundError(f"No se encuentra el archivo de parámetros: {ruta}")
        
    spec = importlib.util.spec_from_file_location(Path(ruta).stem, str(ruta))
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo

def limpiar_cache():
    """
    Limpia el caché de módulos cargados.
    
    Útil para forzar la recarga de parámetros incluso si los archivos
    no han cambiado según su mtime.
    """
    global _cache_modulos
    _cache_modulos.clear()
