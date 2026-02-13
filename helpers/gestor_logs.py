import logging
import os


class GestorLogs:
    """
    Gestor de logs sencillo por script.

    Parámetros:
        level: nivel de logging (por defecto logging.ERROR o variable LOGLEVEL)
        nombre: nombre del logger (por defecto "pvcontrol")
    """

    def __init__(self, nombre="pvcontrol", level=logging.ERROR):
        """
        Inicializa un logger básico para el módulo.

        Args:
            level: nivel de logging
            nombre: nombre del logger
        """
        self._log = logging.getLogger(nombre)

        # Coger el nivel de logging de la variable de entorno LOGLEVEL
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
            # Use the default level if no environment variable is set
            self._log.setLevel(level)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(levelname)s] [%(processName)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        self._log.handlers.clear()
        self._log.addHandler(handler)

    def debug(self, *msg):
        self._log.debug(" ".join(msg))

    def info(self, *msg):
        self._log.info(" ".join(msg))

    def warning(self, *msg):
        self._log.warning(" ".join(msg))

    def error(self, *msg):
        self._log.error(" ".join(msg))

    def manual(self, *msg):
        formatter = self._log.handlers[0].formatter
        assert isinstance(formatter, logging.Formatter)
        formato_original = formatter._style._fmt
        formatter._style._fmt = "[MANUAL] [%(processName)s] %(name)s: %(message)s"
        self._log.critical(" ".join(msg))
        formatter._style._fmt = formato_original

    def es_debug(self):
        return self._log.isEnabledFor(logging.DEBUG)

    def es_info(self):
        return self._log.isEnabledFor(logging.INFO)
