# -*- coding: utf-8 -*-

# Versión 2025-02-19
#

# ######## INICIO PARAMETRIZACION EQUIPO ####################
# 
# UN BLOQUE COMO ESTE SE DEBE INCLUIR EN Parametros_FV.py
#
# ¡¡¡¡ NO MODIFICAR ESTE FICHERO !!!
#
# ###########################################################

BMS_JK_RS485 = {
    'JK1': {'usar':0,
            'dev': '/dev/ttyUSB0',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 3,
          },
          
    'JK2': {'usar':0,
            'dev': '/dev/ttyUSB1',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 3,
          },
           
    'COMANDOS' : {
        ## R
        0x79:{'Captura': True, 'Nombre':'Vceldas', 'Nbytes': 99, 'Estructura':{'Nbytes': 1, 'Nceldas':1, 'Vcelda':2} },
        0x80:{'Captura': True, 'Nombre':'Temp_tube', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0x81:{'Captura': True, 'Nombre':'Temp_bat_box', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0x82:{'Captura': True, 'Nombre':'Temp_bat', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0x83:{'Captura': True, 'Nombre':'Vbat', 'Nbytes': 2, 'Adaptar':'round(x/100,2)'},
        0x84:{'Captura': True, 'Nombre':'Ibat', 'Nbytes': 2, 'Adaptar':'-round(x/100,2) if x < 32768 else round((x-32768)/100,2)'},
        0x85:{'Captura': True, 'Nombre':'SOC', 'Nbytes': 1, 'Adaptar':'x'},
        0x86:{'Captura': False, 'Nombre':'Nsondas_temp', 'Nbytes': 1, 'Adaptar':'x'},
        0x87:{'Captura': True, 'Nombre':'T_uso', 'Nbytes': 2, 'Adaptar':'x'},
        0x89:{'Captura': True, 'Nombre':'AH_ciclados', 'Nbytes': 4, 'Adaptar':'x'},
        0x8a:{'Captura': True, 'Nombre':'Nceldas', 'Nbytes': 2, 'Adaptar':'x'},
        0x8b:{'Captura': True, 'Nombre':'Alarma_bat', 'Nbytes': 2, 'Adaptar':'f"{x:016b}"'},
        0x8c:{'Captura': True, 'Nombre':'Status_bat', 'Nbytes': 2, 'Adaptar':'f"{x:04b}"'},
        
        ## RW
        0x8e:{'Captura': True, 'Nombre':'V_total_max', 'Nbytes': 2, 'Adaptar':'round(x/100,2)'},
        0x8f:{'Captura': True, 'Nombre':'V_total_min', 'Nbytes': 2, 'Adaptar':'round(x/100,2)'},
        0x90:{'Captura': True, 'Nombre':'Vcelda_max', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x91:{'Captura': True, 'Nombre':'Vcelda_max_rec', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x92:{'Captura': True, 'Nombre':'T_Vcelda_max', 'Nbytes': 2, 'Adaptar':'x'},
        0x93:{'Captura': True, 'Nombre':'Vcelda_min', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x94:{'Captura': True, 'Nombre':'Vcelda_min_rec', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x95:{'Captura': True, 'Nombre':'T_Vcelda_min', 'Nbytes': 2, 'Adaptar':'x'},
        0x96:{'Captura': True, 'Nombre':'Vdiff_max', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x97:{'Captura': True, 'Nombre':'Imax_descarga', 'Nbytes': 2, 'Adaptar':'x'},
        0x98:{'Captura': True, 'Nombre':'T_Imax_descarga', 'Nbytes': 2, 'Adaptar':'x'},
        0x99:{'Captura': True, 'Nombre':'Imax_carga', 'Nbytes': 2, 'Adaptar':'x'},
        0x9a:{'Captura': True, 'Nombre':'T_Imax_carga', 'Nbytes': 2, 'Adaptar':'x'},
        0x9b:{'Captura': True, 'Nombre':'Vbalance', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x9c:{'Captura': True, 'Nombre':'Vbalance_ini', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'},
        0x9d:{'Captura': True, 'Nombre':'Rbalance', 'Nbytes': 1, 'Adaptar':'x'},
        0x9e:{'Captura': True, 'Nombre':'Temp_mos_protec', 'Nbytes': 2, 'Adaptar':'x'},
        0x9f:{'Captura': True, 'Nombre':'Temp_mos_protec_rec', 'Nbytes': 2, 'Adaptar':'x'},
        0xa0:{'Captura': True, 'Nombre':'Temp_bat_protec', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0xa1:{'Captura': True, 'Nombre':'Temp_bat_protec_rec', 'Nbytes': 2, 'Adaptar':'x if x<100 else 100-x'},
        0xa2:{'Captura': True, 'Nombre':'Temp_bat_protec_diff', 'Nbytes': 2, 'Adaptar':'x'},
        0xa3:{'Captura': True, 'Nombre':'Temp_bat_max_protec_carga', 'Nbytes': 2, 'Adaptar':'x'},
        0xa4:{'Captura': True, 'Nombre':'Temp_bat_max_protec_descarga', 'Nbytes': 2, 'Adaptar':'x'},
        0xa5:{'Captura': True, 'Nombre':'Temp_bat_min_protec_carga', 'Nbytes': 2, 'Adaptar':'x if x<32768 else x-65536'},
        0xa6:{'Captura': True, 'Nombre':'Temp_bat_min_protec_carga_rec', 'Nbytes': 2, 'Adaptar':'x if x<32768 else x-65536'},
        0xa7:{'Captura': True, 'Nombre':'Temp_bat_min_protec_descarga', 'Nbytes': 2, 'Adaptar':'x if x<32768 else x-65536'},
        0xa8:{'Captura': True, 'Nombre':'Temp_bat_min_protec_descarga_rec', 'Nbytes': 2, 'Adaptar':'x if x<32768 else x-65536'},
        0xa9:{'Captura': True, 'Nombre':'Bat_count', 'Nbytes': 1, 'Adaptar':'x'},
        0xaa:{'Captura': True, 'Nombre':'AH_Bat', 'Nbytes': 4, 'Adaptar':'x'},
        0xab:{'Captura': True, 'Nombre':'Mos_Carga', 'Nbytes': 1, 'Adaptar':'x'},
        0xac:{'Captura': True, 'Nombre':'Mos_descarga', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xad:{'Captura': True, 'Nombre':'Icalibracion', 'Nbytes': 2, 'Adaptar':'x'}, 
        0xae:{'Captura': True, 'Nombre':'Direccion', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xaf:{'Captura': True, 'Nombre':'Bat_tipo', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xb0:{'Captura': True, 'Nombre':'Tiempo_dormir', 'Nbytes': 2, 'Adaptar':'x'}, 
        0xb1:{'Captura': True, 'Nombre':'SOC_alarma', 'Nbytes': 1, 'Adaptar':'x'},
        0xb2:{'Captura': True, 'Nombre':'Pass', 'Nbytes': 10, 'Adaptar':'d[p:p+nb].decode().split("\\x00", 1)[0]'}, 
        0xb3:{'Captura': True, 'Nombre':'Mos_especial', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xb4:{'Captura': True, 'Nombre':'ID_equipo', 'Nbytes': 8, 'Adaptar':'d[p:p+nb].decode()'}, 
        0xb5:{'Captura': True, 'Nombre':'Fecha_equipo', 'Nbytes': 4, 'Adaptar':'d[p:p+nb].decode()'}, 
        0xb6:{'Captura': True, 'Nombre':'Tiempo_activo', 'Nbytes': 4, 'Adaptar':'x'}, 
        0xb7:{'Captura': True, 'Nombre':'SW_version', 'Nbytes': 15, 'Adaptar':'d[p:p+nb].decode()'}, #solo R
        0xb8:{'Captura': True, 'Nombre':'Calibracion', 'Nbytes': 1, 'Adaptar':'x'},
        0xb9:{'Captura': True, 'Nombre':'AH_actual', 'Nbytes': 4, 'Adaptar':'x'}, 
        0xba:{'Captura': True, 'Nombre':'ID_fab', 'Nbytes': 24, 'Adaptar':'d[p:p+nb].decode().split("\\x00", 1)[0][12:]'}, 
        
        0xbb:{'Captura': True, 'Nombre':'Restart', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xbc:{'Captura': True, 'Nombre':'Reset', 'Nbytes': 1, 'Adaptar':'x'}, 
        0xbd:{'Captura': True, 'Nombre':'Upgrade', 'Nbytes': 1, 'Adaptar':'x'},
        0xbe:{'Captura': True, 'Nombre':'Voff', 'Nbytes': 2, 'Adaptar':'round(x/1000,3)'}, 
        
        0xc0:{'Captura': True, 'Nombre':'Nversion', 'Nbytes': 1, 'Adaptar':'x'}, 
    
     }
   
   }


# ########### FIN PARAMETRIZACION EQUIPO ####################
  


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'BMS_JK_RS485'
servicio = 'fv_jk_rs485'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'COMANDOS'])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


EQUIPO = eval(NEQUIPO)

try:
    comandos = EQUIPO['COMANDOS']
    del EQUIPO['COMANDOS']
except:
    pass

import time
from datetime import datetime
import sys  

import MySQLdb,json

import serial

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

DEBUG= 0
if '-p' in sys.argv: DEBUG = 100
elif '-p1' in sys.argv: DEBUG = 1

# Comprobacion que la tabla en BD tiene los campos necesarios
def comprobar_bd(equipo, nceldas):
    ee = 100
    if '-test' not in sys.argv:
        try:
            ee = 110   
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()
            
            # Comprobacion si tabla equipos existe y si no se crea
            sql_create = """ CREATE TABLE IF NOT EXISTS `equipos` (
                          `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
                          `tiempo` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha Actualizacion',
                          `sensores` varchar(3000) COLLATE latin1_spanish_ci NOT NULL,
                           PRIMARY KEY (`id_equipo`)
                         ) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""

            import warnings # quitamos el warning que da si existe la tabla equipos
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                cursor.execute(sql_create)
                        
            ee = 120
            if True: #BMS_JK[equipo]['usar'] == 1: # solo se chequea si se activa el BMS
                ee = 130
                try:#inicializamos registro en BD RAM
                    cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                                      (f"BMS_{equipo}","{}"))
                except:
                    pass   
                ee = 140
                try:
                    Sql = f"""    
                         CREATE TABLE IF NOT EXISTS `datos_celdas_{equipo}` (
                        `id_celda` int(11) NOT NULL AUTO_INCREMENT,
                        `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
                        `Ibat` float NOT NULL DEFAULT 0,
                        `AH_p` float NOT NULL DEFAULT 0,
                        `AH_n` float NOT NULL DEFAULT 0,
                        `SOC` float NOT NULL DEFAULT 0,
                        `C1` float NOT NULL DEFAULT 0,
                         PRIMARY KEY (`id_celda`),
                         KEY `Tiempo` (`Tiempo`)
                         ) 
                         ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
                         """
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')
                        cursor.execute(Sql)
                    
                except:
                    pass
                
                #db.commit()
                ee = 150
                try:
                    ee = 155
                    Sql = f'SELECT * FROM datos_celdas_{equipo} LIMIT 1' 
                    nreg=cursor.execute(Sql)
                    #ncel = len(cursor.description) - 3 # Nº de celdas declaradas en BD
                    ncampos = [c[0] for c in cursor.description] # nombre de los campos
                    
                    ncel = 0
                    for campo in ncampos:
                        if campo[0] == 'C': ncel += 1
                        
                    ee = 159
                    #print(ncel, ncampos)
                    ee = 160
                    
                    ### Comprobacion nombres de campos
                    for c in ['Ibat','AH_p', 'AH_n', 'SOC']:
                        ee = 165
                        if c not in ncampos:
                            print(f'crear campo {c} en tabla datos_celdas_{equipo}')
                            Sql = f"ALTER TABLE `datos_celdas_{equipo}` ADD `{c}` FLOAT NOT NULL DEFAULT '0' "
                            cursor.execute(Sql)
                    
                    ee = 180
                    ### Comprobacion Nº de celdas
                    if ncel < nceldas:
                        print (Fore.RED+ "ATENCION... el nº de campos en BD es menor que el nº de celdas declaradas en Parametros_FV.py")
                        print ( " se crean nuevos campos en tabla datos_celdas")
                        print ("-" * 50)
                        for K in range(nceldas):
                            try:
                                Sql = f"ALTER TABLE `datos_celdas_{equipo}` ADD `C{K+1}` FLOAT NOT NULL DEFAULT '0'"
                                cursor.execute(Sql)
                                db.commit()
                                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} creado')
                            except:
                                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} ya estaba creado')
                    elif ncel > nceldas:
                        print (Fore.RED+ "ATENCION... el nº de campos en BD es mayor que el nº de celdas declaradas en Parametros_FV.py")
                        print ( " se borraran los campos sobrantes.... si hay datos en estos campos se perderan")
                        print ("-" * 50)
                        for K in range(nceldas,ncel):
                            try:
                                Sql = f"ALTER TABLE `datos_celdas_{equipo}` DROP `C{K+1}`"
                                cursor.execute(Sql)
                                db.commit()
                                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} borrado')
                            except:
                                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} no existe')
                    
                except:
                        print(f'Error {ee} en la actualizacion de campos en datos_celdas_{equipo}')
   
            db.commit()
            cursor.close()
            db.close()

        except:
            print('ERROR en creacion/comprobacion de la Base de datos.....se detiene programa')
            sys.exit()

def leer_equipo(equipo, grabar = True):
    global datos, AH_p, AH_n, contador_ciclos
    
    t0= time.time()
    nombre_equipo = equipo.upper()    
    t_muestra = EQUIPO[equipo]['tiempo_captura']
    
    # ######################################
    # en cm se pone el comando sin CRC
    # ######################################

    #leer Vbat
    #cm = '4E 57 00 13 00 00 00 00 03 03 00 83 00 00 00 00 68'

    #leer Vcelda_max
    #cm = '4E 57 00 13 00 00 00 00 03 03 00 90 00 00 00 00 68'

    #Escribir VCELDA_MAX
    #cm = '4E 57 00 15 00 00 00 00 02 03 00 90 0D B6 00 00 00 00 68'

    # Leer todo
    cm = '4E 57 00 13 00 00 00 00 06 03 00 00 00 00 00 00 68'
    cm_todo = '4E 57 00 13 00 00 00 00 06 03 00 00 00 00 00 00 68'
    
    # calculo del CRC de cm
    crc1 = f'{sum(bytearray.fromhex(cm)):04x}'
    crc = f' 00 00 {crc1[:2]} {crc1[2:4]}'.upper()
     
    cmd = bytearray.fromhex(cm + crc) #comando a mandar

    if DEBUG > 0:
        print (Style.BRIGHT + Fore.GREEN+f'comando = {cm + crc} ...con CRC')
        print(f'cmd= {cmd}')
        print()

    # BUCLE de captura
    if True: #while True:
        try:
            conexion[equipo].write(cmd)
            time.sleep(.1)

            #print('bms.inWaiting()=',bms.inWaiting())
            nlectura = conexion[equipo].inWaiting()
            lectura = conexion[equipo].read(nlectura).hex()
            d = bytearray.fromhex(lectura)
            
            
            #print()
            if DEBUG > 0:
                print(Fore.RESET + f'{time.time():0.2f} - {nlectura}-> lectura = {d}')
                print(Fore.CYAN+'lectura: ',lectura)
                print(Fore.RESET+'=' * 80)
        except:
            print (Fore.RED+f'Error en lectura BMS {equipo}')
            time.sleep(1)
            return #continue
        
        # Interpretacion trama respuesta
        try:
            
            p = 0 # puntero trama respuesta
            stx = d[p:p+2] # Comienzo trama ...fijo a 4e57
            #datos[equipo]['stx']= stx 
            if DEBUG == 100: print(f'stx: {stx}')
            
            p = 2
            long_trama =  int.from_bytes(d[p:p+2], 'big')  #Longitud de la trama
            long_trama1 = int(lectura[4:8],16)
            #datos[equipo]['long_trama']= long_trama 
            if DEBUG == 100: print (f'long_trama {d[p:p+2]}-> {long_trama} {long_trama1}')
            
            p = 4
            bms_numero = int.from_bytes(d[p:p+4])
            bms_numero1 = lectura[8:16]
            #datos[equipo]['bms_num']= bms_numero 
            if DEBUG == 100: print(f'bms_numero = {bms_numero} - {bms_numero1}')
            
            p = 8
            palabra_comando = int.from_bytes(d[p:p+1])
            palabra_comando1 = lectura[16:18]
            #datos[equipo]['palabra_comando']= palabra_comando
            if DEBUG == 100: print(f'palabra_comando = {palabra_comando} - {palabra_comando1}')
            
            p = 9
            fuente_trama = int.from_bytes(d[p:p+1])
            #datos[equipo]['fuente_trama']= fuente_trama
            if DEBUG == 100: print(f'fuente_trama= {fuente_trama}')
            
            p = 10
            tipo_transporte = int.from_bytes(d[p:p+1]) #1: respùesta
            #datos[equipo]['tipo_transporte']= tipo_transporte
            if DEBUG == 100:
                print(f'tipo_transporte= {tipo_transporte}')
                #print(f'resto...{d[11:]}')
        except:
            print(Fore.RED + 'Error en cabecera trama')
            time.sleep(1)
            return #continue
        
        
        if cm != cm_todo : sys.exit() # paro script si comando es distinto de leer todo
        
        
        ##########################################
        #  Captura de los valores de las celdas   
        ##########################################        
        try:        
            p= 11
            identificador79 = int.from_bytes(d[p:p+1])
            #print(f'identificador79= {identificador79} = 0x{identificador79:0x}')
            
            p = 12
            if identificador79 == 0x79:
                nceldas = int(int.from_bytes(d[p:p+1]) / 3) # cada celda tiene 3 bytes
                #datos[equipo]['nceldas']= nceldas 
            
                #print(f'nceldas= {nceldas}')
                
                celdas = {}
                p = 13
                for c in range(nceldas):
                    #print (f'C{c+1} -- {int.from_bytes(d[p+3*c:(p+1)+3*c])}')
                    if int.from_bytes(d[p+3*c:p+1+3*c]) == (c+1):
                        celdas[f'C{c+1}'] =  round(int.from_bytes(d[p+1+3*c:p+3+3*c], 'big')/1000,3)
                    else:
                        print (Fore.RED + f'Error en lectura de celdas')
                        return #continue
                
                if DEBUG > 0:
                    print(Fore.CYAN+f'celdas= {celdas}')
                    print(Fore.RESET+'=' * 80)
            else:
                time.sleep(0.5)
                return #continue
        except:
            print(Fore.RED+'Error en interpretacion Celdas')
            time.sleep(0.5)
            return #continue
        
        if comandos[0x79]['Captura']: 
            
            
            # Actualizar valores actuales
            datos[equipo]['Vceldas'] = list(celdas.values())
            datos[equipo]['Nombres'] = list(celdas.keys()) # No haria falta asignar continuamente
            
            # Actualizar máximos y mínimos
            datos[equipo]["Max"] = [max(datos[equipo]["Max"][i], celdas[nombre]) for i, nombre in enumerate(datos[equipo]["Nombres"])]
            datos[equipo]["Min"] = [min(datos[equipo]["Min"][i], celdas[nombre]) for i, nombre in enumerate(datos[equipo]["Nombres"])]

        p += 3 * nceldas
                
        ##########################################
        # Captura del resto de identificadores
        ##########################################
        
        while True:
            identificador = int.from_bytes(d[p:p+1])
            
            if identificador in comandos:
                nombre = comandos[identificador]['Nombre']
                nb = comandos[identificador]['Nbytes']
                p += 1
                
                x = int.from_bytes(d[p:p+nb])
                x = eval(comandos[identificador]['Adaptar'])
                
                if DEBUG == 100: 
                    print (Style.BRIGHT+Fore.YELLOW+f'Identificador:0x{identificador:0x}->:{Fore.GREEN}{nombre} = {x} {Fore.RESET} --> {d[p:p+nb]}<>{lectura[2*p: 2*(p+nb)]}')
                
                if comandos[identificador]['Captura']: datos[equipo][nombre] = x
                
                p += nb
            else:
               break
        #print(f'identificador80= {identificador80} = 0x{identificador80:0x}')
 
        t1= time.time()
        
        if datos[equipo]['Ibat'] > 0 :  AH_p[equipo] += datos[equipo]['Ibat'] * t_muestra/3600
        else: AH_n[equipo] -= datos[equipo]['Ibat'] * t_muestra/3600
                    
        datos[equipo]['AH_p'] = round(AH_p[equipo],2)
        datos[equipo]['AH_n'] = round(AH_n[equipo],2)
        
        if DEBUG > 0:
            print()
            print(datos[equipo])
        #break
        #time.sleep(1)


        if not grabar:
            comprobar_bd(nombre_equipo, nceldas)
            
        # Guardar en BD
                        
        try:####  ARCHIVOS RAM en BD ############ 
            ee = 300
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            datos[equipo]['tcaptura']= round(t1-t0,2)            
            #datos[equipo]['Nfallos'] = n_fallos_captura[equipo]
            
            salida = json.dumps(datos[equipo])
            ee = 304
            sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'BMS_{nombre_equipo}'") # grabacion en BD RAM
            #print (Fore.RED+sql)
            cursor.execute(sql)
            ee = 310
            db.commit()
            
            #if DEBUG == 0: print(f'{nombre_equipo[-1]}', flush= True, end='') #print(f'{time.time():.1f}') 
            ee = 330
                
        except Exception as e:
            print(Fore.RED+f'error {ee}, Grabacion tabla RAM equipos en {nombre_equipo}')
        
        contador_ciclos[equipo] += 1
        if contador_ciclos[equipo] == EQUIPO[equipo]['ciclos_grabacion']: 
            
            if DEBUG == 100: print(f'{equipo}...Grabando en BD...')
                   
            # Insertar Registro en tabla datos_celdas
            try:
                ee = 120
                campos = ",".join(datos[equipo]['Nombres'])
                campos = 'Ibat, AH_p, AH_n, SOC, ' + campos
                ee = 122
                valores = "','".join(str(v) for v in datos[equipo]['Vceldas'])
                valores = f"'{datos[equipo]['Ibat']}','{datos[equipo]['AH_p']}','{datos[equipo]['AH_n']}','{datos[equipo]['SOC']}','{valores}'"
                ee = 124
                Sql = f"INSERT INTO datos_celdas_{equipo} ({campos}) VALUES ({valores})"
                
                #print(Sql)
                
                cursor.execute(Sql)
                [equipo]
                ee = 126    
                if DEBUG == 1:
                    if equipo[-1] =='1' : print(Fore.GREEN, end='')
                    elif equipo[-1] =='2' : print(Fore.YELLOW, end='')
                    elif equipo[-1] =='3' : print(Fore.BLUE, end='')
                    elif equipo[-1] =='4' : print(Fore.MAGENTA, end='')
                    print ('G',end='',flush=True)
                
            except:
                print(f'error {ee} -  Grabacion tabla datos_celdas_{equipo}')
                 
            
            
            contador_ciclos[equipo] = 0  
            

# Bucle para llamada a funcion leer_equipo

dia = time.strftime("%Y-%m-%d")

t_recarga_parametros = time.time()
t_ultima_captura = {} # marca temporal de la ultima captura de datos de cada equipo

flag_lectura = {} # Flag de lectura para evitar conflicto con lectura desde Telegram

datos = {}  #{ Equipo:{'Vceldas':[....], 'Max':[....], 'Min':[...], 'Nombres': [....]'}, Equipo:{.....}}
AH_p = {}   # Para acumular Ah con mayor precision que en datos
AH_n = {}

conexion={}  # relacion de conexiones serie
contador_ciclos= {} # contador ciclos para grabacion

# Conexion BD
try:
    ee = '1'
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()  
except:
    print (Fore.RED,f'ERROR - inicializando BD RAM ')
    sys.exit()

            
######### BUCLE PRINCIPAL ############### 

 
while True:
    ee = '10a'
    if time.time() - t_recarga_parametros > 300: # cada XX sg
        t_recarga_parametros = time.time()
        if DEBUG == 1: print(Fore.RED + 'recarga Parametros')
        try:
            exec(open(parametros_FV_DIST).read(),globals()) #cargo Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
            exec(open(parametros_FV).read(),globals()) #cargo Parametros_FV.py
        except:
            print(Fore.RED + 'ERROR en recarga Parametros')
            
    ee = '10b'    
    try:
        for e in EQUIPO:
            ee = '10c'
            if EQUIPO[e]['usar'] == 1:
                
                ee = '10d'
                # INICIALIZACION CONEXION Y BD          
                if e not in conexion:
                    ee = '10e'
                    contador_ciclos[e] = 0
                    
                    AH_p[e] = 0
                    AH_n[e] = 0
                    
                    # inicializo diccionario datos del banco
                    datos[e]= {} 
                    datos[e]['ID_fab'] = 0
                    datos[e]['Nceldas'] = 0
                    datos[e]['SOC'] = 0
                    datos[e]['Vbat'] = 0
                    datos[e]['Ibat'] = 0
                    datos[e]['Temp_Bat'] = 0                    
                    datos[e]['AH_p'] = 0
                    datos[e]['AH_n'] = 0
                    datos[e]['s1'] = {}
                    
                    datos[e]['Vceldas'] = [0] * 30
                    datos[e]['Max'] = [0] * 30
                    datos[e]['Min'] = [999] * 30
                    datos[e]['Nombres'] = ['C'] * 30
                    
                    datos[e]['s2'] = {}
                    
                    datos[e]['Fallos_captura'] = 0
                    
                    if DEBUG >= 1 : print(f"Abriendo conexion en {EQUIPO[e]['dev']}", end='')
                    
                    ee = '10e_10'
                    try:
                        conexion[e] = serial.Serial(EQUIPO[e]['dev'])
                        conexion[e].baudrate = 115200
                        conexion[e].timeout  = 0.2
                    except:
                        print("BMS not found.")
                    
                    leer_equipo(e, False) # lectura y comprobacion de BD con nceldas
                    
                    if DEBUG >= 1 : print('.... OK')
                    
                #Cambio de día    
                dia_anterior = dia
                dia = time.strftime("%Y-%m-%d")

                if dia_anterior != dia: #cambio de dia
                    ee = '10e_20'
                    AH_p[e] = 0
                    AH_n[e] = 0
                    
                    datos[e]['Max'] = [0] * 30
                    datos[e]['Min'] = [999] * 30
                    datos[e]['AH_p'] = 0
                    datos[e]['AH_n'] = 0
                    datos[e]['Fallos_captura'] = 0
                                    
                ee = '10e_50'    
                if e in t_ultima_captura.keys():
                    if time.time() - t_ultima_captura[e] > EQUIPO[e]['tiempo_captura']:# and flag_lectura[e] == 0:
                        ee = '10f'
                        try:
                            leer_equipo(e)
                            t_ultima_captura[e] = time.time()
                        except Exception as error:
                            print(Fore.RED + f"Error {ee} en Bucle Principal... equipo {e} :", type(error).__name__, "–", error) 
                            time.sleep(1)
                            continue
                else:
                    t_ultima_captura[e] = time.time()
                            
                   
    except SystemExit:
        print(f"La captura de {NEQUIPO} se reinicia por no responder durante 5 minutos.")
        raise  # Re-lanza la excepción para detener el programa completamente

    except Exception as error1:
        print(f"Error {ee} en bucle principal", type(error1).__name__, "–", error1) 
        print ('.... se reinicia')
        cursor.close()
        db.close()
    
        sys.exit()
    
    time.sleep(0.1)
