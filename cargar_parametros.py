import importlib.util
from pathlib import Path

# Rutas por defecto en la Raspberry Pi
RUTA_DIST = '/home/pi/PVControl+/Parametros_FV_DIST.py'
RUTA_USER = '/home/pi/PVControl+/Parametros_FV.py'

def cargar_parametros(*params):
    """
    Carga DIST primero, luego USER (sobreescribe) y devuelve las variables solicitadas.

    Args:
        *params: Las variables que se solicitan.

    Returns:
        El valor de la variable (si es una) o una tupla con los valores. 
        Si se solicita una variable que no existe, devuelve None.
    """
    # Cargar DIST y convertir a diccionario de variables
    dist_vars = vars(_cargar_archivo(RUTA_DIST))
    
    # Cargar USER si existe (opcional)
    user_vars = {}
    try:
        user_vars = vars(_cargar_archivo(RUTA_USER))
    except (FileNotFoundError, ImportError):
        # El archivo de usuario es opcional, si no existe no se hace nada
        pass
    
    # Crear el diccionario con los parámetros solicitados
    # PRIORIDAD: El valor de USER (user_vars) prevalece sobre DIST (dist_vars)
    result = {param: user_vars.get(param, dist_vars.get(param, None)) for param in params}
    
    # Si se pide solo un parámetro, devolver el valor directamente
    if len(params) == 1:
        return list(result.values())[0]
        
    # Si se piden varios, devolver la tupla
    return tuple(result.values())
    
def _cargar_archivo(ruta):
    """
    Carga un archivo .py dinámicamente como un módulo.
    """
    if not Path(ruta).exists():
        raise FileNotFoundError(f"No se encuentra el archivo de parámetros: {ruta}")
        
    spec = importlib.util.spec_from_file_location(Path(ruta).stem, str(ruta))
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo
