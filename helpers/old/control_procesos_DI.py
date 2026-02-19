import multiprocessing
import time
import sys
from colorama import Fore
from typing import Optional, List

from helpers.gestor_logs_DI import GestorLogsDI, LoggerProtocol


class ControlProcesosDI:
    """
    Clase para gestionar procesos concurrentes con soporte para inyección de dependencias.
    
    Args:
        logger: Instancia de logger para registrar eventos (opcional)
        
    Ejemplo:
        logger = GestorLogsDI(__name__)
        controlador = ControlProcesosDI(logger=logger)
        procesos = controlador.iniciar_procesos(activos, ejecucion)
    """
    
    def __init__(self, logger: Optional[GestorLogsDI] = None):
        # Usar el logger inyectado o crear uno por defecto
        self._log = logger if logger is not None else GestorLogsDI(__name__)

    def iniciar_procesos(self, activos, ejecucion):
        """Inicia los procesos de captura para cada equipo activo."""
        procesos = []
        for idx, actual in enumerate(activos):
            self._log.info(f"Activando equipo: {actual['id']}")
            proceso = multiprocessing.Process(
                target=ejecucion, args=(actual, idx), name=f"p_{actual['id']}"
            )
            proceso.start()
            procesos.append(proceso)

        self._log.info(f"Procesos activos= {procesos}")
        return procesos

    def vigilar_procesos(self, procesos: List[multiprocessing.Process], activos, ejecucion):
        """Vigila los procesos activos y reinicia los que han terminado."""
        while True:
            proceso = None
            try:
                for p in procesos:
                    proceso = p
                    if not p.is_alive():
                        self._log.info(f"Proceso {p} parado {p.name}")
                        time.sleep(3)
                        nombre = p.name[2:]
                        actual = None
                        indice = None
                        for idx, obj in enumerate(activos):
                            if obj['id'] == nombre:
                                actual = obj
                                indice = idx
                                break
                        if not actual:
                            self._log.error(f"Error: equipo {nombre} no encontrado")
                            continue
                        nuevo_proceso = multiprocessing.Process(
                            target=ejecucion, args=(actual, indice), name=f"p_{nombre}"
                        )
                        nuevo_proceso.start()
                        procesos = multiprocessing.active_children()

                time.sleep(1)

            except KeyboardInterrupt:
                time.sleep(1)
                self._log.error("Finalizando proceso...", proceso.name if proceso else "desconocido")
                for p in procesos:
                    self._log.error(f"{Fore.RED}     ....Terminando hilo..{p}{Fore.RESET}")
                    p.terminate()
                    time.sleep(1)
                sys.exit()