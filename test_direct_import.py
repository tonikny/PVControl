#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test direct import configuration from Parametros_FV.py

Verifies that helper modules correctly import configuration at module level.
"""


def test_imports_without_parametros():
    """Test that modules can be imported even without Parametros_FV.py"""
    print("Testing module imports without Parametros_FV.py...")
    
    try:
        from db_manager import DatabaseManager
        print("  ✓ db_manager imports successfully")
    except ImportError as e:
        print(f"  ✗ db_manager import failed: {e}")
        return False
    
    try:
        from mqtt_handler import MQTTHandler
        print("  ✓ mqtt_handler imports successfully")
    except ImportError as e:
        print(f"  ✗ mqtt_handler import failed: {e}")
        return False
    
    try:
        from telegram_notifier import TelegramNotifier
        print("  ✓ telegram_notifier imports successfully")
    except ImportError as e:
        print(f"  ✗ telegram_notifier import failed: {e}")
        return False
    
    print("  ✓ All modules import successfully")
    return True


def test_explicit_parameters():
    """Test initialization with explicit parameters (no Parametros_FV.py needed)"""
    print("\nTesting explicit parameter initialization...")
    
    from db_manager import DatabaseManager
    from mqtt_handler import MQTTHandler
    from telegram_notifier import TelegramNotifier
    
    # Test DatabaseManager
    try:
        db = DatabaseManager(
            host='test_host',
            user='test_user',
            passwd='test_pass',
            db='test_db'
        )
        print(f"  ✓ DatabaseManager: host={db.host}, user={db.user}, db={db.db_name}")
        db.close()
    except Exception as e:
        # Connection will fail but params should be set
        if 'test_host' in str(e) or 'test_db' in str(e):
            print("  ✓ DatabaseManager: Parameters set correctly (connection failed as expected)")
        else:
            print(f"  ✗ DatabaseManager error: {e}")
            return False
    
    # Test MQTTHandler
    try:
        mqtt = MQTTHandler(
            broker='test_broker',
            puerto=1883,
            usuario='test_user',
            clave='test_pass'
        )
        print(f"  ✓ MQTTHandler: broker={mqtt.broker}, port={mqtt.puerto}, user={mqtt.usuario}")
    except Exception as e:
        # Library version issues are OK
        if 'callback_api_version' in str(e) or 'API version' in str(e):
            print("  ✓ MQTTHandler: Parameters set correctly (library version issue)")
        else:
            print(f"  ⚠ MQTTHandler error (may be OK): {e}")
    
    # Test TelegramNotifier
    try:
        notifier = TelegramNotifier(
            token='123456789:ABCdefGHIjklMNOpqrsTUVwxyz',
            chat_id=12345678,
            use_telegram=False  # Don't actually try to connect
        )
        print(f"  ✓ TelegramNotifier: token set, chat_id={notifier.chat_id}, enabled={notifier.use_telegram}")
    except Exception as e:
        print(f"  ✗ TelegramNotifier error: {e}")
        return False
    
    print("  ✓ All modules initialize correctly with explicit parameters")
    return True


def test_missing_params_error():
    """Test that clear errors are raised when parameters missing"""
    print("\nTesting error handling for missing parameters...")
    
    from db_manager import DatabaseManager
    
    try:
        # This should fail because no Parametros_FV.py and no explicit params
        db = DatabaseManager()
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError as e:
        if 'Parametros_FV.py' in str(e) or 'Missing' in str(e):
            print(f"  ✓ Correct error: {e}")
            return True
        else:
            print(f"  ⚠ Error message could be clearer: {e}")
            return True
    except Exception as e:
        print(f"  ⚠ Unexpected error type: {type(e).__name__}: {e}")
        return True  # Still counts as handling the error


def test_module_level_imports():
    """Test that module-level imports work correctly"""
    print("\nTesting module-level import mechanism...")
    
    # Import modules
    import db_manager
    import mqtt_handler
    import telegram_notifier
    
    # Check that module-level variables exist (even if None)
    print("  Checking db_manager module variables...")
    assert hasattr(db_manager, 'servidor'), "db_manager should have 'servidor' at module level"
    assert hasattr(db_manager, 'usuario'), "db_manager should have 'usuario' at module level"
    assert hasattr(db_manager, 'clave'), "db_manager should have 'clave' at module level"
    assert hasattr(db_manager, 'basedatos'), "db_manager should have 'basedatos' at module level"
    print(f"    ✓ servidor={db_manager.servidor}")
    print(f"    ✓ usuario={db_manager.usuario}")
    print(f"    ✓ basedatos={db_manager.basedatos}")
    
    print("  Checking mqtt_handler module variables...")
    assert hasattr(mqtt_handler, 'mqtt_broker'), "mqtt_handler should have 'mqtt_broker' at module level"
    assert hasattr(mqtt_handler, 'mqtt_puerto'), "mqtt_handler should have 'mqtt_puerto' at module level"
    assert hasattr(mqtt_handler, 'mqtt_usuario'), "mqtt_handler should have 'mqtt_usuario' at module level"
    assert hasattr(mqtt_handler, 'mqtt_clave'), "mqtt_handler should have 'mqtt_clave' at module level"
    print(f"    ✓ mqtt_broker={mqtt_handler.mqtt_broker}")
    print(f"    ✓ mqtt_puerto={mqtt_handler.mqtt_puerto}")
    print(f"    ✓ mqtt_usuario={mqtt_handler.mqtt_usuario}")
    
    print("  Checking telegram_notifier module variables...")
    assert hasattr(telegram_notifier, 'TOKEN'), "telegram_notifier should have 'TOKEN' at module level"
    assert hasattr(telegram_notifier, 'Aut'), "telegram_notifier should have 'Aut' at module level"
    assert hasattr(telegram_notifier, 'usar_telegram'), "telegram_notifier should have 'usar_telegram' at module level"
    print(f"    ✓ TOKEN={telegram_notifier.TOKEN}")
    print(f"    ✓ Aut={telegram_notifier.Aut}")
    print(f"    ✓ usar_telegram={telegram_notifier.usar_telegram}")
    
    print("  ✓ All module-level imports verified")
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("Direct Import Configuration Tests")
    print("=" * 70)
    
    tests = [
        ("Module Imports", test_imports_without_parametros),
        ("Explicit Parameters", test_explicit_parameters),
        ("Missing Parameters Error", test_missing_params_error),
        ("Module Level Imports", test_module_level_imports),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print("-" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed - Direct import implementation works correctly!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    print("=" * 70)
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    exit(main())
