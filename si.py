#!/usr/bin/python
# -*- coding: utf-8 -*-
#  version 08/Ene/23
# --------------------------------------------------------------------------
from colorama import Fore, Back, Style
import colorama  # colores en ventana Terminal
from pyModbusTCP.client import ModbusClient
import time
import sys
import subprocess
import MySQLdb
import json
from Parametros_FV_DIST import *
from Parametros_FV import *
import pickle



if usar_SI == 0:
    print(subprocess.getoutput('sudo systemctl stop si1'))
    sys.exit()


si = ModbusClient(host= '192.168.0.100', port=502, unit_id=3)
si.open()

Equipo = sys.argv[1]
cont = 0
crear_pkl = 0  # poner a 1 para versiones antiguas de PVControl que no usan BD en RAM

DEBUG = False
# Comprobacion argumentos en comando
if '-p' in sys.argv:
    DEBUG = True  # para test .... realiza print en distintos sitios

colorama.init()


print(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' si.py')
print()

time.sleep(1)

try:  # inicializamos BD
    # No se crea tabla especifica de fronius
    db = MySQLdb.connect(host=servidor, user=usuario,
                         passwd=clave, db=basedatos)
    cursor = db.cursor()

    try:
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                       (Equipo, '{}'))
        db.commit()
    except:
        pass
except:
    print(Fore.RED + 'ERROR inicializando BD RAM')
    sys.exit()


def leer_datos():

    if 1==1: #try:        
        equipo = si.read_holding_registers(30057, 2)
        if equipo !=None:
            equipo = 65536*equipo[0]+equipo[1]
        else: equipo=0
        
        
        if equipo != 3015118151:
            a = calcula_host()
        equipo = 3015118151
        #print('Equipo',equipo, 'IP :')
        Vbat = si.read_holding_registers(30851, 2)
        Vbat = round(Vbat[1]*0.01, 2)
        
        Ibat = si.read_holding_registers(30843, 2)
        
        p_desc = si.read_holding_registers(31395, 2)
        p_desc = p_desc[1]
        
        p_l1 = si.read_holding_registers(30777, 2)
        if p_l1[0] <= 32768:
            p_l1 = -(p_l1[1]+p_l1[0]*65535)
        else:
            p_l1 = (65535-p_l1[1]+(65535-p_l1[0])*65536)

        p_l2 = si.read_holding_registers(30779, 2)
        if p_l2[0] <= 32768:
            p_l2 = -(p_l2[1]+p_l2[0]*65535)
        else:
            p_l2 = (65535-p_l2[1]+(65535-p_l2[0])*65536)

        p_l3 = si.read_holding_registers(30781, 2)

        if p_l3[0] <= 32768:
            p_l3 = -(p_l3[1]+p_l3[0]*65535)

        else:
            p_l3 = (65535-p_l3[1]+(65535-p_l3[0])*65536)

        p_carg = si.read_holding_registers(31393, 2)
        p_carg = p_carg[1]
        Aux1 = si.read_holding_registers(30803, 2)
        Aux1 = round(Aux1[1]*0.01, 2)

        if Ibat[0] <= 32768:
            Ibat = -(Ibat[1]+Ibat[0]*65535)*0.001

        else:
            Ibat = (65535-Ibat[1]+(65535-Ibat[0])*65536)*0.001
            
        p_gen = si.read_holding_registers(31419, 6)       
        p_gen_L1 = p_gen[1]
        if p_gen_L1 > 32768: p_gen_L1 = p_gen_L1 - 65535
        p_gen_L2 = p_gen[3]
        if p_gen_L2 > 32768: p_gen_L2 = p_gen_L2 - 65535
        p_gen_L3 = p_gen[5]
        if p_gen_L3 > 32768: p_gen_L3 = p_gen_L3 - 65535
        
        Temp = si.read_holding_registers(30849, 2)
        Temp = Temp[1]*0.1
        
        print('TEMP', Temp)
        
        if DEBUG: print(p_gen, p_gen_L1, p_gen_L2, p_gen_L3)

        datos = {'Vbat': Vbat, 'Ibat': Ibat,
                 'Pdesc': p_desc, 'Pcarg': p_carg, 'Aux1': Aux1, 'PL1': p_l1, 'PL2' : p_l2, 'PL3' : p_l3,
                 'p_gen_L1':p_gen_L1, 'p_gen_L2':p_gen_L2, 'p_gen_L3':p_gen_L3,'temp':Temp}                 
        
        
        
        
                 
        
        if DEBUG:
            print(datos)

    #except:
        #if DEBUG:
            #print('error de lectura SI')
        #logBD('Error de Lectura SI Vbat,Ibat...')
        #si.close()
        #time.sleep(3)
        #si.open()
        #pass

    if datos != None:
        return(datos)
    else:
        print('No hay datos')
        return(None)


def leer_datos_est():

    try:
        t_to_abs = si.read_holding_registers(31007, 2)
        t_to_abs = t_to_abs[1]
        Temp = si.read_holding_registers(30849, 2)
        Temp = Temp[1]*0.1
        v_abs = si.read_holding_registers(40085, 2)
        v_abs = v_abs[1]*0.01 * 24
        v_flot = si.read_holding_registers(40091, 2)
        v_flot = v_flot[1]*0.01 * 24
        SOC_si = si.read_holding_registers(30845, 2)
        SOC_si = SOC_si[1]
    except:
        print('Error lectura V Objetivo')
        logBD('Error de Lectura SI Temp,SOC...')
        Vobj = Vobj + 0.5
        si.close()
        time.sleep(3)
        si.open()
        pass

    if t_to_abs == 0:
        Vobj = v_flot - (Temp-20) * 24 * 0.004 - 0.8
    if t_to_abs != 0:
        Vobj = v_abs - (Temp-20) * 24 * 0.004 - 0.8

    if Vobj < 53:
        Vobj = 65.00

    if DEBUG:
        print('   Vabs', v_abs, 'V_flot', v_flot, 't_to_abs',
              t_to_abs, 'Vobj', Vobj, 'SOC', SOC_si)

    try:
        db = MySQLdb.connect(host=servidor, user=usuario,
                             passwd=clave, db=basedatos)
        cursor = db.cursor()
        query = """ UPDATE parametros SET objetivo_PID = %s WHERE id_parametros =%s """
        data = (Vobj, 1)
        cursor.execute(query, data)
        db.commit()
    except:

        pass
    try:
        cursor.close()

    except:
        pass
    return(None)

def calcula_host():
    global si
    x = 100
    equipo = 0

    while equipo != 3015118151:
        
        ip = '192.168.0.' + str(x)
        
        if DEBUG: print('Intentando conectar a IP: ', ip)

        si = ModbusClient(host= ip, port=502, unit_id=3)

        if si.open():

            equipo = si.read_holding_registers(30057, 2)
            equipo = 65536*equipo[0]+equipo[1]
            
        else: equipo = None
        
        print('IP: ',ip,'Equipo SMA:',equipo)

        x = x+1
        if x==256:x=1
        print('Host salida calcula datos: ', ip)
        print('---------------------------------------------------')
        time.sleep(1)
    return(ip)
 
        
while True:

    try:

        datos = leer_datos()
        #if cont % 10 == 0:
        #    leer_datos_est()
            #cont = 1
        #cont += 1

        #if DEBUG:
            #print('datos=', datos, 'cont', cont)

        if datos != None:
            if crear_pkl == 0:
                try:  # ARCHIVOS RAM en BD ############
                    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

                    salida = json.dumps(datos)
                    # print(salida)
                    # grabacion en BD RAM
                    sql = (
                        f"UPDATE equipos SET tiempo = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{sys.argv[1]}'")
                    # print(sql)
                    cursor.execute(sql)
                    db.commit()
                except:
                    print(
                        Fore.RED+f'error, Grabacion tabla RAM equipos en {Equipo}')
            else:
                # lo logico es dejar de grabar el archivo pkl
                with open('/run/shm/datos_sb.pkl', mode='wb') as f:
                    pickle.dump(datos, f)

    except:
        si.close()
        time.sleep(6)
        si.open()
        pass

    time.sleep(5)
