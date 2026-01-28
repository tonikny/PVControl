#!/bin/bash
# Script para reparar permisos de PVControl+

echo "Reparando permisos para PVControl+..."

# Directorio principal
INSTALL_DIR="/home/pi/PVControl+"

# Asegurar que www-data está en el grupo pi
sudo usermod -a -G pi www-data

# Configurar permisos
sudo chown -R pi:pi "$INSTALL_DIR"
sudo chmod -R 775 "$INSTALL_DIR"

# Set GUID en directorios para que nuevos archivos hereden el grupo
find "$INSTALL_DIR" -type d -exec sudo chmod g+s {} \;

# Scripts ejecutables
find "$INSTALL_DIR" -name "*.sh" -exec sudo chmod 775 {} \;
find "$INSTALL_DIR" -name "*.py" -exec sudo chmod 775 {} \;

# Permisos específicos para directorios críticos
if [ -d "/var/www/html" ]; then
    sudo chown -R pi:www-data /var/www/html
    sudo chmod -R 775 /var/www/html
    find /var/www/html -type d -exec sudo chmod 2775 {} \;
fi

# Para MariaDB - asegurar permisos de backup
if [ -d "/var/lib/mysql" ]; then
    sudo chmod 755 /var/lib/mysql
    sudo usermod -a -G mysql pi
fi

echo "Permisos reparados. Reinicia Apache para aplicar cambios:"
echo "sudo systemctl restart apache2"