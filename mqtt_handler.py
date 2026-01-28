# -*- coding: utf-8 -*-
"""
MQTT Handler Module

This module provides a clean interface for MQTT communication in PVControl+ applications.
It handles connection management, topic subscription, and thread-safe command queue
management for equipment control.

Configuration is automatically imported from Parametros_FV.py (or Parametros_FV_DIST.py as fallback).

Key Features:
- Automatic reconnection handling
- Thread-safe command queue using queue.Queue
- Equipment-specific topic subscription
- Customizable message callbacks
- Auto-imports configuration from Parametros_FV.py

Usage:
    from mqtt_handler import MQTTHandler
    
    def handle_message(equipo, comando):
        print(f"Received command '{comando}' for equipment '{equipo}'")
    
    # Initialize with auto-imported config from Parametros_FV.py
    mqtt = MQTTHandler(on_message_callback=handle_message)
    
    # Or override with explicit parameters
    mqtt = MQTTHandler(
        broker='localhost',
        puerto=1883,
        usuario='mqtt_user',
        clave='mqtt_pass',
        on_message_callback=handle_message
    )
    
    # Subscribe to equipment topics
    mqtt.subscribe_equipment(['INVERTER1', 'ANENJI1'])
    
    # Start listening
    mqtt.connect()
    
    # Check for pending commands (non-blocking)
    cmd = mqtt.get_pending_command()
    if cmd:
        print(f"Processing: {cmd['equipo']} -> {cmd['comando']}")
    
    # Cleanup
    mqtt.disconnect()
"""

import paho.mqtt.client as mqtt
from typing import Optional, List, Callable, Dict
import queue
import time

# Import MQTT configuration from Parametros_FV.py
# Falls back to Parametros_FV_DIST.py if Parametros_FV.py doesn't exist
try:
    from Parametros_FV import mqtt_broker, mqtt_puerto, mqtt_usuario, mqtt_clave
except ImportError:
    try:
        from Parametros_FV_DIST import mqtt_broker, mqtt_puerto, mqtt_usuario, mqtt_clave
    except ImportError:
        # If neither file exists, set to None (will require explicit parameters)
        mqtt_broker = None
        mqtt_puerto = None
        mqtt_usuario = None
        mqtt_clave = None


class MQTTHandler:
    """
    Manages MQTT connections and message handling for PVControl+ equipment.
    
    Provides thread-safe command queue and automatic reconnection.
    Configuration is automatically imported from Parametros_FV.py at module level.
    """
    
    def __init__(self, broker: Optional[str] = None, puerto: Optional[int] = None, 
                 usuario: Optional[str] = None, clave: Optional[str] = None,
                 on_message_callback: Optional[Callable[[str, str], None]] = None,
                 debug: bool = False):
        """
        Initialize MQTT handler.
        
        Args:
            broker: MQTT broker hostname or IP (default: auto-imported 'mqtt_broker' from Parametros_FV.py)
            puerto: MQTT broker port (default: auto-imported 'mqtt_puerto' from Parametros_FV.py)
            usuario: MQTT username (default: auto-imported 'mqtt_usuario' from Parametros_FV.py)
            clave: MQTT password (default: auto-imported 'mqtt_clave' from Parametros_FV.py)
            on_message_callback: Optional callback function(equipo, comando)
            debug: Enable debug output
        
        Configuration is imported from Parametros_FV.py at module level.
        Parameters can be explicitly provided to override the imported defaults.
        """
        # Use provided parameters or fall back to module-level imported config
        self.broker = broker or mqtt_broker
        self.puerto = puerto or mqtt_puerto
        self.usuario = usuario or mqtt_usuario
        self.clave = clave or mqtt_clave
        self.debug = debug
        self.on_message_callback = on_message_callback
        
        if not all([self.broker, self.puerto, self.usuario, self.clave]):
            raise ValueError(
                "MQTT parameters must be provided explicitly or imported from Parametros_FV.py. "
                f"Missing: broker={self.broker}, puerto={self.puerto}, usuario={self.usuario}"
            )
        
        # Thread-safe command queue (replaces global comando_mqtt)
        self.command_queue: queue.Queue = queue.Queue()
        
        # Equipment list for subscriptions
        self.equipos: List[str] = []
        
        # Create MQTT client
        self.client: Optional[mqtt.Client] = None
        self._setup_client()
    
    def _setup_client(self) -> None:
        """
        Setup MQTT client with callbacks.
        """
        # Use a unique client ID based on timestamp to avoid conflicts
        client_id = f"PVControl_{int(time.time())}"
        self.client = mqtt.Client(client_id)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Set reconnection parameters
        self.client.reconnect_delay_set(min_delay=3, max_delay=15)
        
        # Set credentials
        self.client.username_pw_set(self.usuario, password=self.clave)
    
    def _on_connect(self, client, userdata, flags, rc) -> None:
        """
        Internal callback for MQTT connection.
        
        Automatically subscribes to all registered equipment topics.
        """
        if rc == 0:
            if self.debug:
                print(f"MQTT Connected to {self.broker}:{self.puerto}")
            
            # Subscribe to all equipment topics
            for equipo in self.equipos:
                topic = f"PVControl/{equipo}"
                client.subscribe(topic)
                if self.debug:
                    print(f"Subscribed to topic: {topic}")
        else:
            print(f"MQTT Connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc) -> None:
        """
        Internal callback for MQTT disconnection.
        
        Handles automatic reconnection.
        """
        if rc != 0:
            print(f"MQTT Disconnected unexpectedly (rc={rc}), will attempt reconnection")
        else:
            # Clean disconnect
            client.loop_stop()
    
    def _on_message(self, client, userdata, msg) -> None:
        """
        Internal callback for received MQTT messages.
        
        Extracts equipment ID and command, adds to queue, and calls user callback.
        """
        try:
            # Extract equipment from topic (format: "PVControl/EQUIPMENT")
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 2:
                equipo = topic_parts[1].upper()
            else:
                equipo = msg.topic.upper()
            
            # Decode message
            comando = msg.payload.decode().strip()
            
            if self.debug:
                print(f"MQTT Message: {equipo} -> {comando}")
            
            # Add to command queue
            command_dict = {'equipo': equipo, 'comando': comando}
            self.command_queue.put(command_dict)
            
            # Call user callback if provided
            if self.on_message_callback:
                self.on_message_callback(equipo, comando)
                
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def subscribe_equipment(self, equipos: List[str]) -> None:
        """
        Register equipment list for topic subscription.
        
        Topics will be subscribed in format: PVControl/{equipo}
        
        Args:
            equipos: List of equipment identifiers (e.g., ['INVERTER1', 'ANENJI1'])
        """
        self.equipos = equipos
    
    def connect(self) -> bool:
        """
        Connect to MQTT broker and start message loop.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client.connect(self.broker, self.puerto)
            time.sleep(0.2)  # Allow connection to establish
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Error connecting to MQTT broker at {self.broker}:{self.puerto}: {e}")
            return False
    
    def get_pending_command(self) -> Optional[Dict[str, str]]:
        """
        Get next pending command from queue (non-blocking).
        
        Returns:
            Dictionary with 'equipo' and 'comando' keys, or None if queue empty
        
        Example:
            >>> cmd = mqtt.get_pending_command()
            >>> if cmd:
            ...     print(f"{cmd['equipo']}: {cmd['comando']}")
        """
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def has_pending_commands(self) -> bool:
        """
        Check if command queue has pending items.
        
        Returns:
            True if commands are waiting, False otherwise
        """
        return not self.command_queue.empty()
    
    def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> bool:
        """
        Publish message to MQTT topic.
        
        Args:
            topic: MQTT topic string
            payload: Message payload
            qos: Quality of Service level (0, 1, or 2)
            retain: Whether broker should retain message
        
        Returns:
            True if publish successful, False otherwise
        """
        try:
            result = self.client.publish(topic, payload, qos=qos, retain=retain)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error publishing to {topic}: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from MQTT broker and stop message loop.
        """
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.disconnect()
        return False
