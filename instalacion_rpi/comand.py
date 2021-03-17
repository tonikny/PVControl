import os
import time
import subprocess #,commands
import sys

time.sleep(1)
#'apt autoremove','apt remove apache2','apt purge apache2',
#'apt remove php*','apt purge php*',
#'apt remove mariadb*','apt purge mariadb*'


lista = [#clonacion PVControl+
         'git clone https://git.code.sf.net/p/pvcontrol/code PVControl+'
    
         # Sistema
         'apt update',
         'apt upgrade -y',
         'apt install ca-certificates apt-transport-https lsb-release gnupg curl nano unzip -y',
         'wget -q https://packages.sury.org/php/apt.gpg -O- | apt-key add -',
         'echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/php.list',
         'apt update',
         
         # Apache & php
         'apt install apache2 -y',
         'apt install php8.0 php8.0-cli php8.0-common php8.0-curl php8.0-gd php8.0-intl php8.0-mbstring php8.0-mysql php8.0-opcache php8.0-readline php8.0-xml php8.0-xsl php8.0-zip php8.0-bz2 libapache2-mod-php8.0 -y',
         
         # MariaDB
         'sudo apt install mariadb-server mariadb-client -y',
         'echo "CREATE USER \'rpi\'@\'localhost\' IDENTIFIED BY \'fv\';" | sudo mysql -uroot',
         'echo "GRANT ALL PRIVILEGES ON *.* TO \'rpi\'@\'localhost\' WITH GRANT OPTION;"  | sudo mysql -uroot',
         'sudo mysql_secure_installation',
         'sudo apt-get install python3-mysqldb',
         
         # Phpmyadmin
         'wget https://www.phpmyadmin.net/downloads/phpMyAdmin-latest-all-languages.zip -O phpmyadmin.zip',
         'unzip phpmyadmin.zip',
         'rm phpmyadmin.zip',
         'mv phpMyAdmin-*-all-languages /usr/share/phpmyadmin',
         'chmod -R 0755 /usr/share/phpmyadmin',
         'wget pvcontrol.adnsolar.eu/phpmyadmin.conf','mv phpmyadmin.conf /etc/apache2/conf-available/phpmyadmin.conf',
         'a2enconf phpmyadmin',
         'systemctl reload apache2',
         'mkdir /usr/share/phpmyadmin/tmp/',
         'chown -R www-data:www-data /usr/share/phpmyadmin/tmp/',
         
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
    
