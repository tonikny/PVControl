import importlib.util
from pathlib import Path
import os


class GestorParametros:
    """Gestor de parámetros de configuración con caché basada en mtime.

    Esta clase encapsula la lógica de carga y cacheo de parámetros desde
    los archivos DIST y USER, utilizando el tiempo de modificación (mtime)
    para evitar recargas innecesarias.

    Attributes:
        BASE_PATH: Ruta base del proyecto PVControl+.
        RUTA_DIST: Ruta al archivo de parámetros por defecto.
        RUTA_USER: Ruta al archivo de parámetros de usuario.
    """

    BASE_PATH = '/home/pi/PVControl+'
    RUTA_DIST = os.path.join(BASE_PATH, 'Parametros_FV_DIST.py')
    RUTA_USER = os.path.join(BASE_PATH, 'Parametros_FV.py')

    def __init__(self):
        """Inicializa el gestor con caché vacío."""
        self._cache = {}
        self._mtime_dist = None
        self._mtime_user = None

    def _obtener_mtime_actual(self, ruta):
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

    def _hay_cambios(self, mtime_dist_actual, mtime_user_actual):
        """Verifica si los archivos han cambiado desde la última carga.

        Args:
            mtime_dist_actual: Tiempo de modificación actual del archivo DIST.
            mtime_user_actual: Tiempo de modificación actual del archivo USER.

        Returns:
            bool: True si algún archivo ha cambiado, False en caso contrario.
        """
        return (mtime_dist_actual != self._mtime_dist or
                mtime_user_actual != self._mtime_user)

    def _actualizar_estado(self, parametros, mtime_dist, mtime_user):
        """Actualiza la caché con los nuevos parámetros y tiempos de modificación.

        Args:
            parametros: Diccionario de parámetros cargados.
            mtime_dist: Tiempo de modificación del archivo DIST.
            mtime_user: Tiempo de modificación del archivo USER.
        """
        self._cache = parametros
        self._mtime_dist = mtime_dist
        self._mtime_user = mtime_user

    def _cargar_archivo_py(self, ruta):
        """Carga un archivo Python dinámicamente y devuelve sus variables.

        Args:
            ruta: Ruta al archivo Python a cargar.

        Returns:
            dict: Diccionario con las variables del módulo, o dict vacío si hay error.
        """
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

    def recargar_parametros(self, force=False):
        """Recarga los parámetros desde los archivos DIST y USER.

        Esta función utiliza caché basada en el tiempo de modificación (mtime)
        de los archivos. Solo recarga los archivos si han sido modificados
        desde la última carga, o si se fuerza la recarga con force=True.

        Args:
            force: Si es True, fuerza la recarga de los archivos sin
                   considerar el caché. Por defecto es False.

        Returns:
            dict: El diccionario completo de parámetros.
        """
        # Obtener los tiempos de modificación actuales
        mtime_dist_actual = self._obtener_mtime_actual(self.RUTA_DIST)
        mtime_user_actual = self._obtener_mtime_actual(self.RUTA_USER)

        # Si no hay cambios y no se fuerza la recarga, devolver caché
        if not force and not self._hay_cambios(mtime_dist_actual, mtime_user_actual):
            return self._cache

        # Cargar DIST (valores por defecto)
        dist_vars = self._cargar_archivo_py(self.RUTA_DIST)

        # Cargar USER si existe (valores de usuario que sobreescriben DIST)
        user_vars = {}
        if os.path.exists(self.RUTA_USER):
            user_vars = self._cargar_archivo_py(self.RUTA_USER)

        # Combinar (USER prevalece sobre DIST)
        combinados = {k: v for k, v in dist_vars.items()}
        combinados.update({k: v for k, v in user_vars.items()})

        # Actualizar el estado con los nuevos parámetros y tiempos
        self._actualizar_estado(combinados, mtime_dist_actual, mtime_user_actual)

        return combinados

    def cargar_parametros(self, *params):
        """Carga los parámetros desde los archivos DIST y USER.

        Args:
            *params: Nombres de los parámetros a obtener.

        Returns:
            Si se pide un solo parámetro: su valor.
            Si se piden varios: una tupla con los valores.
            Si no se piden parámetros: el diccionario completo.
        """
        # Usar recargar_parametros para aprovechar el caché (sin forzar recarga)
        parametros = self.recargar_parametros(force=False)

        # Si no se piden parámetros, devolver el diccionario completo
        if not params:
            return parametros

        resultado = [parametros.get(p) for p in params]

        if len(params) == 1:
            return resultado[0]
        return tuple(resultado)

    def convertir_dict_a_list(self, equipo):
        """Convierte un diccionario de equipos a una lista de diccionarios.

        Args:
            equipo: Diccionario donde las claves son IDs de equipo.

        Returns:
            list: Lista de diccionarios con el ID incluido en cada elemento.
        """
        return [
            {"id": key, **value}
            for key, value in equipo.items()
        ]

    def obtener_ruta_user(self):
        """Devuelve la ruta al archivo de parámetros del usuario.

        Returns:
            str: Ruta completa al archivo Parametros_FV.py.
        """
        return self.RUTA_USER

    def obtener_ruta_dist(self):
        """Devuelve la ruta al archivo de parámetros por defecto.

        Returns:
            str: Ruta completa al archivo Parametros_FV_DIST.py.
        """
        return self.RUTA_DIST

    def obtener_base_path(self):
        """Devuelve la ruta base del proyecto.

        Returns:
            str: Ruta base del proyecto PVControl+.
        """
        return self.BASE_PATH
