# -*- coding: utf-8 -*-
"""
Módulo de notificaciones Telegram.

Proporciona una interfaz segura para enviar mensajes de Telegram con control de
timeout y gestión de errores. La configuración se obtiene desde Parametros_FV.py
mediante GestorParametros.
"""

from typing import Optional, Union

import telebot
import timeout_decorator

from helpers.gestor_parametros import GestorParametros


class GestorTelegram:
    """
    Gestiona notificaciones de Telegram con control de errores.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        id_chat: Optional[Union[int, str]] = None,
        usar_telegram: Optional[bool] = None,
        timeout: int = 20,
    ):
        """
        Inicializa el gestor de Telegram.

        Args:
            token: token del bot de Telegram
            id_chat: ID de chat o usuario
            usar_telegram: habilita o deshabilita Telegram
            timeout: timeout en segundos para el envío
        """
        gestor = GestorParametros()
        try:
            token_cfg, autorizados_cfg, usar_cfg = gestor.leer_parametros(
                "TOKEN", "Aut", "usar_telegram"
            )
        except (AttributeError, FileNotFoundError):
            token_cfg = None
            autorizados_cfg = []
            usar_cfg = 0

        self.token = token or token_cfg
        self.id_chat = id_chat or (autorizados_cfg[0] if autorizados_cfg else None)

        if usar_telegram is None:
            self.usar_telegram = usar_cfg == 1
        else:
            self.usar_telegram = usar_telegram

        self.timeout_seconds = timeout
        self.bot: Optional[telebot.TeleBot] = None

        if self.usar_telegram and not self.token:
            raise ValueError(
                "Debe proporcionar un token de Telegram o definirlo en Parametros_FV.py"
            )

        if self.usar_telegram and self.token:
            self._inicializar_bot()

    def _inicializar_bot(self) -> None:
        try:
            self.bot = telebot.TeleBot(self.token)
            self.bot.skip_pending = True
        except Exception as e:
            print(f"Error inicializando Telegram: {e}")
            raise

    def habilitar(self) -> None:
        """
        Habilita las notificaciones de Telegram.
        """
        self.usar_telegram = True
        if self.bot is None:
            self._inicializar_bot()

    def deshabilitar(self) -> None:
        """
        Deshabilita las notificaciones de Telegram.
        """
        self.usar_telegram = False

    def esta_habilitado(self) -> bool:
        """
        Indica si Telegram está habilitado.
        """
        return self.usar_telegram and self.bot is not None

    @timeout_decorator.timeout(20, use_signals=False)
    def _enviar_con_timeout(self, id_chat: Union[int, str], mensaje: str) -> None:
        if self.bot:
            self.bot.send_message(id_chat, mensaje, parse_mode="HTML")

    def enviar_mensaje(self, mensaje: str, id_chat: Optional[Union[int, str]] = None) -> bool:
        """
        Envía un mensaje de Telegram con timeout.
        """
        if not self.usar_telegram or not self.bot:
            return False

        destino = id_chat if id_chat is not None else self.id_chat
        self._enviar_con_timeout(destino, mensaje)
        return True

    def enviar_mensaje_seguro(
        self,
        mensaje: str,
        id_chat: Optional[Union[int, str]] = None,
        silencioso: bool = True,
    ) -> bool:
        """
        Envía un mensaje capturando errores.
        """
        if not self.usar_telegram or not self.bot:
            return False

        try:
            destino = id_chat if id_chat is not None else self.id_chat
            self._enviar_con_timeout(destino, mensaje)
            return True
        except timeout_decorator.TimeoutError:
            error_msg = f"Timeout de Telegram ({self.timeout_seconds}s superados)"
            print(error_msg)
            if not silencioso:
                raise
            return False
        except Exception as e:
            error_msg = f"Error enviando mensaje Telegram: {type(e).__name__} - {e}"
            print(error_msg)
            if not silencioso:
                raise
            return False

    def enviar_mensaje_inicio(self, nombre_programa: str) -> bool:
        """
        Envía notificación de arranque.
        """
        mensaje = f"Arrancando Programa Control {nombre_programa}"
        return self.enviar_mensaje_seguro(mensaje)

    def enviar_mensaje_error(
        self, descripcion_error: str, codigo_error: Optional[str] = None
    ) -> bool:
        """
        Envía un mensaje de error formateado.
        """
        if codigo_error:
            mensaje = f"🔴 <b>Error {codigo_error}:</b> {descripcion_error}"
        else:
            mensaje = f"🔴 <b>Error:</b> {descripcion_error}"

        return self.enviar_mensaje_seguro(mensaje)

    def enviar_mensaje_alerta(self, texto_alerta: str, nivel: str = "warning") -> bool:
        """
        Envía una alerta formateada.
        """
        iconos = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨",
        }
        icono = iconos.get(nivel.lower(), "📢")
        mensaje = f"{icono} <b>Alerta:</b> {texto_alerta}"

        return self.enviar_mensaje_seguro(mensaje)
