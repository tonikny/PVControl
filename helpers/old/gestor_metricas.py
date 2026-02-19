import time
from collections import defaultdict
from typing import Dict, List, Optional, Any

class GestorMetricas:
    """
    Gestor de métricas para monitorear el rendimiento y operación del sistema.
    """
    
    def __init__(self):
        self.metricas = defaultdict(list)
    
    def registrar_metrica(self, nombre: str, valor: float):
        """
        Registra una métrica con su valor y timestamp.
        
        Args:
            nombre: Nombre de la métrica
            valor: Valor numérico de la métrica
        """
        self.metricas[nombre].append({
            'timestamp': time.time(),
            'valor': valor
        })
    
    def obtener_promedio(self, nombre: str) -> Optional[float]:
        """
        Obtiene el promedio de una métrica.
        
        Args:
            nombre: Nombre de la métrica
            
        Returns:
            Promedio de los valores o None si no hay valores
        """
        if not self.metricas[nombre]:
            return None
        valores = [m['valor'] for m in self.metricas[nombre]]
        return sum(valores) / len(valores)
    
    def obtener_suma(self, nombre: str) -> float:
        """
        Obtiene la suma de una métrica.
        
        Args:
            nombre: Nombre de la métrica
            
        Returns:
            Suma de los valores
        """
        if not self.metricas[nombre]:
            return 0.0
        valores = [m['valor'] for m in self.metricas[nombre]]
        return sum(valores)
    
    def obtener_contador(self, nombre: str) -> int:
        """
        Obtiene el conteo de veces que se registró una métrica.
        
        Args:
            nombre: Nombre de la métrica
            
        Returns:
            Número de veces que se registró la métrica
        """
        return len(self.metricas[nombre])
    
    def limpiar_antiguas(self, segundos_maximos: int = 3600):
        """
        Elimina métricas antiguas para liberar memoria.
        
        Args:
            segundos_maximos: Tiempo máximo en segundos para mantener métricas
        """
        ahora = time.time()
        for nombre, lista in self.metricas.items():
            self.metricas[nombre] = [
                m for m in lista 
                if ahora - m['timestamp'] <= segundos_maximos
            ]
    
    def obtener_valores_recientes(self, nombre: str, segundos: int = 300) -> List[Dict[str, Any]]:
        """
        Obtiene los valores recientes de una métrica.
        
        Args:
            nombre: Nombre de la métrica
            segundos: Número de segundos hacia atrás para buscar valores
            
        Returns:
            Lista de valores recientes
        """
        ahora = time.time()
        return [
            m for m in self.metricas[nombre]
            if ahora - m['timestamp'] <= segundos
        ]
    
    def resetear_metrica(self, nombre: str):
        """
        Resetea completamente una métrica eliminando todos sus valores.
        
        Args:
            nombre: Nombre de la métrica a resetear
        """
        if nombre in self.metricas:
            del self.metricas[nombre]