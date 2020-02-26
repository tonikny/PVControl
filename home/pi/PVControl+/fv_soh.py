#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2019-08-11

import time
import MySQLdb

import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token

from Parametros_FV import *


def logBD(texto) : # Incluir en tabla de Log
    try:
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,texto))
        db.commit()
    except:
        db.rollback()

    return

if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]


Ti=time.time()

Ahn = 0.0
Ahp = 0.0
AhCPn = 0.0
AhCPp = 0.0
ipt = 0.0



try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql='SELECT Tiempo, Ibat, Temp  FROM datos WHERE DATE(Tiempo) = DATE_ADD(CURDATE(), INTERVAL -1 DAY) ORDER BY Tiempo;'
    nfilas=cursor.execute(sql)
    nfilas=int(nfilas)
    var=cursor.fetchall()
        
except Exception as e:
   print ("Error en la base de datos - fv_soh.py")


fecha= var[0][0].strftime("%Y-%m-%d")

#print ('fecha=',fecha)
#print ('nfilas=',nfilas)

i=0

#print (time.time()-Ti)

for i in range(nfilas-1): 

    diferencia= (var[i+1][0]-var[i][0]).total_seconds()
    
    #print (diferencia)
 
    ibat=float(var[i][1])
    temp=float(var[i][2])

    if ibat < 0:
        Ahn = Ahn - (ibat * diferencia/3600)
        if temp > 20:
            ipt1 = -ibat
            ipt = ipt1**CP * 2**((temp-20)/10)
            AhCPn = AhCPn + (ipt * diferencia/3600)
        else:
            AhCPn = AhCPn - (ibat * diferencia/3600)
    else :
        Ahp = Ahp + (ibat * diferencia/3600)
        if temp > 20:
            ipt = ibat**CP * 2**((temp-20)/10)
            AhCPp = AhCPp + (ipt * diferencia/3600)
        else:
            AhCPp = AhCPp + (ibat * diferencia/3600)
              
#print (time.time()-Ti)   

#print ('Ahp=',Ahp)
#print ('Ahn=',Ahn)
#print ('AhCPp=',AhCPp)
#print ('AhCPn=',AhCPn)

try:
    tg_msg="Registro SOH no grabado "
    
    cursor.execute("""INSERT INTO soh (fecha,Ahn,Ahp,AhCPn,AhCPp)
                 VALUES(%s,%s,%s,%s,%s)""",
                 (fecha,Ahn,Ahp,AhCPn,AhCPp))
    #print (fecha,Ahn,Ahp,AhCPn,AhCPp)
    db.commit()
    if usar_telegram == 1:
        tg_msg="Ciclado Ah/AhCP dia " + fecha + "=" + str(int(Ahn)) + "/" + str(int(AhCPn))
        try:
            bot.send_message( cid, tg_msg)
        except:
            pass

except:
    db.rollback()
    logBD(tg_msg)
    if usar_telegram == 1:        
        try:
            bot.send_message( cid, tg_msg)
        except:
            pass

cursor.close()
db.close()

