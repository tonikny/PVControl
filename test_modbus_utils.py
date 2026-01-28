#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for modbus_utils module

Tests verify that data type conversions work correctly for Modbus register values.
"""

import unittest
from modbus_utils import convert_u16, convert_s16, convert_u32, apply_byte_order


class TestModbusUtils(unittest.TestCase):
    """Test cases for modbus_utils conversion functions."""
    
    def test_convert_u16_no_decimals(self):
        """Test unsigned 16-bit conversion without decimals."""
        self.assertEqual(convert_u16(1000, decimales=0), 1000.0)
        self.assertEqual(convert_u16(65535, decimales=0), 65535.0)
        self.assertEqual(convert_u16(0, decimales=0), 0.0)
    
    def test_convert_u16_with_decimals(self):
        """Test unsigned 16-bit conversion with decimal scaling."""
        self.assertEqual(convert_u16(523, decimales=1), 52.3)
        self.assertEqual(convert_u16(12345, decimales=2), 123.45)
        self.assertEqual(convert_u16(1000, decimales=3), 1.0)
    
    def test_convert_u16_with_offset(self):
        """Test unsigned 16-bit conversion with offset."""
        self.assertEqual(convert_u16(1000, decimales=0, offset=100), 1100.0)
        self.assertEqual(convert_u16(523, decimales=1, offset=10), 62.3)
    
    def test_convert_s16_positive(self):
        """Test signed 16-bit conversion with positive values."""
        self.assertEqual(convert_s16(100, decimales=0), 100.0)
        self.assertEqual(convert_s16(523, decimales=1), 52.3)
        self.assertEqual(convert_s16(32767, decimales=0), 32767.0)
    
    def test_convert_s16_negative(self):
        """Test signed 16-bit conversion with negative values (two's complement)."""
        self.assertEqual(convert_s16(65535, decimales=0), -1.0)
        self.assertEqual(convert_s16(65535, decimales=2), -0.01)
        self.assertEqual(convert_s16(32768, decimales=0), -32768.0)
        self.assertEqual(convert_s16(65000, decimales=0), -536.0)
    
    def test_convert_s16_with_offset(self):
        """Test signed 16-bit conversion with offset."""
        self.assertEqual(convert_s16(100, decimales=0, offset=50), 150.0)
        self.assertEqual(convert_s16(65535, decimales=0, offset=10), 9.0)
    
    def test_convert_u32_simple(self):
        """Test unsigned 32-bit conversion from two registers."""
        # Low=0, High=1 -> 65536
        self.assertEqual(convert_u32(0, 1, decimales=0), 65536.0)
        
        # Low=1234, High=5678
        expected = 5678 * 65536 + 1234
        self.assertEqual(convert_u32(1234, 5678, decimales=0), float(expected))
        
        # Low=65535, High=65535 -> max 32-bit
        self.assertEqual(convert_u32(65535, 65535, decimales=0), 4294967295.0)
    
    def test_convert_u32_with_decimals(self):
        """Test unsigned 32-bit conversion with decimal scaling."""
        result = convert_u32(1234, 0, decimales=2)
        self.assertEqual(result, 12.34)
    
    def test_convert_u32_with_offset(self):
        """Test unsigned 32-bit conversion with offset."""
        result = convert_u32(100, 0, decimales=0, offset=50)
        self.assertEqual(result, 150.0)
    
    def test_apply_byte_order_normal(self):
        """Test byte order with normal order (orden_bytes=0)."""
        self.assertEqual(apply_byte_order(0x1234, orden_bytes=0), 0x1234)
        self.assertEqual(apply_byte_order(65535, orden_bytes=0), 65535)
    
    def test_apply_byte_order_reversed(self):
        """Test byte order with reversed bytes (orden_bytes=1)."""
        # 0x1234 -> bytes [0x12, 0x34] little-endian -> interpret as big-endian [0x34, 0x12] -> 0x3412
        result = apply_byte_order(0x1234, orden_bytes=1)
        self.assertEqual(result, 0x3412)
        
        # 0xABCD -> 0xCDAB
        result = apply_byte_order(0xABCD, orden_bytes=1)
        self.assertEqual(result, 0xCDAB)
    
    def test_conversion_chain_u16(self):
        """Test complete conversion chain for u16 similar to fv_rs485.py."""
        # Simulate registro with value 485 representing 48.5V
        raw_value = 485
        result = convert_u16(raw_value, decimales=1)
        self.assertEqual(result, 48.5)
    
    def test_conversion_chain_s16(self):
        """Test complete conversion chain for s16 similar to fv_rs485.py."""
        # Simulate registro with negative current -5.2A represented as 65484
        raw_value = 65484  # -52 in two's complement
        result = convert_s16(raw_value, decimales=1)
        self.assertEqual(result, -5.2)
    
    def test_edge_cases(self):
        """Test edge cases and boundary values."""
        # Zero values
        self.assertEqual(convert_u16(0, 0), 0.0)
        self.assertEqual(convert_s16(0, 0), 0.0)
        self.assertEqual(convert_u32(0, 0, 0), 0.0)
        
        # Maximum values
        self.assertEqual(convert_u16(65535, 0), 65535.0)
        self.assertEqual(convert_s16(32767, 0), 32767.0)
        
        # Boundary for signed values
        self.assertEqual(convert_s16(32767, 0), 32767.0)  # Max positive
        self.assertEqual(convert_s16(32768, 0), -32768.0)  # Min negative


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world scenarios from PVControl+ equipment."""
    
    def test_anenji_battery_voltage(self):
        """Test Anenji battery voltage reading (register 215, dec=1)."""
        # Vbat register reads 485 representing 48.5V
        self.assertEqual(convert_u16(485, decimales=1), 48.5)
    
    def test_anenji_battery_current_positive(self):
        """Test Anenji battery current charging (register 216, s16, dec=1)."""
        # Ibat register reads 52 representing 5.2A charging
        self.assertEqual(convert_s16(52, decimales=1), 5.2)
    
    def test_anenji_battery_current_negative(self):
        """Test Anenji battery current discharging (register 216, s16, dec=1)."""
        # Ibat register reads 65484 representing -5.2A discharging
        self.assertEqual(convert_s16(65484, decimales=1), -5.2)
    
    def test_epever_solar_voltage(self):
        """Test Epever solar voltage reading (register 0x3100, dec=2)."""
        # Vplaca register reads 4850 representing 48.50V
        self.assertEqual(convert_u16(4850, decimales=2), 48.5)
    
    def test_powmr_reversed_bytes(self):
        """Test PowerMR device with reversed byte order."""
        # PowerMR device sends bytes in reversed order
        raw_value = 0x1234
        corrected = apply_byte_order(raw_value, orden_bytes=1)
        # After byte reversal, convert normally
        result = convert_u16(corrected, decimales=0)
        self.assertEqual(result, 0x3412)


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestModbusUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
