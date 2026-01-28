# Direct Import Implementation

## Overview

The helper modules now directly import configuration parameters from `Parametros_FV.py` (with fallback to `Parametros_FV_DIST.py`) at the module level. This is cleaner and more Pythonic than frame introspection.

## Implementation Details

### Database Manager (db_manager.py)

```python
# Import at module level
try:
    from Parametros_FV import servidor, usuario, clave, basedatos
except ImportError:
    try:
        from Parametros_FV_DIST import servidor, usuario, clave, basedatos
    except ImportError:
        servidor = None
        usuario = None
        clave = None
        basedatos = None

class DatabaseManager:
    def __init__(self, host: Optional[str] = None, ...):
        # Use provided or fall back to imported
        self.host = host or servidor
        self.user = user or usuario
        self.passwd = passwd or clave
        self.db_name = db or basedatos
```

**Variables imported:**
- `servidor` - Database host
- `usuario` - Database username
- `clave` - Database password
- `basedatos` - Database name

### MQTT Handler (mqtt_handler.py)

```python
# Import at module level
try:
    from Parametros_FV import mqtt_broker, mqtt_puerto, mqtt_usuario, mqtt_clave
except ImportError:
    try:
        from Parametros_FV_DIST import mqtt_broker, mqtt_puerto, mqtt_usuario, mqtt_clave
    except ImportError:
        mqtt_broker = None
        mqtt_puerto = None
        mqtt_usuario = None
        mqtt_clave = None

class MQTTHandler:
    def __init__(self, broker: Optional[str] = None, ...):
        # Use provided or fall back to imported
        self.broker = broker or mqtt_broker
        self.puerto = puerto or mqtt_puerto
        self.usuario = usuario or mqtt_usuario
        self.clave = clave or mqtt_clave
```

**Variables imported:**
- `mqtt_broker` - MQTT broker hostname/IP
- `mqtt_puerto` - MQTT broker port
- `mqtt_usuario` - MQTT username
- `mqtt_clave` - MQTT password

### Telegram Notifier (telegram_notifier.py)

```python
# Import at module level
try:
    from Parametros_FV import TOKEN, Aut, usar_telegram
except ImportError:
    try:
        from Parametros_FV_DIST import TOKEN, Aut, usar_telegram
    except ImportError:
        TOKEN = None
        Aut = []
        usar_telegram = 0

class TelegramNotifier:
    def __init__(self, token: Optional[str] = None, ...):
        # Use provided or fall back to imported
        self.token = token or TOKEN
        self.chat_id = chat_id or (Aut[0] if Aut and len(Aut) > 0 else None)
        self.use_telegram = (usar_telegram == 1) if use_telegram is None else use_telegram
```

**Variables imported:**
- `TOKEN` - Telegram bot token
- `Aut` - List of authorized chat IDs
- `usar_telegram` - Enable/disable flag (1=enabled, 0=disabled)

## Benefits

### 1. Cleaner Code
- No frame introspection magic
- Standard Python import mechanism
- Clear and explicit

### 2. Works in All Contexts
- Works when imported directly
- Works when exec()'d by device scripts
- Works in unit tests (when Parametros files not available)

### 3. Flexible Fallback Chain
1. Explicit parameters (highest priority)
2. Parametros_FV.py imports
3. Parametros_FV_DIST.py imports
4. None (will raise error if required)

### 4. Type-Safe
- All parameters remain properly typed
- IDE auto-completion works
- Static analysis tools understand it

## Usage in fv_rs485.py

```python
from db_manager import DatabaseManager
from mqtt_handler import MQTTHandler
from telegram_notifier import TelegramNotifier

# Simple initialization - all config auto-imported
db_manager = DatabaseManager()
mqtt_handler = MQTTHandler(on_message_callback=handler, debug=True)
telegram_notifier = TelegramNotifier()
```

## Usage in Device Scripts

Device scripts continue to work without changes:

```python
# fv_anenji.py
ANENJI = { ... }
exec(open("/home/pi/PVControl+/fv_rs485.py").read(), globals())
```

The helper modules are imported by fv_rs485.py, and they import config from Parametros_FV.py directly.

## Testing

### With Real Configuration
```python
# If Parametros_FV.py exists, modules use those values
from db_manager import DatabaseManager
db = DatabaseManager()  # Uses servidor, usuario, clave, basedatos from Parametros_FV.py
```

### With Explicit Parameters
```python
# For testing without Parametros_FV.py
from db_manager import DatabaseManager
db = DatabaseManager(
    host='test_host',
    user='test_user',
    passwd='test_pass',
    db='test_db'
)
```

### Fallback Behavior
```python
# If Parametros_FV.py doesn't exist
# 1. Tries Parametros_FV_DIST.py
# 2. Sets to None if neither exists
# 3. Raises error when __init__() is called without explicit params
```

## Error Handling

Clear error messages when configuration is missing:

```python
ValueError: Database parameters must be provided explicitly or imported from Parametros_FV.py. 
Missing: host=None, user=None, db=None
```

## Comparison with Previous Approach

### Before (Frame Introspection)
```python
def __init__(self, host: Optional[str] = None, ...):
    if host is None:
        import sys
        frame = sys._getframe(1)
        host = frame.f_globals.get('servidor')
```

**Problems:**
- Magic/unclear
- Depends on call stack
- Hard to understand
- Breaks with decorators/wrappers

### After (Direct Import)
```python
# Module level
from Parametros_FV import servidor, usuario, clave, basedatos

def __init__(self, host: Optional[str] = None, ...):
    self.host = host or servidor
```

**Benefits:**
- Clear and explicit
- Standard Python
- Independent of call stack
- Works everywhere

## Verification

All tests pass:
```bash
$ ./check_phase1.sh
✅ modbus_utils.py
✅ db_manager.py
✅ mqtt_handler.py
✅ telegram_notifier.py
✅ fv_rs485.py compiles
✅ All imports work
✅ Unit tests pass (19/19)
✅ Device scripts compatible
```

## Summary

The helper modules now use **direct module-level imports** from Parametros_FV.py instead of frame introspection. This is:

- ✅ **Cleaner** - Standard Python import mechanism
- ✅ **Simpler** - No magic or introspection
- ✅ **More reliable** - Works in all contexts
- ✅ **Type-safe** - IDEs and linters understand it
- ✅ **Flexible** - Still supports explicit parameters for testing
- ✅ **Backward compatible** - All existing code works

The configuration flows naturally from Parametros_FV.py → helper modules → fv_rs485.py, exactly as intended in the PVControl+ architecture.

---

**Date**: 2024-01-28  
**Status**: ✅ Implemented and Tested  
**Method**: Direct module-level imports with fallback chain
