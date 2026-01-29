# Usage Guide: Serial Port Timeout Fix for hibrido.py

## Quick Start

### Running with Normal Logging
```bash
python hibrido.py
```
No change in usage - the script will automatically use the new robust serial port handling.

### Running with Debug Mode (Recommended for Testing)
```bash
python hibrido.py -p
```
This enables DEBUG=100 mode, which shows:
- Port open/close operations
- Buffer flush operations
- Detailed error messages
- Command execution timing

### Running with Error Logging Only
```bash
python hibrido.py -p1
```
This enables DEBUG=1 mode, which shows:
- Error messages only
- Warning messages
- No verbose trace output

## What's Different?

### Before the Fix
- Serial port opened once at startup
- Port handle could become stale if USB device reset
- No buffer clearing between commands
- Timeout errors caused permanent disconnection
- Required manual restart to recover

### After the Fix
- Serial port opened fresh for each command
- Automatic recovery from USB device resets
- RX/TX buffers cleared before each command
- Timeout errors trigger automatic retry on next command
- Self-healing - no manual intervention needed

## Expected Behavior

### Normal Operation
You should see (with `-p` flag):
```
Successfully opened port /dev/ttyUSB2 on attempt 1
Flushing RX/TX buffers for /dev/ttyUSB2
Command successful - closing port /dev/ttyUSB2
Port /dev/ttyUSB2 closed successfully
```

### During USB Disconnect/Reconnect
You might see (with `-p` flag):
```
SerialException opening /dev/ttyUSB2 (attempt 1/3): could not open port
SerialException opening /dev/ttyUSB2 (attempt 2/3): could not open port
Successfully opened port /dev/ttyUSB2 on attempt 3
```
Then normal operation resumes automatically.

### Error That Requires Attention
```
Failed to open /dev/ttyUSB2 after 3 attempts
Serial port error on /dev/ttyUSB2: ...
```
This indicates a hardware problem - check:
- USB cable connection
- USB device permissions
- dmesg output for USB errors

## Troubleshooting

### "Timed Out" Errors Still Occurring
1. Check USB cable quality (try a different cable)
2. Check USB port (try a different USB port)
3. Check inverter is powered on and responding
4. Verify device path in Parametros_FV.py

### "Port does not exist" Errors
1. Check device is physically connected
2. Run `ls -la /dev/ttyUSB*` to verify device path
3. Update `dev_hibrido` in Parametros_FV.py if needed

### "Permission denied" Errors
1. Check user is in dialout group: `groups`
2. Add user to dialout: `sudo usermod -aG dialout $USER`
3. Log out and back in for group changes to take effect

### High CPU Usage
This is expected during the 0.15s stabilization period after opening the port. 
CPU usage should return to normal during the idle period between commands.

## Performance Notes

### Command Timing
- Port open: ~0.15-0.20s (includes stabilization)
- Buffer flush: ~0.01s
- Command send: ~0.01s
- Response read: ~0.1-0.5s (depends on inverter)
- Port close: ~0.01s
- **Total per command: ~0.3-0.9s**

### Recovery Timing
- Port open retry (3 attempts): ~1.5-2.0s
- Previous timeout wait: 15s
- **Net improvement: ~13s faster recovery**

## Advanced Configuration

### Adjusting Retry Attempts
Edit line 711 in hibrido.py:
```python
def open_and_verify_port(device_path, baud_rate=2400, timeout=1, max_retries=3):
```
Change `max_retries=3` to your desired value (e.g., 5 for slower USB devices).

### Adjusting Port Timeout
Edit line 711 in hibrido.py:
```python
def open_and_verify_port(device_path, baud_rate=2400, timeout=1, max_retries=3):
```
Change `timeout=1` to your desired value in seconds.

### Adjusting Stabilization Delay
Edit line 739 in hibrido.py:
```python
time.sleep(0.15)  # Give the device time to stabilize
```
Change `0.15` to your desired value in seconds (range: 0.1-0.3 recommended).

## Integration with systemd

If running as a systemd service, no changes needed. The service will:
- Start automatically on boot
- Restart automatically on crash (if configured)
- Use the new robust serial handling automatically

To check service status:
```bash
sudo systemctl status hibrido
```

To view logs:
```bash
sudo journalctl -u hibrido -f
```

## Monitoring

### Key Metrics to Monitor
1. **Number of timeouts**: Should be zero or very low
2. **Number of successful commands**: Should be steady
3. **Port open failures**: Should be zero under normal conditions
4. **Response time**: Should be consistent (~0.5s per command)

### Using MQTT for Monitoring
The script publishes to `PVControl/Hibrido/Tcaptura` which includes:
- Time taken for last capture
- Number of captures
- Number of failures

Monitor these values to detect issues early.

## Compatibility

### Supported Devices
- ✓ /dev/ttyUSB* devices (USB-to-serial adapters)
- ✓ /dev/hidraw* devices (HID USB devices)

### Supported Protocols
- ✓ Protocol 16 (various inverters)
- ✓ Protocol 18 (various inverters)
- ✓ Protocol 30 (Axpert King and similar)

### Supported Python Versions
- ✓ Python 3.7+
- ✓ Python 3.9+ (recommended)
- ✓ Python 3.11+ (tested)

## FAQ

### Q: Will this fix slow down my system?
A: Minimal impact. Each command adds ~0.2s for port open/close, but eliminates 15s timeout delays.

### Q: Do I need to restart the service?
A: Yes, after updating the code:
```bash
sudo systemctl restart hibrido
```

### Q: Can I revert to the old behavior?
A: Yes, restore the original hibrido.py from git backup. However, this is not recommended.

### Q: Will this work with multiple inverters?
A: Yes, the fix applies to all inverters configured in `usar_hibrido`.

### Q: Does this affect MQTT publishing?
A: No, MQTT protocol and topics remain unchanged.

### Q: Does this affect database storage?
A: No, database schema and queries remain unchanged.

## Support

If you experience issues after this fix:
1. Enable debug mode: `python hibrido.py -p`
2. Capture output for at least 5 minutes
3. Check for error patterns
4. Review the HIBRIDO_SERIAL_PORT_FIX.md for technical details

## Version History

- **2024-01-29**: Initial serial port health checking and recovery implementation
  - Added `open_and_verify_port()` helper function
  - Per-command port opening/closing for ttyUSB devices
  - Per-command device opening/closing for hidraw devices
  - Buffer flushing before each command
  - Enhanced exception handling with specific error types
  - Resource cleanup with try-finally blocks
