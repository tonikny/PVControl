import os
import time
import subprocess #,commands
import sys

time.sleep(1)
#'apt autoremove','apt remove apache2','apt purge apache2',
#'apt remove php*','apt purge php*',
#'apt remove mariadb*','apt purge mariadb*'


lista = [#clonacion PVControl+
		 'sudo apt install git',		 
         'git clone https://git.code.sf.net/p/pvcontrol/code PVControl+',
    
         # Sistema
         'sudo apt update',
         'sudo apt upgrade -y',
         'sudo apt install python3-pip',         
         'sudo apt install ca-certificates apt-transport-https lsb-release gnupg curl nano unzip -y',
         'wget -q https://packages.sury.org/php/apt.gpg -O- | sudo apt-key add -',
         'echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/php.list',
         'sudo apt update',
         'sudo dpkg-reconfigure locales',
         
         # Apache & php
         'sudo apt install apache2 -y',
         'sudo apt install php8.0 php8.0-cli php8.0-common php8.0-curl php8.0-gd php8.0-intl php8.0-mbstring php8.0-mysql php8.0-opcache php8.0-readline php8.0-xml php8.0-xsl php8.0-zip php8.0-bz2 libapache2-mod-php8.0 -y',
         
         # MariaDB
         'sudo apt install mariadb-server mariadb-client -y',
         'echo "CREATE USER \'rpi\'@\'localhost\' IDENTIFIED BY \'fv\';" | sudo mysql -uroot',
         'echo "GRANT ALL PRIVILEGES ON *.* TO \'rpi\'@\'localhost\' WITH GRANT OPTION;"  | sudo mysql -uroot',        
         'sudo mysql_secure_installation',
         #'echo "create database phpmyadmin character set utf8"  | sudo mysql -uroot',
        
         #'mysql u- rpi -pfv < /home/pi/phpmyadmin.sql',         
         'sudo apt-get install python3-mysqldb',
         
         # Phpmyadmin
         'wget https://www.phpmyadmin.net/downloads/phpMyAdmin-latest-all-languages.zip -O phpmyadmin.zip',
         'sudo unzip phpmyadmin.zip',
         'sudo rm phpmyadmin.zip',
         'sudo mv phpMyAdmin-*-all-languages /usr/share/phpmyadmin',
         'sudo chmod -R 0755 /usr/share/phpmyadmin',
         'wget pvcontrol.adnsolar.eu/phpmyadmin.conf',
         'sudo mv phpmyadmin.conf /etc/apache2/conf-available/phpmyadmin.conf',
         'sudo a2enconf phpmyadmin',
         'sudo systemctl reload apache2',
         'sudo mkdir /usr/share/phpmyadmin/tmp/',
         'sudo chown -R www-data:www-data /usr/share/phpmyadmin/tmp/',                 
         
         # WiringPi
         'cd /tmp',
         'wget https://project-downloads.drogon.net/wiringpi-latest.deb',
         'sudo dpkg -i wiringpi-latest.deb',
         'cd /home/pi',
         
         # Mosquitto MQTT
         'sudo apt-get install mosquitto mosquitto-clients -y' ,
         'sudo pip3 install paho-mqtt',
         'sudo bash -c \'echo "allow_anonymous false" > /etc/mosquitto/conf.d/default.conf\'',
         'sudo bash -c \'echo -n "password_file /home/pi/PVControl+/passwd_mosquitto" >> /etc/mosquitto/conf.d/default.conf\'',       
         'sudo systemctl restart mosquitto',
         
         # PVControl
         'sudo pip3 install smbus',
         'sudo pip3 install Adafruit_ADS1x15',
         'sudo pip3 install pytelegrambotapi',
         'sudo pip3 install colorama',         
         'pip3 install click',
         'sudo pip3 install RPi.GPIO',
         'sudo pip3 install pymodbus',
         'sudo pip3 install pymodbusTCP',
         '/home/pi/PVControl+/./install_BD.sh',
         'python3 /home/pi/PVControl+/Actualizar_BD.py',
         'sudo chown root PVControl+/etc/cron.d/pvcontrol',
         'sudo pip3 install timeout_decorator',
         'sudo pip3 install crc16' , 
         # Configuracion phpmyadmin
         'wget https://pvcontrol.adnsolar.eu/phpmyadmin.sql',
         'sudo mysql -u root -pfv < phpmyadmin.sql',
         'wget https://pvcontrol.adnsolar.eu/conf_phpmyadmin',
         'sudo cp conf_phpmyadmin /usr/share/phpmyadmin/config.inc.php',
         'sudo service apache2 restart'        
         
         ]


for i in lista:
    print ('#' * 60)
    print (i)
    print ('#' * 60)
    res = subprocess.run(i, shell=True)
    print ('-' * 60)
    print('returncode:', res.returncode)
    print ('-' * 60)
    print()
    print()
    time.sleep(1)
    print(' ')
    
