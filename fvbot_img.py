#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2019-12-22

import time 
import telebot # Librería de la API del bot.
import sys
import os,glob # para mandar ultimo video

# -----------------------------------------------
## Los parametros si se usa en PVControl+ lo logico es pillarlos del fichero Parametros_FV.py"
from Parametros_FV import * # importo TOKEN de Telegram etc

"""
###### Actualizar con Claves propias y descomentar esta parte si no se quiere usar Parametros_FV.py

TOKEN = 'XXXXXXXX'  # bot PVControl ...cambiar por el que cada uno de de alta
Aut = [AAAAA] # Usuario/Grupo de Telegram donde se enviara la imagen

motion_telegram = 1 # 1 = Envia foto deteccion a Telegram
motion_clarifai = 1 # activa reconocimiento por Clarifai
api_key = 'ZZZZZ'   # Key Clarifai

"""

from clarifai.rest import ClarifaiApp
from clarifai.rest import Workflow # si se quiere utilizar algun workflow

if motion_telegram == 0:
    sys.exit()

hora_actual = int(time.strftime("%H")) # hora
dia_sem = int(time.strftime("%u")) # dia de la semana

try:
    with open('/run/shm/motion.cfg', mode='r') as f:
        modo_alarma = f.read()
except:
    modo_alarma='PRG'
    with open('/run/shm/motion.cfg', mode='w') as f:
        f.write('PRG')
        
if int(horario_alarma[dia_sem][hora_actual]) == 0 and modo_alarma == 'PRG':
    print ('fuera de horario de alarma')
    sys.exit()

bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
bot.skip_pending=True # Skip the pending messages

cid=Aut[0] # poner el usuario donde queremos mandar el msg 
alarma=0

narg = len(sys.argv)
#print ('Narg=',narg)

if narg > 1:
    imagen = str(sys.argv[1])
    #print ('arg=',imagen)
else:
    imagen = "/home/pi/PVControl+/test.jpg" #imagen de prueba

# --------Analizar Foto en Clarifai ------------------------------
try:
    if motion_clarifai == 1:
        
        app = ClarifaiApp(api_key=api_key)
        
        # Si se quiere subir la imagen capturada para categorizarla despues descomentar la siguiente linea
        #app.inputs.create_image_from_filename(imagen)
        
        
        # Deteccion usando el modelo estandard de deteccion de caras
        # al menos una cara en la foto capturada
        ##model = app.models.get('face')
        ##respuesta = model.predict_by_filename(imagen)
        ##caras = respuesta['outputs'][0]['data']
        
        
        # Deteccion usando el Workflow propio creado de caras mas deteccion propia 
        workflow = Workflow(app.api, workflow_id= workflow_id)
        respuesta = workflow.predict_by_filename(imagen)

        alarma = float(respuesta['results'][0]['outputs'][1]['data']['concepts'][0]['value'])
        alarma = round(alarma*100,0)

        caras = respuesta['results'][0]['outputs'][0]['data']    
        ncaras =len(caras)
        
        msg_telegram = 'Alarma= ' + str(alarma) +'% \nNumero de Caras detectadas = ' + str(ncaras)

    else:
        msg_telegram = 'No activada la deteccion por Clarifai'

except:
    msg_telegram = 'Error en Clarifai'

print (msg_telegram)

# ----------------------- BUCLE Mandar Foto a Telegram----------------------------------

salir = False
N = 0
Nmax = 1 # Numero maximo de intentos para mandar la imagen

while not(salir) and N < Nmax:
    
    print(alarma,imagen,msg_telegram)
    
    try:
        print(imagen)
        if alarma > 90:
            bot.send_photo(cid_alarma, photo=open(imagen, 'rb'), caption=msg_telegram)
            time.sleep(60)
            video = max(glob.iglob('/home/pi/motion/videos/*.mp4'), key=os.path.getctime)
            bot.send_video(cid_alarma, data=open(video, 'rb'), caption=video)
        else:               
            bot.send_photo(cid, photo=open(imagen, 'rb'), caption=msg_telegram)    
        salir = True
    except:
        print ('error')
        bot.send_message( cid_alarma, 'Error msg Telegram')
        #salir = False
        time.sleep(10)
        N += 1
        
if N >= Nmax: 
    print(' Img Telegram no enviada en '+str(N)+' intentos')
    
