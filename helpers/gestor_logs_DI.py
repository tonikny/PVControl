import multiprocessing
import logging
import os
import sys
import atexit
from logging.handlers import QueueHandler, QueueListener
from typing import Protocol


class LoggerProtocol(Protocol):
    """
    Protocolo que define la interfaz para la funcionalidad de logging.
    """
    def debug(self, *msg) -> None: ...
    def info(self, *msg) -> None: ...
    def warning(self, *msg) -> None: ...
    def error(self, *msg) -> None: ...
    def manual(self, *msg) -> None: ...
    def es_debug(self) -> bool: ...
    def es_info(self) -> bool: ...


class GestorLogsDI:
    """
    Gestor de logs sencillo por script con soporte para inyección de dependencias.
    Compatible con entornos multiproceso.

    Parámetros:
        level: nivel de logging (por defecto logging.ERROR o variable LOGLEVEL)
        nombre: nombre del logger (por defecto "pvcontrol")
    """

    # Variables de clase para el sistema de logging multiproceso
    _log_queue = None
    _log_listener = None
    _main_logger = None
    _initialized = False
    _lock = multiprocessing.Lock()  # Bloqueo para inicialización segura en hilos

    def __init__(self, nombre="pvcontrol", level=None):
        """
        Inicializa un logger básico para el módulo.

        Args:
            nombre: nombre del logger (por defecto "pvcontrol")
            level: nivel de logging (por defecto determinado por argumentos de línea de comandos)
        """
        # Inicializar el sistema de logging multiproceso si aún no se ha hecho
        self._initialize_multiprocess_logging()

        # Crear un logger que use el manejador de cola para seguridad multiproceso
        self._log = logging.getLogger(nombre)

        # Si no se proporciona un nivel, determinarlo desde los argumentos de línea de comandos
        if level is None:
            level = self._get_level_from_cmd_args()

        # Agregar manejador de cola para seguridad multiproceso
        queue_handler = QueueHandler(GestorLogsDI._log_queue)
        if not any(isinstance(h, QueueHandler) for h in self._log.handlers):
            self._log.addHandler(queue_handler)

        # Establecer el nivel - Verificar primero la variable de entorno LOGLEVEL
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

    @classmethod
    def _initialize_multiprocess_logging(cls):
        """Inicializa el sistema de logging multiproceso seguro."""
        with cls._lock:
            if cls._initialized:
                return

            # Crear una cola para registros de log
            cls._log_queue = multiprocessing.Queue()

            # Crear el logger principal
            cls._main_logger = logging.getLogger("PVControl")
            cls._main_logger.setLevel(logging.DEBUG)

            # Crear un manejador para el logger principal (consola, archivo, etc.)
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('[%(levelname)s] [%(processName)s] %(name)s: %(message)s')
            handler.setFormatter(formatter)
            cls._main_logger.addHandler(handler)

            # Crear un listener que consumirá los registros de log desde la cola
            cls._log_listener = QueueListener(cls._log_queue, handler, respect_handler_level=True)
            cls._log_listener.start()

            cls._initialized = True

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

    def _format_message(self, *msg):
        """Formatea el mensaje asegurando que los códigos de color se reseteen correctamente."""
        mensaje = " ".join(msg)
        # Asegurar que el mensaje tenga un reset code para ressetear los colores
        if '\x1b[' in mensaje:
            mensaje += '\x1b[0m'
        return mensaje

    def debug(self, *msg):
        mensaje = self._format_message(*msg)
        self._log.debug(mensaje)

    def info(self, *msg):
        mensaje = self._format_message(*msg)
        self._log.info(mensaje)

    def warning(self, *msg):
        mensaje = self._format_message(*msg)
        self._log.warning(mensaje)

    def error(self, *msg):
        mensaje = self._format_message(*msg)
        self._log.error(mensaje)

    def manual(self, *msg):
        """
        Muestra un mensaje manual que siempre se registra,
        independientemente del nivel de log actual.
        """
        # Enviar el mensaje directamente a los mismos handlers del logger principal
        # para asegurar que vaya a todas las salidas configuradas (archivo, consola, etc.)
        mensaje = f"[MANUAL] {self._log.name}: {' '.join(msg)}"

        # Escribir directamente a los mismos streams de salida que el logger principal
        # y asegurar que se reseteen los colores para no afectar otros mensajes
        if GestorLogsDI._main_logger:
            for handler in GestorLogsDI._main_logger.handlers:
                if hasattr(handler, 'stream'):
                    # Resetear colores antes de escribir el mensaje manual
                    handler.stream.write('\x1b[0m')  # Resetear todos los estilos
                    handler.stream.write(mensaje + "\n")
                    # Escribir un código de reseteo de color ANSI al final
                    handler.stream.write('\x1b[0m')  # Código ANSI para resetear todos los estilos
                    handler.stream.flush()

    def es_debug(self):
        return self._log.isEnabledFor(logging.DEBUG)

    def es_info(self):
        return self._log.isEnabledFor(logging.INFO)

    @classmethod
    def cleanup(cls):
        """Limpia el sistema de logging."""
        if cls._log_listener:
            cls._log_listener.stop()
        cls._initialized = False


# Registrar la limpieza automática al salir del programa
atexit.register(GestorLogsDI.cleanup)