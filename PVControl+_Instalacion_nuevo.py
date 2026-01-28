#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2023-12-1

#### TEMAS PREVIOS ANTES DE EJECUTAR #############################

# CLONACION 
#     git clone https://git.code.sf.net/p/pvcontrol/code PVControl+

# Cambiar a rama bookworm
#     cd PVControl+               # cambiar a carpeta PVControl+
#     git checkout -b bookworm origin/bookworm

# Creacion entorno virtual de Python
#      python -m venv env          # crear entorno virtual
#
#      source env/bin/activate     # activar entorno si se quiere especificamente
#      deactivate                  # para desactivar entorno 
#

# Editar archivo /home/pi/.bashrc y añadir al final del fichero la linea:
#      export PATH="/home/pi/PVControl+/env/bin:$PATH"
#
# Activar PATH ( reiniciar RPi o teclear ....
#       export PATH="/home/pi/PVControl+/env/bin:$PATH"

# Editar archivo /home/pi/PVControl+/env/pyvenv.cfg y modificar la siguiente linea
#      include-system-site-packages = true

# ################################################################

# Programa de Instalacion del PVControl+
#
# Ejecutar desde /home/pi con el siguiente comando

#    python PVControl+_Instalacion.py opciones

#       opciones posibles:
#          sin opciones instala Base + Python + Links
#          .b  ... instala mysql, phpmyadmin, apache
#          .py ... instala librerias Python
#          -l  ... no instala, solo actualiza links    
#          -d  ... instala docker y Home Assistant   
#          -m  ... instala motionEye   


# Una vez clonado el repositario git y se quiere instalar lo habitual ....
#    sudo python PVControl+_Instalacion.py


import os
import time
import subprocess #,commands
import sys
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
import click

time.sleep(1)
#'apt autoremove','apt remove apache2','apt purge apache2',
#'apt remove php*','apt purge php*',
#'apt remove mariadb*','apt purge mariadb*'


"""
Clonar = [#clonacion PVControl+
         'git clone https://git.code.sf.net/p/pvcontrol/code PVControl+',   
           ]
"""

Base = [# Sistema, DB, Apache & php, Mosquitto,
         'sudo apt update',
         'sudo apt-get full-upgrade',
         'sudo chmod 755 /home/pi',
         'sudo apt install php8.2 php8.2-cli php8.2-common php8.2-curl php8.2-gd php8.2-intl php8.2-mbstring php8.2-mysql php8.2-opcache php8.2-readline php8.2-xml php8.2-xsl php8.2-zip php8.2-bz2 libapache2-mod-php8.2 -y',

         'sudo apt install mariadb-server mariadb-client python3-mysqldb -y',
         'echo "CREATE USER \'rpi\'@\'localhost\' IDENTIFIED BY \'fv\';" | sudo mysql -uroot',
         'echo "GRANT ALL PRIVILEGES ON *.* TO \'rpi\'@\'localhost\' WITH GRANT OPTION;"  | sudo mysql -uroot',
         'echo "CREATE DATABASE control_solar;"  | sudo mysql -uroot',
         'sudo mysql -uroot control_solar < /home/pi/PVControl+/PVControl+.sql',
         
         # Mosquitto MQTT
         'sudo apt-get install mosquitto mosquitto-clients -y' ,
         'sudo apt install python3-paho-mqtt',
         
         'sudo bash -c \'echo "allow_anonymous false" > /etc/mosquitto/conf.d/default.conf\'',
         'sudo bash -c \'echo "listener 1883" >> /etc/mosquitto/conf.d/default.conf\'',
         'sudo bash -c \'echo "password_file /home/pi/PVControl+/passwd_mosquitto" >> /etc/mosquitto/conf.d/default.conf\'',       
         'sudo systemctl restart mosquitto',
                  
         # Phpmyadmin
         'wget https://www.phpmyadmin.net/downloads/phpMyAdmin-latest-all-languages.zip -O phpmyadmin.zip',
         'unzip phpmyadmin.zip',
         'rm phpmyadmin.zip',
         'sudo mv phpMyAdmin-*-all-languages /usr/share/phpmyadmin',
         'sudo chmod -R 0755 /usr/share/phpmyadmin',
         'sudo cp /home/pi/PVControl+/util/phpmyadmin.conf /etc/apache2/conf-available/phpmyadmin.conf',
         'sudo a2enconf phpmyadmin',
         'sudo systemctl reload apache2',
         'sudo mkdir /usr/share/phpmyadmin/tmp/',
         'sudo chown -R www-data:www-data /usr/share/phpmyadmin/tmp/'
         ]
                  
Python = [ 
         # Librerias Python3
         
         #'sudo apt install python3-pymodbus', 
         #'sudo apt install python3-luma.core',
         #'sudo apt install python3-luma.oled',
         #'sudo apt install python3-bleak',
         
         # con env
         #'cd /home/pi/PVControl+',
         #'source /home/pi/PVControl+/env/bin/activate',
         
         
         'pip install pymodbus',
         'pip install luma.core',
         'pip install luma.oled',
         'pip install bleak',  # JK
         'pip install rpi.gpio',
         'pip install smbus',
         'pip install adafruit-ads1x15',
         'pip install pymodbusTCP',
         'pip install minimalmodbus',
         'pip install esptool',
         'pip install pyTelegramBotAPI',
         'pip install pyautogui',
         'pip install pynput',
         'pip install timeout_decorator',
         'pip install crc16',
         'pip install clarifai',
         'pip install clarifai-grpc', # parece no necesaria
         'pip install goodwe',
         'pip install pysolarmanv5', #DEYE
         'pip install can', #Pylontech
         'pip install cantools', #Pylontech
         
         
         # Varios
         # motionEye
         #### ver .....https://github.com/motioneye-project/motioneye/wiki/Installation
         
         ]


HA = [# docker y HA
         
         # Docker
         'sudo apt install raspberrypi-kernel raspberrypi-kernel-headers',
         'curl -sSL https://get.docker.com | sh',
         'sudo usermod -aG docker pi',
   
         # Home Assistant
         'docker run -d --name homeassistant --privileged --restart=unless-stopped -e TZ=Europe/Madrid -v /home/pi/PVControl+/HA:/config --network=host  ghcr.io/home-assistant/home-assistant:stable',
           ]



MotionEye = [# motionEye
         
          #### ver .....https://github.com/motioneye-project/motioneye/wiki/Installation
         
           ]

lista = Base + Python

if '-b' in sys.argv:
   lista = Base

if '-py' in sys.argv:
   lista = Python

if '-d' in sys.argv:
   lista = HA
   
if '-m' in sys.argv:
   lista = MotionEye

if '-l' in sys.argv or '--link' in sys.argv:
   lista = ''
   

   

for i in lista:
    print (Style.BRIGHT + Fore.YELLOW + '#' * 60)
    print (i)
    print ('#' * 60 + Fore.RESET)
    res = subprocess.run(i, shell=True)
    if res.returncode == 0:
        print (Style.BRIGHT + Fore.GREEN + '-' * 60)
        print('returncode:', res.returncode)
        print ('-' * 60)
    else:
        print (Style.BRIGHT + Fore.RED + '-' * 60)
        print('returncode:', res.returncode)
        print ('-' * 60)
        print ()
        salir = click.prompt(Fore.CYAN + '  Error detectado.... pulse una 0 para seguir o 1 para abortar ', type=str, default='0')
        if salir == '1': sys.exit()
        
    print(Fore.RESET)
    print()
    time.sleep(1)
    print(' ')
    
#Paginas web
print()
print(Fore.YELLOW+'######## Activando WEB PVControl+ #########')
res = subprocess.run(['sudo','rm', '-R','/var/www/html'])
res = subprocess.run(['sudo','ln', '-s','/home/pi/PVControl+/html','/var/www'])
print (Fore.GREEN+ '  ---- OK -----')

#Escritorio
print()
print(Fore.YELLOW+'######## Enlaces en escritorio #########')
res = subprocess.run(['ln', '-s','/home/pi/PVControl+/PVControl_Configuracion_Inicial.py','/home/pi/Desktop/PVControl_Configuracion_Inicial.py'])
res = subprocess.run(['ln', '-s','/home/pi/PVControl+/Arrancar_servicios_PVControl+.py','/home/pi/Desktop/Arrancar_servicios_PVControl+.py'])
res = subprocess.run(['ln', '-s','/home/pi/PVControl+/Parar_Servicios_PVControl+.py','/home/pi/Desktop/Parar_Servicios_PVControl+.py'])
res = subprocess.run(['ln', '-s','/home/pi/PVControl+/Ver_Programas_en_Ejecucion_PVControl+.sh','/home/pi/Desktop/Ver_Programas_en_Ejecucion_PVControl+.sh'])
res = subprocess.run(['ln', '-s','/home/pi/PVControl+/PVControl+/PVControl_Instalacion_HomeAssistant.py','/home/pi/Desktop/PVControl_Instalacion_HomeAssistant.py'])

print (Fore.GREEN+ '  ---- OK -----')

print()
print(Fore.CYAN+'######## Proceso Completado #########')

