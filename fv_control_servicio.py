import sys,subprocess

#Parametros Instalacion FV
from Parametros_FV import *

parar_servicio = False

try:
    if eval(control) == 0: parar_servicio = True
except:
    parar_servicio = True

if parar_servicio:   
    print (f'Se ejecuta ... sudo systemctl stop {servicio}...  parada servicio {servicio}')
    print (subprocess.getoutput(f'sudo systemctl stop {servicio}'))
    sys.exit()
