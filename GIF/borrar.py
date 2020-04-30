import time,sys

import subprocess,shlex

#command_line = 'ps -eo cmd | grep -v grep | grep python'
command_line = 'ps -eo cmd | grep python'

args = shlex.split(command_line)
print (args)
print('####################')
p1 = subprocess.Popen(['ps','-eo','cmd'], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['grep', '-v','grep'], stdin=p1.stdout, stdout=subprocess.PIPE)
p3 = subprocess.Popen(['grep', 'python'], stdin=p2.stdout, stdout=subprocess.PIPE)
p2.stdout.close()  # permite a p2 recibir SIGPIPE si p3 existe.
p1.stdout.close()  # permite a p1 recibir SIGPIPE si p2 existe.
salida = p3.communicate()[0]
salida_py= salida.decode(encoding='UTF-8')

print (salida_py)
print('##########vvvv##########')

#pp2 = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#output, err = pp2.communicate()
#print ('Son las ', output, err)




sys.exit()



with subprocess.run(["ifconfig"], stdout=subprocess.PIPE) as proc:
    log.write(proc.stdout.read())
sys.exit()

outfd = ''
errfd = ''

# Supongamos que queremos ejecutamos el comando: ls -l -a
subprocess.call(['ps', 'ax'], stdout=outfd, stderr=errfd)


# Por último mostramos lo que tienen las variables
print ('stdout: %s\n' % outfd)
print ('stderr: %s' % errfd)

sys.exit()





# importamos el módulo
import subprocess

# Creamos los descriptores de archivos como dos vulgares archivos
# con permisos de escritura llamados 'archivo_out' y 'archivo_err'
outfd = open('archivo_out', 'w+')
errfd = open('archivo_err', 'w+')

# Supongamos que queremos ejecutamos el comando: ls -l -a
subprocess.call(['ps', 'ax'], stdout=outfd, stderr=errfd)

# Cerramos los archivos para que se escriban los cambios y se liberen
# los buffers de I/O
outfd.close()
errfd.close()

# Ahora leemos todo lo que tengan los archivos y guardamos en la variable
# output la salida estándar y en err la salida de error.
fd = open('archivo_out', 'r')
output = fd.read()
fd.close()

fd = open('archivo_err', 'r')
err = fd.read()
fd.close()

# Por último mostramos lo que tienen las variables
print ('stdout: %s\n' % output)
print ('stderr: %s' % err)

sys.exit()


import os
resultado=os.system("ps ax")
print (resultado)



import subprocess
from subprocess import call
#pp = call('ps -eo cmd | grep -v grep | grep python')
#print (pp)

pp2 = subprocess.Popen('ps ax', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, err = pp2.communicate()
print ('Son las ', output)
sys.exit()

pp2 = subprocess.check_output('ps ax')
print ('Ejecutando...', pp2)

pp2 = subprocess.check_output('ps -eo cmd | grep -v grep | grep python')
print ('Ejecutando...', pp2)



while True:
    """
    with open('/run/shm/pp.txt', 'r') as f:
        for linea in f:
            print(linea,end='')
            time.sleep(1)
    
    
    """
    with open('/run/shm/pp.txt', 'r') as f:
        contenido = f.read()
        print(contenido)
        time.sleep(1)
        #cc=contenido.split('.py')
    print('##################')
    
    """
    time.sleep(2)
    print (contenido[0])
    time.sleep(2)
    print('VVVVVV1')
    print (contenido[1])
    time.sleep(2)
    print('VVVVVV2')
    print (contenido[2])
    time.sleep(2)
    print('VVVVVV3')
    print (contenido[3])
    #print('VVVVVV')
    #print (contenido[4])
    
    
    time.sleep(5)
    """
    
