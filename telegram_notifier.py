# -*- coding: utf-8 -*-
"""
Telegram Notifier Module

This module provides a safe, reusable Telegram bot interface for PVControl+ notifications.
It handles message sending with timeout protection, error handling, and graceful degradation
when Telegram is disabled or unavailable.

Key Features:
- Timeout protection for send operations
- Automatic error handling and logging
- Optional enable/disable functionality
- HTML parse mode support

Usage:
    from telegram_notifier import TelegramNotifier
    
    # Initialize with bot token and chat ID
    notifier = TelegramNotifier(
        token='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
        chat_id=12345678,
        use_telegram=True
    )
    
    # Send a simple message
    notifier.send_message('System started successfully')
    
    # Send HTML formatted message (safe method with error handling)
    notifier.send_message_safe('<b>Alert:</b> Battery voltage low!')
    
    # Disable temporarily
    notifier.disable()
"""

import telebot
import timeout_decorator
from typing import Optional, Union


class TelegramNotifier:
    """
    Manages Telegram bot notifications with timeout and error handling.
    
    Provides safe message sending with automatic error recovery.
    Configuration can be passed explicitly or imported from Parametros_FV.py globals.
    """
    
    def __init__(self, token: Optional[str] = None, chat_id: Optional[Union[int, str]] = None, 
                 use_telegram: Optional[bool] = None, timeout: int = 20):
        """
        Initialize Telegram notifier.
        
        Args:
            token: Telegram bot token from BotFather (default: from Parametros_FV.py 'TOKEN')
            chat_id: Chat ID or username (default: from Parametros_FV.py 'Aut[0]')
            use_telegram: Enable/disable Telegram (default: from Parametros_FV.py 'usar_telegram')
            timeout: Timeout in seconds for send operations (default: 20)
        
        If parameters are not provided, attempts to import from global namespace
        (Parametros_FV.py variables: TOKEN, Aut, usar_telegram).
        
        Raises:
            Exception: If bot initialization fails (only when use_telegram=True)
        """
        # Try to get from globals if not provided
        if token is None:
            import sys
            frame = sys._getframe(1)
            token = frame.f_globals.get('TOKEN')
        if chat_id is None:
            import sys
            frame = sys._getframe(1)
            aut = frame.f_globals.get('Aut')
            if aut and len(aut) > 0:
                chat_id = aut[0]
        if use_telegram is None:
            import sys
            frame = sys._getframe(1)
            usar = frame.f_globals.get('usar_telegram', 0)
            use_telegram = (usar == 1)
        
        # Validate required parameters
        if use_telegram and not token:
            raise ValueError("Telegram token must be provided or available in global namespace when use_telegram=True")
        
        self.token = token
        self.chat_id = chat_id
        self.use_telegram = use_telegram if use_telegram is not None else False
        self.timeout_seconds = timeout
        self.bot: Optional[telebot.TeleBot] = None
        
        if self.use_telegram and self.token:
            self._initialize_bot()
    
    def _initialize_bot(self) -> None:
        """
        Initialize Telegram bot connection.
        
        Raises:
            Exception: If bot initialization fails
        """
        try:
            self.bot = telebot.TeleBot(self.token)
            self.bot.skip_pending = True  # Skip pending messages on startup
        except Exception as e:
            print(f"Error initializing Telegram bot: {e}")
            raise
    
    def enable(self) -> None:
        """
        Enable Telegram notifications.
        
        Initializes bot if not already initialized.
        """
        self.use_telegram = True
        if self.bot is None:
            self._initialize_bot()
    
    def disable(self) -> None:
        """
        Disable Telegram notifications.
        
        Messages will be silently ignored when disabled.
        """
        self.use_telegram = False
    
    def is_enabled(self) -> bool:
        """
        Check if Telegram notifications are enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self.use_telegram and self.bot is not None
    
    @timeout_decorator.timeout(20, use_signals=False)
    def _send_with_timeout(self, chat_id: Union[int, str], message: str) -> None:
        """
        Send message with timeout protection.
        
        Args:
            chat_id: Target chat ID
            message: Message text (supports HTML formatting)
        
        Raises:
            timeout_decorator.TimeoutError: If send exceeds timeout
            Exception: For other Telegram API errors
        """
        if self.bot:
            self.bot.send_message(chat_id, message, parse_mode="HTML")
    
    def send_message(self, message: str, chat_id: Optional[Union[int, str]] = None) -> bool:
        """
        Send Telegram message with timeout protection.
        
        This method will attempt to send the message and raise exceptions on failure.
        For safer error handling, use send_message_safe() instead.
        
        Args:
            message: Message text (HTML formatting supported)
            chat_id: Optional chat ID override (uses instance chat_id if not provided)
        
        Returns:
            True if message sent successfully, False if Telegram is disabled
        
        Raises:
            timeout_decorator.TimeoutError: If send exceeds timeout
            Exception: For other Telegram API errors
        
        Example:
            >>> notifier.send_message('<b>Warning:</b> High temperature detected')
            True
        """
        if not self.use_telegram or not self.bot:
            return False
        
        target_chat_id = chat_id if chat_id is not None else self.chat_id
        self._send_with_timeout(target_chat_id, message)
        return True
    
    def send_message_safe(self, message: str, 
                         chat_id: Optional[Union[int, str]] = None,
                         silent_on_error: bool = True) -> bool:
        """
        Send Telegram message with automatic error handling.
        
        This is the recommended method for most use cases as it handles all errors
        gracefully and never raises exceptions.
        
        Args:
            message: Message text (HTML formatting supported)
            chat_id: Optional chat ID override
            silent_on_error: If True, errors are only printed; if False, errors are raised
        
        Returns:
            True if message sent successfully, False otherwise
        
        Example:
            >>> notifier.send_message_safe('System restarted')
            True
        """
        if not self.use_telegram or not self.bot:
            return False
        
        try:
            target_chat_id = chat_id if chat_id is not None else self.chat_id
            self._send_with_timeout(target_chat_id, message)
            return True
            
        except timeout_decorator.TimeoutError:
            error_msg = f"Telegram send timeout ({self.timeout_seconds}s exceeded)"
            print(error_msg)
            if not silent_on_error:
                raise
            return False
            
        except Exception as e:
            error_msg = f"Error sending Telegram message: {type(e).__name__} - {e}"
            print(error_msg)
            if not silent_on_error:
                raise
            return False
    
    def send_startup_message(self, program_name: str) -> bool:
        """
        Send a standardized startup notification.
        
        Args:
            program_name: Name of the starting program/service
        
        Returns:
            True if sent successfully, False otherwise
        
        Example:
            >>> notifier.send_startup_message('fv_anenji')
            True
        """
        message = f'Arrancando Programa Control {program_name}'
        return self.send_message_safe(message)
    
    def send_error_message(self, error_description: str, 
                          error_code: Optional[str] = None) -> bool:
        """
        Send a formatted error notification.
        
        Args:
            error_description: Description of the error
            error_code: Optional error code or identifier
        
        Returns:
            True if sent successfully, False otherwise
        
        Example:
            >>> notifier.send_error_message('Database connection failed', 'DB_ERR_001')
            True
        """
        if error_code:
            message = f'🔴 <b>Error {error_code}:</b> {error_description}'
        else:
            message = f'🔴 <b>Error:</b> {error_description}'
        
        return self.send_message_safe(message)
    
    def send_alert_message(self, alert_text: str, level: str = 'warning') -> bool:
        """
        Send a formatted alert notification.
        
        Args:
            alert_text: Alert message text
            level: Alert level - 'info', 'warning', or 'critical'
        
        Returns:
            True if sent successfully, False otherwise
        
        Example:
            >>> notifier.send_alert_message('Battery voltage low', level='warning')
            True
        """
        icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'critical': '🚨'
        }
        icon = icons.get(level.lower(), '📢')
        message = f'{icon} <b>Alerta:</b> {alert_text}'
        
        return self.send_message_safe(message)
