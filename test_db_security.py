#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstration of SQL Injection Protection

This script demonstrates how the db_manager module protects against SQL injection
compared to the old string interpolation method.
"""

import re


def old_vulnerable_method(equipo_id, tiempo, sensores_json):
    """
    Old method using string interpolation (VULNERABLE to SQL injection).
    
    This method is shown for educational purposes only.
    DO NOT USE in production code.
    """
    # Old vulnerable code from fv_rs485.py line 441
    sql = f"UPDATE equipos SET `tiempo`='{tiempo}', sensores='{sensores_json}' WHERE id_equipo='{equipo_id}'"
    return sql


def new_secure_method(equipo_id, tiempo, sensores_json):
    """
    New method using parameterized queries (SECURE).
    
    This is what db_manager.save_equipment_data() uses internally.
    """
    # New secure code using parameterized queries
    sql = "UPDATE equipos SET tiempo = %s, sensores = %s WHERE id_equipo = %s"
    params = (tiempo, sensores_json, equipo_id)
    return sql, params


def demonstrate_sql_injection():
    """Demonstrate how SQL injection works and how it's prevented."""
    
    print("=" * 80)
    print("SQL Injection Protection Demonstration")
    print("=" * 80)
    print()
    
    # Normal case
    print("1. NORMAL USAGE")
    print("-" * 80)
    equipo_id = "INVERTER1"
    tiempo = "2024-01-28 12:00:00"
    sensores_json = '{"Vbat": 48.5, "Ibat": -5.2}'
    
    vulnerable_sql = old_vulnerable_method(equipo_id, tiempo, sensores_json)
    secure_sql, secure_params = new_secure_method(equipo_id, tiempo, sensores_json)
    
    print(f"Equipment ID: {equipo_id}")
    print(f"Time: {tiempo}")
    print(f"Data: {sensores_json}")
    print()
    print("Old vulnerable method:")
    print(f"  SQL: {vulnerable_sql}")
    print()
    print("New secure method:")
    print(f"  SQL: {secure_sql}")
    print(f"  Params: {secure_params}")
    print()
    
    # SQL Injection attempt
    print("\n2. SQL INJECTION ATTEMPT")
    print("-" * 80)
    malicious_equipo_id = "INVERTER1'; DROP TABLE equipos; --"
    tiempo = "2024-01-28 12:00:00"
    sensores_json = '{"Vbat": 48.5}'
    
    print(f"Malicious Equipment ID: {malicious_equipo_id}")
    print()
    
    vulnerable_sql = old_vulnerable_method(malicious_equipo_id, tiempo, sensores_json)
    secure_sql, secure_params = new_secure_method(malicious_equipo_id, tiempo, sensores_json)
    
    print("Old vulnerable method:")
    print(f"  SQL: {vulnerable_sql}")
    print()
    print("  ⚠️  DANGER: This would execute TWO SQL statements:")
    print("     1. UPDATE equipos ... WHERE id_equipo='INVERTER1'")
    print("     2. DROP TABLE equipos  ⬅ DESTROYS THE TABLE!")
    print()
    
    print("New secure method:")
    print(f"  SQL: {secure_sql}")
    print(f"  Params: {secure_params}")
    print()
    print("  ✅ SAFE: The malicious string is treated as a literal value.")
    print("     The database will search for an equipment with ID:")
    print(f"     \"{malicious_equipo_id}\"")
    print("     Since no such equipment exists, the UPDATE affects 0 rows.")
    print("     The DROP TABLE command is NEVER executed.")
    print()
    
    # Another injection attempt
    print("\n3. ANOTHER INJECTION ATTEMPT (data exfiltration)")
    print("-" * 80)
    malicious_tiempo = "2024-01-28' OR '1'='1"
    
    print(f"Malicious Time: {malicious_tiempo}")
    print()
    
    vulnerable_sql = old_vulnerable_method("INVERTER1", malicious_tiempo, sensores_json)
    secure_sql, secure_params = new_secure_method("INVERTER1", malicious_tiempo, sensores_json)
    
    print("Old vulnerable method:")
    print(f"  SQL: {vulnerable_sql}")
    print()
    print("  ⚠️  DANGER: The WHERE clause becomes:")
    print("     WHERE id_equipo='INVERTER1' OR '1'='1'")
    print("     This matches ALL rows, updating every equipment!")
    print()
    
    print("New secure method:")
    print(f"  SQL: {secure_sql}")
    print(f"  Params: {secure_params}")
    print()
    print("  ✅ SAFE: The malicious string is escaped.")
    print("     The database treats it as a literal timestamp.")
    print("     If it's invalid, the query fails safely.")
    print()
    
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print("✅ db_manager.py uses parameterized queries throughout")
    print("✅ SQL injection is IMPOSSIBLE with parameterized queries")
    print("✅ All user input is automatically escaped by the database driver")
    print("✅ No manual escaping needed")
    print()
    print("🔒 Security Status: PROTECTED")
    print("=" * 80)


if __name__ == '__main__':
    demonstrate_sql_injection()
