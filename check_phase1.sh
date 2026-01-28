#!/bin/bash
echo "========================================="
echo "Phase 1 Verification Script"
echo "========================================="
echo ""

# Check 1: Module compilation
echo "1. Checking module compilation..."
python3 -m py_compile modbus_utils.py && echo "  ✅ modbus_utils.py" || echo "  ❌ modbus_utils.py"
python3 -m py_compile db_manager.py && echo "  ✅ db_manager.py" || echo "  ❌ db_manager.py"
python3 -m py_compile mqtt_handler.py && echo "  ✅ mqtt_handler.py" || echo "  ❌ mqtt_handler.py"
python3 -m py_compile telegram_notifier.py && echo "  ✅ telegram_notifier.py" || echo "  ❌ telegram_notifier.py"
echo ""

# Check 2: Modified file compilation
echo "2. Checking fv_rs485.py..."
python3 -m py_compile fv_rs485.py && echo "  ✅ fv_rs485.py compiles" || echo "  ❌ fv_rs485.py failed"
echo ""

# Check 3: Import tests
echo "3. Checking module imports..."
python3 -c "from modbus_utils import convert_u16, convert_s16, convert_u32, apply_byte_order" && echo "  ✅ modbus_utils imports" || echo "  ❌ modbus_utils import failed"
python3 -c "from db_manager import DatabaseManager" && echo "  ✅ db_manager imports" || echo "  ❌ db_manager import failed"
python3 -c "from mqtt_handler import MQTTHandler" && echo "  ✅ mqtt_handler imports" || echo "  ❌ mqtt_handler import failed"
python3 -c "from telegram_notifier import TelegramNotifier" && echo "  ✅ telegram_notifier imports" || echo "  ❌ telegram_notifier import failed"
echo ""

# Check 4: Unit tests
echo "4. Running unit tests..."
python3 test_modbus_utils.py 2>&1 | grep -E "(OK|FAILED|Error)" | tail -1
echo ""

# Check 5: Device script syntax
echo "5. Checking device script compatibility..."
for file in fv_anenji.py fv_epever.py fv_growatt.py fv_powmr.py fv_srne.py; do
  python3 -c "import ast; ast.parse(open('$file').read())" 2>/dev/null && echo "  ✅ $file" || echo "  ⚠️  $file"
done
echo ""

echo "========================================="
echo "Phase 1 Verification Complete"
echo "========================================="
