import serial
import time

# --- Configure your serial port ---
DEV_PORT = "/dev/ttyUSB2"   # FTDI adapter
BAUDRATE = 2400
TIMEOUT = 5  # seconds

# --- Axpert King QPIGS fields ---
FIELDS = [
    "AC_Voltage", "AC_Frequency", "AC_Current", "AC_Power",
    "AC_Load_Percent", 
    "DC_Battery_Voltage", 
    "Battery_Charging_Current",
    "Battery_Capacity", "Inverter_Temperature", "PV_Input_Voltage",
    "PV_Input_Current", "PV_Input_Power", "Battery_Charging_Voltage",
    "Battery_Charging_State", "Reserved1", "Reserved2", "Reserved3",
    "Reserved4", "Reserved5", "Reserved6"
]

def read_qpigs():
    try:
        with serial.Serial(DEV_PORT, baudrate=BAUDRATE, bytesize=8, parity='N',
                           stopbits=1, timeout=TIMEOUT) as ser:
            time.sleep(0.2)  # small delay after opening

            # Send QPIGS command with carriage return
            ser.write(b'QPIGS\r')
            ser.flush()

            time.sleep(0.3)  # wait for response

            # Read response (adjust size if needed)
            response = ser.read(200)
            if not response:
                print("No response from inverter")
                return None

            # Decode and clean up
            resp_str = response.decode(errors='ignore').strip()
            resp_str = resp_str.strip('()')  # remove parentheses

            # Split values and map to fields
            values = resp_str.split()
            data = dict(zip(FIELDS, values))

            return data

    except serial.SerialException as e:
        print("Serial error:", e)
        return None

# --- Example usage ---
if __name__ == "__main__":
    data = read_qpigs()
    if data:
        for k, v in data.items():
            print(f"{k}: {v}")
