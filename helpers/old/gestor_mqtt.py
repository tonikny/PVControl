"""
Módulo de gestión MQTT.

Este módulo proporciona una interfaz sencilla para comunicación MQTT en PVControl+.
Incluye gestión de conexión, suscripciones por equipo y una cola segura de comandos.

La configuración se lee desde Parametros_FV.py (o Parametros_FV_DIST.py como respaldo)
a través de GestorParametros.
"""

from typing import Optional, List, Callable, Dict
import queue
import time

import paho.mqtt.client as mqtt

from helpers.gestor_parametros import GestorParametros


class GestorMQTT:
    """
    Gestiona la conexión MQTT y el enrutado de mensajes para equipos de PVControl+.
    """

    def __init__(
        self,
        broker: Optional[str] = None,
        puerto: Optional[int] = None,
        usuario: Optional[str] = None,
        clave: Optional[str] = None,
        al_recibir: Optional[Callable[[str, str], None]] = None,
        depurar: bool = False,
    ):
        """
        Inicializa el gestor MQTT.

        Args:
            broker: servidor MQTT (por defecto auto-importado desde parámetros)
            puerto: puerto del broker (por defecto auto-importado)
            usuario: usuario MQTT (por defecto auto-importado)
            clave: contraseña MQTT (por defecto auto-importada)
            al_recibir: callback opcional (equipo, comando)
            depurar: habilita mensajes de depuración
        """
        gestor = GestorParametros()
        try:
            broker_cfg, puerto_cfg, usuario_cfg, clave_cfg = gestor.leer_parametros(
                "mqtt_broker", "mqtt_puerto", "mqtt_usuario", "mqtt_clave"
            )
        except (AttributeError, FileNotFoundError):
            broker_cfg = puerto_cfg = usuario_cfg = clave_cfg = None

        self.broker = broker or broker_cfg
        self.puerto = puerto or puerto_cfg
        self.usuario = usuario or usuario_cfg
        self.clave = clave or clave_cfg
        self.depurar = depurar
        self.al_recibir = al_recibir

        if not all([self.broker, self.puerto, self.usuario, self.clave]):
            raise ValueError(
                "Parámetros MQTT incompletos. Proporcione valores explícitos "
                "o defínalos en Parametros_FV.py."
            )

        self.cola_comandos: queue.Queue = queue.Queue()
        self.equipos: List[str] = []
        self.cliente: Optional[mqtt.Client] = None
        self._configurar_cliente()

    def _configurar_cliente(self) -> None:
        cliente_id = f"PVControl_{int(time.time())}"
        self.cliente = mqtt.Client(cliente_id)
        self.cliente.on_connect = self._al_conectar
        self.cliente.on_disconnect = self._al_desconectar
        self.cliente.on_message = self._al_mensaje
        self.cliente.reconnect_delay_set(min_delay=3, max_delay=15)
        self.cliente.username_pw_set(self.usuario, password=self.clave)

    def _al_conectar(self, client, userdata, flags, rc) -> None:
        if rc == 0:
            if self.depurar:
                print(f"MQTT conectado a {self.broker}:{self.puerto}")
            for equipo in self.equipos:
                topic = f"PVControl/{equipo}"
                client.subscribe(topic)
                if self.depurar:
                    print(f"Suscrito a tópico: {topic}")
        else:
            print(f"Conexión MQTT fallida con código {rc}")

    def _al_desconectar(self, client, userdata, rc) -> None:
        if rc != 0:
            print(f"MQTT desconectado inesperadamente (rc={rc}), reintentando")
        else:
            client.loop_stop()

    def _al_mensaje(self, client, userdata, msg) -> None:
        try:
            partes_topic = msg.topic.split("/")
            equipo = partes_topic[1].upper() if len(partes_topic) >= 2 else msg.topic.upper()
            comando = msg.payload.decode().strip()

            if self.depurar:
                print(f"MQTT mensaje: {equipo} -> {comando}")

            self.cola_comandos.put({"equipo": equipo, "comando": comando})

            if self.al_recibir:
                self.al_recibir(equipo, comando)
        except Exception as e:
            print(f"Error procesando mensaje MQTT: {e}")

    def suscribir_equipos(self, equipos: List[str]) -> None:
        """
        Registra la lista de equipos para suscripción de tópicos.
        """
        self.equipos = equipos

    def conectar(self) -> bool:
        """
        Conecta al broker MQTT e inicia el loop de mensajes.
        """
        try:
            self.cliente.connect(self.broker, self.puerto)
            time.sleep(0.2)
            self.cliente.loop_start()
            return True
        except Exception as e:
            print(f"Error conectando a MQTT en {self.broker}:{self.puerto}: {e}")
            return False

    def obtener_comando_pendiente(self) -> Optional[Dict[str, str]]:
        """
        Devuelve el siguiente comando pendiente (no bloqueante).
        """
        try:
            return self.cola_comandos.get_nowait()
        except queue.Empty:
            return None

    def hay_comandos_pendientes(self) -> bool:
        """
        Indica si hay comandos pendientes en la cola.
        """
        return not self.cola_comandos.empty()

    def publicar(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> bool:
        """
        Publica un mensaje en el broker MQTT.
        """
        try:
            result = self.cliente.publish(topic, payload, qos=qos, retain=retain)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error publicando en {topic}: {e}")
            return False

    def desconectar(self) -> None:
        """
        Desconecta del broker y detiene el loop.
        """
        if self.cliente:
            self.cliente.loop_stop()
            self.cliente.disconnect()

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.desconectar()
        return False
