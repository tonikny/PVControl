"""
Sistema de logging especializado para aplicaciones multiproceso de PVControl+

Este módulo proporciona una clase LoggerMultiprocessing que está diseñada específicamente
para manejar logging en entornos multiproceso como los usados en PVControl+.
"""

import multiprocessing
import logging
import os
import sys
import atexit
from logging.handlers import QueueHandler, QueueListener
from typing import Optional


class LoggerMultiprocessing:
    """
    Sistema de logging especializado para aplicaciones multiproceso de PVControl+.
    
    Esta clase proporciona un sistema de logging seguro para entornos multiproceso,
    donde múltiples procesos necesitan escribir logs sin causar problemas de sincronización.
    
    Args:
        nombre: Nombre del logger (por defecto "pvcontrol")
        nivel: Nivel de logging (por defecto se determina desde argumentos de línea de comandos)
    """
    
    # Variables de clase para el sistema de logging multiproceso
    _log_queue: Optional[multiprocessing.Queue] = None
    _log_listener: Optional[QueueListener] = None
    _main_logger: Optional[logging.Logger] = None
    _initialized = False
    _lock = multiprocessing.Lock()  # Bloqueo para inicialización segura en hilos
    _init_pid: Optional[int] = None  # PID donde se inicializó

    def __init__(self, nombre: str = "pvcontrol", nivel: Optional[int] = None):
        """
        Inicializa un logger seguro para entornos multiproceso.
        
        Args:
            nombre: Nombre del logger (por defecto "pvcontrol")
            nivel: Nivel de logging (por defecto determinado por argumentos de línea de comandos)
        """
        # Inicializar el sistema de logging multiproceso si aún no se ha hecho
        self._initialize_multiprocess_logging()

        # Crear un logger que use el manejador de cola para seguridad multiproceso
        self._log = logging.getLogger(nombre)

        # Si no se proporciona un nivel, determinarlo desde los argumentos de línea de comandos
        if nivel is None:
            nivel = self._get_level_from_cmd_args()

        # Agregar manejador de cola para seguridad multiproceso
        queue_handler = QueueHandler(LoggerMultiprocessing._log_queue)
        if not any(isinstance(h, QueueHandler) for h in self._log.handlers):
            self._log.addHandler(queue_handler)

        # Set the level - Check for LOGLEVEL environment variable first
        env_level = os.getenv("LOGLEVEL")
        if env_level:
            try:
                level_value = getattr(logging, env_level.upper())
                self._log.setLevel(level_value)
            except AttributeError:
                self._log.warning(
                    f"Nivel de logging no reconocido: {env_level}, "
                    f"usando valor por defecto: {nivel}"
                )
                self._log.setLevel(nivel)
        else:
            # Usar el nivel por defecto si no se establece variable de entorno
            self._log.setLevel(nivel)

    @classmethod
    def _initialize_multiprocess_logging(cls):
        """Inicializa el sistema de logging multiproceso seguro."""
        current_pid = os.getpid()
        
        # Detectar si estamos en un proceso forked
        if cls._initialized and cls._init_pid != current_pid:
            # Estamos en un proceso hijo después de un fork
            # Necesitamos re-inicializar para evitar deadlocks
            cls._initialized = False
            cls._lock = multiprocessing.Lock()
        
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
            cls._init_pid = current_pid

    def _get_level_from_cmd_args(self) -> int:
        """Determina el nivel de logging basado en los argumentos de línea de comandos."""
        if "-p1" in sys.argv:
            return logging.WARNING
        elif "-p2" in sys.argv:
            return logging.INFO
        elif "-p" in sys.argv:
            return logging.DEBUG
        else:
            return logging.ERROR

    def _format_message(self, *msg) -> str:
        """Formatea el mensaje asegurando que los códigos de color se reseteen correctamente."""
        message = " ".join(msg)
        # Asegurar que el mensaje tenga un reset code para ressetear los colores
        if '\x1b[' in message:
            message += '\x1b[0m'
        return message

    def debug(self, *msg) -> None:
        message = self._format_message(*msg)
        self._log.debug(message)

    def info(self, *msg) -> None:
        message = self._format_message(*msg)
        self._log.info(message)

    def warning(self, *msg) -> None:
        message = self._format_message(*msg)
        self._log.warning(message)

    def error(self, *msg) -> None:
        message = self._format_message(*msg)
        self._log.error(message)

    def manual(self, *msg) -> None:
        """
        Muestra un mensaje manual que siempre se registra,
        independientemente del nivel de log actual.
        """
        # Enviar el mensaje directamente a los mismos handlers del logger principal
        # para asegurar que vaya a todas las salidas configuradas (archivo, consola, etc.)
        message = f"[MANUAL] {self._log.name}: {' '.join(msg)}"

        # Escribir directamente a los mismos streams de salida que el logger principal
        # y asegurar que se reseteen los colores para no afectar otros mensajes
        if LoggerMultiprocessing._main_logger:
            for handler in LoggerMultiprocessing._main_logger.handlers:
                if hasattr(handler, 'stream'):
                    # Resetear colores antes de escribir el mensaje manual
                    handler.stream.write('\x1b[0m')  # Resetear todos los estilos
                    handler.stream.write(message + "\n")
                    # Escribir un código de reseteo de color ANSI al final
                    handler.stream.write('\x1b[0m')  # Código ANSI para resetear todos los estilos
                    handler.stream.flush()

    def es_debug(self) -> bool:
        return self._log.isEnabledFor(logging.DEBUG)

    def es_info(self) -> bool:
        return self._log.isEnabledFor(logging.INFO)

    @classmethod
    def cleanup(cls) -> None:
        """Limpia el sistema de logging."""
        if cls._log_listener:
            cls._log_listener.stop()
        cls._initialized = False


# Registrar la limpieza automática al salir del programa
atexit.register(LoggerMultiprocessing.cleanup)