# -*- coding: utf-8 -*-
"""
Modbus Utilities Module

This module provides reusable data type conversion functions for Modbus RTU/TCP communications.
It handles conversions between raw register values and engineering units with proper scaling,
sign handling, and byte order management.

Designed to work with minimalmodbus and similar Modbus libraries.

Usage:
    from modbus_utils import convert_u16, convert_s16, convert_u32, apply_byte_order
    
    # Convert unsigned 16-bit value with 1 decimal place
    voltage = convert_u16(523, decimales=1)  # Returns 52.3
    
    # Convert signed 16-bit value
    current = convert_s16(65535, decimales=2)  # Returns -0.01
    
    # Convert unsigned 32-bit value from two registers
    energy = convert_u32(valor_bajo=1234, valor_alto=5678, decimales=0)
    
    # Handle reversed byte order (PowerMR and similar devices)
    corrected_value = apply_byte_order(0x1234, orden_bytes=1)
"""

from typing import Union


def convert_u16(valor: int, decimales: int = 0, offset: Union[int, float] = 0) -> float:
    """
    Convert unsigned 16-bit register value to float with decimal scaling and offset.
    
    Args:
        valor: Raw register value (0-65535)
        decimales: Number of decimal places for scaling (default: 0)
        offset: Offset to add after scaling (default: 0)
    
    Returns:
        Scaled and offset-adjusted float value
    
    Example:
        >>> convert_u16(523, decimales=1)
        52.3
        >>> convert_u16(1000, decimales=0, offset=100)
        1100.0
    """
    return round(valor * 10 ** -decimales, decimales) + offset


def convert_s16(valor: int, decimales: int = 0, offset: Union[int, float] = 0) -> float:
    """
    Convert signed 16-bit register value to float with decimal scaling and offset.
    
    Handles two's complement representation where values >= 32768 represent negative numbers.
    
    Args:
        valor: Raw register value (0-65535)
        decimales: Number of decimal places for scaling (default: 0)
        offset: Offset to add after scaling (default: 0)
    
    Returns:
        Signed, scaled and offset-adjusted float value
    
    Example:
        >>> convert_s16(65535, decimales=2)
        -0.01
        >>> convert_s16(32768, decimales=0)
        -32768.0
        >>> convert_s16(100, decimales=1)
        10.0
    """
    # Convert to signed value if >= 32768
    signed_valor = valor if valor < 32768 else valor - 65536
    return round(signed_valor * 10 ** -decimales, decimales) + offset


def convert_u32(valor_bajo: int, valor_alto: int, decimales: int = 0, 
                offset: Union[int, float] = 0) -> float:
    """
    Convert unsigned 32-bit value from two 16-bit registers to float.
    
    Combines low and high registers according to standard Modbus convention:
    value = (high_register * 65536) + low_register
    
    Args:
        valor_bajo: Low 16-bit register value (0-65535)
        valor_alto: High 16-bit register value (0-65535)
        decimales: Number of decimal places for scaling (default: 0)
        offset: Offset to add after scaling (default: 0)
    
    Returns:
        Scaled and offset-adjusted float value
    
    Example:
        >>> convert_u32(valor_bajo=1234, valor_alto=5678, decimales=0)
        372046706.0
        >>> convert_u32(valor_bajo=0, valor_alto=1, decimales=0)
        65536.0
    """
    combined_value = valor_alto * 65536 + valor_bajo
    return round(combined_value * 10 ** -decimales, decimales) + offset


def apply_byte_order(valor: int, orden_bytes: int) -> int:
    """
    Apply byte order correction for devices that reverse byte order (e.g., PowerMR).
    
    Some Modbus devices reverse the byte order within 16-bit registers.
    This function swaps bytes when needed.
    
    Args:
        valor: Raw 16-bit register value (0-65535)
        orden_bytes: 0 = normal order, 1 = reversed byte order
    
    Returns:
        Byte-order corrected value
    
    Example:
        >>> apply_byte_order(0x1234, orden_bytes=0)
        4660
        >>> apply_byte_order(0x1234, orden_bytes=1)
        13330
    """
    if orden_bytes == 1:
        # Convert to bytes in little-endian, then interpret as big-endian integer
        return int.from_bytes(valor.to_bytes(2, 'little'), 'big')
    return valor
