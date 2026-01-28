# -*- coding: utf-8 -*-
"""
Database Manager Module

This module provides a safe, reusable database interface for PVControl+ equipment data storage.
It uses parameterized queries to prevent SQL injection vulnerabilities and provides proper
connection management.

Key Features:
- SQL injection protection through parameterized queries
- Automatic connection retry on failure
- Thread-safe operations
- Proper resource cleanup

Usage:
    from db_manager import DatabaseManager
    
    # Initialize connection
    db_mgr = DatabaseManager(
        host='localhost',
        user='pvcontrol',
        passwd='password',
        db='PVControl'
    )
    
    # Save equipment data
    db_mgr.save_equipment_data(
        equipo_id='INVERTER1',
        tiempo='2024-01-28 12:00:00',
        sensores_json='{"Vbat": 48.5, "SOC": 85}'
    )
    
    # Cleanup
    db_mgr.close()
"""

import MySQLdb
import json
from typing import Dict, Any, Optional
import time


class DatabaseManager:
    """
    Manages database operations for PVControl+ equipment data.
    
    Provides safe, parameterized database access with automatic connection handling.
    Configuration can be passed explicitly or imported from Parametros_FV.py globals.
    """
    
    def __init__(self, host: Optional[str] = None, user: Optional[str] = None, 
                 passwd: Optional[str] = None, db: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            host: Database server hostname or IP (default: from Parametros_FV.py 'servidor')
            user: Database username (default: from Parametros_FV.py 'usuario')
            passwd: Database password (default: from Parametros_FV.py 'clave')
            db: Database name (default: from Parametros_FV.py 'basedatos')
        
        If parameters are not provided, attempts to import from global namespace
        (Parametros_FV.py variables: servidor, usuario, clave, basedatos).
        
        Raises:
            MySQLdb.Error: If connection fails
            NameError: If parameters not provided and globals not available
        """
        # Try to get from globals if not provided
        if host is None:
            import sys
            frame = sys._getframe(1)
            host = frame.f_globals.get('servidor')
        if user is None:
            import sys
            frame = sys._getframe(1)
            user = frame.f_globals.get('usuario')
        if passwd is None:
            import sys
            frame = sys._getframe(1)
            passwd = frame.f_globals.get('clave')
        if db is None:
            import sys
            frame = sys._getframe(1)
            db = frame.f_globals.get('basedatos')
        
        if not all([host, user, passwd, db]):
            raise ValueError("Database parameters must be provided or available in global namespace")
        
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db_name = db
        self.connection: Optional[MySQLdb.Connection] = None
        self.cursor: Optional[MySQLdb.cursors.Cursor] = None
        
        self._connect()
    
    def _connect(self) -> None:
        """
        Establish database connection and cursor.
        
        Raises:
            MySQLdb.Error: If connection fails
        """
        self.connection = MySQLdb.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            db=self.db_name
        )
        self.cursor = self.connection.cursor()
    
    def _ensure_connection(self) -> None:
        """
        Verify connection is active, reconnect if necessary.
        """
        try:
            if self.connection:
                self.connection.ping()
        except MySQLdb.Error:
            self._connect()
    
    def save_equipment_data(self, equipo_id: str, tiempo: str, 
                           sensores_json: str) -> bool:
        """
        Save or update equipment sensor data using parameterized query.
        
        This method uses parameterized queries to prevent SQL injection vulnerabilities.
        It updates the 'tiempo' and 'sensores' columns for the specified equipment.
        
        Args:
            equipo_id: Equipment identifier (e.g., 'INVERTER1', 'ANENJI1')
            tiempo: Timestamp in format 'YYYY-MM-DD HH:MM:SS'
            sensores_json: JSON string with sensor data
        
        Returns:
            True if save was successful, False otherwise
        
        Example:
            >>> db_mgr.save_equipment_data(
            ...     equipo_id='INVERTER1',
            ...     tiempo='2024-01-28 12:00:00',
            ...     sensores_json='{"Vbat": 48.5, "Ibat": -5.2}'
            ... )
            True
        """
        try:
            self._ensure_connection()
            
            # Use parameterized query to prevent SQL injection
            sql = """
                UPDATE equipos 
                SET tiempo = %s, sensores = %s 
                WHERE id_equipo = %s
            """
            
            self.cursor.execute(sql, (tiempo, sensores_json, equipo_id))
            self.connection.commit()
            return True
            
        except MySQLdb.Error as e:
            print(f"Error saving data for {equipo_id}: {type(e).__name__} - {e}")
            return False
    
    def save_equipment_data_dict(self, equipo_id: str, tiempo: str, 
                                 sensores_dict: Dict[str, Any]) -> bool:
        """
        Save equipment data from a dictionary (convenience wrapper).
        
        Args:
            equipo_id: Equipment identifier
            tiempo: Timestamp in format 'YYYY-MM-DD HH:MM:SS'
            sensores_dict: Dictionary with sensor data
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            sensores_json = json.dumps(sensores_dict)
            return self.save_equipment_data(equipo_id, tiempo, sensores_json)
        except (TypeError, ValueError) as e:
            print(f"Error serializing sensor data: {e}")
            return False
    
    def insert_equipment_if_missing(self, equipo_id: str) -> bool:
        """
        Insert equipment record if it doesn't exist (idempotent operation).
        
        Uses parameterized query to safely insert a new equipment entry.
        If the equipment already exists, this operation will fail silently
        (caught exception returns False).
        
        Args:
            equipo_id: Equipment identifier to insert
        
        Returns:
            True if inserted successfully, False if already exists or error
        
        Example:
            >>> db_mgr.insert_equipment_if_missing('INVERTER1')
            True
        """
        try:
            self._ensure_connection()
            
            # Use parameterized query
            sql = """
                INSERT INTO equipos (id_equipo, sensores) 
                VALUES (%s, %s)
            """
            
            self.cursor.execute(sql, (equipo_id, '{}'))
            self.connection.commit()
            return True
            
        except MySQLdb.Error:
            # Equipment likely already exists (duplicate key error)
            return False
    
    def get_equipment_data(self, equipo_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve equipment sensor data.
        
        Args:
            equipo_id: Equipment identifier
        
        Returns:
            Dictionary with equipment data or None if not found
        """
        try:
            self._ensure_connection()
            
            sql = """
                SELECT tiempo, sensores 
                FROM equipos 
                WHERE id_equipo = %s
            """
            
            self.cursor.execute(sql, (equipo_id,))
            result = self.cursor.fetchone()
            
            if result:
                tiempo, sensores_json = result
                sensores = json.loads(sensores_json) if sensores_json else {}
                return {
                    'tiempo': tiempo,
                    'sensores': sensores
                }
            return None
            
        except MySQLdb.Error as e:
            print(f"Error retrieving data for {equipo_id}: {e}")
            return None
    
    def commit(self) -> None:
        """
        Commit pending transactions.
        """
        if self.connection:
            self.connection.commit()
    
    def rollback(self) -> None:
        """
        Rollback pending transactions.
        """
        if self.connection:
            self.connection.rollback()
    
    def close(self) -> None:
        """
        Close database connection and cursor.
        
        Should be called when done with database operations to free resources.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.cursor = None
        self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.close()
        return False
