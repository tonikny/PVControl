#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 2021-12-3  Manda un mensaje de informacion FV al Telegram
#... uso habitual con crontab configurando archivo pvcontrol
#....ese archivo debe ser root luego editarlo con .... sudo nano /home/pi/PVControl+/etc/cron.d/pvcontrol

import time, datetime
import MySQLdb 

import telebot # Librería de la API del bot.
import requests # consulta ip publica
#import commands # temperatura Cpu

from Parametros_FV import *

import sys
if msg_periodico_telegram == 0:
    sys.exit()
    
import subprocess
import glob
sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave")

bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
bot.skip_pending=True # Skip the pending messages

cid=Aut[0] # poner el usuario donde queremos mandar el msg 

# --------------------- DEFINICION DE FUNCIONES --------------

def logBD(msg) : # Incluir en tabla de Log
    try: 
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,msg))
        #print (tiempo,' ', msg)
        db.commit()
    except:
        db.rollback()
    
    return


def detect_public_ip(): # cambiar .... parece que ya no funciona
    try:
        # Use a get request for api.duckduckgo.com
        raw = requests.get('https://api.duckduckgo.com/?q=ip&format=json')
        # load the request as json, look for Answer.
        # split on spaces, find the 5th index ( as it starts at 0 ), which is the IP address
        answer = raw.json()["Answer"].split()[4]
    # if there are any connection issues, error out
    except Exception as e:
        return 'Error: {0}'.format(e)
    # otherwise, return answer
    else:
        return answer

    
## RECUPERAR ULTIMO REGISTRO DE LA BD y SITUACION RELES ##

try:

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

   #DATOS FV
    sql='SELECT Tiempo,SOC,Vbat,Aux1,Ibat,Iplaca,Vplaca,Whp_bat,Whn_bat,Wh_placa,Temp,PWM FROM datos ORDER BY id DESC limit 1'
    cursor.execute(sql)
    var=cursor.fetchone()
    Hora_BD=str(var[0])
    SOC=float(var[1])
    Vbat=float(var[2])
    Aux1=float(var[3])
    Ibat=float(var[4])
    Iplaca=float(var[5])
    Vplaca=float(var[6])
    Whp_bat=float(var[7])
    Whn_bat=float(var[8])
    Wh_placa=float(var[9])
    Temp=float(var[10])
    PWM=int(var[11])
    
   # RELES
    sql_reles='SELECT * FROM reles'
    nreles=cursor.execute(sql_reles)
    nreles=int(nreles)  # = numero de reles
    TR=cursor.fetchall()

    ### CELDAS
    sql='SELECT * FROM datos_celdas ORDER BY id_celda DESC LIMIT 1'
    TC1 = []
    try:
        nparametros=cursor.execute(sql)
        columns = [column[0] for column in cursor.description]      
        for row in cursor.fetchall(): TC1.append(dict(zip(columns, row)))
    except:
        pass      
    
except Exception as e:
    
    Hora_BD='Error BD'
    SOC=0
    Vbat=0
    Aux1=0
    Ibat=0
    Iplaca=0
    Vplaca=0
    Whp_bat=0
    Whn_bat=0
    Wh_placa=0
    Temp=0
    PWM=0

    nreles=0

tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------- BUCLE PRINCIPAL --------------------------------------

salir=False
N=1
Nmax=28
               
while salir!=True and N<Nmax:

    #print (salir,N)
    
    # ------------------------ LECTURA FECHA / HORA ----------------------

    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    diasemana = time.strftime("%w") 
    hora = time.strftime("%H:%M:%S")
    
    # ----------- MSG TELEGRAM ------------------------
    
    if SOC==100: SOC = '100'
    else: SOC = f'{SOC:.1f}' 
    
    L1=f'SOC={SOC}% - Vbat={Vbat:.1f}v -PWM={PWM:.0f}'
    L2=f'Iplaca={Iplaca:.1f}A - Ibat={Ibat:.1f}A - Vpl={Vplaca:.0f}'
    L3=f'Kwh: Placa={Wh_placa/1000:.1f} - Bat={Whp_bat/1000:.1f}-{Whn_bat/1000:.1f}={(Whp_bat-Whn_bat)/1000:.1f}'
            
    L4='RELES('
   
    for I in range(nreles): # Reles wifi
        Puerto=(TR[I][0]%10)-1
        addr=int((TR[I][0]-Puerto)/10)
        if int(addr/10)== 2:
            valor=int(TR[I][3]/10)
            if valor ==10:
                texto='X'
            else:
                texto=str(valor)
            L4=L4+texto
    L4=L4+') ('

    for I in range(nreles): # Reles i2C
        Puerto=(TR[I][0]%10)-1
        addr=int((TR[I][0]-Puerto)/10)
        if int(addr/10)== 3:
            valor=int(TR[I][3]/10)
            if valor ==10:
                texto='X'
            else:
                texto=str(valor)
            L4=L4+texto
            
    L4 = L4 + ')'

    #L5 =  Hora_BD + ' - T=' + str(round(Temp,1))+'ºC'
    
    Temperaturas = str(round(Temp,1))+'//'
    for sensor in sensores:
      tfile = open(sensor)
      texto = tfile.read()
      tfile.close()
      segundalinea = texto.split("\n")[1]
      temp_datos = segundalinea.split(" ")[9]
      temp_s = float(temp_datos[2:])/1000
      Temperaturas = Temperaturas + str(round(temp_s,1)) + '/'
      #print ("sensor", sensor, "=", temp_s, " grados.")
    
    temp_cpu = subprocess.getoutput('sudo /opt/vc/bin/vcgencmd measure_temp')
    temp_cpu=temp_cpu[0:len(temp_cpu)-2]
    
    L5 = 'T='+Temperaturas+'ºC -- CPU='+temp_cpu[5:] +'ºC'   

    #L6 =  'IP = '+ str(detect_public_ip())
    
    #### CELDAS
    
    L_celdas = ''
    if len(TC1) > 0: # Hay datos de celdas
        TC = TC1[0] # Se crea diccionario TC con primer elemento de la lista
        if datetime.datetime.timestamp(TC['Tiempo']) < time.time() - 60: L_celdas = '\n Error celdas desactualizadas' # añade ERROR si los datos son mas antiguos de 60sg
    
        del TC['Tiempo'] #borramos las claves no utilizadas para calcular max y min
        del TC['id_celda']
        
        Cmax = max(TC, key = TC.get) # clave del valor maximo
        Cmin = min(TC, key = TC.get) # clave del valor minimo
        
        L_celdas += f'\nCmax={Cmax}:{TC[Cmax]:.3f}V -- Cmin={Cmin}:{TC[Cmin]:.3f}V -- Dif={(TC[Cmax]-TC[Cmin])*1000:.0f}mV'
  
    
   ###Usando BOT
    tg_msg = L1+'\n'+L2+'\n'+L3+'\n'+L4+'\n'+L5 +L_celdas #+'\n'+L6

    try:               
        bot.send_message( cid, tg_msg)
        salir=True
    except:
        salir=False
        time.sleep(60)
        N=N+1
        if N == 10:
            pass
            #En mi caso a los 10 intentos reinicio el router que lo tengo en el rele 334
            """
            sql = "UPDATE reles SET modo='OFF' WHERE id_rele=334 " 
            cursor.execute(sql)
            db.commit()
            logBD("Apago rele del Router a los 10 intentos")
            time.sleep(10)

            sql = "UPDATE reles SET modo='PRG' WHERE id_rele=334 " 
            cursor.execute(sql)
            db.commit()
            logBD("Enciendo rele del Router")
            time.sleep(60)
            """
           
#--------------------------------------------------

if N>=Nmax: 
    logBD(' Msg Telegram no enviado en '+str(N)+' intentos') # incluyo mensaje en el log

cursor.close()
db.close()
  
