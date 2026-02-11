import multiprocessing
import time
import sys
from colorama import Fore

def iniciar_procesos(activos, ejecucion):
    """Inicia los procesos de captura para cada equipo activo."""
    procesos = []
    for idx, actual in enumerate(activos):
        print(f"Activando equipo: {actual['id']}")
        proceso = multiprocessing.Process(
            target=ejecucion, args=(actual, idx), name=f"p_{actual['id']}"
        )
        proceso.start()
        procesos.append(proceso)

    print("Procesos activos=", procesos)
    return procesos


def vigilar_procesos(procesos, activos, ejecucion):
    """Vigila los procesos activos y reinicia los que han terminado."""
    while True:
        try:
            for p in procesos:
                if not p.is_alive():
                    print(f"Proceso {p} parado {p.name}")
                    time.sleep(3)
                    nombre = p.name[2:]
                    actual = None
                    for obj,idx in activos:
                        if obj.id == nombre:
                            actual = obj
                            break
                    if not actual:
                        print(f"Error: equipo {nombre} no encontrado")
                        continue
                    nuevo_proceso = multiprocessing.Process(
                        target=ejecucion, args=(actual, idx), name=f"p_{nombre}"
                    )
                    nuevo_proceso.start()
                    procesos = multiprocessing.active_children()

            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            print()
            print(Fore.RED + "=" * 50)
            print("Finalizando proceso...", p.name)
            for p in procesos:
                print(f"     ....Terminando hilo..{p}")
                p.terminate()
                time.sleep(1)
            sys.exit()
