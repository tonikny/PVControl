#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2022-01-22

# #################### Control Ejecucion Servicio ########################################
servicio = 'fvbot'
control = 'usar_telegram'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import time # Librería para hacer que el programa que controla el bot no se acabe.
import random
import datetime
import token
import os
import sys


import MySQLdb
import paho.mqtt.client as mqtt

import requests,glob # control del motion via web

bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
bot.skip_pending=True # Skip the pending messages

nfallos=0
cid = Aut[0]
#bot.send_message(cid, 'Arrancando Bot Telegram')

# Control motion Camara -----------------
def webcontrol(chat_id, tipo, cmd):
    req = 'http://localhost:7999/1/'+tipo+'/'+cmd
    res = requests.get(req).text
    if res == '': res = 'OK'
    bot.send_message(chat_id, f'{req}\n{res}')

# Conexion MQTT -------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectandose al broker")
        global Connected                #variable global
        Connected = True                 
    else:
        print("Fallo Conexion al Broker")

Connected = False #variable global variable estado conexion

print("creando instancia MQTT")
client = mqtt.Client()
client.username_pw_set(mqtt_usuario, password=mqtt_clave) 
client.on_connect= on_connect   
client.connect(mqtt_broker)
client.loop_start()       
while Connected != True:  
    time.sleep(0.1)
#-----------------------------------------


#markup=types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=True,resize_keyboard=True)

#############################################
#Listener
def listener(messages): #definimos función 'listener', recibe como parámetro 'messages'.
    try:
        for m in messages: # Por cada dato 'm' en el dato 'messages'
            cid = m.chat.id # Almacenaremos el ID de la conversación.

            tg_to=cid
            tg_to_u=str(m.chat.first_name)
            tg_from=cid

            if m.content_type == 'text':
               
                #print (m)
                
                print (" Mensaje de [" + str(cid) + "]: " + m.text) # Y haremos que imprima algo parecido a esto -> [52033876]: /start
                
                if m.text[0]=='#':
                    tg_orden=str(m.text[1:])
                    
                    if cid in Aut:
                        orden_autorizada=1
                    else:
                        orden_autorizada=0
                        bot.send_message( cid, f'Usuario {cid} no autorizado')
                        
                    #bot.send_message( cid, "Orden introducida "+tg_orden)
                    bot.send_chat_action(cid,'typing')
                    
                    tipo_orden= tg_orden[0].upper() # H, I, R, P, V....

                    print ('Orden introducida ',tg_orden, ' tipo=',tipo_orden)
                    

                    #------------------ ORDEN RELES -----------------------
                    if tipo_orden=='R':
                        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                        cursor = db.cursor()
                        try:
                            objeto_orden= tg_orden[1:4]
                            orden= tg_orden[4:].upper()
                        except:
                            objeto_orden=''
                            orden=''
                        try:
                            orden1=orden[0]
                        except:
                            orden1=''
                        
                        try:
                            orden2=orden[1:]
                        except:
                            orden2=''   

                        # -------- Sub_Orden ON/OFF/PRG ---------    
                        if orden in ('PRG','ON', 'OFF'):
                            if orden_autorizada==1:
                                try:
                                    sql = f"UPDATE reles SET modo='{orden}' WHERE id_rele={objeto_orden}"
                                    cursor.execute(sql)
                                    db.commit()
                                                                        
                                    msg='Rele Nº'+objeto_orden+' puesto a '+ orden + ' por ' +tg_to_u
                                    bot.send_message( cid, msg)
                                    
                                except:
                                    msg='No se puede actualizar la tabla reles con la orden recibida   '+sql
                                    bot.send_message( cid, msg)
                                                                        
                            else:
                                msg=tg_from+' NO tiene permiso para esta orden'
                                bot.send_message( cid, msg)
                        
                        # -------- Sub_Orden Modo Manual (ejem sintaxis #r611M30  pone en modo manual al 30% el rele 611 ---------
                        elif orden1=='M':
                            if orden_autorizada==1:
                              try:
                                  orden='MAN'
                                  sql = f"UPDATE reles SET modo='{orden}', estado={orden2} WHERE id_rele={objeto_orden}"
                                  cursor.execute(sql)
                                  db.commit()
                                  
                                  msg=f"Rele Nº {objeto_orden} puesto a modo={orden} y estado={orden2} por {tg_to_u}"
                                  bot.send_message( cid, msg)
                              except:
                                    msg='No se puede actualizar la tabla reles con la orden recibida   '+sql
                                    bot.send_message( cid, msg)    
                                  
                                  
                                  
                        # -------- Sub_Orden Cambio Nombre Rele ---------    
                        elif orden1=='N':
                            if orden_autorizada==1:
                                try:
                                    sql = "UPDATE reles SET nombre='"+orden2+ "' WHERE id_rele="+objeto_orden
                                    cursor.execute(sql)
                                    db.commit()
                                    msg='Nombre Rele Nº'+objeto_orden+' ='+ orden2 + ' por ' +tg_to_u
                                    bot.send_message( cid, msg)
                                    
                                except:
                                    msg='No se puede actualizar la tabla reles con la orden recibida   '+sql
                                    bot.send_message( cid, msg)
                            else:
                                msg=tg_from+' NO tiene permiso para esta orden'
                                bot.send_message( cid, msg)

                        # -------- Sub_Orden Creacion Rele ---------    
                        elif orden1=='C':
                            if orden_autorizada==1:
                                try:
                                    orden2=orden2[1:]
                                    cursor.execute("""INSERT INTO reles
                                                   (id_rele,nombre,modo,estado,grabacion)
                                                   VALUES (%s,%s,%s,%s,%s)""",
                                                        (objeto_orden,orden2,'OFF',0,'N'))

                                    db.commit()
                                    msg='Creado Rele Nº'+objeto_orden+' ='+ orden2 + ' por ' +tg_to_u
                                    bot.send_message( cid, msg)

                                except:
                                    msg='No se puede crear rele con la orden recibida   '
                                    bot.send_message( cid, msg)
                            else:
                                msg=tg_from+' NO tiene permiso para esta orden'
                                bot.send_message( cid, msg)

                        # -------- Sub_Orden Borrado Rele ---------    
                        elif orden1=='B':
                            if orden_autorizada==1:
                                try:
                                    sql = "DELETE FROM reles  WHERE id_rele="+objeto_orden
                                    cursor.execute(sql)
                                    db.commit()
                                    msg='Borrado Rele Nº'+objeto_orden+' por ' +tg_to_u
                                    bot.send_message( cid, msg)

                                except:
                                    msg='No se puede crear rele con la orden recibida   '
                                    bot.send_message( cid, msg)
                            else:
                                msg=tg_from+' NO tiene permiso para esta orden'
                                bot.send_message( cid, msg)

                        # -------- Sub_Orden informacion Reles ---------
                        elif orden=='':
                            try:
                                sql = "SELECT id_rele,nombre,modo,estado,grabacion FROM reles"
                                cursor.execute(sql)
                                nreles=cursor.execute(sql)
                                nreles=int(nreles)  # = numero de reles
                                TR=cursor.fetchall()
                                msg=' ----- ESTADO RELES -----'+ '\n'
                                msg=msg+'_id_|_S_|Mod|Gr| Nombre'+ '\n'
                                for I in range(nreles):
                                    msg=msg+str(TR[I][0])+'|_'+ str(TR[I][3])+'_|'+TR[I][2].ljust(3)+'|'+ TR[I][4]
                                    msg=msg+ ' | '+TR[I][1] +'\n'
                                    #msg=msg+str(TR[I])+ '\n'
                                    
                                msg=msg + '----------------------------------------------------------'+ '\n'
                                msg=msg + '  EJEMPLOS COMANDOS RELES '+ '\n'
                                msg=msg + '----------------------------------------------------------'+ '\n'
                                msg=msg + ' #R201ON  activa rele 201'+ '\n'
                                msg=msg + ' #R201OFF  apaga rele 201'+ '\n'
                                msg=msg + ' #R201PRG  rele 201 programado'+ '\n'
                                msg=msg + ' #R201N=XX cambia nombre a XX'+ '\n'
                                msg=msg + ' #R201C=XX crea rele 201 N=XX-OFF'+ '\n'
                                msg=msg + ' #R201B borra rele 201'+ '\n'
                                            
                                msg=msg + ' #R  Muestra este mensaje'
                                
                                bot.send_message( cid, msg)

                            except:
                                msg= 'Error al acceder a la tabla reles'
                                bot.send_message( cid, msg) 
                        else:
                            msg='No interpreto correctamente la orden recibida'
                            bot.send_message( cid, msg)
                        cursor.close()
                        db.close()

                    #------------------ ORDEN INFORMACION -----------------------
                    elif tipo_orden=='I':
                        try:
                            subprocess.run(['python3','/home/pi/PVControl+/fvbot_msg.py','-m'])
                        except:
                            print ('Error en ejecucion de fvbot_msg.py')
                    #------------------ ORDEN PARAMETROS -----------------------
                    elif tipo_orden=='P':
                        try:
                            #print('a=',tg_orden[1:3])
                            np = int(tg_orden[1:3])
                            objeto_orden= tg_orden[1:3]
                            orden= tg_orden[4:].upper()
                            #print('b')
                        except:
                            try:
                                #print('c',tg_orden[1:2])
                                np = int(tg_orden[1:2])
                                objeto_orden= tg_orden[1:2]
                                orden= tg_orden[3:].upper()
                                #print('d')
                            except:
                                #print('e')
                                objeto_orden=''   
                        try:
                            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                            cursor = db.cursor()
                            sql='SELECT * FROM parametros'
                            nparametros=cursor.execute(sql)
                            nparametros=int(nparametros)  # = numero de filas de parametros.---- debe ser 1
            
                            columns = [column[0] for column in cursor.description]
                            TP1 = []
                            for row in cursor.fetchall(): TP1.append(dict(zip(columns, row)))
                            TP = TP1[0] # solo la primera fila
             
                        except:
                            bot.send_message( cid, 'Error en lectura tabla parametros')
                        

                        if objeto_orden=='':
                            cursor.close()
                            db.close()
                            
                            L='Tabla de parametros de la BD\n'
                            np=0
                            for p in TP:
                                np += 1
                                if columns[np-1] != 'id_parametros':
                                    L += f'P{np}={TP[p]} -- {columns[np-1]}\n'
                            
                            L += ('\n### Ejemplos de comandos ###\n' +
                            'P1=S    ..Grabar datos a Si\n' +
                            'P2=N    ..Grabar reles a No\n' +
                            'P3=5    ..T_muestras en 5 sg\n' +
                            'P4=1    ..N_muestras para grabar a 1\n' +
                            'P5=95.7 ..Actualizar SOC a 95.7%\n' +
                            'P6=28.8 ..Actualizar Objetivo_PID a 28.8V\n' +
                            'P7=Vbat ..Actualizar Sensor_PIDa Vbat\n' +
                            'P8=10   ..Actualizar Kp del PID a 10\n' +
                            '....\n' +
                            'P12=28.8..Actualizar Vflot a 28.8V\n' +
                            '....'
                            )
                            
                            bot.send_message( cid, L) 
                        
                        elif orden_autorizada==1:
                            ncolumna= int(objeto_orden)
                            sql = f"UPDATE parametros SET {columns[ncolumna-1]}='{orden}'"
                            try:
                                cursor.execute(sql)
                                db.commit()
                                bot.send_message( cid, f'{columns[ncolumna-1]} puesto a {orden}')
                            except:
                                bot.send_message( cid, f'Error en ejecucion orden: {sql}')
                            cursor.close()
                            db.close()
                        else:
                            bot.send_message( cid, msg)    
                        
                    #------------------ ORDEN AYUDA -----------------------
                    elif tipo_orden=='?':
                        L1='--- ORDENES ACEPTADAS ---'
                        L2=''#reiniciar..reinicia la RPi'
                        L3=''#teamviewer..reinicia teamviewer'
                        L4='#?..Muestra esta ayuda'
                        L5='#i..Informacion resumida FV'
                        L6='#p..Ayuda para comandos parametros'
                        L7='#r..Ayuda para comandos reles'
                        L8='#h..Ayuda para comandos Hibrido'
                        L9='#V..Ayuda para comandos Camara'
                        
                        msg=L1+'\n'+L2+'\n'+L3+'\n'+L4+'\n'+L5+'\n'+L6+'\n'+L7+'\n'+L8+'\n'+L9
                        bot.send_message( cid, msg)

                    #------------------ COMANDO HIBRIDO -----------------------
                    elif tipo_orden=='H':
                        if tg_orden[1].isnumeric():
                            print('PVControl/Hibrido'+tg_orden[1],tg_orden[2:])
                            client.publish('PVControl/Hibrido'+tg_orden[1],tg_orden[2:])
                        else:
                            print('PVControl/Hibrido',tg_orden[1:])
                            client.publish('PVControl/Hibrido',tg_orden[1:])
                        
                    #------------------ ORDEN VIGILANCIA -----------------------
                    elif tipo_orden=='V':
                        try:
                            orden= tg_orden[1:].upper()
                        except:
                            print ('error tg_orden')
                            orden=''
                        print('orden V=',orden)
                        #print('10')
                        
                        if orden == 'FOTO':
                            requests.get('http://localhost:8080/0/action/snapshot')
                        elif orden == 'PRG':
                            webcontrol(cid, 'detection', 'start')
                            with open('/run/shm/motion.cfg', mode='w') as f:
                                f.write('PRG')
                        elif orden == 'ESTADO':
                            webcontrol(cid, 'detection', 'status')
                        elif orden == 'OFF':
                            webcontrol(cid, 'detection', 'pause')
                            with open('/run/shm/motion.cfg', mode='w') as f:
                                f.write('OFF')
                        elif orden == 'ON':
                            webcontrol(cid, 'detection', 'start')
                            with open('/run/shm/motion.cfg', mode='w') as f:
                                f.write('ON')
                        elif orden == 'CHECK':
                            webcontrol(cid, 'detection', 'connection')
                        elif orden == 'TIME':
                            bot.send_message(cid, 'hora '+str(datetime.datetime.now()))
                        elif orden == 'VIDEO':
                            # the most recent video in this particular folder of complete vids
                            print('Video =',)
                            video = max(glob.iglob('/home/pi/motion/videos/*.mp4'), key=os.path.getctime)
                            print(video)
                            # send video, adapt the the first argument to your own telegram id
                            bot.send_video(cid, data=open(video, 'rb'), caption=video)
                        elif orden == '':
                            bot.send_message(cid, "foto,estado,pausa,start,check,time,video")
                        else:
                            bot.send_message(cid, "Comando no valido "+orden)
                            bot.send_message(cid, "foto,estado,pausa,start,check,time,video")
                                        
                    #------------------ ORDEN LINUX -------------------
                    elif tipo_orden=='L':
                        comando= tg_orden[1:]
                        print ("Comando: ", comando)
                        proceso = subprocess.run(comando, shell=True,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE,
                                                 text=True
                                                )
                        if proceso.returncode==0:
                            msg = proceso.stdout
                        else:
                            msg = proceso.stderr
                            
                        maxlong = 4096
                        for t in [msg[i:i+maxlong] for i in range(0, len(msg), maxlong)]:
                            bot.send_message (cid, t)
                            
                    #------------------ ORDEN INCORRECTA -------------------
                    else:
                        msg='Orden incorrecta .. #'
                        bot.send_message( cid, msg)
    except:
        print ('Fallo')
        
bot.set_update_listener(listener) # definimos al bot la funcion 'listener' como "escucha".

#############################################
#Funciones

# -------- Funcion Help ------------
@bot.message_handler(commands=['?','start']) 
def command_ayuda(m): 
    global markup

    cid = m.chat.id
    #conexion a la bbdd
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    #sql para sacar datos de vceldas y verificamos si la instalacion tiene o no el moniteado de celdas
    sql_Vceldas="""SELECT * FROM datos_celdas ORDER BY id_celda DESC LIMIT 1 """
    celdas=0
    try:
        cursor.execute(sql_Vceldas)
        var=cursor.fetchone() 
        print(var)
        if len(var) >0: celdas=1  
        
    except:
        pass
    cursor.close()
    db.close()
    
    markup = types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=False,resize_keyboard=True)
    itembtn1 = types.KeyboardButton('/i Informacion FV\n')    
    itembtn3 = types.KeyboardButton('/p Actualizar parametros BD')
    itembtn4 = types.KeyboardButton('/r Actualizar Reles')
    itembtn5 = types.KeyboardButton('/V Configurar Alarma Camara')
    itembtn6 = types.KeyboardButton('')

    if celdas == 0:   ##Botones para seleccion ordenes sin Vceldas
        markup.add(itembtn1, itembtn3, itembtn4, itembtn5, itembtn6)
        
    else:        ##Botones para seleccion ordenes con Vceldas
        itembtn2 = types.KeyboardButton('/vc Vceldas')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
         
    msg=bot.send_message(cid, "Elige COMANDO:", reply_markup=markup)
    
    
#------------- TEAMVIEWER ---------------------------
@bot.message_handler(commands=['teamviewer_restart'])
def command_teamviewer_r(m):
    cid = m.chat.id
    if cid in Aut:
        #os.system('sudo teamviewer --daemon restart')
        os.system('sudo systemctl restart teamviewerd')
        bot.send_message(cid, "Teamviewer reiniciado")

@bot.message_handler(commands=['teamviewer_stop'])
def command_teamviewer_s(m):
    cid = m.chat.id 
    if cid in Aut:
        os.system('sudo teamviewer --daemon stop')
        bot.send_message(cid, "Teamviewer parado")

#------------- RASPBERRY ---------------------------
@bot.message_handler(commands=['raspberry_restart'])
def command_raspberry_r(m):
    cid = m.chat.id
    if cid in Aut:
        os.system('sudo shutdown -r now')
        
        
        
        
        
#------------- Vceldas ---------------------------
@bot.message_handler(commands=['vc'])
def command_teamviewer_r(m):
      
    cid = m.chat.id

    bot.send_chat_action(cid,'typing')

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
   
    #### CELDAS
    #sql para sacar datos de vceldas  
    sql='SELECT * FROM datos_celdas ORDER BY id_celda DESC LIMIT 1'
    nparametros=cursor.execute(sql)
    
    columns = [column[0] for column in cursor.description]
    #print(columns)
    TC1 = []
    for row in cursor.fetchall(): TC1.append(dict(zip(columns, row)))
    
    
    L_celdas = ''
    
    Valor_celdas = ''
    if len(TC1) > 0: # Hay datos de celdas
        TC = TC1[0] # Se crea diccionario TC con primer elemento de la lista
       
        del TC['Tiempo'] #borramos las claves no utilizadas para calcular max y min
        del TC['id_celda']
        
        Cmax = max(TC, key = TC.get) # clave del valor maximo
        Cmin = min(TC, key = TC.get) # clave del valor minimo
        
        
    for x in TC:
        l=''
        if x == Cmax: l=' --MAX'   
        elif x== Cmin:l=' --min'   
        Valor_celdas += f'{x:3}:{TC[x]}V{l}\n'
            
    L_celdas += (f'\n<code>{Valor_celdas}</code>' + '-'*50+
                 f'\n <b> Vbat={sum(TC.values()):.2f}V -- Dif= {(TC[Cmax]-TC[Cmin])*1000:.0f}mV </b> ')
    
    ##### MENSAJE    
    tg_msg=L_celdas
    
    #print (tg_msg)
    bot.send_message(cid, tg_msg, parse_mode="HTML")
    
    cursor.close()
    db.close()
               
        

#------------- INFORMACION ---------------------------
@bot.message_handler(commands=['i'])
def command_i(m):
    try:
        subprocess.run(['python3','/home/pi/PVControl+/fvbot_msg.py','-m'])
    except:
        print ('Error en ejecucion de fvbot_msg.py')
                            
    
# -------- Funcion Tabla Parametros BD ------------
@bot.message_handler(commands=['p'])
def command_p(m):
    global markup

    cid = m.chat.id
    
    bot.send_chat_action(cid,'typing')

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql_reles='SELECT * FROM parametros'
    nparametros=cursor.execute(sql_reles)
    TP=cursor.fetchone()
    cursor.close()
    db.close()
    
    msg=('PARAMETROS\nGrabar Datos= '+TP[0]+'\n'+'Grabar Reles= '+TP[1]+'\n'+
         'Tiempo Muestra= '+str(TP[2])+'\n'+ 'Num Muestras entre registros BD= '+str(TP[3])
         +'\n'+'SOC= '+str(TP[4])+'%')
    bot.send_message(cid, msg)
    

##Botones para seleccion campo de la tabla parametros 
    markup = types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=False,resize_keyboard=True)

    #markup = types.ForceReply(force_replay)
    
    itembtn1 = types.KeyboardButton('/GD Grabar datos FV en BD')
    itembtn2 = types.KeyboardButton('/GR Grabar reles en BD')
    itembtn3 = types.KeyboardButton('/TM T_muestra en segundos')
    itembtn4 = types.KeyboardButton('/NM N_muestras para guardar')
    itembtn5 = types.KeyboardButton('/SOC Actualizar SOC')
    itembtn6 = types.KeyboardButton('/VPLACA Actualizar Vplaca_diver')
    
    itembtn7 = types.KeyboardButton('/? Volver Menu Principal')

    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)
      
    msg=bot.send_message(cid, "Elige parametro:", reply_markup=markup)

# ---------------- GD -----------------------
@bot.message_handler(commands=['GD'])
def GD(message):
    cid=message.chat.id
       
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Grabar datos S/N = ",reply_markup=FR)
    bot.register_next_step_handler(msg,GD_upgrade)
    
def GD_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        if cid in Aut:
            print ('Usuario autorizado',cid)
            m=message.text.upper()
            if m!='S' and m!='N':
                raise
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET grabar_datos='"+m+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"Parametro grabar_datos modificado a "+m,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)
    except:
        bot.send_message(cid, "No se puede modificar grabar_datos\n Vuelve a intentarlo")

# ---------------- GR -----------------------
@bot.message_handler(commands=['GR'])
def GR(message):
    cid=message.chat.id

    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Grabar reles S/N = ",reply_markup=FR)

    bot.register_next_step_handler(msg,GR_upgrade)

def GR_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        if cid in Aut:
            m=message.text.upper()
            if m!='S' and m!='N':
                raise
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET grabar_reles='"+m+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"Parametro grabar_reles modificado a "+m,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)

    except:
        bot.send_message(cid, "No se puede modificar grabar_reles\n Vuelve a intentarlo",reply_markup=markup)
       
# ---------------- TM -----------------------
@bot.message_handler(commands=['TM'])
def TM(message):
    cid=message.chat.id
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Tiempo muestra en segundos = ",reply_markup=FR)
    bot.register_next_step_handler(msg,TM_upgrade)

def TM_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        if cid in Aut:
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET t_muestra='"+message.text+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"Parametro t_muestra modificado a "+message.text,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)

    except:
        bot.send_message(cid, "No se puede modificar t_muestra\n Vuelve a intentarlo",reply_markup=markup)

# ---------------- NM -----------------------
@bot.message_handler(commands=['NM'])
def NM(message):
    cid=message.chat.id
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Numero de muestras = ",reply_markup=FR)
    bot.register_next_step_handler(msg,NM_upgrade)

def NM_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        if cid in Aut:
            if float(message.text)<1:
                bot.send_message(cid, "Ha de ser mayor que 0")
                raise
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET n_muestras_grab='"+message.text+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"Parametro n_muestras modificado a "+message.text,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)

    except:
        bot.send_message(cid, "No se puede modificar n_muestras\n Vuelve a intentarlo",reply_markup=markup)

# ---------------- SOC -----------------------
@bot.message_handler(commands=['SOC'])
def SOC(message):
    cid=message.chat.id
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Introduce nuevo SOC:",reply_markup=FR)
    bot.register_next_step_handler(msg,SOC_upgrade)

def SOC_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    #bot.send_message(cid, "Nuevo SOC = "+message.text)
    try:
        if cid in Aut:
            if float(message.text)>100 or float(message.text)<0:
                raise
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET nuevo_soc='"+message.text+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"SOC cambiado a "+message.text,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)
 
    except:
        bot.send_message(cid, "No se puede actualizar el nuevo SOC\n Vuelve a intentarlo",reply_markup=markup)
    
# ---------------- Vplaca_diver -----------------------
@bot.message_handler(commands=['O_diver'])
def O_diver(message):
    cid=message.chat.id
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Introduce nuevo Objetivo_diver:",reply_markup=FR)
    bot.register_next_step_handler(msg,O_diver_upgrade)

def O_diver_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        if cid in Aut:
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET objetivo_diver='"+message.text+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"objetivo_diver cambiado a "+message.text,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)
 
    except:
        bot.send_message(cid, "No se puede actualizar\n Vuelve a intentarlo",reply_markup=markup)

# ----------------------- RELES  ---------------------------------------
@bot.message_handler(commands=['r'])
def reles(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        
        sql = "SELECT id_rele,nombre,modo,estado,grabacion FROM reles"
        cursor.execute(sql)
        nreles=cursor.execute(sql)
        nreles=int(nreles)  # = numero de reles
        TR=cursor.fetchall()
        cursor.close()
        db.close()
        
        msg=' ----- ESTADO RELES -----'+ '\n'
        msg=msg+'_id_|_S_|Mod|Gr| Nombre'+ '\n'
        for I in range(nreles):
            msg=msg+str(TR[I][0])+'|_'+ str(TR[I][3])+'_|'+TR[I][2].ljust(3)+'|'+ TR[I][4]
            msg=msg+ ' | '+TR[I][1] +'\n'
                        
        
        bot.send_message(cid, msg)
    

##Botones reles 
        markup = types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=False,resize_keyboard=True)

        #markup = types.ForceReply(force_replay)
        
        itembtn1 = types.KeyboardButton('/ON Poner Rele a ON')
        itembtn2 = types.KeyboardButton('/OFF Poner Rele a OFF')
        itembtn3 = types.KeyboardButton('/PRG Poner Rele a PRG')
        itembtn4 = types.KeyboardButton('/Crear_Rele')
        itembtn5 = types.KeyboardButton('/Borrar_Rele')
        itembtn6 = types.KeyboardButton('/? Volver Menu Principal')

        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)

        msg=bot.send_message(cid, "Elige parametro:", reply_markup=markup)

    except:
        msg= 'Error al acceder a la tabla reles'
        bot.send_message(cid, msg)

# ---------------- RELE ON -----------------------
@bot.message_handler(commands=['ON'])
def rele_on(message):
    cid=message.chat.id
    
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "introduce Nº Rele= ",reply_markup=FR)
    
    bot.register_next_step_handler(msg,rele_on_upgrade)

def rele_on_upgrade(message):
    cid=message.chat.id
    print (message.text)
    orden='ON'
    rele_upgrade(orden,message.text,cid)
    
# ---------------- RELE OFF -----------------------
@bot.message_handler(commands=['OFF'])
def rele_on(message):
    cid=message.chat.id
    
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "introduce Nº Rele= ",reply_markup=FR)
    
    bot.register_next_step_handler(msg,rele_off_upgrade)

def rele_off_upgrade(message):
    cid=message.chat.id
    print (message.text)
    orden='OFF'
    rele_upgrade(orden,message.text,cid)

# ---------------- RELE PRG -----------------------
@bot.message_handler(commands=['PRG'])
def rele_on(message):
    cid=message.chat.id
    
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "introduce Nº Rele= ",reply_markup=FR)
    
    bot.register_next_step_handler(msg,rele_prg_upgrade)

def rele_prg_upgrade(message):
    cid=message.chat.id
    print (message.text)
    orden='PRG'
    rele_upgrade(orden,message.text,cid)

# ---------------- RELE CAMBIO MODO ----------------------- 
def rele_upgrade(orden,nrele,cid):    
    try:
        sql = "UPDATE reles SET modo='"+orden+"' WHERE id_rele=" + nrele
        
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

        msg='Rele '+ nrele + ' puesto a '+ orden
               
        bot.send_message(cid, msg, reply_markup=markup)
    except:
        msg='No se puede actualizar la tabla reles con la orden recibida   '
        bot.send_message(cid, msg, reply_markup=markup)


        bot.send_message(cid, saludo)
            
# ---------------- HIBRIDO -----------------------
@bot.message_handler(commands=['H','h'])
def comando_hibrido(message):
    cid=message.chat.id
    
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "introduce Comando = ",reply_markup=FR)
    
    bot.register_next_step_handler(msg,mandar_comando_hibrido)

def mandar_comando_hibrido(message):
    cid=message.chat.id
    #print (message.text)
    if cid in Aut:
        client.publish('PVControl/Hibrido',message.text)
    
# -------- Funcion Alarma ------------
@bot.message_handler(commands=['V','v']) 
def command_motion(m): 
    global markup
    cid = m.chat.id
##Botones para seleccion ordenes 
    markup = types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=False,resize_keyboard=True)
    itembtn1 = types.KeyboardButton('/PRG_ Programacion Horaria')
    itembtn2 = types.KeyboardButton('/ON_ Siempre activo')
    itembtn3 = types.KeyboardButton('/OFF_ Desconectado')
    itembtn4 = types.KeyboardButton('/Foto')
    itembtn5 = types.KeyboardButton('/Video')
    itembtn6 = types.KeyboardButton('/Estado Camara')
    itembtn7 = types.KeyboardButton('/? Volver Menu Principal')
    itembtn8 = types.KeyboardButton('')
    
    #itembtn4 = types.KeyboardButton('/s Salir')

    markup.add(itembtn1, itembtn2, itembtn3,itembtn4, itembtn5, itembtn6, itembtn7, itembtn8)
     
    msg=bot.send_message(cid, 'Pulsa opcion...',reply_markup=markup)
    
#    hideBoard=types.ReplyKeyboardHide()
    
@bot.message_handler(commands=['PRG_']) 
def command_motion_prg(m): 
    global markup
    cid = m.chat.id
    if cid in Aut:
        webcontrol(cid, 'detection', 'start')
        with open('/run/shm/motion.cfg', mode='w') as f:
            f.write('PRG')

@bot.message_handler(commands=['ON_']) 
def command_motion_on(m): 
    global markup
    cid = m.chat.id
    if cid in Aut:
        webcontrol(cid, 'detection', 'start')
        with open('/run/shm/motion.cfg', mode='w') as f:
            f.write('ON')

@bot.message_handler(commands=['OFF_']) 
def command_motion_off(m): 
    global markup
    cid = m.chat.id
    if cid in Aut:
        webcontrol(cid, 'detection', 'pause')
        with open('/run/shm/motion.cfg', mode='w') as f:
            f.write('OFF')

@bot.message_handler(commands=['Foto']) 
def command_motion_foto(m): 
    global markup
    cid = m.chat.id
    if cid in Aut:
        requests.get('http://localhost:7999/1/action/snapshot')

@bot.message_handler(commands=['Video']) 
def command_motion_video(m): 
    global markup
    cid = m.chat.id
    if cid in Aut:
        ultimo_video = max(glob.iglob('/home/pi/motioneye/capturas/*.mp4'), key=os.path.getctime)
        print(cid, ultimo_video)
        video = open(ultimo_video, 'rb')            
        bot.send_video(cid, video,caption= video.name)

@bot.message_handler(commands=['Estado']) 
def command_motion_estado(m): 
    global markup
    cid = m.chat.id
    if cid in Aut:
        webcontrol(cid, 'detection', 'status')
    
""" 
    elif orden == 'CHECK':
        webcontrol(cid, 'detection', 'connection')
    elif orden == 'TIME':
        bot.send_message(cid, 'hora '+str(datetime.datetime.now()))      
"""
           
#############################################
#Polling
def telegram_polling():
    global nfallos
    try:
        bot.polling(none_stop=True,interval=5, timeout=60) #constantly get messages from Telegram
    except:
        nfallos=nfallos+1
        print (time.strftime("%c"), nfallos,' Error polling Telegram')
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()


telegram_polling()
    
