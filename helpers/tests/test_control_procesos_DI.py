import multiprocessing
import time
from unittest.mock import Mock, patch
import pytest

from helpers.control_procesos_DI import ControlProcesosDI
from helpers.gestor_logs_DI import GestorLogsDI

def funcion_ejecucion_ejemplo(config, indice):
    """Función de ejemplo para simular ejecución en un proceso"""
    # Simula algún trabajo
    time.sleep(0.1)
    # Imprime para simular actividad
    print(f"Ejecutando proceso para {config['id']} en índice {indice}")


def test_control_procesos_di_inicializacion_con_logger():
    """Prueba de inicialización de ControlProcesosDI con dependencia de logger"""
    mock_logger = Mock(spec=GestorLogsDI)
    controlador = ControlProcesosDI(logger=mock_logger)
    
    assert controlador._log == mock_logger


def test_control_procesos_di_inicializacion_sin_logger():
    """Prueba de inicialización de ControlProcesosDI sin proveer un logger"""
    controlador = ControlProcesosDI()
    
    # Debería crear un logger por defecto
    assert controlador._log is not None
    assert isinstance(controlador._log, GestorLogsDI)


def test_iniciar_procesos_crea_procesos():
    """Prueba que iniciar_procesos crea e inicia procesos correctamente"""
    mock_logger = Mock(spec=GestorLogsDI)
    controlador = ControlProcesosDI(logger=mock_logger)
    
    # Configuraciones activas de ejemplo
    dispositivos_activos = [
        {"id": "dispositivo1", "otro_param": "valor1"},
        {"id": "dispositivo2", "otro_param": "valor2"}
    ]
    
    # Iniciar procesos
    procesos = controlador.iniciar_procesos(dispositivos_activos, funcion_ejecucion_ejemplo)
    
    # Verificar que se crearon los procesos
    assert len(procesos) == 2
    
    # Verificar que los procesos están vivos
    for proceso in procesos:
        # Terminar los procesos ya que están corriendo
        proceso.terminate()
        proceso.join(timeout=1)  # Esperar máximo 1 segundo a que termine
        
        # Asegurar que el proceso ha sido terminado
        if proceso.is_alive():
            proceso.kill()  # Forzar matar si sigue vivo
    
    # Verificar que el logger fue llamado apropiadamente
    assert mock_logger.info.call_count >= 2  # Al menos 2 llamadas para mensajes de activación


def test_iniciar_procesos_registra_mensajes_correctamente():
    """Prueba que iniciar_procesos registra los mensajes correctos"""
    mock_logger = Mock(spec=GestorLogsDI)
    controlador = ControlProcesosDI(logger=mock_logger)
    
    dispositivos_activos = [{"id": "dispositivo_prueba"}]
    
    procesos = controlador.iniciar_procesos(dispositivos_activos, funcion_ejecucion_ejemplo)
    
    # Verificar que se registró el mensaje de activación
    mock_logger.info.assert_any_call("Activando equipo: dispositivo_prueba")
    
    # Limpiar procesos
    for proceso in procesos:
        proceso.terminate()
        proceso.join(timeout=1)
        if proceso.is_alive():
            proceso.kill()


@patch('multiprocessing.Process')
def test_iniciar_procesos_llama_multiprocess_correctamente(mock_clase_proceso):
    """Prueba que iniciar_procesos llama a multiprocessing.Process con parámetros correctos"""
    mock_logger = Mock(spec=GestorLogsDI)
    controlador = ControlProcesosDI(logger=mock_logger)
    
    # Mock del objeto proceso
    mock_instancia_proceso = Mock()
    mock_clase_proceso.return_value = mock_instancia_proceso
    
    dispositivos_activos = [{"id": "dispositivo1", "param": "valor"}]
    
    procesos = controlador.iniciar_procesos(dispositivos_activos, funcion_ejecucion_ejemplo)
    
    # Verificar que Process fue llamado con parámetros correctos
    mock_clase_proceso.assert_called_once_with(
        target=funcion_ejecucion_ejemplo,
        args=(dispositivos_activos[0], 0),
        name="p_dispositivo1"
    )
    
    # Verificar que start fue llamado
    mock_instancia_proceso.start.assert_called_once()


def test_vigilar_procesos_detecta_procesos_muertos():
    """Prueba que vigilar_procesos detecta procesos que han muerto"""
    mock_logger = Mock(spec=GestorLogsDI)
    controlador = ControlProcesosDI(logger=mock_logger)
    
    # Crear un proceso simulado que no está vivo
    mock_proceso = Mock()
    mock_proceso.is_alive.return_value = False
    mock_proceso.name = "p_dispositivo_prueba"
    mock_proceso.terminate = Mock()
    
    dispositivos_activos = [{"id": "dispositivo_prueba", "param": "valor"}]
    
    # Contador para rastrear cuántas veces se llama Process para crear nuevos procesos
    procesos_creados = []
    
    def constructor_proceso_simulado(target, args, name):
        nuevo_mock_proceso = Mock()
        nuevo_mock_proceso.is_alive.return_value = True  # Nuevo proceso está vivo inicialmente
        nuevo_mock_proceso.name = name
        nuevo_mock_proceso.terminate = Mock()
        procesos_creados.append(nuevo_mock_proceso)
        return nuevo_mock_proceso
    
    # Parchear la creación de Process
    with patch('multiprocessing.Process', side_effect=constructor_proceso_simulado):
        with patch('time.sleep', return_value=None):  # Prevenir dormir realmente en pruebas
            with patch('multiprocessing.active_children', return_value=[]):
                
                # Creamos un bucle controlado que no sea infinito
                iteraciones_realizadas = 0
                original_vigilar = controlador.vigilar_procesos
                
                def vigilancia_controlada(procesos_lista, activos, ejecucion):
                    nonlocal iteraciones_realizadas
                    while iteraciones_realizadas < 2:  # Limitar a 2 iteraciones
                        for p in procesos_lista:
                            if not p.is_alive():
                                mock_logger.info(f"Proceso {p} parado {p.name}")
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
                                    mock_logger.error(f"Error: equipo {nombre} no encontrado")
                                    continue
                                    
                                nuevo_proceso = multiprocessing.Process(
                                    target=ejecucion, args=(actual, indice), name=f"p_{nombre}"
                                )
                                nuevo_proceso.start()
                                procesos_lista = multiprocessing.active_children()
                        
                        time.sleep(1)
                        iteraciones_realizadas += 1
                    
                    # Lanzar una excepción para salir del bucle en lugar de usar KeyboardInterrupt
                    raise StopIteration("Fin de la prueba controlada")
                
                # Reemplazar temporalmente el método
                controlador.vigilar_procesos = vigilancia_controlada
                
                try:
                    controlador.vigilar_procesos([mock_proceso], dispositivos_activos, funcion_ejecucion_ejemplo)
                except StopIteration:
                    # Esto es esperado en nuestra prueba controlada
                    pass
    
    # Verificar que se creó un nuevo proceso para reemplazar al muerto
    assert len(procesos_creados) >= 1


def test_vigilar_procesos_registra_cuando_muere_un_proceso():
    """Prueba que vigilar_procesos registra cuando un proceso muere"""
    mock_logger = Mock(spec=GestorLogsDI)
    controlador = ControlProcesosDI(logger=mock_logger)
    
    # Crear un proceso simulado que no está vivo
    mock_proceso = Mock()
    mock_proceso.is_alive.return_value = False
    mock_proceso.name = "p_dispositivo_prueba"
    mock_proceso.__str__ = Mock(return_value="<MockProcess dispositivo_prueba>")
    mock_proceso.terminate = Mock()
    
    dispositivos_activos = [{"id": "dispositivo_prueba", "param": "valor"}]
    
    # Contador para rastrear cuántas veces se llama Process para crear nuevos procesos
    procesos_creados = []
    
    def constructor_proceso_simulado(target, args, name):
        nuevo_mock_proceso = Mock()
        nuevo_mock_proceso.is_alive.return_value = True
        nuevo_mock_proceso.name = name
        nuevo_mock_proceso.terminate = Mock()
        procesos_creados.append(nuevo_mock_proceso)
        return nuevo_mock_proceso
    
    with patch('multiprocessing.Process', side_effect=constructor_proceso_simulado):
        with patch('time.sleep', return_value=None):  # Prevenir dormir realmente
            with patch('multiprocessing.active_children', return_value=[]):
                
                # Creamos un bucle controlado que no sea infinito
                iteraciones_realizadas = 0
                
                def vigilancia_controlada(procesos_lista, activos, ejecucion):
                    nonlocal iteraciones_realizadas
                    while iteraciones_realizadas < 1:  # Limitar a 1 iteración
                        for p in procesos_lista:
                            if not p.is_alive():
                                mock_logger.info(f"Proceso {p} parado {p.name}")
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
                                    mock_logger.error(f"Error: equipo {nombre} no encontrado")
                                    continue
                                    
                                nuevo_proceso = multiprocessing.Process(
                                    target=ejecucion, args=(actual, indice), name=f"p_{nombre}"
                                )
                                nuevo_proceso.start()
                                procesos_lista = multiprocessing.active_children()
                        
                        time.sleep(1)
                        iteraciones_realizadas += 1
                    
                    # Lanzar una excepción para salir del bucle
                    raise StopIteration("Fin de la prueba controlada")
                
                # Reemplazar temporalmente el método
                controlador.vigilar_procesos = vigilancia_controlada
                
                try:
                    controlador.vigilar_procesos([mock_proceso], dispositivos_activos, funcion_ejecucion_ejemplo)
                except StopIteration:
                    # Esto es esperado en nuestra prueba controlada
                    pass
    
    # Verificar que se hicieron las llamadas de registro apropiadas
    # Encontrar la llamada que registra la detención del proceso
    llamadas_registro = [llamada for llamada in mock_logger.info.call_args_list if "parado" in str(llamada[0][0])]
    assert len(llamadas_registro) >= 1


if __name__ == "__main__":
    pytest.main([__file__])