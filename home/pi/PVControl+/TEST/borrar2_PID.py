import time
import MySQLdb 

#Parametros Instalacion FV
from Parametros_FV import *




IPWM = 17
def Calcular_PID (PWM,valor,objetivo,P,I,D):
    global IPWM
    
    if PWM <= 0 or PWM >= PWM_Max: IPWM = -IPWM
        
    return IPWM



db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()
sql_reles='SELECT * FROM reles'
nreles=cursor.execute(sql_reles)
nreles=int(nreles)  # = numero de reles
TR=cursor.fetchall()

print(TR)

time.sleep(10)
                  

## Simulo lectura de la tabla Reles
# id_rele, nombre, modo,estado,grabacion,salto, prioridad)
Reles = [[201,'Rele201','PRG',0,'N',5,3],
         [202,'Rele202','PRG',0,'N',20,2],
         [203,'Rele203','PRG',0,'N',10,4],
         [204,'Rele204','PRG',0,'N',5,1]]

Nreles_Diver = len(Reles)
PWM_Max= Nreles_Diver * 100
PWM = 0

print (PWM_Max)
print (Reles)

print('Ordeno lista Reles por Prioridad')
Reles_Ord = sorted(Reles, key=lambda rr: rr[6])
print (Reles_Ord,'/n')
print ('-------------')
print ('Empieza la Simulacion PID')

while True:

    IPWM = Calcular_PID(PWM,0,0,0,0,0)

    PWM += IPWM
    
    if PWM >= PWM_Max: PWM = PWM_Max
    if PWM <= 0:PWM = 0
        
    print('PWM=',PWM, 'Incr=',IPWM)

    PWM_R = PWM
    for i in range(Nreles_Diver):
        valor = min(100,PWM_R)
        salto = Reles_Ord[i][5]
        Reles_Ord[i][3] = int(salto * round(valor/salto))
        
        PWM_R -= Reles_Ord[i][3]
        PWM_R = max(0,PWM_R)

        print('Rele',i, Reles_Ord [i][0],Reles_Ord [i][3],PWM_R)
        
    print('.....................')
    time.sleep(1)




