# PVControl+ Helper Modules

This document describes the reusable helper modules extracted from `fv_rs485.py` to improve code quality, testability, and maintainability.

## Overview

Four helper modules have been created to separate concerns and eliminate code duplication:

1. **modbus_utils.py** - Data type conversions for Modbus registers
2. **db_manager.py** - Safe database operations with parameterized queries
3. **mqtt_handler.py** - MQTT connection and message handling
4. **telegram_notifier.py** - Telegram bot notifications with error handling

All modules maintain **backward compatibility** with the existing `exec()` pattern used by device-specific scripts.

---

## 1. modbus_utils.py

### Purpose
Provides reusable functions for converting Modbus register values to engineering units.

### Functions

#### `convert_u16(valor, decimales=0, offset=0)`
Convert unsigned 16-bit register value to float.

```python
from modbus_utils import convert_u16

# Read battery voltage: register value 485 = 48.5V
voltage = convert_u16(485, decimales=1)  # Returns 48.5
```

#### `convert_s16(valor, decimales=0, offset=0)`
Convert signed 16-bit register value (two's complement) to float.

```python
from modbus_utils import convert_s16

# Read battery current: register value 65484 = -5.2A (discharging)
current = convert_s16(65484, decimales=1)  # Returns -5.2
```

#### `convert_u32(valor_bajo, valor_alto, decimales=0, offset=0)`
Convert two 16-bit registers to a 32-bit unsigned value.

```python
from modbus_utils import convert_u32

# Read energy counter from two registers
energy = convert_u32(valor_bajo=1234, valor_alto=5678, decimales=0)
```

#### `apply_byte_order(valor, orden_bytes)`
Handle reversed byte order for devices like PowerMR.

```python
from modbus_utils import apply_byte_order

# Correct byte order for PowerMR devices
corrected = apply_byte_order(raw_value, orden_bytes=1)
```

### Testing
Run unit tests with:
```bash
python3 test_modbus_utils.py
```

---

## 2. db_manager.py

### Purpose
Provides safe database operations using **parameterized queries** to prevent SQL injection vulnerabilities.

### Key Security Improvement
**Before (vulnerable):**
```python
sql = f"UPDATE equipos SET tiempo='{tiempo}', sensores='{salida}' WHERE id_equipo='{equipo}'"
cursor.execute(sql)
```

**After (secure):**
```python
db_manager.save_equipment_data(equipo, tiempo, salida)
```

### Usage

#### Initialize Connection
```python
from db_manager import DatabaseManager

db_mgr = DatabaseManager(
    host='localhost',
    user='pvcontrol',
    passwd='password',
    db='PVControl'
)
```

#### Save Equipment Data
```python
import json

data = {'Vbat': 48.5, 'Ibat': -5.2, 'SOC': 85}
db_mgr.save_equipment_data(
    equipo_id='INVERTER1',
    tiempo='2024-01-28 12:00:00',
    sensores_json=json.dumps(data)
)
```

#### Insert Equipment Record
```python
# Insert equipment if it doesn't exist (idempotent)
db_mgr.insert_equipment_if_missing('INVERTER1')
```

#### Context Manager (automatic cleanup)
```python
with DatabaseManager(host, user, passwd, db) as db_mgr:
    db_mgr.save_equipment_data(equipo_id, tiempo, data)
    # Connection automatically closed
```

### Methods
- `save_equipment_data(equipo_id, tiempo, sensores_json)` - Update equipment data
- `save_equipment_data_dict(equipo_id, tiempo, sensores_dict)` - Update with dict (auto-converts to JSON)
- `insert_equipment_if_missing(equipo_id)` - Insert record if missing
- `get_equipment_data(equipo_id)` - Retrieve equipment data
- `close()` - Close connection

---

## 3. mqtt_handler.py

### Purpose
Provides clean MQTT interface with automatic reconnection and thread-safe command queue.

### Key Improvements
- **Thread-safe command queue** replaces global `comando_mqtt` variable
- Automatic reconnection handling
- Equipment-specific topic subscription
- Non-blocking command retrieval

### Usage

#### Initialize Handler
```python
from mqtt_handler import MQTTHandler

def handle_command(equipo, comando):
    print(f"Received: {equipo} -> {comando}")

mqtt = MQTTHandler(
    broker='localhost',
    puerto=1883,
    usuario='mqtt_user',
    clave='mqtt_pass',
    on_message_callback=handle_command,
    debug=True
)
```

#### Subscribe and Connect
```python
# Subscribe to equipment topics
mqtt.subscribe_equipment(['INVERTER1', 'ANENJI1', 'EPEVER1'])

# Connect to broker
mqtt.connect()
```

#### Process Commands
```python
# Non-blocking command retrieval
cmd = mqtt.get_pending_command()
if cmd:
    print(f"Equipment: {cmd['equipo']}")
    print(f"Command: {cmd['comando']}")
```

#### Publish Messages
```python
mqtt.publish('PVControl/Status', 'System OK', qos=1)
```

### Methods
- `connect()` - Connect to MQTT broker
- `subscribe_equipment(equipos_list)` - Subscribe to equipment topics
- `get_pending_command()` - Get next command (non-blocking)
- `has_pending_commands()` - Check if commands pending
- `publish(topic, payload, qos, retain)` - Publish message
- `disconnect()` - Disconnect from broker

---

## 4. telegram_notifier.py

### Purpose
Provides safe Telegram bot interface with timeout protection and error handling.

### Key Improvements
- **Timeout protection** prevents hanging on network issues
- Automatic error handling and logging
- Formatted message helpers (startup, error, alert)
- Graceful degradation when disabled

### Usage

#### Initialize Notifier
```python
from telegram_notifier import TelegramNotifier

notifier = TelegramNotifier(
    token='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
    chat_id=12345678,
    use_telegram=True,
    timeout=20
)
```

#### Send Messages
```python
# Simple message
notifier.send_message('<b>System started</b>')

# Safe send (with error handling)
notifier.send_message_safe('Battery voltage: 48.5V')

# Startup notification
notifier.send_startup_message('fv_anenji')

# Error notification
notifier.send_error_message('Database connection failed', 'DB_ERR_001')

# Alert notification
notifier.send_alert_message('Battery voltage low', level='warning')
```

#### Enable/Disable
```python
notifier.disable()  # Temporarily disable notifications
notifier.enable()   # Re-enable notifications
```

### Methods
- `send_message(message, chat_id)` - Send message (may raise exceptions)
- `send_message_safe(message, chat_id)` - Send with error handling (recommended)
- `send_startup_message(program_name)` - Formatted startup notification
- `send_error_message(description, code)` - Formatted error notification
- `send_alert_message(text, level)` - Formatted alert (info/warning/critical)
- `enable()` / `disable()` - Toggle notifications
- `is_enabled()` - Check if enabled

---

## Integration with fv_rs485.py

The modules are imported and used in `fv_rs485.py` while maintaining backward compatibility:

```python
# Import helper modules
from modbus_utils import convert_u16, convert_s16, convert_u32, apply_byte_order
from db_manager import DatabaseManager
from mqtt_handler import MQTTHandler
from telegram_notifier import TelegramNotifier

# Initialize modules
db_manager = DatabaseManager(host=servidor, user=usuario, passwd=clave, db=basedatos)
mqtt_handler = MQTTHandler(broker=mqtt_broker, puerto=mqtt_puerto, ...)
telegram_notifier = TelegramNotifier(token=TOKEN, chat_id=Aut[0], ...)

# Use in conversion logic
voltage = convert_u16(raw_value, decimales=1, offset=0)

# Use in database operations
db_manager.save_equipment_data(equipo_id, tiempo, sensores_json)

# Use in MQTT handling
cmd = mqtt_handler.get_pending_command()

# Use in notifications
telegram_notifier.send_message_safe('Equipment started')
```

## Backward Compatibility

All device-specific scripts (`fv_anenji.py`, `fv_epever.py`, etc.) continue to work without modifications:

```python
# Device script remains unchanged
exec(open("/home/pi/PVControl+/fv_rs485.py").read(), globals())
```

The `exec()` pattern ensures all new modules are loaded into the global namespace.

## Benefits

1. **Security**: SQL injection vulnerabilities eliminated
2. **Testability**: Functions can be unit tested independently
3. **Maintainability**: Single source of truth for common operations
4. **Reusability**: Modules can be imported by other scripts
5. **Code Quality**: Type hints, docstrings, and proper error handling
6. **Reduced Duplication**: Conversion logic no longer duplicated

## Testing

### Run All Tests
```bash
python3 test_modbus_utils.py
```

### Verify Imports
```bash
python3 -c "from modbus_utils import *"
python3 -c "from db_manager import DatabaseManager"
python3 -c "from mqtt_handler import MQTTHandler"
python3 -c "from telegram_notifier import TelegramNotifier"
```

### Check Syntax
```bash
python3 -m py_compile modbus_utils.py
python3 -m py_compile db_manager.py
python3 -m py_compile mqtt_handler.py
python3 -m py_compile telegram_notifier.py
python3 -m py_compile fv_rs485.py
```

## Next Steps (Future Phases)

**Phase 2**: Update device-specific scripts to directly import modules
- Modify `fv_anenji.py`, `fv_epever.py`, etc. to import modules directly
- Remove `exec()` pattern for cleaner code
- Maintain same functionality

**Phase 3**: Additional improvements
- Add logging module to replace print statements
- Create configuration manager for parameters
- Add validation module for register ranges
- Create equipment class hierarchy

## Support

For questions or issues with these modules, refer to:
- Module docstrings for detailed API documentation
- Unit tests in `test_modbus_utils.py` for usage examples
- Inline comments in `fv_rs485.py` for integration patterns
