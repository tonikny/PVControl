#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-10-23

# #################### Control Ejecucion Servicio ########################################
servicio = 'fv_mux'
control = 'usar_mux'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

import MySQLdb,json,time,datetime
from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_mux') #+Style.RESET_ALL)

Nlog = Nlog_max = 2 # Contador Numero de log maximos cada minuto
minuto = time.strftime("%H:%M")

n_muestras_mux_contador = 1 # contador grabacion BD

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

bus = SMBus(1) # Activo Bus I2C

if pin_ADS_mux1[0] == 'A': #existe Mux1
    ads_mux1= int(pin_ADS_mux1[-1]) - 1
    adc1 = Adafruit_ADS1x15.ADS1115(address=72+ads_mux1, busnum=1)
    print (Fore.GREEN + ' Activando Mux1 en entrada',pin_ADS_mux1[0:2],'del ADS Nº',pin_ADS_mux1[3])
    if captura_mux == 'D':
        print (' Mux2 configurado para modo captura diferencial ')
        if usar_mux >16:
            print (Fore.RED, "ERROR.. el Nº maximo de entradas en modo diferencial es 16 en lugar de ", usar_mux)
            

if pin_ADS_mux2[0] == 'A' and usar_mux > 16 : #activo Mux2 si hay mas de 16 celdas
    ads_mux2= int(pin_ADS_mux2[-1]) - 1
    adc2 = Adafruit_ADS1x15.ADS1115(address=72+ads_mux2, busnum=1)
    print (' Activando Mux2 en entrada',pin_ADS_mux2[0:2],'del ADS Nº',pin_ADS_mux2[3])
    

DatosMux = {}  #diccionario para los datos de cada celda
DatosMux_ant = {}  #diccionario para los datos anteriores de las celdas

DatosMux_v = {}  #diccionario para los datos de entrada al Mux en voltaje a conector
DatosMux_v_l ={} #diccionario para los datos de entrada al Mux en voltaje leido por el ADS
DatosMux_n = {}  #Creamos diccionario para los datos Mux en numero capturado en ADS
DatosMux_err = {}  #Creamos diccionario para ver margen de error en captura
Vcelda_max = [0.0] * usar_mux # Maximo de cada celda diaria
Vcelda_min = [1000.0] * usar_mux # Minino de cada celda diaria

dia = time.strftime("%Y-%m-%d")

# Comprobacion que la tabla en BD tiene los campos necesarios
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    # Comprobacion si tabla equipos existe y si no se crea
    sql_create = """ CREATE TABLE IF NOT EXISTS `equipos` (
                  `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
                  `tiempo` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha Actualizacion',
                  `sensores` varchar(1000) COLLATE latin1_spanish_ci NOT NULL,
                   PRIMARY KEY (`id_equipo`)
                 ) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""

    import warnings # quitamos el warning que da si existe la tabla equipos
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cursor.execute(sql_create)

    try: #inicializamos registro en BD RAM
        cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                      ('CELDAS','"{}"'))
        db.commit()
    except:
        pass
    """
    try: # se actualiza el nombre de la tabla desde imagen 2020
      cursor.execute("RENAME TABLE `datos_mux_1` TO `datos_celdas`")
      db.commit()
    except:
        pass
    
    try: # se actualiza el nombre del indice desde imagen 2020
      cursor.execute("ALTER TABLE `datos_mux` CHANGE `id_mux_1` `id_celda` INT(11) NOT NULL AUTO_INCREMENT")
      db.commit()
    except:
        pass
   
    try: # se actualiza el nombre de la tabla desde imagen 2021
      cursor.execute("RENAME TABLE `datos_mux` TO `datos_celdas`")
      db.commit()
    except:
        pass
    try: # se actualiza el nombre del indice desde imagen 2020
      cursor.execute("ALTER TABLE `datos_celdas` CHANGE `id_mux` `id_celda` INT(11) NOT NULL AUTO_INCREMENT")
      db.commit()
    except:
        pass

    """
    
    Sql='SELECT * FROM datos_celdas' 
    nreg=cursor.execute(Sql)
    ncel = len(cursor.description) - 2 # Nº de celdas declaradas en BD
    
    if ncel < usar_mux:
        print (Fore.RED+ "ATENCION... el nº de campos en BD es menor que el nº de celdas declaradas en Parametros_FV.py")
        print ( " se crean nuevos campos en tabla datos_celdas")
        print ("-" * 50)
        for K in range(usar_mux):
            try:
                Sql = f"ALTER TABLE `datos_celdas` ADD `C{K+1}` FLOAT NOT NULL DEFAULT '0'"
                cursor.execute(Sql)
                db.commit()
                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} creado')
            except:
                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} ya estaba creado')
    elif ncel > usar_mux:
        print (Fore.RED+ "ATENCION... el nº de campos en BD es mayor que el nº de celdas declaradas en Parametros_FV.py")
        print ( " se borraran los campos sobrantes.... si hay datos en estos campos se perderan")
        print ("-" * 50)
        for K in range(usar_mux,ncel):
            try:
                Sql = f"ALTER TABLE `datos_celdas` DROP `C{K+1}`"
                cursor.execute(Sql)
                db.commit()
                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} borrado')
            except:
                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} no existe')
    cursor.close()
    db.close()        
except:
    print (Fore.RED,'ERROR inicializando BD')
    sys.exit()
# ==========================================================
#----------------- BUCLE -----------------------------------
# ==========================================================

db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()

flag_primer_bucle = True
try:
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
            Vcelda_max = [0.0] * usar_mux 
            Vcelda_min = [1000.0] * usar_mux

        #### CAPTURA VALORES ratios MUX ############
        sql = 'SELECT * FROM parametros1 WHERE nombre = "mux_calibracion"'
        existe_mux_calibracion = int(cursor.execute(sql))
        d_={}
        if existe_mux_calibracion < 1: # NO existe registro en parametros1
            d_['r_mux']= r_mux
            i = 'Fichero Parametros_FV.py'
        else:
            for row in cursor.fetchall(): d_['r_mux'] = json.loads(row[2])
            i= 'Tabla Parametros1 en BD'
            
        if DEBUG >= 100: print(f'Calibracion Mux actual en {i}=',d_['r_mux'])    

        #### CAPTURA VALORES MUX ############
        crono.append(time.time())
        
        for K in range(1,usar_mux+1):  # For para ir recorriendo cada entrada del Mux  
            bus.write_byte(32,K-1 % 16) # escribo en PCF 32
            if DEBUG >= 100:
                estado = bus.read_byte(32) # compruebo dato PCF
                if estado != (K-1) % 16:
                    print ('Error en escritura/lectura PCF 32 con datos', (K-1) % 16,'/',estado)  
            time.sleep(0.1)
            try:
                ###### Lectura Mux        
                N = 25 # Nº de lecturas de cada celda 
                if captura_mux == 'D': #lectura modo diferencial
                    lecturas = [adc1.read_adc_difference(3, gain= gain_mux, data_rate = 128) for i in range(N) ]    
                else:
                    if K > 16:
                        lecturas = [adc2.read_adc(int(pin_ADS_mux2[1]), gain= gain_mux, data_rate = 128) for i in range(N)]
                    else:
                        lecturas = [adc1.read_adc(int(pin_ADS_mux1[1]), gain= gain_mux, data_rate = 128) for i in range(N)]
                   
                lecturas= lecturas[1:] # quito la primera lectura dado que da mas errores
                Suma = sum(lecturas)
                Max = max(lecturas)
                Min = min(lecturas)
                lectura_ADS = Suma/len(lecturas)
                if DEBUG >= 100:
                    print (Fore.GREEN+'Lecturas Celda',K,'=', lecturas, lectura_ADS,Max, Min)        
            except:
                logBD('-ERROR MEDIDA MUX-'+ str(K))
                    
            # CALCULO VALORES CELDAS
            DatosMux_n['C'+str(K)] = lectura_ADS  # Valor numerico capturado
            DatosMux_err['C'+str(K)] = Max-Min    # Rango error valor numerico capturado
            DatosMux_v['C'+str(K)] = round(lectura_ADS * 0.000125/gain_mux * d_['r_mux'][K-1],4) # Valor V en conector.. 4,096V/32767=0.000125    
            DatosMux_v_l['C'+str(K)] = round(lectura_ADS * 0.000125/gain_mux ,4)   # Valor V en ADS  

        crono.append(['ADS',round(time.time() - t0,2)])
       
        DatosMux_ant = DatosMux.copy() #situacion anterior
        
        if captura_mux == 'D': #lectura modo diferencial
            DatosMux = DatosMux_v.copy()
        else:
            DatosMux['C1'] = DatosMux_v['C1']
            for K in range(2,usar_mux + 1):
                K1 = 'C'+str(K)
                DatosMux[K1] = round(DatosMux_v[K1] - DatosMux_v['C'+str(K-1)],2) # Voltaje en Celda(N) - Voltaje en Celda(N-1)
        
        if flag_primer_bucle: # ejecuta un nuevo ciclo lectura en el primer bucle para tener datos anteriores y actuales
            flag_primer_bucle = False
            continue 
        """    
        #Filtro variaciones rapidas... veremos si se usa o no    
        for x in DatosMux:
            salto_max = 0.1       
            if x[0] =='C':
                if (DatosMux[x] - DatosMux_ant[x]) > salto_max:  DatosMux[x] = DatosMux_ant[x] + salto_max
                elif (DatosMux[x] - DatosMux_ant[x]) < -salto_max:  DatosMux[x] = DatosMux_ant[x] - salto_max  
        """
        
        ## Calculo valor minimo y maximo diario de cada celda y valor min/max de todas las celdas
        CeldaMax = CeldaMin = ('C1',DatosMux['C1'])
        for K in range(usar_mux):
            K1 = 'C'+str(K+1)
            Vcelda_max[K] = max(Vcelda_max[K],DatosMux[K1])
            Vcelda_min[K] = min(Vcelda_min[K],DatosMux[K1])
            
            if DatosMux[K1] > CeldaMax[1]: CeldaMax = (K1,DatosMux[K1])
            if DatosMux[K1] < CeldaMin[1]: CeldaMin = (K1,DatosMux[K1])
        DifCeldas = round(CeldaMax[1]-CeldaMin[1],2)

        crono.append(['Listas',round(time.time() - t0,2)])
        # PRINT dependiendo argumentos
        if DEBUG >= 2:
            print(Fore.GREEN,'Valores numericos capturados=',DatosMux_n.values())
            print('----------')
        if DEBUG >= 3:
            print(Fore.RED,'Error en ',N-1, 'Capturas=',DatosMux_err.values())
            print('----------')
        if DEBUG >= 2:
            print()
            print('#' * 80)
            print(Fore.BLUE,'Voltajes en Conector capturados =',*DatosMux_v.values())
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
            # Log si hay celdas descompensadas
            if DifCeldas > celdas_log_dif:
                log = ('='.join(map(str, CeldaMax)) + ' / ' + '='.join(map(str, CeldaMin)) +
                       ' / Dif=' + str(DifCeldas))
                #print('error celdas',minuto,Nlog, log)
                logBD ('Celdas descomp. ' + log)
            
            # Insertar Registro en BD
            if n_muestras_mux_contador == 1 : #n_muestras_mux: 
                campos = ",".join(DatosMux.keys())
                valores = "','".join(str(v) for v in DatosMux.values())
                Sql = "INSERT INTO datos_celdas ("+campos+") VALUES ('"+valores+"')"
                cursor.execute(Sql)
                print (Fore.RED+'G',end='/',flush=True)
            
            if n_muestras_mux_contador >= n_muestras_mux:
                n_muestras_mux_contador = 1
            else:
                n_muestras_mux_contador +=1
                
        except:
            print('error, BD', Sql)
            db.rollback()
            pass
        crono.append(['BD',round(time.time() - t0,2)])
        
        ####  ARCHIVOS RAM en BD ############ 
        
        try:
            datos = {'Nombre' : list(DatosMux.keys()), 'Max': Vcelda_max,'Valor' : list(DatosMux.values()),'Min' : Vcelda_min}
                    
            if DEBUG >= 1: print (list(DatosMux.values()))
             
            salida = json.dumps(datos)
            sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'CELDAS'") # grabacion en BD RAM
            cursor.execute(sql)
                
        except:
            print('error, Grabacion tabla RAM equipos')
        
        db.commit()
        #cursor.close()
        #db.close()
            
        crono.append(['RAM',round(time.time() - t0,2)])
        if DEBUG == 50:
            print (Fore.BLUE,'Crono =', crono[1:])
        elif DEBUG == 0: print (Fore.BLUE,round(time.time()-tiempo_sg,2),end='/',flush=True) # Print de control
        
        
        time.sleep(max(t_muestra_mux - (time.time()-tiempo_sg),0))
        
except:
    print ()
    print ('#' * 80)
    print (Fore.RED+'saliendo de fv_mux.py')
    cursor.close()
    db.close()       
