RUTA_DIST = '/home/pi/PVControl+/Parametros_FV_DIST.py'
RUTA_USER = '/home/pi/PVControl+/Parametros_FV.py'

def cargar_parametros(*params):
    """
    Carga DIST primero, luego USER (sobreescribe) y devuelve las variables solicitadas.

    Args:
        *params: Las variables que se solicitan.

    Returns:
        Una tupla con los valores de las variables solicitadas. Si se solicita una variable que no existe, devuelve None para esa variable.

    Raises:
        FileNotFoundError: Si el archivo de variables USER no existe.

    Examples:
        var1, var2, var3 = cargar_parametros('var1', 'var2', 'var3')
        Devuelve los valores de las variables 'var1', 'var2' y 'var3' o None si no existe la variable.
    """
    # Cargar DIST
    dist_vars = _cargar_archivo(RUTA_DIST)
    
    # Cargar USER si existe (opcional)
    user_vars = {}
    try:
        user_vars = _cargar_archivo(RUTA_USER)
    except FileNotFoundError:
        print(f"Archivo usuario {RUTA_USER} no encontrado, usando solo defaults")
    
    # Create a dictionary with the requested parameters, using default values if not found in user_vars
    result = {param: dist_vars.get(param, user_vars.get(param, None)) for param in params}
    
    # Unpack the dictionary into separate variables
    return tuple(result.values())
    
def _cargar_archivo(ruta):
    """Carga archivo .py como módulo"""
    spec = importlib.util.spec_from_file_location(Path(ruta).stem, str(ruta))
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo
