import sys,subprocess

#Parametros Instalacion FV
basepath = '/home/pi/PVControl+/'
parametros_FV = basepath + "Parametros_FV.py"
parametros_FV_DIST = basepath + "Parametros_FV_DIST.py"

exec(open(parametros_FV_DIST).read(),globals())   #carga Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
exec(open(parametros_FV).read(),globals())        #carga Parametros_FV.py  .... Valores especificos de cada instalacion

#####################
    
parar_servicio = False

try:
    if eval(control) == 0: parar_servicio = True
except:
    parar_servicio = True

if parar_servicio:   
    print (f'Se ejecuta ... sudo systemctl stop {servicio}...  parada servicio {servicio}')
    print (subprocess.getoutput(f'sudo systemctl stop {servicio}'))
    sys.exit()
