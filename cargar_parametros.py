def cargar_parametros(*params):
    """Carga DIST primero, luego USER (sobreescribe) y devuelve las variables solicitadas"""
    # Cargar DIST
    dist_vars = cargar_vars_de_archivo(RUTA_DIST)
    
    # Cargar USER si existe (opcional)
    user_vars = {}
    try:
        user_vars = cargar_vars_de_archivo(RUTA_USER)
    except FileNotFoundError:
        print(f"Archivo usuario {RUTA_USER} no encontrado, usando solo defaults")
    
    # Create a dictionary with the requested parameters, using default values if not found in user_vars
    result = {param: dist_vars.get(param, user_vars.get(param, None)) for param in params}
    
    # Unpack the dictionary into separate variables
    return tuple(result.values())
    