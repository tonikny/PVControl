#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-08-28

N= 25 # repeticion lecturas
data_rate= 128 # data_rate apliacado en ADS

import sys,json,time,datetime
import MySQLdb 
from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.
import click
from Parametros_FV import *

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_mux_calibracion') #+Style.RESET_ALL)

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


## Ver si existe datos de calibracion del Mux en BD
db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()
try:
    sql = """CREATE TABLE IF NOT EXISTS `parametros2` (
              `id_parametro` int(11) NOT NULL,
              `nombre` varchar(100) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
              `valor` varchar(100) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
              PRIMARY KEY (`id_parametro`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
         """
    
    import warnings # quitamos el warning que da si existe la tabla
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cursor.execute(sql)
        db.commit()
        
except:
    print ('Error en tabla parametros1')
    sys.exit()

try:
    sql = 'SELECT * FROM parametros1 WHERE nombre = "mux_calibracion"'
    existe_mux_calibracion = int(cursor.execute(sql))
    d_={}
    if existe_mux_calibracion < 1:
        d_['r_mux']= r_mux
        i = 'Fichero Parametros_FV.py'
    else:
        for row in cursor.fetchall(): d_['r_mux'] = json.loads(row[2])
        i= 'Tabla Parametros1 en BD'
        
    print(f'Calibracion Mux actual en {i}=',d_['r_mux'])      
except:
    print(f'Error en datos calibracion MUX en {i}')
    sys.exit()

## Configuracion ADS
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
    

#Inicializacion Diccionarios
DatosMux = {}      # datos de cada celda

DatosMux_v = {}    # datos de entrada al Mux en voltaje a conector
DatosMux_v_l ={}   # datos de entrada al Mux en voltaje leido por el ADS
DatosMux_n = {}    # datos Mux en numero capturado en ADS
DatosMux_err = {}  # margen de error en captura

VceldaReal  = [0 for i in range(16)] # inicializo a 0 los datos reales medidos con polimetro de cada celda
VceldaRatio  = [1 for i in range(16)] # inicializo a 1 el ratio conversion divisores tension

dia = time.strftime("%Y-%m-%d")

# Comprobacion que la tabla en BD tiene los campos necesarios
        
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    # Comprobacion si tabla equipos existe y si no se crea
    sql_create = """ CREATE TABLE IF NOT EXISTS `equipos` (
                  `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
                  `sensores` varchar(500) COLLATE latin1_spanish_ci NOT NULL,
                   PRIMARY KEY (`id_equipo`)
                 ) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""

    import warnings # quitamos el warning que da si existe la tabla equipos
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cursor.execute(sql_create)
    
    try: # se actualiza el nombre de la tabla desde imagen 2020
      cursor.execute("""RENAME TABLE `datos_mux_1` TO `datos_mux`""")
      db.commit()
    except:
        pass
    
    try: # se actualiza el nombre del indice desde imagen 2020
      cursor.execute("""ALTER TABLE `datos_mux` CHANGE `id_mux_1` `id_mux` INT(11) NOT NULL AUTO_INCREMENT""")
      db.commit()
    except:
        pass
    
    Sql='SELECT * FROM datos_mux' 
    nreg=cursor.execute(Sql)
    ncel = len(cursor.description) - 2 # Nº de campos de celdas en BD
    
    if ncel < usar_mux:
        print (Fore.RED+ f"ATENCION... el nº de celdas en BD es ={ncel}")
        print (f" es menor que el nº de celdas declaradas en Parametros_FV.py = {usar_mux}")
        print ( " se crean nuevos campos en tabla datos_mux")
        print ("-" * 50)
        salir = click.prompt(Fore.CYAN + '  .... pulse una 0 para seguir o 1 para abortar ', type=str, default='0')
        if salir == '1': sys.exit()

        for K in range(usar_mux):
            try:
                Sql = f"ALTER TABLE `datos_mux` ADD `C{K}` FLOAT NOT NULL DEFAULT '0'"
                cursor.execute(Sql)
                db.commit()
                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K} creado')
            except:
                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K} ya estaba creado')
    elif ncel > usar_mux:
        print (Fore.RED+ f"ATENCION... el nº de celda en BD ={ncel}")
        print (f"es mayor que el nº de celdas declaradas en Parametros_FV.py= {usar_mux}")
        print ( " se borraran los campos sobrantes.... si hay datos en estos campos se perderan")
        print ("-" * 50)
        salir = click.prompt(Fore.CYAN + '  .... pulse una 0 para seguir o 1 para abortar ', type=str, default='0')
        if salir == '1': sys.exit()

        for K in range(usar_mux,ncel):
            try:
                Sql = f"ALTER TABLE `datos_mux` DROP `C{K}`"
                cursor.execute(Sql)
                db.commit()
                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K} borrado')
            except:
                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K} no existe')
    
except:
    print ('ERROR inicializando BD')

# ==========================================================
#----------------- BUCLE -----------------------------------
# ==========================================================

VceldaReal  = [0 for i in range(usar_mux)] # inicializo a 0 los datos reales medidos con polimetro de cada celda
VceldaRatio  = [1 for i in range(usar_mux)] # inicializo a 1 el ratio conversion divisores tension

while True:
    crono = [] # cronografo tiempo ejecucion
    t0=time.time()

    #### CAPTURA VALORES MUX ############
    crono.append(time.time())
    
    for K in range(usar_mux):  # For para ir recorriendo cada entrada del Mux
        bus.write_byte(32,K % 16) # escribo en PCF 32
        if DEBUG >= 100:
            estado = bus.read_byte(32) # compruebo dato PCF
            if estado != K % 16:
                print ('Error en escritura/lectura PCF 32 con datos', K % 16,'/',estado)  
        time.sleep(0.1)
        try:
            ###### Lectura Mux        
            # N = 5 # Nº de lecturas de cada celda 
            if captura_mux == 'D': #lectura modo diferencial
                lecturas = [adc1.read_adc_difference(3, gain= gain_mux, data_rate = data_rate) for i in range(N) ]    
            else:
                if K > 16:
                    lecturas = [adc2.read_adc(int(pin_ADS_mux2[1]), gain= gain_mux, data_rate = data_rate) for i in range(N)]
                else:
                    lecturas = [adc1.read_adc(int(pin_ADS_mux1[1]), gain= gain_mux, data_rate = data_rate) for i in range(N)]
               
            lecturas= lecturas[1:] # quito la primera lectura dado que da errores
            Suma = sum(lecturas)
            Max = max(lecturas)
            Min = min(lecturas)
            lectura_ADS = Suma/len(lecturas)
            if DEBUG >= 100:
                print (Fore.GREEN+'Lecturas Celda',K+1,'=', lecturas, lectura_ADS,Max, Min)        
        except:
            print('-ERROR MEDIDA MUX-'+ str(K))
                
        try: # compruebo si esta dado de alta el ratio en la BD
            i = d_['r_mux'][K]
        except:
            d_['r_mux'].append(0.0)
            
        # CALCULO VALORES CELDAS
        DatosMux_n['C'+str(K)] = lectura_ADS  # Valor numerico capturado
        DatosMux_err['C'+str(K)] = Max-Min    # Rango error valor numerico capturado
        DatosMux_v['C'+str(K)] = round(lectura_ADS * 0.000125/gain_mux * d_['r_mux'][K],4) # Valor V en conector.. 4,096V/32767=0.000125    
        DatosMux_v_l['C'+str(K)] = round(lectura_ADS * 0.125/gain_mux ,4)   # Valor mV en ADS  

        print (Fore.RED, '=' * 80)
        print (Fore.BLUE, f'Voltaje medido con Ratio actual={DatosMux_v["C"+str(K)]:.4f} -- ', end='')
        print (f'mV en ADS= {DatosMux_v_l["C"+str(K)]:.2f} --- Ratio actual={d_["r_mux"][K]:.4f}')

        VceldaReal[K] = click.prompt(Fore.CYAN + 'Voltaje real en  '+Fore.RESET+f'celda{K+1}='+ Fore.CYAN, type=float, default=DatosMux_v["C"+str(K)])
        if DatosMux_v_l['C'+str(K)] != 0:
            VceldaRatio[K] = round(VceldaReal[K] / DatosMux_v_l['C'+str(K)]*1000,5)
        else:
            VceldaRatio[K] = 0
            
        print(Fore.GREEN,f'Nuevo Ratio para la Celda{K+1}={VceldaRatio[K]}')
        print (Fore.RED, '=' * 80)
        
    crono.append(['ADS',round(time.time() - t0,2)])
    
    # CALCULO VALORES DE CADA CELDA
    if captura_mux == 'D': #lectura modo diferencial
        DatosMux = DatosMux_v.copy()
    else:                  #lectura modo simple
        DatosMux['C0'] = DatosMux_v['C0']
        for K in range(1,usar_mux):DatosMux['C'+str(K)] = round(DatosMux_v['C'+str(K)] - DatosMux_v['C'+str(K-1)],2)
    
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
              
    print()
    print (Fore.RESET, '=' * 80)
    print (Fore.CYAN,'    Nuevos Ratios para la Celdas grabados en tabla Parametros1= '+Fore.RESET+f'{VceldaRatio}')
    print (Fore.RESET, '=' * 80)            
    print()
    d_['r_mux']= VceldaRatio
    try:
        cursor.execute("""INSERT INTO parametros1 (id_parametro,nombre,valor) VALUES (%s,%s,%s)""",
                      (1000,"mux_calibracion", f"{VceldaRatio}"))
    except:
        try:
            sql = f"UPDATE parametros1 SET valor= '{VceldaRatio}' WHERE nombre='mux_calibracion'"
            cursor.execute(sql)
            
        except:
            print ('Error grabacion tabla parametros1')
    db.commit()
    try:
        click.confirm('Continuar?', abort=True)
    except:
        sys.exit()

cursor.close()
db.close()        
