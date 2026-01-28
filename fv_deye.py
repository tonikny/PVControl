# -*- coding: utf-8 -*-

# Versión 2025-12-01
#
#

# #################### Control Ejecucion Servicio ########################################
equipo = 'deye'
servicio = 'fv_deye'
control = 'sum(usar_deye)'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

import sys, time, datetime
import MySQLdb,json
import subprocess

import telebot # Librería de la API del bot.
import token


# Aseguramos que la libreria pysolarmanv5 esta instalada
try:
    import minimalmodbus
    from pysolarmanv5 import PySolarmanV5
    
except:
    res = subprocess.run('pip3 install pysolarmanv5' , shell=True)
    if res.returncode == 0:
        try:
            from pysolarmanv5 import PySolarmanV5
        except:
            print ('Error en instalacion libreria pysolarmanv5')
            
            #sys.exit()

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0])

#Comprobacion argumentos en comando
simular = DEBUG= 0
narg = len(sys.argv)
if '-p' in sys.argv: DEBUG= 1 # para desarrollo permite print en distintos sitios


def leer_equipo(I_equipo): # bucle de lectura de cada equipo
    global n_fallos_lectura
    
    t0= time.time()
    
    # creamos que registro en tabla equipos
    try:
        ee = '10'
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        
        try: #inicializamos registro RAM en BD 
            ee = '10b'
            nombre_equipo = nombre_deye[I_equipo].upper()
            
            cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                          (nombre_equipo,'{}'))   
            db.commit()
        except:
            pass             
                            
    except:
        print (Fore.RED,f'ERROR {ee} - inicializando BD RAM')
        sys.exit()


    # Conexion al equipo
    if dev_deye[I_equipo][:4] == '/dev': # se usa RS485
        
        tipo_conexion = 'RS485'
        modbus = minimalmodbus.Instrument(dev_deye[I_equipo], 1)
        modbus.serial.baudrate = 9600
        modbus.serial.bytesize = 8
        modbus.serial.parity = minimalmodbus.serial.PARITY_NONE
        modbus.serial.stopbits = 1
        modbus.serial.timeout = 3
        modbus.debug = False
        modbus.mode = minimalmodbus.MODE_RTU
        
    else: # se usa Dongle Wifi
        tipo_conexion = 'WIFI'
        modbus = PySolarmanV5(dev_deye[I_equipo], n_serie_dongle[I_equipo], port=8899, mb_slave_id=mb_slave_id[I_equipo], verbose=False)
        
    #Captura 
    t1= time.time()
    
    datos= {} # inicializo diccionario
    error = False
    
    # --- BLOQUE 1: Registros 59 - 172 ---
    try:
        ee = 100
        if tipo_conexion == 'RS485':
            
            d = modbus.read_registers(59, 114, 3)
        else:
            try:
                d = modbus.read_holding_registers(register_addr=59, quantity=114) # leo registros del 59 al 172 
                
            except:
                error = True
                
        if not error:
            ee = 110
            if d[0] == 0: # registro 59
                datos['EstadoInv'] = "Stand By"
            elif d[0] == 1:
                datos['EstadoInv'] = "Self Checking"
            elif d[0] == 2:
                datos['EstadoInv'] = "Normal"
            elif d[0] == 3:
                datos['EstadoInv'] = "Fault"
                
            datos['DayActivePower'] = round(d[1]/10,2) # registro 60
            datos['TotalActivePower'] = round(d[4]/10,2) # registro 63
            datos['DayBattCharge'] = round(d[11]/10,2) # registro 70 que sera el de la posicion 70-59 = 11
            datos['DayBattDischarge'] = round(d[12]/10,2) # registro 71
            datos['TotalBatteryChargePower'] = round(d[13]/10,2) # registro 72
            datos['TotalBatteryDischargePower'] = round(d[15]/10,2) # registro 74
            datos['DayGridBuyPower'] = round(d[17]/10,2) # registro 76
            datos['DayGridSellPower'] = round(d[18]/10,2) # registro 77
            datos['TotalGridBuyPower'] = round(d[19]/10,2) # registro 78
            datos['TotalGridSellPower'] = round(d[22]/10,2) # registro 81
            datos['DayLoadPower'] = round(d[25]/10,2) # registro 84
            datos['TotalLoadPower'] = round(d[26]/10,2) # registro 85
            datos['YearLoadPower'] = round(d[28]/10,2) # registro 87
            datos['RadiatorTempDC'] = round((d[31]-1000)/10,2) # registro 90
            datos['IGBTTemp'] = round((d[32]-1000)/10,2) # registro 91
            
            ee = 120
            
            # --- SE ELIMINAN REGISTROS 92 y 95 (Inductance1Temp y EnvironmentTemp) por anomalía y por no ser registros de Temp ---
            
            datos['HistPVPower'] = round(d[37]/10,2) # registro 96
            
            # Mapeo de Voltajes de Absorción/Flotación a Registros 100 y 101 (Protocolo Oficial) ---
            # d[41] es el registro 100 (100 - 59 = 41)
            datos['AbsorptionV'] = round(d[41]/100,2) # registro 100 (0x0064) - Absorption V
            # d[42] es el registro 101 (101 - 59 = 42)
            datos['FloatV'] = round(d[42]/100,2)      # registro 101 (0x0065) - Float V
            
            datos['DayPVPower'] = round(d[49]/10,2) # registro 108
            datos['Vplaca1'] = round(d[50]/10,2) # registro 109
            datos['Iplaca1'] = round(d[51]/10,2) # registro 110
            datos['Vplaca2'] = round(d[52]/10,2) # registro 111
            datos['Iplaca2'] = round(d[53]/10,2) # registro 112
            datos['Vred'] = round(d[91]/10,2) # registro 150
            datos['LoadVoltageL1'] = round(d[98]/10,2) # registro 157
            datos['Ired'] = round(d[103]/100,2) # registro 162
            datos['Ired2'] = round(d[104]/100,2) # registro 163
            
            if d[111] > 32767 : d[111] -= 65535  # campo signet int 
            datos['GrideSideL2P'] = round(d[111]/10,2) # registro 170
            
            if d[113] > 32767 : d[113] -= 65535
            datos['Wred'] = round(d[113]/10,2) # registro 172
            
    except:
        error = True
        print(f'error en captura {ee}')
    
    t2= time.time()
    
    # --- BLOQUE 2: Registros 178 - 284  ---
    if not error:
        try:
            
            ee = 200
            if tipo_conexion == 'RS485':
                d = modbus.read_registers(178, 107, 3) 
            else:
                try:
                    d = modbus.read_holding_registers(register_addr=178, quantity=107) 
                except:
                    error = True
                    
            if not error:
                ee = 210
                # --- Mapeo Original (TIEMPO REAL) ---
                datos['Wconsumo'] = round(d[0],2) # registro 178
                datos['Tbat'] = round((d[4] - 1000)/10,2) # registro 182
                datos['Vbat'] = round(d[5]/100,2) # registro 183
                datos['SOC'] = round(d[6],2) # registro 184
                datos['PV1InputPower'] = round(d[8],2) # registro 186
                datos['PV2InputPower'] = round(d[9],2) # registro 187 
                
                if d[12] > 32767 : d[12] -= 65535
                datos['BatteryOutputPower'] = d[12] # registro 190
                
                if d[13] > 32767 : d[13] -= 65535
                
                datos['Ibatn'] = round(d[13]/100,2) # registro 191
                datos['Ibat'] = -round(d[13]/100,2) # registro 191 con signo negativo si sale de bateria
                datos['Fout'] = round(d[15]/100,2) # registro 193
                datos['GridSideRelayStatus'] = d[16] # registro 194
                datos['GeneratorSideRelayStatus'] = d[17] # registro 195
                if (d[70]) == 0: # registro 248
                    datos['TimeOfUseSelling'] = "OFF"
                else:
                    datos['TimeOfUseSelling'] = "ON"
                
                ee = 220
                if d[106] == 0: #registro 284
                    datos['GridMode'] = "General_Standard"
                elif d[106] == 1:
                    datos['GridMode'] = "UL1741&IEE1547"
                elif d[106] == 2:
                    datos['GridMode'] = "CPUC_RULE21"
                elif d[106] == 3:
                    datos['GridMode'] = "SRD-UL1741"
                
                
                # --- Mapeo de Configuración ---
                # Índice = Registro - 178
                
                datos['BatteryControlMode'] = d[22] # 200 (0x00C8)
                
                # 201 (0x00C9) ya NO se usa aquí
                
                datos['ZeroExportW'] = d[28] # 206 (0x00CE) 
                datos['MaxChargeCurrent'] = d[32] # 210 (0x00D2)
                datos['MaxDischargeCurrent'] = d[33] # 211 (0x00D3)
                datos['ShutdownSOC'] = d[39] # 217 (0x00D9)
                datos['LowSOC'] = d[41] # 219 (0x00DB) 
                datos['ShutdownV'] = round(d[42] / 100, 2) # 220 (0x00DC) 
                datos['RestartV'] = round(d[43] / 100, 2) # 221 (0x00DD) 
                datos['LowV'] = round(d[44] / 100, 2) # 222 (0x00DE)
                datos['GenStartV'] = round(d[47] / 100, 2) # 225 (0x00E1) 
                datos['GenStartSOC'] = d[48] # 226 (0x00E2)
                
        except:
            error= True
            print(f'error en captura {ee}')
        
    t3= time.time()
    
    if DEBUG == 1:
        if tipo_conexion == 'RS485':  print(Fore.BLUE, end='')
        else : print(Fore.CYAN, end='')
        print ('=' *80)
        print (f'Tipo Captura = {tipo_conexion}   Tiempo captura ={t3-t1:.2f}sg -- Bloque 1: {t2-t1:.2f}sg -- Bloque 2 (Consolidado): {t3-t2:.2f}sg')
        print(time.strftime("%Y-%m-%d %H:%M:%S"), datos) 

    
    try:####  ARCHIVOS RAM en BD ############ 
        ee = '300' 
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        if not error:
            datos['Nfallos'] = n_fallos_lectura[I_equipo]
            
            salida = json.dumps(datos)
            sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{nombre_equipo}'") 
            cursor.execute(sql)
            ee = 310
            db.commit()
            print('G', flush= True, end='')
        else:
            n_fallos_lectura[I_equipo] += 1
            print(f'{tiempo} - Error {ee} en captura equipo {nombre_equipo}')
            
    except:
        print(Fore.RED+f'error {ee}, Grabacion tabla RAM equipos en {nombre_equipo}')
    
    cursor.close()
    db.close()
    
    if tipo_conexion == 'WIFI':  modbus.disconnect()
    
    
# Bucle para llamada a funcion leer_equipo
n_recarga_parametros = 0
n_fallos_lectura = [0] * 10 
dia = time.strftime("%Y-%m-%d")

while True:
    n_recarga_parametros += 1
    if n_recarga_parametros == 15: # cada XX bucles
        n_recarga_parametros = 0
        if DEBUG == 1: print(Fore.RED + 'recarga Parametros')
        exec(open(parametros_FV_DIST).read(),globals()) 
        exec(open(parametros_FV).read(),globals()) 
    
    dia_anterior = dia
    dia = time.strftime("%Y-%m-%d")

    if dia_anterior != dia: #cambio de dia
        n_fallos_lectura = [0] * 10
        
    try:
        for i in range(len(eval(f'usar_{equipo}'))):
            if eval(f'usar_{equipo}[{i}]') == 1:
                if int(time.time()) % eval(f't_muestra_{equipo}[{i}]') == 0:
                    leer_equipo(i)
                    
    except:
        print ('Error desconocido....')
        sys.exit()
    
    time.sleep(1)
