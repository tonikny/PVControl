#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2025-03-03

parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"

########## Valores por defecto si no hay nada en Parametros_FV.py  ###########
usar_pylontech_consola = 0
baudrate_pylontech_consola = 115200
port_pylontech_consola ='/dev/ttyUSB0'
timeout_pylontech_consola = 1
n_pylontech = 4 # Número de baterías pylontech que forman el banco
  

# #################### Control Ejecucion Servicio ########################################
servicio = 'pylontech_consola'
control = 'usar_pylontech_consola'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

import serial
import time
from datetime import date
from Parametros_FV import *
import json
import colorama
from colorama import Fore, Back, Style
import sys
import MySQLdb
from datetime import datetime
from utils import Utils
try:
    import telebot
    import token
except: 
    usar_tg=0
    pass


if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

if usar_pylontech_consola == 0:
    print(subprocess.getoutput('sudo systemctl stop pylontech_consola'))
    sys.exit()

try:  
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(Aut[0], f'Inicializando TG')
    print('BOT: ', bot, 'Usar_TG: ', usar_tg)
except:
    usar_tg=0
    pass

colorama.init()
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' pylontech_consola') #+Style.RESET_ALL)


#Comprobacion argumentos en comando
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 100
else:
    DEBUG = 0
print (Fore.YELLOW + 'DEBUG=',DEBUG)

AH_p = [0]*n_pylontech
AH_n = [0]*n_pylontech
AH = [0]*n_pylontech

ser = serial.Serial()
ser.baudrate= baudrate_pylontech_consola
ser.port= port_pylontech_consola
ser.timeout = 1
#ser.open()
time.sleep(0.05)

db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()

def logBD(texto) : # Incluir en tabla de Log
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    #global Nlog, minuto
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    #Nlog -=1
    #if time.strftime("%H:%M") != minuto:
    #    minuto = time.strftime("%H:%M")
    #    Nlog = Nlog_max
    #print(Fore.YELLOW, 'Pasa por logBD', 'Texto: ', texto)
    #if Nlog > 0:
    try: 
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,texto))
        #print (tiempo,' ', texto)
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print('Error al insertar en log', e)

    return

def calculo_max_min():
    tiempo = datetime(datetime.now().year,datetime.now().month,datetime.now().day, 0,0,0)
    #print(tiempo)
    Vceldas_max = []
    Vceldas_min = []
    db = MySQLdb.connect(host='localhost', user='rpi', passwd='fv', db='control_solar')
    cursor = db.cursor()
    for j in range(0,n_pylontech):
        Vceldas_max.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        Vceldas_min.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        #print(Vceldas_max[0])
        for i in range(0,15):
            sql = (f"SELECT MAX(C{i+1}) FROM datos_celdas_BMS_PYL{j+1} WHERE Tiempo > '{tiempo}'")
            cursor.execute(sql)
            a = cursor.fetchall()
            Vceldas_max[j][i] = a[0][0]
        
            
        for i in range(0,15):
            sql = (f"SELECT MIN(C{i+1}) FROM datos_celdas_BMS_PYL{j+1} WHERE Tiempo > '{tiempo}'")
            cursor.execute(sql)
            a = cursor.fetchall()
            Vceldas_min[j][i] = a[0][0]
            
        sql = (f"SELECT AH_p, AH_n, Tiempo FROM datos_celdas_BMS_PYL{j+1}  WHERE Tiempo > '{tiempo}' ORDER BY id_celda DESC LIMIT 1")
        cursor.execute(sql)
        a = cursor.fetchall()
        #print(a)
        AH[j] = a
    #print(Fore.WHITE,datetime.now(),Fore.BLUE, 'AH', AH) 
        
    #for i in range(0,4):
    #    print(Vceldas_max[i])        
    #    print(Vceldas_min[i])
    cursor.close()
    db.close()    
    return(Vceldas_max, Vceldas_min,AH)

def lectura_datos():
    
    
    
    ser = serial.Serial()
    ser.baudrate= baudrate_pylontech_consola
    ser.port= port_pylontech_consola
    ser.open()
    time.sleep(0.05)
    line_str_array = ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
    c = [[0]*15]* n_pylontech
    t = [[0]*15]* n_pylontech
    s = [['']*15]* n_pylontech
    Intensidad = [0] * n_pylontech
    SOC = [0] * n_pylontech
    SOCT=[[0]*15]* n_pylontech
    
    for i in range (0,n_pylontech):
        c[i] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        t[i] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        SOCT[i] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        s[i] = ['','','','','','','','','','','','','','','']
        Intensidad[i] = 0
        SOC[i] = 0
        
        a = 'bat ' + str(i+1) + '\n'
        #print(c)
        ser.write(bytearray(a,'utf-8'))
        time.sleep(0.20)
        line_str =' '
        l = 0
        while ser.in_waiting > 0:
        
            line          = ser.read()    
            line_str = line_str + line.decode('latin-1')
            #print(line)
            if line == b'\n':
                #print(l,line_str)
                line_str_array[l] = line_str
                #print(line_str)
                line_str =''
                l+=1
        time.sleep(0.15)
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        
        
        Intensidad[i] = int(line_str_array[3][15]+line_str_array[3][16]+line_str_array[3][17]+line_str_array[3][18]+line_str_array[3][19]+line_str_array[3][20]+line_str_array[3][21]+line_str_array[3][22]+line_str_array[3][23])/1000
        #print('Intensidad',Intensidad[i])
        
        
        #####     Calculo SOC      #######
        try:
            if line_str_array[3][90].isdigit():
                SOC[i] =        int(line_str_array[3][86]+line_str_array[3][87]+line_str_array[3][88]+line_str_array[3][89] +line_str_array[3][90])
            else:
                SOC[i] =        int(line_str_array[3][86]+line_str_array[3][87]+line_str_array[3][88]+line_str_array[3][89]) #+line_str_array[3][90])          
            #print('SOC', SOC)
        except Exception as e:
            print(e)
            raise
        #print('SOC',SOC[i])      
        if DEBUG == 1: print('i:', i, '86:',line_str_array[3][86],'87:',line_str_array[3][87],'88:',line_str_array[3][88],'89:',line_str_array[3][89],'90:',line_str_array[3][90] )
        
        
        #####     Calculo Tensiones      ####### 
        
        try:
            for j in range (3,18):
                c[i][j-3]= (int(line_str_array[j][9])*1000+int(line_str_array[j][10])*100+int(line_str_array[j][11])*10+int(line_str_array[j][12]))/1000
                if c[i][j-3] > 3.8 or c[i][j-3] < 2.75 : 
                    logBD(f'lectura incoherentede tension en bateria {i+1} celda {j-2}: {c[i][j-3]}')
                    if usar_tg: bot.send_message(Aut[0], f'lectura incoherentede tension en bateria {i+1} celda {j-2}: {c[i][j-3]}')
                    
                if c[i][j-3] > 3.65 or c[i][j-3] < 3.05 : 
                    logBD(f'lectura alta/baja tension en bateria {i+1} celda {j-2}: {c[i][j-3]}')
                    #bot.send_message(Aut[0], f'lectura alta/baja tension en bateria {i+1} celda {j-2}: {c[i][j-3]}')
        except:
            print('Error captura tensiones')
            
            time.sleep(1)
            sys.exit()
            ser.close()            
            pass   
        #print('Tensiones',c[i])
        
        
        
        #####     Calculo temperaturas      ####### 
        
        try:
            for j in range (3,18):
                #print(line_str_array[j][25],line_str_array[j][26])
                #for k in range(26,31):
                    #if line_str_array[j][k] == ' ' : line_str_array[j][k] = '0'                   
                
                    #else: a = int(line_str_array[j][26])
                #t[i][j-3]= a*10000+int(line_str_array[j][27])*1000+int(line_str_array[j][28])*100+int(line_str_array[j][29])*10+int(line_str_array[j][30])
                t[i][j-3]= int(line_str_array[j][26]+line_str_array[j][27]+line_str_array[j][28]+line_str_array[j][29]+line_str_array[j][30])
            #print(line_str_array[j][25],line_str_array[j][26])
        except:
            print(t[i])
            print('Error captura temperaturas')
            #t = None            
            break
            
            
        ###########  Calculo SOC   ####################    
        try:
            for j in range (3,18):
                if line_str_array[j][90].isdigit():
                    SOCT[i][j-3] =  int(line_str_array[j][86]+line_str_array[j][87]+line_str_array[j][88]+line_str_array[j][89] +line_str_array[j][90])
                else:
                    SOCT[i][j-3] =  int(line_str_array[j][86]+line_str_array[j][87]+line_str_array[j][88]+line_str_array[j][89]) #+line_str_array[3][90])          
            
                
        except Exception as e:
            print(e)
            pass
            
        
        #############################################################
        if DEBUG == 1: print(Fore.RED, 'Temperaturas', t[i])
        
        #print('Temperaturas', t[i])
        
        try:
            for j in range (3,18):
                s[i][j-3]= line_str_array[j][49] + line_str_array[j][50] + line_str_array[j][51] + line_str_array[j][52] + line_str_array[j][53] +line_str_array[j][54] 
        except:
            print('Error captura estados')
            s = None            
            pass
            
        #print('Estados', s[i])
            
        if DEBUG == 1: print(Fore.YELLOW, 'Estados', s[i])
        
    if DEBUG==1:print(Fore.BLUE, c,t,s)
    #print('SOC', SOCT)
    #if c[0][0] == 1 or c[1][0] == 2 or c[2][0] == 3  : sys.exit()
    #if DEBUG==1:print(Fore.RED, 'if' , c[0][0], c[1][0], c[2][0])
    ser.close()
    #print('c,t,s,Intensidad, SOC', c,t,s,Intensidad, SOC)
    return (c,t,s,Intensidad, SOC,SOCT)

def lectura_log():
    ser = serial.Serial()
    ser.baudrate= baudrate_pylontech_consola
    ser.port= port_pylontech_consola
    ser.open()
    
        
    a = 'log\n'
    #print('LOG:', a)
    ser.write(bytearray(a,'utf-8'))
    time.sleep(0.2)
    line_str =' '
    l = 0
    log = ''
    while ser.in_waiting > 0:
        
        line          = ser.read()    
        line_str = line_str + line.decode('latin-1')
        #print(line)
        if line == b'\n':
            #print(l,line_str)
            #line_str_array[l] = line_str
            if l == 5 or l ==6 :
                log = log + line_str
            #if i == 3: print('Linea:', l, line_str)
            line_str =''
            l+=1
    return(log)

logBD('Arrancando Pylontech Consola')
if usar_tg: bot.send_message(Aut[0], f'Arrancando Pylontech Consola')

nceldas = 15
Nombre_Celdas = ['C'] * nceldas
for i in range(nceldas): Nombre_Celdas[i] = f'C{i+1}'

log_ant = ''
Intensidad = [0,0]
SOC =  [0,0]
equipo = []
Vceldas =  []
Tceldas = []
Eceldas = []
PYL = [0]*n_pylontech
dfet = [0]*n_pylontech
cfet = [1]*n_pylontech
dfet_flag = [0,0,0,0]
cfet_flag = [0,0,0,0]
Vbat = [0]*n_pylontech

VMAX = 3
SOCMIN = 50
dia = 0
dia_ant = 0

for i in range(1,n_pylontech + 1):
    equipo.append("BMS_PYL" + str(i))
    Vceldas.append([i,i,i,i,i,i,i,i,i,i,i,i,i,i,i])
    Tceldas.append([i,i,i,i,i,i,i,i,i,i,i,i,i,i,i])
    Eceldas.append([str(i),str(i),str(i),str(i),str(i),
                    str(i),str(i),str(i),str(i),str(i),
                    str(i),str(i),str(i),str(i),str(i)])
                    
if DEBUG == 1: 
    print('--------------------------------------------------------------')
    print(' Inicialización de  valores de celdas')
                    
    for i in range(0, n_pylontech):
        print(Fore.GREEN, Vceldas[i])
        print(Fore.YELLOW, Tceldas[i])
        print(Fore.GREEN, Eceldas[i])
    
    print('--------------------------------------------------------------')
    print('Equipos creados: ', equipo)

###-------------------------Inicialización tabla equipos-------------------------------###

for i in range(0,n_pylontech):           
    try:
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        
        try: #inicializamos registro en BD RAM
            cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                          (equipo[i],'{}'))
            db.commit()
        except:
            pass
        cursor.close()
        db.close()    

    except Exception as e:
        print (e)
        sys.exit()
        
###-------------------------Inicialización tablas datos_celdas-------------------------------###  
      
db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()
    
for i in range(0,n_pylontech):
    try:
        Sql = f"""    
                     CREATE TABLE IF NOT EXISTS `datos_celdas_{equipo[i]}` (
                    `id_celda` int(11) NOT NULL AUTO_INCREMENT,
                    `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
                    `Ibat` float NOT NULL DEFAULT 0,
                    `AH_p` float NOT NULL DEFAULT 0,
                    `AH_n` float NOT NULL DEFAULT 0,
                    `SOC` float NOT NULL DEFAULT 0,
                    `C1` float NOT NULL DEFAULT 0,`C2` float NOT NULL DEFAULT 0,`C3` float NOT NULL DEFAULT 0,
                    `C4` float NOT NULL DEFAULT 0,`C5` float NOT NULL DEFAULT 0,`C6` float NOT NULL DEFAULT 0,
                    `C7` float NOT NULL DEFAULT 0,`C8` float NOT NULL DEFAULT 0,`C9` float NOT NULL DEFAULT 0,
                    `C10` float NOT NULL DEFAULT 0,`C11` float NOT NULL DEFAULT 0,`C12` float NOT NULL DEFAULT 0,
                    `C13` float NOT NULL DEFAULT 0,`C14` float NOT NULL DEFAULT 0,`C15` float NOT NULL DEFAULT 0,
                     PRIMARY KEY (`id_celda`),
                     KEY `Tiempo` (`Tiempo`)
                     ) 
                     ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
                     """
        
        
        
        cursor.execute(Sql)
        db.commit()
    

    except Exception as e:
        print('error inicializacion tablas datos celdas', e)
        pass
    
cursor.close()
db.close()

###-------------------------------------------------------------------------------------------### 
try:      
    datos = calculo_max_min()
    #print(datos)
    Vceldas_max = datos[0]
    Vceldas_min = datos[1]
    #print(AH)
    for i in range(0,n_pylontech):
        AH_p[i] = AH[i][0][0]
        AH_n[i] = AH[i][0][1]
    print(datetime.now(),' AH_p', AH_p, 'AH_n', AH_n)
except Exception as e:
    print(e)
    raise
    
if DEBUG == 1: 
    print(Fore.BLUE, '----------------------------------------------------------------------------------------')
    print('Maximos y minimos iniciales')
    print(Fore.YELLOW, '--------------Vceldas_max---------------------------------------------------------------')
    for i in range(0, n_pylontech):
        print('Máximos celdas batería', i+1, Vceldas_max[i])
    print(Fore.GREEN,'--------------Vceldas_min---------------------------------------------------------------')
    for i in range(0, n_pylontech):
        print('Mínimos celdas batería', i+1, Vceldas_min[i])

time.sleep(1)



        
    
        


while True:
    #print("------------------------------------------------------------------------------------")
    #print('Tiempo: ', round(time.time(),0))
    
    dia_ant = date.today()
    
    try:
        t1 = time.time()
        #print('antes funcion lectura datos')
        datos = lectura_datos()
        #print('DATOS', datos)
        Vceldas = datos[0]
        #print('VCELDAS!!!!!', Vceldas)
        Tceldas = datos[1]
        Eceldas = datos[2]
        Intensidad = datos[3]
        Ibat = round(sum(Intensidad),2)
        SOC = datos[4]
        #print('SOC', SOC)
        SOCT = datos[5]
        #print('Valor máximo de celda: ', max(max(Vceldas[0]),max(Vceldas[1]), max(Vceldas[2]))) 
        e= 15
        VMAX = max([max(row) for row in Vceldas])
        #VMAX = max(max(Vceldas[0]), max(Vceldas[1]), max(Vceldas[2]))
        SOCMIN = min([min(row) for row in SOCT])
        
    except Exception as e:
        print('error en while true',e)
        pass
    
    #time.sleep(1)
    
    #log = lectura_log()    
        
    #if DEBUG == 1: print(log)
        
    #if log != log_ant: logBD(log)
    
    for i in range(0,n_pylontech):
        Vbat[i]=sum(Vceldas[i])
    
    
    for i in range(0, n_pylontech):    
        
        PYL[i] = {"Vceldas": Vceldas[i], "Max":Vceldas_max[i], "Min":Vceldas_min[i],"Estado":Eceldas[i], "Nombres":["C1","C2","C3","C4","C5","C6","C7","C8","C9","C10","C11","C12","C13","C14","C15"],
        "Ibat":Intensidad[i], "SOC":SOCT[i], "VMAX": VMAX, "SOCMIN":SOCMIN, "Tceldas":Tceldas[i],"dfet": dfet,"dfet_flag": dfet_flag, "cfet" : cfet, "cfet_flag": cfet_flag, "Ibat_t": Ibat, "Vbat": round(sum(Vceldas[i]),2), "SOC Bateria": min(SOCT[i])}
        #print(PYL[i])
    
    try:
    
        for i in range(0, n_pylontech):
            for j in range(0,15):
                if Vceldas[i][j] > Vceldas_max[i][j]: Vceldas_max[i][j] = Vceldas[i][j]
                if Vceldas[i][j] < Vceldas_min[i][j]: Vceldas_min[i][j] = Vceldas[i][j]
            
    except:
        
        calculo_max_min()
        pass
        
            
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    
    for i in range(0,n_pylontech):
        try:            
             
                
        
            salida = json.dumps(PYL[i])
            if DEBUG == 1:
                print(Fore.GREEN, '-------------------------------------------------------------------------------------------------------')
                print (Fore.YELLOW, salida)
            
            cursor = db.cursor()
            
            sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{equipo[i]}'") # grabacion en BD RAM
            
            cursor.execute(sql)
            db.commit()            
            
        except:
            #print(Fore.RED+f'error, Grabacion tabla RAM equipos -- {DATOS}')
            sys.exit()
        
    cursor.close()
    db.close()
            
    

    
    #valores = Vceldas[0]
    #print('Ibat: ', Ibat)
    for i in range(0,n_pylontech):
        if Intensidad[i] > 0: AH_p[i] = AH_p[i] + Intensidad[i]/720
        if Intensidad[i] < 0: AH_n[i] = AH_n[i] - Intensidad[i]/720
    
    for i in range(0,n_pylontech):
        
        try:
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()
            ee = 120
            campos = ",".join(Nombre_Celdas)
            campos = 'Tiempo, Ibat, AH_p, AH_n, SOC, ' + campos
            #print(equipo[0], "campos", campos)
            #print(" ")
            ee = 122
            valores = "','".join(str(v) for v in Vceldas[i])
            valores = f"'{tiempo}','{Intensidad[i]}','{AH_p[i]}','{AH_n[i]}','{min(SOCT[i])}','{valores}'"
            
            
            if DEBUG==1:
                print(Fore.GREEN, "-------------------------------------------------------------------------------------------------------")
                print(Fore.YELLOW, valores)
            ee = 124
            Sql = f"INSERT INTO datos_celdas_{equipo[i]} ({campos}) VALUES ({valores})"
            ee= 125               
            #print(Sql)
                            
            cursor.execute(Sql)
            ee = 126             
            db.commit()

                        
        except Exception as e:
            print(f"An error occurred: {e}")
            print(f'error {ee} -  Grabacion tabla datos_celdas_{equipo[i]}')
                         
    cursor.close()
    db.close()
    t2 = time.time()-t1
    if DEBUG == 1: print(Fore.GREEN, 'Timepo ciclo: ', round(t2,3))
    
    
    Utils().pausa(t_muestra_pylontech_consola*1000,500)
    
    dia = date.today()
    
    if dia!=dia_ant: 
        calculo_max_min()
        AH_p = [0]*n_pylontech
        AH_n = [0]*n_pylontech
        AH = [0]*n_pylontech
        
    if DEBUG==1:  print(Fore.BLUE, 'dia_ant:', dia_ant, 'dia:', dia)
