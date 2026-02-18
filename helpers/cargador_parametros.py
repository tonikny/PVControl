"""
Cargador de Parámetros para PVControl+

Carga parámetros importando directamente los módulos.
El archivo USER sobreescribe las variables del DIST.

Único lugar donde se definen las rutas de los archivos de configuración.
"""

import os
import importlib.util

# =============================================================================
# CONFIGURACIÓN - ÚNICO LUGAR PARA CAMBIAR LAS RUTAS
# =============================================================================
RUTA_PARAMETROS_DIST = "/home/pi/PVControl+/Parametros_FV_DIST.py"
RUTA_PARAMETROS_USER = "/home/pi/PVControl+/Parametros_FV.py"
# =============================================================================


def _importar_desde_ruta(ruta_archivo: str, nombre_modulo: str) -> dict:
    """
    Importa un módulo desde una ruta específica y devuelve sus atributos públicos.
    """
    spec = importlib.util.spec_from_file_location(nombre_modulo, ruta_archivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    
    return {k: v for k, v in modulo.__dict__.items() if not k.startswith('_')}


def cargar_parametros() -> dict:
    """
    Carga parámetros desde ambos archivos fusionándolos.
    
    El orden de carga es:
    1. Parametros_FV_DIST.py - Valores por defecto
    2. Parametros_FV.py - Valores del usuario (sobreescribe)
    
    Returns:
        dict con todos los parámetros fusionados
    """
    # 1. Cargar valores por defecto (DIST)
    params = _importar_desde_ruta(RUTA_PARAMETROS_DIST, "parametros_dist")
    
    # 2. Cargar valores del usuario (USER) y sobreescribir
    if os.path.exists(RUTA_PARAMETROS_USER):
        params_user = _importar_desde_ruta(RUTA_PARAMETROS_USER, "parametros_user")
        params.update(params_user)
    
    return params


def obtener_parametro(nombre: str, default=None):
    """Obtiene un único parámetro"""
    params = cargar_parametros()
    return params.get(nombre, default)


def recargar_si_cambiaron(ultima_version: float):
    """Verifica cambios y recarga si es necesario"""
    try:
        actual_mtime = os.path.getmtime(RUTA_PARAMETROS_USER)
        if actual_mtime != ultima_version:
            return cargar_parametros(), actual_mtime
        return None, ultima_version
    except FileNotFoundError:
        return None, ultima_version


def convertir_dict_a_lista(equipo: dict) -> list:
    """
    Convierte un dict a una lista de dicts con el id incluido.
    
    Param:
    ```
    EQUIPO = {
        'EQUIPO1': {
            'usar': True,
            'ip': '237.84.2.178',
            'puerto': 80
        }
    }
    ```
    Return:
    ```
    EQUIPO = [
        {
            'id': 'EQUIPO1',
            'usar': True,
            'ip': '237.84.2.178',
            'puerto': 80
        }
    ]
    ```
    """
    return [
        {"id": key, **value}
        for key, value in equipo.items()
    ]


def obtener_todos_ads(params: dict) -> list:
    """
    Obtiene TODOS los ADS configurados (activos o no).
    
    Args:
        params: Diccionario de parámetros cargados
    
    Returns:
        Lista de dicts con configuración de cada ADS
    """
    if 'ADS' not in params:
        return []
    
    return convertir_dict_a_lista(params['ADS'])


def obtener_ads_activos(params: dict) -> list:
    """
    Obtiene solo los ADS activos (usar = True).
    
    Args:
        params: Diccionario de parámetros cargados
    
    Returns:
        Lista de dicts con configuración de ADS activos
    """
    todos_ads = obtener_todos_ads(params)
    return [ads for ads in todos_ads if ads.get('usar', False)]
