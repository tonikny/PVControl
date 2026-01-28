import RPi.GPIO as GPIO # reles 4XX via GPIO
GPIO.setmode(GPIO.BOARD) #para RPi
#GPIO.setwarnings(False)

import time,csv,sys
import datetime,glob
import MySQLdb 

#Parametros Instalacion FV
from Parametros_FV import *


#Comprobacion argumentos en comando de fv.py
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p2':
    DEBUG = 2
elif str(sys.argv[narg-1]) == '-p3':
    DEBUG = 3
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 10
else:
    DEBUG = 0
print ('DEBUG=',DEBUG)

## RECUPERAR DE LA BD Tabla RELES ##
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    sql = 'SELECT * FROM reles'
    nreles = cursor.execute(sql)
    nreles = int(nreles)  # = numero de reles
    TR = cursor.fetchall()
    cursor.close()
    db.close()
    
except Exception as e:
    print ("Error, la base de datos no existe")

try:
    Reles_SSR = [ ]
    
    NGPIO =0 # Num Reles GPIO

    for I in range(nreles):         
        if int(TR[I][0]/100) == 4:
            NGPIO_PIN = TR[I][0] % 100
            print (NGPIO_PIN , TR[I][0] % 100)
            
            GPIO.setup(NGPIO_PIN, GPIO.OUT)
            Reles_SSR.append ([GPIO.PWM(NGPIO_PIN, 5),NGPIO_PIN])
            
            
            print  ('NGPIO=',NGPIO)
            Reles_SSR[NGPIO][0].start(0)
            NGPIO +=1

    print (Reles_SSR)
    #print (Reles_SSR_P)
    
    #print(dir(Reles_SSR[0]))
    
    while True:
        for I in range (100):
            print (I,end='-')
            time.sleep(1)
            Reles_SSR[0][0].ChangeDutyCycle(I)
            if I == 0:
                Reles_SSR[0][0].ChangeFrequency(50)
            else:
                if I <= 50:
                    Reles_SSR[0][0].ChangeFrequency(I)
                    print ('Frec0=',I,end='-')
                else:
                    Reles_SSR[0][0].ChangeFrequency(100-I)
                    print ('Frec0=',100-I,end='-')
            
            Reles_SSR[1][0].ChangeDutyCycle(100-I)
            print (' // Duty1=',100-I,end='-')
            if 100-I <= 50:
                Reles_SSR[1][0].ChangeFrequency(100-I)
                print ('Frec1=',100-I)
            else:
                Reles_SSR[1][0].ChangeFrequency(I+0.01)
                print ('Frec1=',I)
        print()
        print(time.time(),'-------------')
        
     

    #print (Reles_SSR[0].ChangeDutyCycle())

except:
    print('error')
    for I in range (NGPIO):
        print (I)
        Reles_SSR[I].stop()

finally:
    GPIO.cleanup()
    

sys.exit()
        
"""
if NGPIO ==1:
    SSR1 = GPIO.PWM(NGPIO_PIN, 5) #  Frecuencia = 5
elif NGPIO ==1:
    SSR2 = GPIO.PWM(NGPIO_PIN, 5) #  Frecuencia = 5
elif NGPIO ==1:
    SSR3 = GPIO.PWM(NGPIO_PIN, 5) #  Frecuencia = 5
elif NGPIO ==1:
    SSR4 = GPIO.PWM(NGPIO_PIN, 5) #  Frecuencia = 5
"""


