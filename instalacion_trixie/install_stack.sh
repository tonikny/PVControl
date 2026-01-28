#!/bin/bash
# Instalacion de servicios para Trixie

# Colores brillantes y definidos
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
CYAN='\033[0;96m'
NC='\033[0m'

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}   INSTALANDO STACK PARA RASPBERRY OS TRIXIE${NC}"
echo -e "${BLUE}=============================================${NC}"

# Definir rutas absolutas
PVC_HOME="/home/pi/PVControl+"
PVSQL_FILE="$PVC_HOME/PVControl+.sql"
PARAM_FV_DIST="$PVC_HOME/Parametros_FV_DIST.py"
PARAM_FV="$PVC_HOME/Parametros_FV.py"
PARAM_WEB_DIST="$PVC_HOME/html/Parametros_Web_DIST.js"
PARAM_WEB="$PVC_HOME/html/Parametros_Web.js"
VERSION_INC="$PVC_HOME/html/version.inc"
PHPMA_CONF="$PVC_HOME/util/phpmyadmin.conf"
CONFIG_INICIAL="$PVC_HOME/PVControl_Configuracion_Inicial.py"
ARRANCAR_SERVICIOS="$PVC_HOME/Arrancar_servicios_PVControl+.py"
PARAR_SERVICIOS="$PVC_HOME/Parar_Servicios_PVControl+.py"
VER_PROGRAMAS="$PVC_HOME/Ver_Programas_en_Ejecucion_PVControl+.sh"
HA_INSTALACION="$PVC_HOME/PVControl_Instalacion_HomeAssistant.py"

# Obtener IP para mostrar al final
IP_ADDRESS=$(hostname -I | awk '{print $1}')

# Actualizar sistema
echo -e "${BLUE}[INFO] Actualizando sistema...${NC}"
sudo apt update
sudo apt full-upgrade -y
echo -e "${GREEN}[OK] Sistema actualizado${NC}"

# Instalar MariaDB
echo -e "${BLUE}[INFO] Instalando MariaDB...${NC}"
sudo apt install mariadb-server mariadb-client python3-mysqldb -y
echo -e "${GREEN}[OK] MariaDB instalado${NC}"

# Configurar MariaDB
echo -e "${BLUE}[INFO] Configurando MariaDB...${NC}"
sudo mysql -e "CREATE USER IF NOT EXISTS 'rpi'@'localhost' IDENTIFIED BY 'fv';"
sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'rpi'@'localhost' WITH GRANT OPTION;"
sudo mysql -e "CREATE DATABASE IF NOT EXISTS control_solar;"
echo -e "${GREEN}[OK] MariaDB configurado${NC}"

# Importar BD si existe
if [ -f "$PVSQL_FILE" ]; then
    echo -e "${BLUE}[INFO] Importando base de datos...${NC}"
    sudo mysql control_solar < "$PVSQL_FILE"
    echo -e "${GREEN}[OK] Base de datos importada${NC}"
else
    echo -e "${YELLOW}[AVISO] PVControl+.sql no encontrado en $PVSQL_FILE, saltando importacion${NC}"
fi

# Instalar Apache + PHP 8.4 para Trixie
echo -e "${BLUE}[INFO] Instalando Apache + PHP 8.4...${NC}"
sudo apt install apache2 php8.4 php8.4-mysql libapache2-mod-php8.4 php8.4-zip -y
echo -e "${GREEN}[OK] Apache + PHP 8.4 instalados${NC}"

# CONFIGURACION ESPECIFICA PARA TRIXIE - Pagina Web PVControl+
echo -e "${BLUE}[INFO] Configurando pagina web PVControl+ para Trixie...${NC}"
sudo rm -rf /var/www/html
sudo ln -sf "$PVC_HOME/html" /var/www/html

# CONFIGURACION ESPECIFICA PARA TRIXIE - Permisos básicos para enlaces simbólicos
echo -e "${BLUE}[INFO] Configurando permisos básicos para Apache Trixie...${NC}"

# Dar permisos básicos al directorio home de pi para que Apache pueda acceder
sudo chmod 755 /home/pi

# Dar permisos básicos al directorio del proyecto
sudo chmod 755 "$PVC_HOME"
sudo chmod -R 755 "$PVC_HOME/html"

# Configurar Apache para permitir enlaces simbólicos
echo -e "${BLUE}[INFO] Configurando Apache para enlaces simbólicos...${NC}"

# Crear configuración específica para PVControl+
sudo tee /etc/apache2/conf-available/pvcontrol-enlaces.conf > /dev/null << EOF
# Configuración para permitir enlaces simbólicos a PVControl+
<Directory /home/pi/PVControl+/html>
    Options FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
EOF

# Habilitar la configuración
sudo a2enconf pvcontrol-enlaces

# Configurar el Virtual Host específicamente
echo -e "${BLUE}[INFO] Configurando Virtual Host para PVControl+...${NC}"
sudo tee /etc/apache2/sites-available/000-default.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html

    <Directory /var/www/html>
        Options FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOF

# Habilitar módulos necesarios
sudo a2enmod rewrite
sudo systemctl restart apache2

echo -e "${GREEN}[OK] Pagina web configurada para Trixie${NC}"

# Crear archivos de configuracion desde distribucion
echo -e "${BLUE}[INFO] Creando archivos de configuracion...${NC}"

# 1. Parametros_FV.py
if [ -f "$PARAM_FV_DIST" ] && [ ! -f "$PARAM_FV" ]; then
    cp "$PARAM_FV_DIST" "$PARAM_FV"
    echo -e "${GREEN}[OK] Parametros_FV.py creado${NC}"
else
    echo -e "${YELLOW}[AVISO] Parametros_FV_DIST.py no encontrado o Parametros_FV.py ya existe${NC}"
fi

# 2. /html/Parametros_Web.js
if [ -f "$PARAM_WEB_DIST" ] && [ ! -f "$PARAM_WEB" ]; then
    cp "$PARAM_WEB_DIST" "$PARAM_WEB"
    echo -e "${GREEN}[OK] html/Parametros_Web.js creado${NC}"
else
    echo -e "${YELLOW}[AVISO] html/Parametros_Web_DIST.js no encontrado o html/Parametros_Web.js ya existe${NC}"
fi

# 3. /html/version.inc
echo -e "${BLUE}[INFO] Creando archivo version.inc...${NC}"
sudo tee "$VERSION_INC" > /dev/null << 'EOF'
<?php
// Version de la web para la pagina de "relojes"
// SC = bat sin celdas, CC = bat con celdas, RD = sin bat
$version = "SC";

// Archivo por defecto que se carga al iniciar la web
$archivo_inicio = "fv.html";
?>
EOF
echo -e "${GREEN}[OK] html/version.inc creado${NC}"

# Instalar Mosquitto
echo -e "${BLUE}[INFO] Instalando Mosquitto...${NC}"
sudo apt install mosquitto mosquitto-clients -y
echo -e "${GREEN}[OK] Mosquitto instalado${NC}"

# Configurar Mosquitto
echo -e "${BLUE}[INFO] Configurando Mosquitto...${NC}"

# Crear la configuración de Mosquitto
sudo tee /etc/mosquitto/conf.d/default.conf > /dev/null << EOF
allow_anonymous false

# Puerto estándar MQTT 
listener 1883

# Puerto para WebSockets
listener 9001 0.0.0.0
protocol websockets
 
# Autenticación
password_file /etc/mosquitto/passwd_mosquitto
EOF

# Copiar el archivo de contraseñas a /etc/mosquitto/
echo -e "${BLUE}[INFO] Copiando archivo de contraseñas a /etc/mosquitto/...${NC}"
sudo cp /home/pi/PVControl+/passwd_mosquitto /etc/mosquitto/passwd_mosquitto

# Reiniciar Mosquitto para aplicar cambios
echo -e "${BLUE}[INFO] Reiniciando servicio Mosquitto...${NC}"
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto

# Verificar que Mosquitto está funcionando
if sudo systemctl is-active --quiet mosquitto; then
    echo -e "${GREEN}[OK] Mosquitto configurado y funcionando correctamente${NC}"
else
    echo -e "${RED}[ERROR] Problema al iniciar Mosquitto. Revisar logs: sudo journalctl -u mosquitto${NC}"
fi

# Instalar PHPMyAdmin
echo -e "${BLUE}[INFO] Instalando PHPMyAdmin...${NC}"
wget -q https://www.phpmyadmin.net/downloads/phpMyAdmin-latest-all-languages.zip -O /tmp/phpmyadmin.zip
unzip -q /tmp/phpmyadmin.zip -d /tmp/
sudo rm -rf /usr/share/phpmyadmin
sudo mv /tmp/phpMyAdmin-*-all-languages /usr/share/phpmyadmin
sudo chmod -R 0755 /usr/share/phpmyadmin
echo -e "${GREEN}[OK] PHPMyAdmin instalado${NC}"

# Configurar PHPMyAdmin
echo -e "${BLUE}[INFO] Configurando PHPMyAdmin...${NC}"

# Crear directorio util si no existe
mkdir -p "$PVC_HOME/util"

if [ -f "$PHPMA_CONF" ]; then
    echo -e "${GREEN}[OK] Archivo de configuracion encontrado${NC}"
else
    echo -e "${YELLOW}[AVISO] Creando configuracion de PHPMyAdmin...${NC}"
    sudo tee "$PHPMA_CONF" > /dev/null << 'EOF'
Alias /phpmyadmin /usr/share/phpmyadmin

<Directory /usr/share/phpmyadmin>
    Options FollowSymLinks
    DirectoryIndex index.php
    AllowOverride All
    Require all granted
</Directory>

<Directory /usr/share/phpmyadmin/config>
    Require all denied
</Directory>

<Directory /usr/share/phpmyadmin/setup>
    Require all denied
</Directory>
EOF
    echo -e "${GREEN}[OK] Archivo de configuracion creado${NC}"
fi

# Copiar y activar la configuracion
sudo cp "$PHPMA_CONF" /etc/apache2/conf-available/phpmyadmin-pvcontrol.conf
sudo a2enconf phpmyadmin-pvcontrol
echo -e "${GREEN}[OK] PHPMyAdmin configurado y activado${NC}"

# Crear directorio temporal para PHPMyAdmin
sudo mkdir -p /usr/share/phpmyadmin/tmp
sudo chown -R www-data:www-data /usr/share/phpmyadmin/tmp

sudo systemctl reload apache2
echo -e "${GREEN}[OK] Apache recargado${NC}"

# =============================================================================
# CONFIGURAR PHP 8.4 PARA BACKUPS  Max 200MB, 300seg
# =============================================================================
echo -e "${BLUE}[INFO] Configurando PHP 8.4 para backups grandes...${NC}"

PHP_INI="/etc/php/8.4/apache2/php.ini"

if [ -f "$PHP_INI" ]; then
    # Backup
    sudo cp "$PHP_INI" "${PHP_INI}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Modificar valores
    sudo sed -i "s/^\(;\s*\)\?upload_max_filesize.*/upload_max_filesize = 200M/" "$PHP_INI"
    sudo sed -i "s/^\(;\s*\)\?post_max_size.*/post_max_size = 210M/" "$PHP_INI"
    sudo sed -i "s/^\(;\s*\)\?memory_limit.*/memory_limit = 512M/" "$PHP_INI"
    sudo sed -i "s/^\(;\s*\)\?max_execution_time.*/max_execution_time = 300/" "$PHP_INI"
    sudo sed -i "s/^\(;\s*\)\?max_input_time.*/max_input_time = 300/" "$PHP_INI"
    
    echo -e "${GREEN}[OK] php.ini configurado${NC}"
    
    # Reiniciar Apache para aplicar cambios
    sudo systemctl restart apache2
    echo -e "${GREEN}[OK] Apache reiniciado con nueva configuración${NC}"
else
    echo -e "${YELLOW}[AVISO] php.ini de PHP 8.4 no encontrado${NC}"
    echo -e "${YELLOW}  La configuración de backups grandes puede no funcionar${NC}"
fi





# Crear enlaces en el escritorio
echo -e "${BLUE}[INFO] Creando enlaces en el escritorio...${NC}"

if [ -f "$CONFIG_INICIAL" ]; then
    ln -sf "$CONFIG_INICIAL" /home/pi/Desktop/PVControl_Configuracion_Inicial.py
    echo -e "${GREEN}[OK] Enlace PVControl_Configuracion_Inicial.py creado${NC}"
fi

if [ -f "$ARRANCAR_SERVICIOS" ]; then
    ln -sf "$ARRANCAR_SERVICIOS" /home/pi/Desktop/Arrancar_servicios_PVControl+.py
    echo -e "${GREEN}[OK] Enlace Arrancar_servicios_PVControl+.py creado${NC}"
fi

if [ -f "$PARAR_SERVICIOS" ]; then
    ln -sf "$PARAR_SERVICIOS" /home/pi/Desktop/Parar_Servicios_PVControl+.py
    echo -e "${GREEN}[OK] Enlace Parar_Servicios_PVControl+.py creado${NC}"
fi

if [ -f "$VER_PROGRAMAS" ]; then
    ln -sf "$VER_PROGRAMAS" /home/pi/Desktop/Ver_Programas_en_Ejecucion_PVControl+.sh
    echo -e "${GREEN}[OK] Enlace Ver_Programas_en_Ejecucion_PVControl+.sh creado${NC}"
fi

if [ -f "$HA_INSTALACION" ]; then
    ln -sf "$HA_INSTALACION" /home/pi/Desktop/PVControl_Instalacion_HomeAssistant.py
    echo -e "${GREEN}[OK] Enlace PVControl_Instalacion_HomeAssistant.py creado${NC}"
fi

# Configurar VNC Server automaticamente
echo -e "${BLUE}[INFO] Configurando VNC Server...${NC}"

# Verificar si VNC ya esta activado
if sudo raspi-config nonint get_vnc | grep -q "1"; then
    echo -e "${YELLOW}[AVISO] VNC no esta activado, activando...${NC}"
    
    # Instalar VNC server si no esta instalado
    if ! command -v vncserver &> /dev/null; then
        echo -e "${YELLOW}[AVISO] Instalando VNC Server...${NC}"
        sudo apt update
        sudo apt install realvnc-vnc-server -y
    fi

    # Habilitar VNC
    sudo raspi-config nonint do_vnc 0
    
    # Configurar VNC para iniciar automaticamente
    sudo systemctl enable vncserver-x11-serviced.service
    sudo systemctl start vncserver-x11-serviced.service
    
    # Configurar resolucion por defecto
    sudo raspi-config nonint do_resolution 2 16
    
    echo -e "${GREEN}[OK] VNC Server activado y configurado${NC}"
else
    echo -e "${GREEN}[OK] VNC ya estaba activado${NC}"
fi

# =================================================================
# CONFIGURACIÓN CENTRALIZADA DE PERMISOS TOTALES
# =================================================================

echo -e "${BLUE}[INFO] Estableciendo permisos TOTALES para acceso web...${NC}"

# Ejecutar script centralizado de permisos si existe
if [ -f "$PVC_HOME/instalacion_trixie/setup_permisos.sh" ]; then
    echo -e "${BLUE}[INFO] Ejecutando script centralizado de permisos...${NC}"
    chmod +x "$PVC_HOME/instalacion_trixie/setup_permisos.sh"
    "$PVC_HOME/instalacion_trixie/setup_permisos.sh"
else
    echo -e "${YELLOW}[AVISO] Script de permisos no encontrado, usando configuración básica TOTAL...${NC}"
    
    # Configuración básica de permisos totales
    sudo usermod -a -G pi www-data
    sudo usermod -a -G www-data pi
    sudo chown -R pi:pi "$PVC_HOME"
    sudo chmod -R 777 "$PVC_HOME"
    
    # Sudo ilimitado
    echo "www-data ALL=(pi) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/pvcontrol-total
    echo "pi ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/pi-total
    sudo chmod 440 /etc/sudoers.d/pvcontrol-total
    sudo chmod 440 /etc/sudoers.d/pi-total
    
    echo -e "${GREEN}[OK] Permisos básicos totales configurados${NC}"
fi

# Verificación final de la web
echo -e "${BLUE}[INFO] Realizando verificación final...${NC}"
sleep 2  # Dar tiempo a que Apache se estabilice

if curl -s -I http://localhost > /dev/null; then
    echo -e "${GREEN}[OK] Web funcionando correctamente${NC}"
    echo -e "${BLUE}Web disponible en: http://$IP_ADDRESS${NC}"
else
    echo -e "${YELLOW}[AVISO] La web podría tener problemas. Revisar: sudo tail -f /var/log/apache2/error.log${NC}"
fi

# Verificación de permisos web
echo -e "${BLUE}[INFO] Verificando permisos web...${NC}"
if sudo -u www-data ls -la "$PVC_HOME" > /dev/null 2>&1; then
    echo -e "${GREEN}[OK] Apache tiene acceso total a PVControl+${NC}"
else
    echo -e "${RED}[ERROR] Problema con los permisos de Apache${NC}"
fi

# Mostrar informacion de conexion
echo -e "${BLUE}VNC disponible en: $IP_ADDRESS${NC}"
echo -e "${BLUE}Usa VNC Viewer y conecta a: $IP_ADDRESS:0${NC}"

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}   STACK INSTALADO CORRECTAMENTE${NC}"
echo -e "${GREEN}=============================================${NC}"
echo -e "${BLUE}Archivos de configuracion creados:${NC}"
echo -e "${BLUE}- Parametros_FV.py${NC}"
echo -e "${BLUE}- html/Parametros_Web.js${NC}"
echo -e "${BLUE}- html/version.inc${NC}"
echo -e "${BLUE}Enlaces creados en el escritorio${NC}"
echo -e "${BLUE}Permisos TOTALES configurados para web${NC}"
echo -e "${BLUE}Web: http://$IP_ADDRESS${NC}"
echo -e "${BLUE}PHPMyAdmin: http://$IP_ADDRESS/phpmyadmin${NC}"
echo -e "${BLUE}Usuario BD: rpi | Contraseña: fv${NC}"