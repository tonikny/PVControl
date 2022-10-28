#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 2022-01-21  Manda un mensaje de informacion FV al Telegram
#... uso habitual con crontab configurando archivo pvcontrol
#....el archivo pvcontrol debe ser root luego editarlo con .... sudo nano /home/pi/PVControl+/etc/cron.d/pvcontrol

import time, datetime,sys
import MySQLdb,json 
import subprocess
import glob
import telebot # Librería de la API del bot.
import requests # consulta ip publica
#import commands # temperatura Cpu
# Mensaje por defecto si no se especifoca en Parametros_FV.py

msg_telegram = ["\U0001F50B <b><u>Batería</u></b>: (<code>{d_['FV']['Mod_bat']}</code>)",
				"     SOC: <b>{d_['FV']['SOC']:.1f}</b>%     \U000024CB <b>{d_['FV']['Vbat']:.1f}</b>V     \U000024BE <b>{d_['FV']['Ibat']:.1f}</b>A",
				#"     \U0001F4CA {L_celdas}",

                "\U0001F31E <b><u>Placas</u></b>:",
                "     \U000024C5 <b>{d_['FV']['Wplaca']:.0f}</b>W     \U000024BE <b>{d_['FV']['Iplaca']:.1f}</b>A     \U000024CB <b>{d_['FV']['Vplaca']:.0f}</b>V",

                "\U0001F4A1 <b><u>Consumo</u></b>:",
                "     \U000024C5 <b>{d_['FV']['Wconsumo']:.0f}</b>W     \U000024BE <b>{d_['FV']['Iplaca']-d_['FV']['Ibat']:.1f}</b>A     PWM: <b>{d_['FV']['PWM']:.0f}</b>",
                "     Relés: <b>{L_reles}</b>",

                #"\U0001F50C <b><u>Red</u></b>:",
                #"     \U000024C5 <b>{d_['FV']['Wred']:.0f}</b>W     \U000024BE <b>{d_['FV']['Ired']:.1f}</b>A     \U000024CB <b>{d_['FV']['Vred']:.0f}</b>V",

                "\U0001F4C6 <b><u>Diario (KWh)</u></b>:",
                "     \U0001F31E <b>{d_['FV']['Wh_placa']/1000:.1f}</b> \U0001F50B <i>{d_['FV']['Whp_bat']/1000:.1f}-{d_['FV']['Whn_bat']/1000:.1f}</i> = <b>{(d_['FV']['Whp_bat']-d_['FV']['Whn_bat'])/1000:.1f}</b> \U0001F4A1 <b>{(d_['FV']['Wh_consumo'])/1000:.1f}</b>",
                #"     \U0001F50C <b>{(d_['FV']['Wh_red'])/1000:.1f}</b>",

                "\U0001F321 <b><u>Temperaturas (ºC)</u></b>:",
                "     Bat: <b>{d_['FV']['Temp']}</b> / CPU: <b>{d_['TEMP']['Temp_cpu']:.1f}</b>",

                "\U0001F4BB <b><u>Conexión (IP)</u></b>:",
                "     \U0001F3E0 {L_ip_local}  \U0001F30D <span class='tg-spoiler'>{L_ip}</span>",
                ]

from Parametros_FV import *

DEBUG= False
if '-p' in sys.argv: DEBUG= True 
if '-m' in sys.argv: msg_periodico_telegram = 1 

if msg_periodico_telegram == 0: sys.exit()
    
sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave")

bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
bot.skip_pending=True # Skip the pending messages

try:
    cid = m.chat.id
except:
    cid=Aut[0] # poner el usuario donde queremos mandar el msg 

bot.send_chat_action(cid,'typing')
 



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


## RECUPERAR REGISTROS EQUIPOS DE LA BD ##

try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    d_={}
    sql = 'SELECT * FROM equipos'
    nequipos = int(cursor.execute(sql))
    for row in cursor.fetchall(): 
        d_[row[0]] = json.loads(row[2])
        if row[0] == 'FV': fecha = row[1] # fecha del registro FV en BD
    
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
    pass

    
# ------------------------ LECTURA FECHA / HORA ----------------------

tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
diasemana = time.strftime("%w") 
hora = time.strftime("%H:%M:%S")

# ----------- Lineas preformateadas ------------------------

try:
    # Reles
    L_reles = ''
    Rele={}
    for r in d_['RELES']:
        tipo_rele = int(int(r)/100)
        if tipo_rele not in Rele.keys(): Rele[tipo_rele] = '' # inicializo valor
        valor = f"{d_['RELES'][r]['estado']/10:1.0f}"
        if valor == '10': valor = 'X'
        Rele[tipo_rele] += valor

    for r in Rele: L_reles +=f'{r}[{Rele[r]}] '
    L_reles = L_reles[:-1] 
except:
    L_reles = 'Error L_reles'

try:
    Temperaturas = ''
    for sensor in sensores:
      tfile = open(sensor)
      texto = tfile.read()
      tfile.close()
      segundalinea = texto.split("\n")[1]
      temp_datos = segundalinea.split(" ")[9]
      temp_s = float(temp_datos[2:])/1000
      Temperaturas = Temperaturas + str(round(temp_s,1)) + '/'
      #print ("sensor", sensor, "=", temp_s, " grados.")
    
    temp_cpu = 0
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        temp_cpu = float(f.read())/1000
        
    L_temp = f'{temp_cpu:.1f} {Temperaturas}'

except:
    L_temp = 'Error L_temp'
 
try:
    #### IP publica
    L_ip = str(detect_public_ip())
except:
    L_ip = 'Error L_ip'

try:
    #### IP privada
    ip_local = subprocess.getoutput('hostname -I')
    L_ip_local = ip_local.split(' ')[0]
except Exception as e:
	L_ip_local = 'Error L_ip_local'

try:
    #### CELDAS
    L_celdas = ''
    if len(TC1) > 0: # Hay datos de celdas
        TC = TC1[0] # Se crea diccionario TC con primer elemento de la lista
        if datetime.datetime.timestamp(TC['Tiempo']) < time.time() - 60:
            L_celdas = '<b><i>**Error celdas desactualizadas**</i></b>\n' # añade ERROR si los datos son mas antiguos de 60sg

        del TC['Tiempo'] #borramos las claves no utilizadas para calcular max y min
        del TC['id_celda']
        
        Cmax = max(TC, key = TC.get) # clave del valor maximo
        Cmin = min(TC, key = TC.get) # clave del valor minimo
        
        L_celdas += f'{Cmax}={TC[Cmax]:.3f}V -- {Cmin}={TC[Cmin]:.3f}V -- {(TC[Cmax]-TC[Cmin])*1000:.0f}mV'

except:
    L_celdas = 'Error L_celdas'


try:
    ### Composicion mensaje
    tg_msg = ''
    for l in msg_telegram:
        ee = l
        if DEBUG:
            print (f'{l}')
            print(eval(f'f"{l}"'))
            print('-' * 50)
        tg_msg += eval(f'f"{l}"')+ '\n'

except:
    tg_msg = f'Error en mensaje {ee}'
# -------------------------------- BUCLE ENVIO MSG --------------------------------------

salir=False
N=1
Nmax=28

while salir!=True and N<Nmax:

    try:               
        bot.send_message( cid, tg_msg, parse_mode="HTML")
        salir=True
    except:
        salir=False
        time.sleep(60)
        N=N+1
        if N == 10:
            pass
            #poner aqui lo que se quiere hacer en caso de 10 intentos fallidos
            
#--------------------------------------------------

if N>=Nmax: 
    logBD(' Msg Telegram no enviado en '+str(N)+' intentos') # incluyo mensaje en el log

cursor.close()
db.close()
  
