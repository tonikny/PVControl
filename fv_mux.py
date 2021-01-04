#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-01-02

# #################### Control Ejecucion Servicio ########################################
servicio = 'fv_mux'
control = 'usar_mux'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

archivo_ram = '/run/shm/datos_mux.json'

import MySQLdb,json,time
import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token

from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

"""
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Style: DIM, NORMAL, BRIGHT, RESET_ALL
"""
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_mux') #+Style.RESET_ALL)

Nlog = Nlog_max = 2 # Contador Numero de log maximos cada minuto
minuto = time.strftime("%H:%M")

def logBD(texto) : # Incluir en tabla de Log
    global Nlog, minuto

    Nlog -=1
    if time.strftime("%H:%M") != minuto:
        minuto = time.strftime("%H:%M")
        Nlog = Nlog_max
    if Nlog > 0:
        try:
            cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,texto))
            db.commit()
        except:
            print()
            print (Fore.RED,'Error log', texto)
            db.rollback()
    return

#Comprobacion argumentos en comando 
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p2':
    DEBUG = 2
elif str(sys.argv[narg-1]) == '-p3':
    DEBUG = 3
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 100
elif str(sys.argv[narg-1]) == '-t':
    DEBUG = 50
else:
    DEBUG = 0
print (Fore.RED + 'DEBUG=',DEBUG)

if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]


bus = SMBus(1) # Activo Bus I2C

if pin_ADS_mux1[0:2] == 'A2': #activo Mux1
    ads_mux1= int(pin_ADS_mux1[-1]) - 1
    adc1 = Adafruit_ADS1x15.ADS1115(address=72+ads_mux1, busnum=1)
    print (' Activando Mux1 en ',pin_ADS_mux1)

if pin_ADS_mux2[0:2] == 'A3': #activo Mux2
    ads_mux2= int(pin_ADS_mux2[-1]) - 1
    adc2 = Adafruit_ADS1x15.ADS1115(address=72+ads_mux2, busnum=1)
    print (' Activando Mux2 en ',pin_ADS_mux2)

DatosMux = {}  #diccionario para los datos de cada celda
DatosMux_ant = {}  #diccionario para los datos anteriores de las celdas

DatosMux_v = {}  #diccionario para los datos de entrada al Mux en voltaje a conector
DatosMux_n = {}  #Creamos diccionario para los datos Mux en numero capturado en ADS
DatosMux_err = {}  #Creamos diccionario para ver margen de error en captura
Vcelda_max = [0.0] * usar_mux # Maximo de cada celda diaria
Vcelda_min = [1000.0] * usar_mux # Minino de cada celda diaria

dia = time.strftime("%Y-%m-%d")

#-------BUCLE ----------------------------------------------
flag_primer_bucle = True
while True:
    crono = [] # cronografo tiempo ejecucion
    t0=time.time()
    
    ### B2---------------------- LECTURA FECHA / HORA ----------------------
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    tiempo_sg = time.time()
    tiempo_us = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    diasemana = time.strftime("%w")
    hora = time.strftime("%H:%M:%S") #No necesario .zfill() ya pone los ceros a la izquierda
    dia_anterior = dia
    dia = time.strftime("%Y-%m-%d")
    
    DatosMux['Tiempo'] = tiempo # asignamos fecha/hora

    if dia_anterior != dia: #cambio de dia
        Vcelda_max = [0.0] * 16 
        Vcelda_min = [1000.0] * 16

    #### CAPTURA VALORES MUX ############
    crono.append(time.time())
    
    for K in range(usar_mux): #para mux2 faltan temas  
        
        bus.write_byte(32,K) # escribo en PCF 32

        if DEBUG >= 100:
            estado = bus.read_byte(32) # compruebo dato PCF
            if estado != K:
                print ('Error en escritura/lectura PCF 32 con datos', K,'/',estado)
       
        time.sleep(0.001)
        
        try:
            ###### Lectura Mux 1       
            Suma = 0; Max=-40000; Min=-Max
            N = 5
            for i in range(N):
                l = adc1.read_adc(2, gain=1,data_rate=32)
                Suma += l
                Max = max(Max,l)
                Min = min(Min,l)
            lectura_ADS = Suma/N
            
            DatosMux_n['C'+str(K)] = lectura_ADS  # Valor numerico capturado
            DatosMux_err['C'+str(K)] = Max-Min    # Rango error valor numerico capturado
            DatosMux_v['C'+str(K)] = round(lectura_ADS * 0.000125 * r_mux1[K]* r_mux1_c[K],4) #    4,096V/32767=0.000125    
            
       
        except:
            logBD('-ERROR MEDIDA MUX1-'+ str(K))
    
    crono.append(['ADS',round(time.time() - t0,2)])
    # CALCULO VALORES CELDAS
    DatosMux_ant = DatosMux.copy() #situacion anterior
    
    DatosMux['C0'] = DatosMux_v['C0']
    for K in range(1,usar_mux):
        K1 = 'C'+str(K)
        DatosMux[K1] = round(DatosMux_v[K1] - DatosMux_v['C'+str(K-1)],2)
    
    
    if flag_primer_bucle: 
        flag_primer_bucle = False
        continue # ejecuta un nuevo ciclo
    
    #Filtro variaciones rapidas    
    for x in DatosMux:
        salto_max = 0.1       
        if x[0] =='C':
            if (DatosMux[x] - DatosMux_ant[x]) > salto_max:  DatosMux[x] = DatosMux_ant[x] + salto_max
            elif (DatosMux[x] - DatosMux_ant[x]) < -salto_max:  DatosMux[x] = DatosMux_ant[x] - salto_max  
        
    CeldaMax = CeldaMin = ('C0',DatosMux['C0'])
    for K in range(usar_mux):
        Vcelda_max[K] = max(Vcelda_max[K],DatosMux[K1])
        Vcelda_min[K] = min(Vcelda_min[K],DatosMux[K1])
        
        if DatosMux[K1] > CeldaMax[1]: CeldaMax = (K1,DatosMux[K1])
        if DatosMux[K1] < CeldaMin[1]: CeldaMin = (K1,DatosMux[K1])
    DifCeldas = round(CeldaMax[1]-CeldaMin[1],2)

    crono.append(['Listas',round(time.time() - t0,2)])
    # PRINT dependiendo argumentos
    if DEBUG >= 2:
        print(Fore.GREEN,'Valores capturados=',DatosMux_n.values())
        print('----------')
    if DEBUG >= 3:
        print(Fore.RED,'Error en ',N, 'Capturas=',DatosMux_err.values())
        print('----------')
    if DEBUG >= 2:
        print()
        print('#' * 80)
        print(Fore.BLUE,'Voltajes capturados =',*DatosMux_v.values())
        print('#' * 80)
        print(Fore.MAGENTA,'Vceldas =',end='')
        print(*DatosMux.values(),sep=' / ')
        
        print(Fore.YELLOW,'Max= ',end='')
        print(*Vcelda_max,sep=' / ')
        print(Fore.YELLOW,'Min= ',end='')
        print(*Vcelda_min,sep=' / ')
        
        print (Fore.CYAN,'CeldaMax=',CeldaMax, ' -- CeldaMin=',CeldaMin,
               ' -- Dif=',round(DifCeldas,2))
               
    crono.append(['print',round(time.time() - t0,2)])
    #### REGISTRO EN BD ############
    try:
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        
        # Log si hay celdas descompensadas
        if DifCeldas > celdas_log_dif:
            log = ('='.join(map(str, CeldaMax)) + ' / ' + '='.join(map(str, CeldaMin)) +
                   ' / Dif=' + str(DifCeldas))
            #print('error celdas',minuto,Nlog, log)
            logBD ('Celdas descomp. ' + log)
        
        # Insertar Registro en BD
        campos = ",".join(DatosMux.keys())
        valores = "','".join(str(v) for v in DatosMux.values())
        Sql = "INSERT INTO datos_mux_1 ("+campos+") VALUES ('"+valores+"')"
        cursor.execute(Sql)
        
        db.commit()
        cursor.close()
        db.close()
        
    except:
        print('error, BD', Sql)
        db.rollback()
        pass
    crono.append(['BD',round(time.time() - t0,2)])
    ####  ARCHIVO RAM ############ 
   
    try:
        with open(archivo_ram, mode='w') as f:
            MUX=[]
            MUX_aux=[]
            for K in range(usar_mux): MUX_aux.append ('C'+str(K+1))
            MUX.append (MUX_aux)
            MUX_aux=[]
            for K in range(usar_mux): MUX_aux.append (Vcelda_max[K])
            MUX.append (MUX_aux)
            MUX_aux=[]
            for K in range(usar_mux): MUX_aux.append (DatosMux['C'+str(K)])
            MUX.append (MUX_aux)
            
            #if DEBUG >= 1: print(MUX_aux) 
            
            MUX_aux=[]
            for K in range(usar_mux): MUX_aux.append (Vcelda_min[K])
            MUX.append (MUX_aux)
            
            if DEBUG >= 1: print (MUX)
            
            json.dump(MUX,f)
    except:
        print('error, Grabacion archivo RAM',archivo_ram)
    
    crono.append(['RAM',round(time.time() - t0,2)])
    if DEBUG == 50:
        print ('Crono =', crono[1:])
    elif DEBUG == 0: print (Fore.BLUE,round(time.time()-tiempo_sg,2),end='/',flush=True) # Print de control
    
    
    time.sleep(t_muestra_mux - (time.time()-tiempo_sg))
    
