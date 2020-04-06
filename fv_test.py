import psutil
 
def TestProceso(nombre):
    for pr in psutil.process_iter():
        try:
            if nombre in pr.cmdline():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            print('error')
    return False;


ruta = '/home/pi/PVControl+/'
lista_proc=['fv.py','fvbot.py','hibrido.py','fv_temp.py','victron.py',
            'bmv.py','fv_oled.py','sma.py','snre.py','huawei.py' ]

for proc in lista_proc:
    if TestProceso(ruta+proc):
        
        print('---------------------',proc, 'ejecutandose')
    else:
        print(proc, 'detenido')
