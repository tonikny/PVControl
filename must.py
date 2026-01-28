### script provisional para 1 unico equipo

import time
import MySQLdb, json

import minimalmodbus
import serial
from serial.tools import list_ports


import Parametros_FV
import subprocess, sys
from Parametros_FV_DIST import *
from Parametros_FV import *

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

equipo = 'must'
N_Equipo = ""

if usar_must == 0:
    print(subprocess.getoutput('sudo systemctl stop must'))
    sys.exit()

print(Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0]) #+Style.RESET_ALL)


def reset_conexion():
    global modbus
    
    print(Fore.CYAN + "Reiniciando conexión serial...")
    try:
        # Cerrar puerto si está abierto
        if 'modbus' in globals() and modbus.serial.is_open:
            modbus.serial.close()
            time.sleep(1)
        
        # Listar puertos disponibles para diagnóstico
        print(Fore.MAGENTA + "Puertos seriales disponibles:")
        for port in list_ports.comports():
            print(f" - {port.device}: {port.description}")
        
        # Recrear la conexión
        modbus = minimalmodbus.Instrument(dev_must, 4)
        modbus.serial.baudrate = 19200
        modbus.serial.bytesize = 8
        modbus.serial.parity = serial.PARITY_NONE
        modbus.serial.stopbits = 1
        modbus.serial.timeout = 3
        modbus.debug = False
        modbus.mode = minimalmodbus.MODE_RTU
        modbus.clear_buffers_before_each_transaction = True
        modbus.close_port_after_each_call = False
        
        # Forzar reinicio del buffer serial
        if modbus.serial.is_open:
            modbus.serial.reset_input_buffer()
            modbus.serial.reset_output_buffer()
        
        print(Fore.GREEN + "Conexión reiniciada exitosamente")
        return True
    except Exception as e:
        print(Fore.RED + f"Error al reiniciar conexión: {str(e)}")
        return False


# Inicializacion + Variables para control de errores

# Listar puertos disponibles para diagnóstico
print(Fore.MAGENTA + "Puertos seriales disponibles:")
for port in list_ports.comports():
    print(f" - {port.device}: {port.description}")


modbus = minimalmodbus.Instrument(dev_must, 4)
modbus.serial.baudrate = 19200
modbus.serial.bytesize = 8
modbus.serial.parity = serial.PARITY_NONE
modbus.serial.stopbits = 1
modbus.serial.timeout = 3
modbus.debug = False
modbus.mode = minimalmodbus.MODE_RTU
modbus.clear_buffers_before_each_transaction = True
modbus.close_port_after_each_call = False

# Forzar reinicio del buffer serial
if modbus.serial.is_open:
    modbus.serial.reset_input_buffer()
    modbus.serial.reset_output_buffer()

print(Fore.GREEN + "Conexión Modbus OK")
        

n_errores = 0
max_errores = 2

DEBUG = False

narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p': DEBUG = True
else: DEBUG = False

try:
    ee = '10'
    db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
    cursor = db.cursor()
 
    try: #inicializamos registro RAM                 
        ee = '10b'
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      (equipo.upper()+ N_Equipo ,'{}'))   
        db.commit()
    except:
        pass             

except:
    print(Fore.RED, f'ERROR {ee} - inicializando BD RAM')
    sys.exit()

datos = {}

error_captura = 0
        

while True:
    
    # Verificar si necesitamos reiniciar la conexión Modbus
    if n_errores >= max_errores:
        print(Fore.RED + "Demasiados errores consecutivos. Reiniciando conexión Modbus...")
        reset_conexion()
        n_errores = 0  # Resetear el contador después del reinicio
        time.sleep(5)  # Esperar un poco más después del reinicio
        continue  # Saltar esta iteración
    
    try:
        print(Fore.YELLOW, f'{time.strftime("%H:%M:%S")}', '=' * 70)
        
        #############
        r = 15201 # Cargador Display
        #############
        lectura = modbus.read_registers(r,21)
        
        l = lectura[15201-r]
            #0：Initialization mode 
            #1：Selftest Mode
            #2: Work Mode
            #3：Stop Mode
        if l == 0: datos['Estado_cargador'] = 'Inicializando'
        elif l == 1: datos['Estado_cargador'] = 'Autotest'
        elif l == 2: datos['Estado_cargador'] = 'OK'
        elif l == 3: datos['Estado_cargador'] = 'STOP'
        else:pass
        

        l = lectura[15202-r]
            #0：Stop
            #1：MPPT 
            #2: Current limiting
        if l == 0: datos['Estado_MPPT'] = 'STOP'
        elif l == 1: datos['Estado_MPPT'] = 'MPPT'
        elif l == 2: datos['Estado_MPPT'] = 'REGULANDO'
        else: pass
        
        
        l = lectura[15203-r]
            #0：Stop
            #1：Absorb charge 
            #2: Float charge            
        if l == 0: datos['Estado_carga'] = 'STOP'
        elif l == 1: datos['Estado_carga'] = 'ABS'
        elif l == 2: datos['Estado_carga'] = 'FLOT'
        else: pass

        
        datos['Vplaca'] = round(lectura[15205-r]/10,1)
        datos['Vbat'] = round(lectura[15206-r]/10,1)

        datos['Iplaca'] = round(lectura[15207-r]/10,1)        
        datos['Wplaca'] = lectura[15208-r]
        #datos['Iplaca_Vbat'] = round(datos['Wplaca'] / datos['Vbat'],1) if datos['Vbat'] != 0 else 0         
        
        
        datos['Wh_placa_dia'] = lectura[15219-r]
        datos['Wh_placa_hora'] = lectura[15220-r]
        datos['Wh_placa_minuto'] = lectura[15221-r]
        
        if DEBUG == 1: print(f'Lectura registros {r}....OK')

        time.sleep(0.2)
        
        ###############
        r = 10103 # Control Cargador Display
        ###############
        lectura = modbus.read_registers(r,8)
        
        datos['Vabs'] = round(lectura[10103-r]/10,1)
        datos['Vflot'] = round(lectura[10104-r]/10,1)
        datos['Vbat_baja'] = round(lectura[10105-r]/10,1)
        datos['Vbat_alta'] = round(lectura[10107-r]/10,1)
        datos['Imax_carga'] = round(lectura[10108-r]/10,1)
        
        l = lectura[10110-r]
            #0:no choose
            #1:Use defined battery
            #2:lithium battery
            #3:SEALED_LEAD  battery  
            #4:AGM  battery  
            #5:GEL  battery  
            #6:FLOODED  battery  "
        if l == 0: datos['Bat_tipo'] = 'NO SELECCION'
        elif l == 1: datos['Bat_tipo'] = 'USE'
        elif l == 2: datos['Bat_tipo'] = 'LI'
        elif l == 3: datos['Bat_tipo'] = 'SEALED'
        elif l == 4: datos['Bat_tipo'] = 'AGM'
        elif l == 5: datos['Bat_tipo'] = 'GEL'
        elif l == 6: datos['Bat_tipo'] = 'FLOODED'
        else: pass



        if DEBUG == 1: print(f'Lectura registros {r}....OK')

        time.sleep(0.2)



        ###############
        r = 25201 # Inversor Display
        ###############
        lectura = modbus.read_registers(r,27)

        datos['Vbat_inv'] = round(lectura[25205-r]/10,1)
        datos['Vred'] = round(lectura[25206-r]/10,1)
        datos['Winv'] = round(lectura[25213-r]/1,1)
        datos['Wgrid'] = round(lectura[25214-r]/1,1)
        datos['Wload'] = round(lectura[25215-r]/1,1)
        
        datos['Finv'] = round(lectura[25225-r]/100,1)
        datos['Fgrid'] = round(lectura[25226-r]/100,1)
        
        
                
        datos['Error_captura'] = error_captura
        

        
        if DEBUG == 1:
            print(Fore.YELLOW, '=' * 70, Fore.GREEN)
            for i in datos: print(f'{i}= {datos[i]}')        
            
    except Exception as e:
        error_captura += 1
        n_errores += 1
        print(Fore.RED + f"Error en el bucle principal: {str(e)}")
        
    try:
        ####  ARCHIVOS RAM en BD ############ 
        ee = '40'
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        salida = json.dumps(datos)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{equipo.upper()}{N_Equipo}'") # grabacion en BD RAM
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print(Fore.RED + f'error, Grabacion tabla RAM equipos en {equipo.upper()}{N_Equipo}: {str(e)}')
        
    time.sleep(t_muestra_must)
