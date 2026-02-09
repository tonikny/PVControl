import importlib.util
from pathlib import Path
import os

# Rutas por defecto en la Raspberry Pi
BASE_PATH = '/home/pi/PVControl+'
RUTA_DIST = os.path.join(BASE_PATH, 'Parametros_FV_DIST.py')
RUTA_USER = os.path.join(BASE_PATH, 'Parametros_FV.py')

# Diccionario para almacenar los parámetros cargados (caché en memoria)
_parametros_cache = {}


class _GestorEstado:
    """Singleton de módulo para gestionar el estado de caché de parámetros."""

    def __init__(self):
        self.cache = {}
        self.mtime_dist = None
        self.mtime_user = None

    def hay_cambios(self, mtime_dist_actual, mtime_user_actual):
        """Verifica si los archivos han cambiado desde la última carga."""
        return (mtime_dist_actual != self.mtime_dist or
                mtime_user_actual != self.mtime_user)

    def actualizar(self, parametros, mtime_dist, mtime_user):
        """Actualiza la caché con los nuevos parámetros y tiempos de modificación."""
        self.cache = parametros
        self.mtime_dist = mtime_dist
        self.mtime_user = mtime_user


# Instancia singleton del gestor de estado
_estado = _GestorEstado()


def _obtener_mtime_actual(ruta):
    """Obtiene de forma segura el tiempo de modificación de un archivo.

    Args:
        ruta: Ruta al archivo.

    Returns:
        float: Tiempo de última modificación, o None si el archivo no existe.
    """
    try:
        return os.path.getmtime(ruta)
    except (OSError, FileNotFoundError):
        return None


def convertir_dict_a_list(equipo):
    return [
        {"id": key, **value}
        for key, value in equipo.items()
    ]

def cargar_parametros(*params):
    """
    Carga los parámetros desde los archivos DIST y USER.

    Args:
        *params: Nombres de los parámetros a obtener.

    Returns:
        Si se pide un solo parámetro: su valor.
        Si se piden varios: una tupla con los valores.
        Si no se piden parámetros: el diccionario completo.
    """
    global _parametros_cache

    # Usar el gestor de estado para cargar parámetros (sin forzar recarga)
    parametros = recargar_parametros(force=False)

    # Mantener compatibilidad con la caché global existente
    _parametros_cache = parametros

    # Si no se piden parámetros, devolver el diccionario completo
    if not params:
        return _parametros_cache

    resultado = [_parametros_cache.get(p) for p in params]

    if len(params) == 1:
        return resultado[0]
    return tuple(resultado)

def recargar_parametros(force=False):
    """
    Recarga los parámetros desde los archivos DIST y USER.

    Esta función utiliza caché basada en el tiempo de modificación (mtime)
    de los archivos. Solo recarga los archivos si han sido modificados
    desde la última carga, o si se fuerza la recarga con force=True.

    Args:
        force: Si es True, fuerza la recarga de los archivos sin
               considerar el caché. Por defecto es False.

    Returns:
        El diccionario completo de parámetros.
    """
    global _estado

    # Obtener los tiempos de modificación actuales
    mtime_dist_actual = _obtener_mtime_actual(RUTA_DIST)
    mtime_user_actual = _obtener_mtime_actual(RUTA_USER)

    # Si no hay cambios y no se fuerza la recarga, devolver caché
    if not force and not _estado.hay_cambios(mtime_dist_actual, mtime_user_actual):
        return _estado.cache

    # Cargar DIST (valores por defecto)
    dist_vars = _cargar_archivo_py(RUTA_DIST)

    # Cargar USER si existe (valores de usuario que sobreescriben DIST)
    user_vars = {}
    if os.path.exists(RUTA_USER):
        user_vars = _cargar_archivo_py(RUTA_USER)

    # Combinar (USER prevalece sobre DIST)
    combinados = {k: v for k, v in dist_vars.items()}
    combinados.update({k: v for k, v in user_vars.items()})

    # Actualizar el estado con los nuevos parámetros y tiempos
    _estado.actualizar(combinados, mtime_dist_actual, mtime_user_actual)

    return combinados

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

def obtener_ruta_user():
    """Devuelve la ruta al archivo de parámetros del usuario."""
    return RUTA_USER

def obtener_ruta_dist():
    """Devuelve la ruta al archivo de parámetros por defecto."""
    return RUTA_DIST

def obtener_base_path():
    """Devuelve la ruta base del proyecto."""
    return BASE_PATH
