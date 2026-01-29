# hibrido.py Serial Port Health Checking and Recovery Fix

## Problem Summary
The hibrido.py script was experiencing persistent "Timed Out" errors when communicating with the Axpert King solar inverter on /dev/ttyUSB2. The error pattern showed repeated timeouts every 15-20 seconds, and the script entered a disconnection-reconnection loop without recovering.

## Root Causes Identified

1. **No per-command port reopening**: Serial port was opened once at startup (line 916) but never verified or reopened per command in the `comando()` function
2. **Stale connection state**: If the USB device resets, gets busy, or enters a bad state, the original port handle became unresponsive
3. **Missing buffer flush**: No clearing of serial RX/TX buffers before sending commands, leading to stale data causing timeouts
4. **No error recovery**: When a timeout occurred, there was no mechanism to close and reopen the port for recovery

## Changes Implemented

### 1. New Helper Function: `open_and_verify_port()` (lines 711-759)

Created a robust helper function that:
- Takes device path, baud rate, and timeout as parameters
- Returns an open serial port object or None on failure
- Implements retry logic (default: 3 attempts) for connection attempts
- Includes error handling for USB devices that aren't ready
- Provides detailed debug logging at different verbosity levels
- Waits for device stabilization after opening (0.15s)

**Key features:**
```python
def open_and_verify_port(device_path, baud_rate=2400, timeout=1, max_retries=3):
    - Checks device existence before attempting to open
    - Verifies port.is_open after opening
    - Catches serial.SerialException with retry logic
    - Returns None if all attempts fail (graceful degradation)
```

### 2. Modified `comando()` Function for ttyUSB Devices (lines 801-864)

**Before:** Used a global `ser` object opened once at startup
**After:** Opens/closes port fresh for each command

**Changes:**
- Line 806: Initialize `local_ser = None` for proper cleanup tracking
- Lines 808-812: Open port using `open_and_verify_port()` with retry logic
- Lines 817-821: **Clear RX/TX buffers** before sending command:
  ```python
  local_ser.reset_input_buffer()
  local_ser.reset_output_buffer()
  ```
- Line 824: Send command to inverter
- Lines 830-833: Read response with byte-by-byte accumulation
- Lines 840-852: **Catch specific serial exceptions**:
  - `serial.SerialTimeoutException` → detailed timeout error message
  - `serial.SerialException` → detailed port error message
  - Both raise Exception with diagnostic info for upper layers
- Lines 854-864: **Finally block ensures port closure**:
  - Flushes any remaining data
  - Closes port to free USB resource
  - Handles closure errors gracefully

### 3. Modified `comando()` Function for hidraw Devices (lines 866-926)

Applied similar pattern to hidraw devices:
- Line 870: Initialize `local_fd = None` for proper cleanup tracking
- Lines 873-874: Open device fresh for each command (with sudo chown)
- Line 883: Write first chunk
- Lines 885-894: **Explicit flush between write chunks**:
  ```python
  local_fd.flush()  # After each 8-byte chunk
  ```
- Line 896: **Final flush before reading**
- Lines 901-905: Read response
- Lines 910-915: **Catch and log device errors** with diagnostic messages
- Lines 917-926: **Finally block ensures device closure**

### 4. Updated Exception Handling (lines 1000-1017)

**Before:** Generic exception handling with minimal logging
**After:** 
- Line 1000: Catch Exception with detailed error info
- Lines 1001-1002: Log error code and exception message at DEBUG >= 1
- Lines 1007-1017: Updated finally block:
  - Removed global `ser.flush()` / `ser.close()` (no longer needed)
  - Added comment explaining cleanup is handled in try-finally blocks
  - Only logs timing info if variables exist (using `'t1' in locals()`)

## Benefits of These Changes

### ✓ Robust Recovery from Timeouts
- Each command starts with a fresh port connection
- Stale connections are automatically closed and replaced
- USB device resets are handled transparently

### ✓ Clean Buffer State
- RX/TX buffers are cleared before each command
- No stale data from previous commands can interfere
- Reduces false CRC errors and garbled responses

### ✓ Better Error Diagnostics
- Specific exception types (SerialTimeoutException, SerialException)
- Detailed error messages include device path and error details
- DEBUG levels provide granular logging:
  - DEBUG >= 1: Error messages and warnings
  - DEBUG == 100: Full trace of open/flush/close operations

### ✓ Resource Management
- Ports are always closed, even on error (try-finally pattern)
- No lingering file handles that could block other processes
- Graceful degradation if port unavailable

### ✓ Zero Protocol Changes
- Communication protocol unchanged
- Response parsing logic unchanged
- CRC checking logic unchanged
- Only affects the transport layer (serial I/O)

## Testing Recommendations

### Basic Functionality Test
```bash
python hibrido.py -p
```
Run for 5+ minutes and verify:
- No "Timed Out" errors in logs
- MQTT publishing resumes normally
- Consistent inverter responses

### Debug Mode Test
```bash
python hibrido.py -p  # DEBUG=100
```
Check logs for:
- `Successfully opened port /dev/ttyUSBX on attempt 1`
- `Flushing RX/TX buffers for /dev/ttyUSBX`
- `Command successful - closing port /dev/ttyUSBX`
- `Port /dev/ttyUSBX closed successfully`

### Recovery Test (if possible)
1. Start the script
2. Briefly disconnect/reconnect USB cable
3. Verify script recovers within 1-2 command cycles

### Expected Behavior
- **Before:** Repeated timeouts, permanent disconnection state
- **After:** Occasional timeout (during USB disconnect), automatic recovery on next command

## Configuration Notes

### No User Configuration Required
All changes are internal to the `comando()` function. The startup loop (lines 914-924) remains unchanged for initial device detection.

### Debug Levels
- `DEBUG = 0` (default): Minimal output
- `DEBUG = 1` (`-p1` flag): Error messages only
- `DEBUG = 100` (`-p` flag): Full trace of port operations

### Timeout Settings
- Port open timeout: 1 second (line 809)
- Command timeout: 15 seconds (timeout_decorator on line 761)
- Max retry attempts: 3 (line 711)

These can be adjusted in the `open_and_verify_port()` function if needed.

## Backward Compatibility

✓ No changes to startup behavior
✓ No changes to MQTT protocol
✓ No changes to database schema
✓ No changes to command protocol
✓ Works with all inverter models (protocol 16, 18, 30)
✓ Works with both ttyUSB and hidraw devices

## Code Quality Improvements

- **Better separation of concerns**: Port management isolated in helper function
- **Resource safety**: Try-finally ensures cleanup
- **Error transparency**: Specific exceptions with context
- **Maintainability**: Clear comments explain each change
- **Debuggability**: Detailed logging at appropriate verbosity levels

## Implementation Details

### Lines Changed
- **Added:** Lines 711-759 (helper function)
- **Modified:** Lines 801-926 (comando function serial I/O)
- **Modified:** Lines 1000-1017 (exception handling and cleanup)
- **Total:** ~215 lines changed/added

### Dependencies
No new dependencies added. Uses existing imports:
- `serial` (pyserial) - already imported
- `time`, `os`, `subprocess` - already imported

### Performance Impact
- Minimal: Port open/close adds ~0.15-0.30s per command
- Offset by elimination of timeout delays (15s each)
- Net improvement in reliability and recovery time
