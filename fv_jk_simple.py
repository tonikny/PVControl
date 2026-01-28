import asyncio
from bleak import BleakScanner, BleakClient

# MAC address del BMS JK (ajusta según tu dispositivo)
JK_MAC = "C8:47:8C:EE:A8:10" #JK1 "C8:47:80:19:3E:9C" Madrid
# UUID BLE del BMS JK
JK_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
MIN_RESPONSE_SIZE = 300
NUM_CELLS = 7  # Número de celdas por defecto

def build_jk_command(cmd, data=[]):
    """Construye una trama según el protocolo JK (cabecera AA 55 90 EB, relleno y CRC)."""
    frame = bytearray([0xAA, 0x55, 0x90, 0xEB, cmd, len(data)]) + bytearray(data)
    frame += bytearray([0] * (13 - len(data)))  # Relleno hasta 13 bytes de datos
    crc = sum(frame) & 0xFF
    frame += bytearray([crc])
    print(f"Comando enviado (tipo {cmd:02X}): {' '.join(f'{b:02X}' for b in frame)}")
    return frame

def show_trama(buf, label):
    print(f"\n{label} ({len(buf)} bytes): {' '.join(f'{b:02X}' for b in buf)}")
    print("Primeros 32 bytes (hex):", ' '.join(f'{b:02X}' for b in buf[:32]))
    print("Primeros 32 bytes (dec):", ' '.join(str(b) for b in buf[:32]))

def find_cell_count_candidates(buf, expected_cells=NUM_CELLS):
    print(f"Buscando candidatos a número de celdas ({expected_cells}) en la trama:")
    posiciones = [i for i, b in enumerate(buf) if b == expected_cells]
    if posiciones:
        print(f"  Valor {expected_cells} encontrado en posiciones: {posiciones}")
    else:
        print(f"  Valor {expected_cells} no encontrado en la trama.")

def find_jk_subframe(buf):
    # Busca la cabecera 55 AA EB 90 en toda la trama
    header = bytes([0x55, 0xAA, 0xEB, 0x90])
    idx = buf.find(header)
    if idx != -1 and len(buf) > idx + 5:
        # Extrae la subtrama desde la cabecera encontrada
        return buf[idx:]
    return buf  # Si no se encuentra, devuelve la trama original

def interpret_trama(buf):
    global NUM_CELLS
    
    # Extrae subtrama si la cabecera está desplazada
    buf = find_jk_subframe(buf)
    if len(buf) < 10:
        print("Trama demasiado corta para interpretar.")
        return
    tipo = buf[4]
    print(f"Tipo de trama recibida: 0x{tipo:02X}")
    find_cell_count_candidates(buf)  # Mostrar candidatos en todas las tramas
    if tipo == 0x03:
        show_trama(buf, "Trama de información")
        # Trama de información del dispositivo
        try:
            model = buf[6:22].split(b'\x00')[0].decode(errors='ignore')
            hw = buf[22:30].split(b'\x00')[0].decode(errors='ignore')
            sw = buf[30:46].split(b'\x00')[0].decode(errors='ignore')
            name = buf[46:62].split(b'\x00')[0].decode(errors='ignore')
            #NUM_CELLS = buf[186:186].split(b'\x00')[0].decode(errors='ignore')
            nc1 = buf[186:187]
            nc2 = buf[186]
            nc3 = buf[187]
            NUM_CELLS = buf[186]
            
            print(nc1, nc2, nc3)
            
            
            print(f"Modelo: {model}, HW: {hw}, SW: {sw}, Nombre: {name}, Nceldas:{NUM_CELLS}")
        except Exception as e:
            print(f"Error interpretando trama de información: {e}")
    elif tipo == 0x02:
        show_trama(buf, "Trama de estado/datos")
        # Trama de estado/datos
        try:
            # Detectar firmware nuevo por offset
            offset = 32 if len(buf) > 200 else 0
            num_cells = NUM_CELLS  # Usar valor fijo para la prueba
            def read_volt(i): return int.from_bytes(buf[6 + i*2:8 + i*2], 'little') / 1000.0
            def read_float(i): return int.from_bytes(buf[i+offset:i+offset+4], 'little', signed=True) * 0.001
            def read_temp(i): return int.from_bytes(buf[i+offset:i+offset+2], 'little', signed=True) / 10.0
            voltages = [read_volt(i) for i in range(num_cells)]
            voltage = read_float(118)
            current = read_float(126)
            soc = buf[141 + offset] if len(buf) > 141 + offset else None
            temp1 = read_temp(130)
            temp2 = read_temp(132)
            mos_temp = read_temp(112)
            print(f"Voltaje total: {voltage:.2f} V")
            print(f"Corriente: {current:.2f} A")
            print(f"SOC: {soc} %")
            print(f"Temperaturas: {temp1:.1f} °C, {temp2:.1f} °C")
            print(f"Temp MOSFET: {mos_temp:.1f} °C")
            print("Voltajes celdas:")
            for i, v in enumerate(voltages):
                print(f"  Celda {i+1}: {v:.3f} V")
        except Exception as e:
            print(f"Error interpretando trama de estado: {e}")
    elif tipo == 0x01:
        show_trama(buf, "Trama tipo 0x01")
        find_cell_count_candidates(buf)
    else:
        print(f"Tipo de trama no reconocido o no implementado: 0x{tipo:02X}")
        show_trama(buf, "Trama desconocida")
        find_cell_count_candidates(buf)

async def main():
    print("Paso 1: Escaneando dispositivos Bluetooth...")
    devices = await BleakScanner.discover(timeout=5)
    found = False
    for d in devices:
        print(f"  {d.name} - {d.address}")
        if d.address.upper() == JK_MAC.upper():
            found = True
    if not found:
        print(f"No se encontró el dispositivo JK BMS con MAC {JK_MAC}.")
        return

    print("Paso 2: Conectando al BMS JK...")
    resp_table = {}
    buffer = bytearray()

    def notification_handler(sender, data):
        # Ensambla la trama completa como en fv_jk_test_IA_OK.py
        HEADER = bytes([0xAA, 0x55, 0x90, 0xEB])
        if data[:4] == HEADER:
            buffer.clear()
        buffer.extend(data)
        if len(buffer) >= MIN_RESPONSE_SIZE:
            tipo = buffer[4]
            resp_table[tipo] = bytes(buffer)
            show_trama(buffer, f"Trama recibida tipo 0x{tipo:02X}")
            interpret_trama(buffer)
            buffer.clear()

    async with BleakClient(JK_MAC) as client:
        if not client.is_connected:
            print("No se pudo conectar al BMS JK.")
            return

        print("Paso 3: Buscando el handle de la característica BLE...")
        await client.get_services()
        char_handle = None
        for service in client.services:
            for char in service.characteristics:
                if char.uuid == JK_UUID:
                    char_handle = char.handle
                    break
            if char_handle:
                break
        if not char_handle:
            print("No se encontró el handle de la característica BLE.")
            return

        print(f"Paso 4: Suscribiéndose a notificaciones BLE (handle {char_handle})...")
        await client.start_notify(char_handle, notification_handler)

        print("Paso 5: Enviando comando de información (0x97)...")
        await client.write_gatt_char(char_handle, build_jk_command(0x97))
        await asyncio.sleep(2)

        print("Paso 6: Enviando comando de estado (0x96)...")
        await client.write_gatt_char(char_handle, build_jk_command(0x96))
        await asyncio.sleep(5)  # Espera para recibir notificaciones

        print("Fin de la captura. Puedes repetir el envío de comandos si lo deseas.")
        await client.stop_notify(char_handle)

if __name__ == "__main__":
    asyncio.run(main())