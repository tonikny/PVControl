import os

import time

import subprocess #,commands

import sys



time.sleep(1)

#'apt autoremove','apt remove apache2','apt purge apache2',

#'apt remove php*','apt purge php*',

#'apt remove mariadb*','apt purge mariadb*'





list = ['apt update',

'apt upgrade -y',

'apt install ca-certificates apt-transport-https lsb-release gnupg curl nano unzip -y',

'wget -q https://packages.sury.org/php/apt.gpg -O- | apt-key add -',

'echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/php.list',

'apt update',

'apt install apache2 -y',

'apt install php8.0 php8.0-cli php8.0-common php8.0-curl php8.0-gd php8.0-intl php8.0-mbstring php8.0-mysql php8.0-opcache php8.0-readline php8.0-xml php8.0-xsl php8.0-zip php8.0-bz2 libapache2-mod-php8.0 -y',

'apt install mariadb-server mariadb-client -y',

'mysql_secure_installation',

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

'wget pvcontrol.adnsolar.eu/conf.sql',

'mysql -u root < conf.sql']





for i in range(len(list)):

    res = subprocess.run(list[i], shell=True)

    print('returncode:', res.returncode)

    time.sleep(1)

    print(' ')

    

    

    
