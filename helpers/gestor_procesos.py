# -*- coding: utf-8 -*-
"""
Gestor de Procesos para PVControl+

Gestiona el ciclo de vida de procesos multiprocessing para captura de datos.

Características:
- Inicio ordenado de múltiples procesos
- Delay configurable entre procesos (evita contención I2C/bus)
- Monitoreo con is_alive()
- Reinicio automático de procesos caídos
- Shutdown limpio con KeyboardInterrupt

Uso:
    from helpers.gestor_procesos import GestorProcesos
    
    def mi_funcion_captura(indice, config, args_extra):
        # Tu lógica de captura aquí
        pass
    
    gestor = GestorProcesos(
        nombre='fv_ads',
        funcion_captura=mi_funcion_captura,
        lista_equipos=lista_ads,
        args_extra=config_bd,
        tiempo_entre_procesos=8
    )
    
    gestor.ejecutar()
"""
from multiprocessing.process import BaseProcess

import sys
import time
import multiprocessing
from typing import Callable, Dict, List, Any, Optional

from helpers.logger import Logger


class GestorProcesos:
    """
    Gestiona procesos multiprocessing para captura de datos.
    
    Atributos:
        nombre: Nombre del servicio (ej: 'fv_ads', 'fv_rs485')
        funcion_captura: Función que se ejecuta en cada proceso
        lista_equipos: Lista de dicts con configuración de equipos
        args_extra: Argumentos extra para pasar a funcion_captura
        tiempo_entre_procesos: Segundos entre inicio de procesos
        log: Logger para este gestor
    """
    
    def __init__(
        self,
        nombre: str,
        funcion_captura: Callable,
        lista_equipos: List[Dict[str, Any]],
        args_extra: Optional[Dict[str, Any]] = None,
        tiempo_entre_procesos: float = 0
    ):
        """
        Inicializa el gestor de procesos.

        Args:
            nombre: Nombre del servicio
            funcion_captura: Función que se ejecuta en cada proceso
                             Firma: func(indice, config_equipo, args_extra)
            lista_equipos: Lista de configuraciones de equipos
            args_extra: Argumentos extra para funcion_captura
            tiempo_entre_procesos: Delay entre inicio de procesos
        """
        self.nombre = nombre
        self.funcion_captura = funcion_captura
        self.lista_equipos = lista_equipos
        self.args_extra = args_extra or {}
        self.tiempo_entre_procesos = tiempo_entre_procesos

        self.log = Logger(f'{nombre}.gestor')
        self.procesos: List[BaseProcess] = []
    
    def _crear_proceso(self, indice: int, config: dict) -> multiprocessing.Process:
        """Crea un nuevo proceso para un equipo."""
        return multiprocessing.Process(
            target=self.funcion_captura,
            args=(indice, config, self.args_extra),
            name=f'p_{config["id"]}'
        )
    
    def _iniciar_todos(self) -> None:
        """Inicia todos los procesos en el orden dado."""
        for i, equipo in enumerate(self.lista_equipos):
            self.log.info(f"Iniciando proceso para {equipo['id']} (intento 1)")
            
            p = self._crear_proceso(i, equipo)
            p.start()
            self.procesos.append(p)
            
            # Delay entre procesos
            if i < len(self.lista_equipos) - 1 and self.tiempo_entre_procesos > 0:
                self.log.info(
                    f"Esperando {self.tiempo_entre_procesos}s antes "
                    f"de iniciar siguiente equipo..."
                )
                time.sleep(self.tiempo_entre_procesos)
    
    def _reiniciar_proceso(self, proceso_caído: BaseProcess) -> None:
        """Reinicia un proceso caído."""
        nombre_equipo = proceso_caído.name.replace('p_', '')
        
        self.log.warning(f"Proceso {proceso_caído} parado {proceso_caído.name}")
        time.sleep(3)  # Pequeña espera antes de reiniciar
        
        # Buscar configuración del equipo
        for i, equipo in enumerate(self.lista_equipos):
            if equipo['id'] == nombre_equipo:
                self.log.info(f"Reiniciando proceso para {nombre_equipo}")
                
                nuevo_p = self._crear_proceso(i, equipo)
                nuevo_p.start()
                
                # Reemplazar en lista
                self.procesos[self.procesos.index(proceso_caído)] = nuevo_p
                break
        
        # Actualizar lista de procesos activos
        self.procesos: list[BaseProcess] = multiprocessing.active_children()
    
    def _monitorear(self) -> None:
        """Bucle de monitoreo de procesos."""
        while True:
            try:
                # Verificar procesos caídos
                for p in list(self.procesos):  # Copia para iterar seguro
                    if not p.is_alive():
                        self._reiniciar_proceso(p)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                self._apagar()
                sys.exit(0)
    
    def _apagar(self) -> None:
        """Apaga todos los procesos limpiamente."""
        self.log.info("Finalizando por KeyboardInterrupt")
        
        for p in self.procesos:
            self.log.info(f"Terminando proceso {p}")
            p.terminate()
            time.sleep(0.5)
    
    def ejecutar(self) -> None:
        """
        Ejecuta el gestor: inicia todos los procesos y los monitorea.

        Este método es bloqueante y no retorna hasta KeyboardInterrupt.
        """
        self.log.info(f"Iniciando gestor de procesos para {self.nombre}")
        self._iniciar_todos()

        self.log.info(
            f"Procesos activos: {multiprocessing.active_children()}"
        )

        self._monitorear()
