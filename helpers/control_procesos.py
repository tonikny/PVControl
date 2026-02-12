import multiprocessing
import time
import sys
from colorama import Fore

from helpers.gestor_logs import GestorLogs

log = GestorLogs(__name__)

def iniciar_procesos(activos, ejecucion):
    """Inicia los procesos de captura para cada equipo activo."""
    procesos = []
    for idx, actual in enumerate(activos):
        log.info(f"Activando equipo: {actual['id']}")
        proceso = multiprocessing.Process(
            target=ejecucion, args=(actual, idx), name=f"p_{actual['id']}"
        )
        proceso.start()
        procesos.append(proceso)

    log.info(f"Procesos activos= {procesos}")
    return procesos


def vigilar_procesos(procesos, activos, ejecucion):
    """Vigila los procesos activos y reinicia los que han terminado."""
    while True:
        proceso = None
        try:
            for p in procesos:
                proceso = p
                if not p.is_alive():
                    log.info(f"Proceso {p} parado {p.name}")
                    time.sleep(3)
                    nombre = p.name[2:]
                    actual = None
                    indice = None
                    for obj,idx in activos:
                        if obj.id == nombre:
                            actual = obj
                            indice = idx
                            break
                    if not actual:
                        log.error(f"Error: equipo {nombre} no encontrado")
                        continue
                    nuevo_proceso = multiprocessing.Process(
                        target=ejecucion, args=(actual, indice), name=f"p_{nombre}"
                    )
                    nuevo_proceso.start()
                    procesos = multiprocessing.active_children()

            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            log.error()
            log.error(Fore.RED + "=" * 50)
            log.error("Finalizando proceso...", proceso.name if proceso else "desconocido")
            for p in procesos:
                log.error(f"     ....Terminando hilo..{p}")
                p.terminate()
                time.sleep(1)
            sys.exit()
