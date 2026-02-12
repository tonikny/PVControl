# -*- coding: utf-8 -*-
"""
Módulo Gestor de Base de Datos

Este módulo proporciona una interfaz segura y reutilizable para el almacenamiento de datos
de equipos en PVControl+. Usa consultas parametrizadas para prevenir vulnerabilidades de
inyección SQL y proporciona gestión adecuada de conexiones.

La configuración se importa automáticamente desde Parametros_FV.py (o Parametros_FV_DIST.py
como respaldo).

Características principales:
- Protección contra inyección SQL mediante consultas parametrizadas
- Reintento automático de conexión en caso de fallo
- Operaciones seguras para hilos
- Limpieza adecuada de recursos
- Importación automática de configuración desde Parametros_FV.py

Uso:
    from helpers.gestor_bd import GestorBD
    
    # Inicializar con configuración auto-importada de Parametros_FV.py
    gestor = GestorBD()
    
    # O sobreescribir con parámetros explícitos
    gestor = GestorBD(
        servidor='localhost',
        usuario='pvcontrol',
        clave='password',
        basedatos='PVControl'
    )
    
    # Guardar datos de equipo
    gestor.guardar_datos_equipo(
        id_equipo='INVERTER1',
        tiempo='2024-01-28 12:00:00',
        sensores_json='{"Vbat": 48.5, "SOC": 85}'
    )
    
    # Limpieza
    gestor.cerrar()
"""

from typing import Dict, Any, Optional
import json
import MySQLdb
from helpers.gestor_parametros import GestorParametros


class GestorBD:
    """
    Gestiona operaciones de base de datos para datos de equipos de PVControl+.
    
    Proporciona acceso seguro y parametrizado a la base de datos con gestión automática
    de conexiones. La configuración se importa automáticamente.
    """
    
    def __init__(self, servidor: Optional[str] = None, usuario: Optional[str] = None, 
                 clave: Optional[str] = None, basedatos: Optional[str] = None):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            servidor: Nombre del servidor o IP (por defecto: auto-importado de parametros de PVControl+)
            usuario: Usuario de base de datos (por defecto: auto-importado de parametros de PVControl+)
            clave: Contraseña de base de datos (por defecto: auto-importado de parametros de PVControl+)
            basedatos: Nombre de base de datos (por defecto: auto-importado de parametros de PVControl+)

        Los parámetros pueden proporcionarse explícitamente para sobreescribir los valores por defecto.
        
        Raises:
            MySQLdb.Error: Si la conexión falla
            ValueError: Si no se proporcionan parámetros y no existen en los parametros de PVControl+
        """

        # Importar configuración de base de datos
        gestor = GestorParametros()
        servidor_cfg, usuario_cfg, clave_cfg, basedatos_cfg = gestor.leer_parametros("servidor", "usuario", "clave", "basedatos")
        
        # Usar parámetros proporcionados o valores importados como respaldo
        self.servidor = servidor or servidor_cfg
        self.usuario = usuario or usuario_cfg
        self.clave = clave or clave_cfg
        self.nombre_bd = basedatos or basedatos_cfg
        
        if not all([self.servidor, self.usuario, self.clave, self.nombre_bd]):
            raise ValueError(
                "Los parámetros de base de datos deben proporcionarse explícitamente o existir en los parámetros de PVControl+"
                f"Faltan: servidor={self.servidor}, usuario={self.usuario}, basedatos={self.nombre_bd}"
            )
        
        self.conexion: Optional[MySQLdb.Connection] = None
        self.cursor: Optional[MySQLdb.cursors.Cursor] = None
        
        self._conectar()
    
    def _conectar(self) -> None:
        """
        Establece la conexión y cursor de base de datos.
        
        Raises:
            MySQLdb.Error: Si la conexión falla
        """
        self.conexion = MySQLdb.connect(
            host=self.servidor,
            user=self.usuario,
            passwd=self.clave,
            db=self.nombre_bd
        )
        self.cursor = self.conexion.cursor()
        if not self.conexion or not self.cursor:
            raise MySQLdb.Error("No se pudo conectar a la base de datos")
    
    def _asegurar_conexion(self) -> None:
        """
        Verifica que la conexión esté activa, reconecta si es necesario.
        """
        try:
            if self.conexion:
                self.conexion.ping()
        except MySQLdb.MySQLError:
            self._conectar()
    
    def guardar_datos_equipo(self, id_equipo: str, tiempo: str, 
                            sensores_json: str) -> bool:
        """
        Guarda o actualiza los datos de sensores del equipo usando consulta parametrizada.
        
        Este método usa consultas parametrizadas para prevenir vulnerabilidades de inyección SQL.
        Actualiza las columnas 'tiempo' y 'sensores' para el equipo especificado.
        
        Args:
            id_equipo: Identificador del equipo (ej. 'INVERTER1', 'ANENJI1')
            tiempo: Marca de tiempo en formato 'YYYY-MM-DD HH:MM:SS'
            sensores_json: Cadena JSON con datos de sensores
        
        Returns:
            True si el guardado fue exitoso, False en caso contrario
        
        Ejemplo:
            >>> gestor.guardar_datos_equipo(
            ...     id_equipo='INVERTER1',
            ...     tiempo='2024-01-28 12:00:00',
            ...     sensores_json='{"Vbat": 48.5, "Ibat": -5.2}'
            ... )
            True
        """
        try:
            self._asegurar_conexion()
            
            # Usar consulta parametrizada para prevenir inyección SQL
            sql = """
                UPDATE equipos 
                SET tiempo = %s, sensores = %s 
                WHERE id_equipo = %s
            """
            
            self.cursor.execute(sql, (tiempo, sensores_json, id_equipo))
            self.conexion.commit()
            return True
            
        except MySQLdb.MySQLError as e:
            print(f"Error guardando datos para {id_equipo}: {type(e).__name__} - {e}")
            return False
    
    def guardar_datos_equipo_dict(self, id_equipo: str, tiempo: str, 
                                  sensores_dict: Dict[str, Any]) -> bool:
        """
        Guarda datos de equipo desde un diccionario (wrapper de guardar_datos_equipo).
        
        Args:
            id_equipo: Identificador del equipo
            tiempo: Marca de tiempo en formato 'YYYY-MM-DD HH:MM:SS'
            sensores_dict: Diccionario con datos de sensores
        
        Returns:
            True si el guardado fue exitoso, False en caso contrario
        """
        try:
            sensores_json = json.dumps(sensores_dict)
            return self.guardar_datos_equipo(id_equipo, tiempo, sensores_json)
        except (TypeError, ValueError) as e:
            print(f"Error serializando datos de sensores: {e}")
            return False
    
    def insertar_equipo_si_falta(self, id_equipo: str) -> bool:
        """
        Inserta registro de equipo si no existe (operación idempotente).
        
        Usa consulta parametrizada para insertar de forma segura una nueva entrada de equipo.
        Si el equipo ya existe, esta operación fallará silenciosamente
        (excepción capturada retorna False).
        
        Args:
            id_equipo: Identificador del equipo a insertar
        
        Returns:
            True si se inserta correctamente, False si ya existe o hay error
        
        Ejemplo:
            >>> gestor.insertar_equipo_si_falta('INVERTER1')
            True
        """
        try:
            self._asegurar_conexion()
            
            # Usar consulta parametrizada
            sql = """
                INSERT INTO equipos (id_equipo, sensores) 
                VALUES (%s, %s)
            """
            #  
            self.cursor.execute(sql, (id_equipo, '{}'))
            self.conexion.commit()
            return True
            
        except MySQLdb.Error:
            # El equipo probablemente ya existe (error de clave duplicada)
            return False
    
    def obtener_datos_equipo(self, id_equipo: str) -> Optional[Dict[str, Any]]:
        """
        Recupera datos de sensores del equipo.
        
        Args:
            id_equipo: Identificador del equipo
        
        Returns:
            Diccionario con datos del equipo o None si no se encuentra
        """
        try:
            self._asegurar_conexion()
            
            sql = """
                SELECT tiempo, sensores 
                FROM equipos 
                WHERE id_equipo = %s
            """
            
            self.cursor.execute(sql, (id_equipo,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                tiempo, sensores_json = resultado
                sensores = json.loads(sensores_json) if sensores_json else {}
                return {
                    'tiempo': tiempo,
                    'sensores': sensores
                }
            return None
            
        except MySQLdb.Error as e:
            print(f"Error recuperando datos para {id_equipo}: {e}")
            return None
    
    def confirmar(self) -> None:
        """
        Confirma transacciones pendientes.
        """
        if self.conexion:
            self.conexion.commit()
    
    def revertir(self) -> None:
        """
        Revierte transacciones pendientes.
        """
        if self.conexion:
            self.conexion.rollback()
    
    def cerrar(self) -> None:
        """
        Cierra la conexión y cursor de base de datos.
        
        Debe llamarse cuando se termina con las operaciones de base de datos para liberar recursos.
        """
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
        self.cursor = None
        self.conexion = None
    
    def __enter__(self):
        """Entrada del context manager."""
        return self
    
    def __exit__(self, tipo_exc, valor_exc, tb_exc):
        """Salida del context manager con limpieza automática."""
        self.cerrar()
        return False
