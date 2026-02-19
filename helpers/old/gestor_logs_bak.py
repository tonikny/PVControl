import logging
import os
import sys


class GestorLogs:
    """
    Gestor de logs sencillo por script.

    Parámetros:
        level: nivel de logging (por defecto logging.ERROR o variable LOGLEVEL)
        nombre: nombre del logger (por defecto "pvcontrol")
    """

    def __init__(self, nombre="pvcontrol", level=None):
        """
        Inicializa un logger básico para el módulo.

        Args:
            nombre: nombre del logger (por defecto "pvcontrol")
            level: nivel de logging (por defecto determinado por argumentos de línea de comandos)
        """
        self._log = logging.getLogger(nombre)

        # Si no se proporciona un nivel, determinarlo desde los argumentos de línea de comandos
        if level is None:
            level = self._get_level_from_cmd_args()

        # Clear handlers for this specific logger name only
        # self._log.handlers.clear()

        # Add handler for this specific logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        self._log.addHandler(handler)

        # Set the level
        env_level = os.getenv("LOGLEVEL")
        if env_level:
            try:
                level_value = getattr(logging, env_level.upper())
                self._log.setLevel(level_value)
            except AttributeError:
                self._log.warning(
                    f"Nivel de logging no reconocido: {env_level}, "
                    f"usando valor por defecto: {level}"
                )
                self._log.setLevel(level)
        else:
            # Usar el nivel por defecto si no se establece variable de entorno
            self._log.setLevel(level)

    def _get_level_from_cmd_args(self):
        """Determina el nivel de logging basado en los argumentos de línea de comandos."""
        
        if "-p1" in sys.argv:
            return logging.WARNING
        elif "-p2" in sys.argv:
            return logging.INFO
        elif "-p" in sys.argv:
            return logging.DEBUG
        else:
            return logging.ERROR

    def debug(self, *msg):
        self._log.debug(" ".join(msg))

    def info(self, *msg):
        self._log.info(" ".join(msg))

    def warning(self, *msg):
        self._log.warning(" ".join(msg))

    def error(self, *msg):
        self._log.error(" ".join(msg))

    def manual(self, *msg):
        """
        Muestra un mensaje manual que siempre se registra,
        independientemente del nivel de log actual.
        """
        message = " ".join(msg)
        
        # Formatear el mensaje como manual sin nivel
        formatted_message = f"[MANUAL] {self._log.name}: {message}\n"
        
        # Enviar directamente a los streams de los handlers
        for handler in self._log.handlers:
            if hasattr(handler, 'stream'):
                handler.stream.write(formatted_message)
                handler.stream.flush()  # Asegurar que se escriba inmediatamente
        # print(" ".join(msg))

    def es_debug(self):
        return self._log.isEnabledFor(logging.DEBUG)

    def es_info(self):
        return self._log.isEnabledFor(logging.INFO)
