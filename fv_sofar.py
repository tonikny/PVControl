#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión XXX2021-12-22

import sys, time
import MySQLdb,json
import subprocess

import minimalmodbus

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0]) #+Style.RESET_ALL)


#### Parametros_FV.py ##########
usar_sofar = [0,0] 

dir_modbus_sofar = [1,2]          # Direccion en la red MODBUS de cada equipo
t_muestra_sofar = [5,5]           # Tiempo en segundos entre muestras
publicar_sofar_mqtt = [0,0]       # Publica o no por MQTT los datos capturados (no implementado aun)
#grabar_datos_sofar = [0,0]       # 1 = Graba la tabla Hibrido... 0 = No graba
n_muestras_sofar = [1,1]          # grabar en BD cada nmuestras
                                      
dev_sofar = ["/dev/ttyUSB0","/dev/ttyUSB0"]    # puerto donde reconoce la RPi a cada equipo                                      
# ###############################################

basepath = '/home/pi/PVControl+/'
parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"
parametros_FV_DIST = "/home/pi/PVControl+/Parametros_FV_DIST.py"
exec(open(parametros_FV_DIST).read(),globals()) #cargo Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
exec(open(parametros_FV).read(),globals()) #cargo Parametros_FV.py
    
equipo = 'sofar'
servicio = "fv_sofar"

if sum(eval(f'usar_{equipo}')) == 0:
    print (subprocess.getoutput(f'sudo systemctl stop {servicio}'))
    sys.exit()

#Comprobacion argumentos en comando
simular = DEBUG= 0
narg = len(sys.argv)
if '-s' in sys.argv: simular= 1 # para desarrollo permite simular respuesta 
if '-p1' in sys.argv: DEBUG= 1 # para desarrollo permite print en distintos sitios
elif '-p' in sys.argv: DEBUG= 100

    
def captura_datos(equipo,I_Equipo):
    global n_muestras_contador, ee2
    
    t_inicio_captura = time.time()
    
    # CAPTURA REGISTROS
    try:
        ee2='100'
        if I_Equipo == 0: N_Equipo = ""
        else: N_Equipo = f"{I_Equipo}"

        datos= {} # Diccionarios datos
    
        ts = 0.1
        if DEBUG == 100:
            print()
            print ('#' * 60)
            
        # OFF GRID
        ee2='110'
        time.sleep(ts)
        D = rs485[I_Equipo].read_registers(0x0504, 36, 3) 
        if DEBUG == 100:
            print()
            print (Fore.YELLOW+f'OFF GRID {I_Equipo} ',D)
            
        datos['Wconsumo_504'] = int(D[0] *10)
        datos['Hz'] = round(D[3]/100,2)
        
        datos['Vred'] = round(D[6]/10,1)
        datos['Wred'] = int(D[8] *10)
        

        
        # ON GRID
        ee2='120'
        time.sleep(ts)
        D = rs485[I_Equipo].read_registers(0x0484, 57, 3) 
        if DEBUG == 100:
            print()
            print (Fore.RED+f'ON GRID {I_Equipo}',D)
        
        datos['Wconsumo_485'] = int(D[1] *10)
        datos['Wconsumo_4AE'] = int(D[42] *10)
        datos['Wconsumo_4AF'] = int(D[43] *10)
        
        
        # Bateria 
        ee2='130'
        
        time.sleep(ts)
        D = rs485[I_Equipo].read_registers(0x0604, 7 * 1, 3) # 7 registros x Bat1 a Bat8
        if DEBUG == 100:            
            print()
            print (Fore.GREEN + f'Bat {I_Equipo}',D)
        
        """
        time.sleep(ts)
        D1 = rs485.read_registers(0x0644, 7 * 4, 3) # 7 registros x bat9 a bat12
        print ('Bat9 ',D1)
        """
        
        
        datos['Vbat1'] = round(D[0]/10,1)
        
        if D[1] > 32767 :   datos['Ibat1'] = round((D[1] - 65535)/100,2)
        else:               datos['Ibat1'] = round(D[1]/100,2)
        
        if D[2] > 32767 :   datos['Wbat1'] = int((D[2] - 65535)*10)
        else:               datos['Wbat1'] = int(D[2]*10)
        
        datos['temp1'] = D[3]
        datos['SOC1'] = D[4]
        datos['SOH1'] = D[5]
        datos['Ciclos1'] = D[6]
        
        """
        datos['Vbat2'] = round(D[7]/10,1)
        if D[8] > 32767 :   datos['Ibat2'] = round((D[8] - 65535)/100,2)
        else:               datos['Ibat2'] = round(D[8]/100,2)
        if D[9] > 32767 :   datos['Wbat2'] = int((D[9] - 65535)*10)
        else:               datos['Wbat2'] = int(D[9]*10)
        
        datos['temp2'] = D[10]
        datos['SOC2'] = D[11]
        datos['SOH2'] = D[12]
        datos['Ciclos2'] = D[13]
        """
        
        ee2='139'
        time.sleep(ts)
        datos['Wbat_t'] = int(rs485[I_Equipo].read_register(0x0667, 1, 3, True) * 1000)
        
        
        # PLacas
        ee2='140'
        time.sleep(ts)
        D = rs485[I_Equipo].read_registers(0x0584, 3 * 2, 3) # 3 registros * 16 strings
        if DEBUG == 100:
            print()
            print (Fore.MAGENTA + f'Placas {I_Equipo}',D)
        
        datos['Vplaca1'] = round(D[0]/10,1)
        datos['Iplaca1'] = round(D[1]/100,2)
        datos['Wplaca1'] = int(D[2]*10)
        
        datos['Vplaca2'] = round(D[3]/10,1)
        datos['Iplaca2'] = round(D[4]/100,2)
        datos['Wplaca2'] = int(D[5]*10)
        
        
        
        ee2='149'
        time.sleep(ts)
        datos['Wplaca_t'] = int(rs485[I_Equipo].read_register(0x05C4, 1, 3, False) *1000)
        
        
        # Energia
        ee2='150'
        time.sleep(ts)
        D = rs485[I_Equipo].read_registers(0x0684, 24, 3) 
        if DEBUG == 100:            
            print()
            print (Fore.RESET + f'Energia {I_Equipo}',D)
        
        # Temperaturas
        ee2='160'
        time.sleep(ts)
        D = rs485[I_Equipo].read_registers(0x0418, 4, 3) # aqui se leen 4 registros desde 0418
        if DEBUG == 100:            
            print()
            print (Fore.RESET + f'Temperaturas {I_Equipo}',D)
        datos['T1_ambiente'] = int(D[0]) # se asigna el primer registro 
        #datos['T2_ambiente'] = int(D[1]) # da siempre 0
        datos['T1_disipador'] = int(D[2])  # se asigna el tercer registro
        #datos['T2_disipador'] = int(D[3]) # da siempre 0
        
        # Campos calculados
        ee2='200'
        """
        datos['Vbat'] = datos['Vbat1']
        datos['Ibat'] = datos['Ibat1']
        
        datos['Vplaca'] = datos['Vplaca1']
        datos['Iplaca'] = round(datos['Iplaca1'] + datos['Iplaca2'],2)
        
        datos['Wplaca'] = datos['Wplaca_t']
        """
    except:
        print (f'Error captura_datos...{ee2}')
        
    # PRINT datos capturados
    t_captura = time.time()-t_inicio_captura
    if DEBUG >= 1:
        if I_Equipo == 0: print (Fore.BLUE, end='')
        elif I_Equipo == 1: print (Fore.CYAN, end='')
        else: print (Fore.YELLOW, end='')
        
        print('=' * 40)
        print(time.strftime("%Y-%m-%d %H:%M:%S"), f' - Equipo {I_Equipo} - t_captura = {t_captura:.2f}')
        print(datos)
        #for i in datos: print(f'{i}= {datos[i]}')    
    
    
    ####  ARCHIVO TABLA equipos en BD ############
    try: 
        ee2='1000'
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        salida = json.dumps(datos)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{equipo.upper()}{N_Equipo}'") # grabacion en BD RAM
        #print (Fore.RED+sql)
        cursor.execute(sql)
        #db.commit()
    except:
        print(Fore.RED+f'error, Grabacion tabla RAM equipos en {equipo.upper()}{N_Equipo}')
    

    db.commit()


# Comprobacion BD - Inicializacion Registros Tabla equipos

n_muestras_contador = [1 for i in range(len(eval(f'usar_{equipo}')))] # contadores grabacion BD

#INICIALIZACION
try:
    ee = '10'
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    rs485 = [] # lista de conexiones Modbus
    
    for i in range(len(eval(f'usar_{equipo}'))):
        ee = '10a'    
        if eval(f'usar_{equipo}[{i}]') == 1:
            if i==0: N_Equipo = ""
            else: N_Equipo = f"{i}"
            
            try: #Inicializamos conexion modbus
                rs485.append(minimalmodbus.Instrument(dev_sofar[i], dir_modbus_sofar[i]))
                rs485[i].serial.baudrate = 9600
                rs485[i].serial.bytesize = 8
                rs485[i].serial.parity = minimalmodbus.serial.PARITY_NONE
                rs485[i].serial.stopbits = 1
                rs485[i].serial.timeout = 1
                rs485[i].debug = False
                rs485[i].mode = minimalmodbus.MODE_RTU
            except:
                print('Error inicializacion conexion Modbus', i)
                sys.exit()

            try: #inicializamos registro RAM y tabla si no existe en BD 
                                   
                ee = '10b'
                cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                              (equipo.upper()+ N_Equipo ,'{}'))   
                db.commit()
            except:
                pass             
    
    cursor.close()
    db.close() 

except:
    print (Fore.RED,f'ERROR {ee} - inicializando ')
    sys.exit()


if __name__ == '__main__':  

    # Conexion BD
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    # Ver numero Equipos activos
    Equipos_activos = [ i for i in range(len(usar_sofar)) if usar_sofar[i] == 1 ] # indices equipos activos
    
    print (Fore.RESET+'=' * 50)
    print(Fore.BLUE+'SOFAR_activos=')
    for i in Equipos_activos: 
        print(Fore.RED+f' SOFAR{i}: {Fore.BLUE} dev={dev_sofar[i]} -t_muestra={t_muestra_sofar[i]}- n_muestras={n_muestras_sofar[i]}')
        print()
    print (Fore.RESET+'=' * 50)
    time.sleep(0.1)
    
    
    #### BUCLE 
    tiempo_sg = [time.time()] * len(usar_sofar)
        
    while True:
        try:
            ee1 = ee2 = 10
            
            for i in Equipos_activos:
                if time.time() - tiempo_sg[i] > eval(f't_muestra_{equipo}[{i}]'):
                    tiempo_sg[i] = time.time()
                    ee1 = 20
                    try:
                        captura_datos(equipo,i)
                    except:
                        print (f'Error_lectura {ee2}')
        except:
            print (f'Error desconocido....{ee1} {ee2}')
            cursor.close()
            db.close() 
            sys.exit()
        
        time.sleep(0.1)
    
    
