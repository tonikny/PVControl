#!/usr/bin/env python3
"""
Script ULTRA-SIMPLE - Usa el mismo método que funciona en el script principal
"""

import socket
import time
import sys

def obtener_ip_local():
    """Obtiene la IP local de la Raspberry"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "192.168.1.10"  # Fallback a la IP que usas normalmente

def descubrir_dongle_simple():
    """Descubre dongles usando el método que SÍ funciona"""
    print("🔍 Buscando dongles...")
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(3)
        
        try:
            sock.sendto(b"set>server=", ('255.255.255.255', 58899))
            datos, direccion = sock.recvfrom(1024)
            ip_dongle = direccion[0]
            respuesta = datos.decode('ascii', errors='ignore').strip()
            
            print(f"✅ Dongle encontrado: {ip_dongle}")
            print(f"   Respuesta: {respuesta}")
            return ip_dongle
            
        except socket.timeout:
            print("❌ No se encontraron dongles")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

def conectar_y_leer_registro_201(ip_dongle, ip_local):
    """Conecta y lee registro 201 usando el MÉTODO QUE SABEMOS FUNCIONA"""
    print(f"\n🚀 Conectando a {ip_dongle}...")
    
    # 1. Configurar dongle (EXACTAMENTE como en el script principal)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            mensaje_config = f"set>server={ip_local}:8899;"
            print(f"📨 Configurando dongle: {mensaje_config}")
            sock.sendto(mensaje_config.encode(), (ip_dongle, 58899))
            print("✅ Configuración enviada")
    except Exception as e:
        print(f"❌ Error configurando: {e}")
        return False
    
    # 2. Esperar conexión (EXACTAMENTE como en el script principal)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.settimeout(10)
            servidor.bind((ip_local, 8899))
            servidor.listen(1)
            print("👂 Esperando conexión del dongle...")
            
            cliente, direccion = servidor.accept()
            cliente.settimeout(5)
            print(f"✅ Conectado desde: {direccion}")
            
            # 3. Crear y enviar comando Modbus (EXACTAMENTE como en el script principal)
            def calcular_crc16_modbus(datos: bytes) -> int:
                crc = 0xFFFF
                for byte in datos:
                    crc ^= byte
                    for _ in range(8):
                        if crc & 1:
                            crc = (crc >> 1) ^ 0xA001
                        else:
                            crc >>= 1
                return crc

            # Crear petición para registro 201 - MÉTODO EXACTO
            id_transaccion = 0x0772
            id_unidad = 0x01
            codigo_funcion = 0x03
            direccion_inicio = 201
            cantidad = 1
            
            # Trama Modbus-RTU (igual que en el script principal)
            trama_rtu = bytearray([
                id_unidad, codigo_funcion,
                (direccion_inicio >> 8) & 0xFF, direccion_inicio & 0xFF,
                (cantidad >> 8) & 0xFF, cantidad & 0xFF
            ])
            
            crc = calcular_crc16_modbus(trama_rtu)
            trama_rtu.extend([crc & 0xFF, (crc >> 8) & 0xFF])
            
            # Cabecera propietaria FF04 (igual que en el script principal)
            carga_util = bytearray([0xFF, 0x04]) + trama_rtu
            longitud = len(carga_util)
            
            # Comando final (igual que en el script principal)
            comando = bytearray([
                (id_transaccion >> 8) & 0xFF, id_transaccion & 0xFF,
                0x00, 0x00,
                (longitud >> 8) & 0xFF, longitud & 0xFF
            ]) + carga_util

            print(f"📤 Enviando comando ({len(comando)} bytes):")
            print(f"   Hex: {' '.join(f'{b:02x}' for b in comando)}")
            
            # 4. Enviar comando
            cliente.sendall(comando)
            print("✅ Comando enviado")
            
            # 5. Recibir respuesta
            respuesta = cliente.recv(1024)
            print(f"📥 Respuesta recibida ({len(respuesta)} bytes):")
            print(f"   Hex: {' '.join(f'{b:02x}' for b in respuesta)}")
            
            # 6. Analizar respuesta (igual que en el script principal)
            if len(respuesta) >= 15:
                print("\n🎉 ANÁLISIS DE RESPUESTA:")
                
                # ID Unidad y función
                id_unidad_resp = respuesta[8]
                funcion_resp = respuesta[9]
                byte_count = respuesta[10]
                
                print(f"   ID Unidad: {id_unidad_resp:02x}")
                print(f"   Función: {funcion_resp:02x}")
                print(f"   Byte count: {byte_count:02x}")
                
                # Valor del registro
                if len(respuesta) >= 13 and byte_count >= 2:
                    valor_registro = int.from_bytes(respuesta[11:13], 'big')
                    print(f"   Valor registro 201: {valor_registro}")
                    
                    # Interpretar Working Mode
                    modos = {
                        0: "0-Power On",
                        1: "1-Standby", 
                        2: "2-Mains",
                        3: "3-Off-Grid",
                        4: "4-Bypass",
                        5: "5-Charging",
                        6: "6-Fault"
                    }
                    modo = modos.get(valor_registro, f"Desconocido ({valor_registro})")
                    print(f"   Working Mode: {modo}")
                    
                    return True
                
            elif len(respuesta) == 8 and respuesta == b'\x07\x72\x00\x00\x00\x02\xff\x04':
                print("\n❌ RESPUESTA DE RECHAZO")
                print("   El equipo rechazó el comando Modbus")
                return False
            else:
                print("\n⚠️  Respuesta inesperada")
                return False
                
            cliente.close()
            return True
            
    except socket.timeout:
        print("❌ Timeout - El dongle no se conectó")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal - SIMPLE Y DIRECTA"""
    print("=" * 60)
    print("TEST ULTRA-SIMPLE - MÉTODO COMPROBADO")
    print("=" * 60)
    
    # Obtener IP local
    ip_local = obtener_ip_local()
    print(f"📍 IP local: {ip_local}")
    
    # Descubrir dongle
    ip_dongle = descubrir_dongle_simple()
    if not ip_dongle:
        sys.exit(1)
    
    # Conectar y leer registro 201
    print(f"\n{'='*60}")
    print(f"PROBANDO COMUNICACIÓN CON {ip_dongle}")
    print(f"{'='*60}")
    
    exito = conectar_y_leer_registro_201(ip_dongle, ip_local)
    
    print(f"\n{'='*60}")
    if exito:
        print("🎉 TEST EXITOSO - El método FUNCIONA")
    else:
        print("💥 TEST FALLIDO - Revisar configuración")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    main()