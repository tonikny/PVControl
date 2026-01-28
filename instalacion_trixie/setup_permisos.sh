#!/bin/bash
# Script de permisos TOTALES para PVControl+ en entorno interno
# OPTIMIZADO para máxima velocidad

# Colores
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   PERMISOS TOTALES PVControl+${NC}"
echo -e "${BLUE}     (Control equivalente a SSH)${NC}"
echo -e "${BLUE}     ⚡ VERSIÓN OPTIMIZADA ⚡${NC}"
echo -e "${BLUE}=========================================${NC}"

PVC_HOME="/home/pi/PVControl+"
APACHE_USER="www-data"
PI_USER="pi"
PI_GROUP="pi"

# Función para configurar usuarios y grupos
setup_users_groups() {
    echo -e "${BLUE}[1/6] Configurando usuarios y grupos...${NC}"
    
    # Agregar www-data al grupo pi para acceso compartido
    sudo usermod -a -G $PI_GROUP $APACHE_USER
    
    # Agregar pi al grupo www-data para máxima integración
    sudo usermod -a -G $APACHE_USER $PI_USER
    
    echo -e "${GREEN}[OK] Usuarios y grupos configurados${NC}"
}

# Función OPTIMIZADA para permisos totales
setup_full_permissions() {
    echo -e "${BLUE}[2/6] Estableciendo permisos totales (OPTIMIZADO)...${NC}"
    
    # ⚡ OPTIMIZACIÓN: Un solo comando chown recursivo
    sudo chown -R $PI_USER:$PI_GROUP "$PVC_HOME"
    
    # ⚡ OPTIMIZACIÓN: Usar chmod recursivo en lugar de find + exec
    # a+rwX = todos pueden leer+escribir, y ejecutar para directorios/archivos ya ejecutables
    sudo chmod -R a+rwX "$PVC_HOME"
    
    echo -e "${GREEN}[OK] Permisos totales establecidos (modo rápido)${NC}"
}

# Función para permisos de ejecución específicos
setup_full_execution() {
    echo -e "${BLUE}[3/6] Configurando ejecución total...${NC}"
    
    # ⚡ OPTIMIZACIÓN: Usar xargs para procesar en lotes (más rápido que -exec)
    # -print0 y xargs -0 manejan nombres de archivo con espacios correctamente
    
    # Scripts shell - permisos de ejecución total
    find "$PVC_HOME" -name "*.sh" -print0 | sudo xargs -0 chmod 777
    
    # Scripts Python - permisos de ejecución total  
    find "$PVC_HOME" -name "*.py" -print0 | sudo xargs -0 chmod 777
    
    # Archivo actualizar - permisos de ejecución
    find "$PVC_HOME" -name "actualizar" -print0 | sudo xargs -0 chmod 777
    
    echo -e "${GREEN}[OK] Permisos de ejecución configurados${NC}"
}

# Función para configuración sudo ILIMITADA
setup_unlimited_sudo() {
    echo -e "${BLUE}[4/6] Configurando sudo ILIMITADO...${NC}"
    
    # Configuración sudo COMPLETA - www-data puede hacer CUALQUIER COMA​NDO como pi
    sudo tee /etc/sudoers.d/pvcontrol-unlimited > /dev/null << 'EOF'
# PERMISOS TOTALES para PVControl+ - ENTORNO INTERNO
# www-data puede ejecutar cualquier comando como usuario pi sin contraseña
www-data ALL=(pi) NOPASSWD: ALL

# www-data también puede ejecutar como root si es necesario
www-data ALL=(root) NOPASSWD: ALL
EOF

    # Configuración para que pi también pueda ejecutar sin contraseña (consistencia)
    sudo tee /etc/sudoers.d/pi-nopasswd > /dev/null << 'EOF'
# Pi puede ejecutar cualquier comando sin contraseña
pi ALL=(ALL) NOPASSWD: ALL
EOF

    # Asegurar permisos seguros en los archivos sudoers
    sudo chmod 440 /etc/sudoers.d/pvcontrol-unlimited
    sudo chmod 440 /etc/sudoers.d/pi-nopasswd
    
    echo -e "${GREEN}[OK] Sudo ilimitado configurado${NC}"
}

# Función para permisos del sistema
setup_system_permissions() {
    echo -e "${BLUE}[5/6] Configurando permisos del sistema...${NC}"
    
    # Permisos para directorio home de pi (necesario para enlaces simbólicos)
    sudo chmod 755 /home/pi
    
    # Permisos básicos para /var/www (directorio por defecto de Apache)
    sudo chmod -R 755 /var/www
    sudo chown -R www-data:www-data /var/www
    
    echo -e "${GREEN}[OK] Permisos del sistema configurados${NC}"
}

# Función para configurar Apache para listar directorios
setup_apache_indexes() {
    echo -e "${BLUE}[6/6] Configurando Apache para listar directorios...${NC}"
    
    # Crear configuración específica para permitir listado de directorios
    # Incluye ambas rutas: la real y la del enlace simbólico
    sudo tee /etc/apache2/conf-available/pvcontrol-enlaces.conf > /dev/null << 'EOF'
# Configuración para permitir enlaces simbólicos y listado de directorios en PVControl+
# Ruta real donde están los archivos
<Directory /home/pi/PVControl+/html>
    Options +Indexes +FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>

# Directorio de configuraciones (ruta real)
<Directory /home/pi/PVControl+/html/configuraciones>
    Options +Indexes +FollowSymLinks
    IndexOptions FancyIndexing VersionSort NameWidth=* HTMLTable Charset=UTF-8
    AllowOverride All
    Require all granted
</Directory>

# Directorio de configuraciones (ruta del enlace simbólico)
<Directory /var/www/html/configuraciones>
    Options +Indexes +FollowSymLinks
    IndexOptions FancyIndexing VersionSort NameWidth=* HTMLTable Charset=UTF-8
    AllowOverride All
    Require all granted
</Directory>
EOF

    # Habilitar la configuración en Apache
    sudo a2enconf pvcontrol-enlaces
    
    # Recargar Apache para aplicar cambios
    sudo systemctl reload apache2
    
    echo -e "${GREEN}[OK] Listado de directorios configurado en Apache${NC}"
}

# Función de verificación rápida
verify_quick_access() {
    echo -e "${BLUE}[INFO] Verificación rápida de acceso...${NC}"
    
    # Verificación básica de que Apache puede acceder
    if sudo -u $APACHE_USER ls -la "$PVC_HOME" > /dev/null 2>&1; then
        echo -e "${GREEN}[OK] Apache tiene acceso básico a PVControl+${NC}"
    else
        echo -e "${RED}[ERROR] Problema de acceso básico${NC}"
    fi
}

# Función principal
main() {
    echo -e "${BLUE}Iniciando configuración de permisos...${NC}"
    echo -e "${YELLOW}⚡ Modo optimizado activado ⚡${NC}"
    
    setup_users_groups
    setup_full_permissions
    setup_full_execution
    setup_unlimited_sudo
    setup_system_permissions
    setup_apache_indexes
    verify_quick_access
    
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}   PERMISOS TOTALES CONFIGURADOS${NC}"
    echo -e "${GREEN}         ⚡ OPTIMIZACIÓN ACTIVADA ⚡${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${BLUE}● Apache (www-data) tiene control TOTAL${NC}"
    echo -e "${BLUE}● Listado de directorios ACTIVADO${NC}"
    echo -e "${BLUE}● Permisos 777/666 en archivos y carpetas${NC}"
    echo -e "${BLUE}● Sudo ilimitado para www-data${NC}"
    echo -e "${BLUE}● Equivalente a conexión SSH completa${NC}"
    echo -e "${YELLOW}● ADVERTENCIA: Solo para redes internas${NC}"
    echo -e "${GREEN}● RENDIMIENTO: Configuración optimizada${NC}"
}

# Ejecutar función principal
main