#!/bin/bash
# Script de configuración de permisos para PVControl+

# Colores
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   CONFIGURACIÓN DE PERMISOS - PVControl+${NC}"
echo -e "${BLUE}=========================================${NC}"

# Variables principales
PVC_HOME="/home/pi/PVControl+"
APACHE_USER="www-data"
PI_USER="pi"
PI_GROUP="pi"

# ============ FUNCIONES PRINCIPALES ============

configurar_usuarios_grupos() {
    echo -e "${BLUE}[1/4] Configurando usuarios y grupos...${NC}"
    
    # Asegurar que www-data está en grupo pi para acceso compartido
    sudo usermod -a -G "$PI_GROUP" "$APACHE_USER" 2>/dev/null || true
    
    echo -e "${GREEN}✓ Usuarios y grupos configurados${NC}"
}

configurar_permisos_completos() {
    echo -e "${BLUE}[2/4] Configurando permisos del sistema...${NC}"
    
    # 1. Propietario consistente para toda la estructura
    echo -e "${YELLOW}Estableciendo propietario pi:pi...${NC}"
    sudo chown -R "$PI_USER:$PI_GROUP" "$PVC_HOME"
    
    # 2. PERMISOS COMPLETOS para toda la estructura
    echo -e "${YELLOW}Aplicando permisos 777/666...${NC}"
    
    # Directorios: rwxrwxrwx (777) - Acceso completo
    sudo find "$PVC_HOME" -type d -exec chmod 777 {} \; 2>/dev/null
    
    # Archivos: rw-rw-rw- (666) - Lectura/escritura para todos
    sudo find "$PVC_HOME" -type f -exec chmod 666 {} \; 2>/dev/null
    
    # 3. Scripts ejecutables: permisos especiales
    echo -e "${YELLOW}Configurando scripts ejecutables...${NC}"
    
    # Scripts Python: ejecutables para todos
    sudo find "$PVC_HOME" -name "*.py" -type f -exec chmod 777 {} \; 2>/dev/null
    
    # Scripts shell: ejecutables para todos
    sudo find "$PVC_HOME" -name "*.sh" -type f -exec chmod 777 {} \; 2>/dev/null
    
    # Archivo 'actualizar' si existe (pestaña web de actualización)
    [ -f "${PVC_HOME}/actualizar" ] && sudo chmod 777 "${PVC_HOME}/actualizar"
    
    # Entorno virtual: permisos completos
    [ -d "${PVC_HOME}/env" ] && sudo chmod -R 777 "${PVC_HOME}/env" 2>/dev/null
    
    echo -e "${GREEN}✓ Permisos del sistema configurados${NC}"
}

configurar_apache_limpio() {
    echo -e "${BLUE}[3/4] Configurando Apache (configuración limpia)...${NC}"
    
    # 1. Configuración de Apache, todo en archivo de configuración
    sudo tee /etc/apache2/conf-available/pvcontrol-limpio.conf > /dev/null << 'EOF'
# CONFIGURACIÓN LIMPIA PVControl+ - Todo en Apache

# Alias principal para acceder a toda la estructura
Alias /pvcontrol "/home/pi/PVControl+"

# ========= CONFIGURACIÓN PARA /pvcontrol (LISTADO) =========
# Cuando se accede a /pvcontrol/ o sus subcarpetas
<Directory "/home/pi/PVControl+">
    Options +Indexes +FollowSymLinks +MultiViews
    AllowOverride None
    Require all granted
    
    # Para /pvcontrol/* SIEMPRE mostrar listado
    # Esto incluye /pvcontrol/html/
    DirectoryIndex disabled
</Directory>

# ========= CONFIGURACIÓN PARA DOCUMENTROOT (SITIO WEB) =========
# Cuando se accede directamente (http://ip_raspberry/)
<Directory "/home/pi/PVControl+/html">
    Options FollowSymLinks MultiViews
    AllowOverride None
    Require all granted
    
    # Archivos índice normales para el sitio web
    DirectoryIndex index.html index.php
</Directory>

# ========= CONFIGURACIÓN ESPECÍFICA PARA /pvcontrol/html =========
# Override: cuando se accede a /pvcontrol/html/, forzar listado
<Location "/pvcontrol/html">
    # Forzar que se muestre listado incluso si hay index.html
    DirectoryIndex disabled
    Options +Indexes
</Location>

# Habilitar listado de directorios
<IfModule mod_autoindex.c>
    IndexOptions FancyIndexing NameWidth=* HTMLTable
</IfModule>
EOF
    
    # 2. Eliminar configuraciones anteriores si existen
    sudo rm -f /etc/apache2/conf-enabled/pvcontrol-*.conf 2>/dev/null
    
    # 3. Habilitar configuración limpia
    sudo a2enconf pvcontrol-limpio
    
    # 4. Habilitar módulos necesarios
    sudo a2enmod autoindex
    sudo a2enmod rewrite
    sudo a2enmod headers
    
    # 5. Asegurar enlace simbólico del DocumentRoot
    sudo rm -f /var/www/html
    sudo ln -sf "${PVC_HOME}/html" /var/www/html
    
    # 6. Permisos para el directorio /home/pi
    sudo chmod 755 /home/pi
    
    # 7. Recargar Apache
    sudo systemctl reload apache2
    
    echo -e "${GREEN}✓ Apache configurado (configuración limpia, sin .htaccess)${NC}"
}
configurar_permisos_sudo_basico() {
    echo -e "${BLUE}[4/4] Configurando permisos sudo básicos...${NC}"
    
    sudo mkdir -p /etc/sudoers.d
    
    # Configuración limpia de sudo
    sudo tee /etc/sudoers.d/pvcontrol-limpio > /dev/null << 'EOF'
# PERMISOS SUDO LIMPIOS - PVControl+

# Permisos básicos para desarrollo web
www-data ALL=(pi) NOPASSWD: ALL

# Control de Apache
www-data ALL=(root) NOPASSWD: /bin/systemctl reload apache2
www-data ALL=(root) NOPASSWD: /bin/systemctl restart apache2

# Usuario pi para desarrollo
pi ALL=(ALL) NOPASSWD: ALL
EOF
    
    sudo chmod 440 /etc/sudoers.d/pvcontrol-limpio
    
    echo -e "${GREEN}✓ Permisos sudo básicos configurados${NC}"
}

# ============ EJECUCIÓN PRINCIPAL ============

main() {
    echo -e "${YELLOW}Iniciando configuración de permisos PVControl+...${NC}"
    echo ""
    
    # Verificar que la carpeta existe
    if [ ! -d "$PVC_HOME" ]; then
        echo -e "${RED}ERROR: No se encuentra $PVC_HOME${NC}"
        echo -e "${YELLOW}Por favor, clona primero el repositorio de PVControl+${NC}"
        exit 1
    fi
    
    # Eliminar .htaccess de pruebas anteriores si existen
    echo -e "${YELLOW}Limpiando archivos .htaccess de pruebas anteriores...${NC}"
    sudo find "$PVC_HOME" -name ".htaccess" -delete 2>/dev/null
    echo -e "${GREEN}✓ Archivos .htaccess eliminados${NC}"
    
    # Ejecutar configuraciones
    configurar_usuarios_grupos
    configurar_permisos_completos
    configurar_apache_limpio
    configurar_permisos_sudo_basico
    
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}     CONFIGURACIÓN LIMPIA DE PERMISOS COMPLETADA         ${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # ============ RESUMEN ============
    echo -e "${BLUE}📋 CONFIGURACIÓN APLICADA:${NC}"
    echo -e "${BLUE}──────────────────────────────────────────────────────${NC}"
    echo ""
    
    echo -e "${GREEN}✅ PERMISOS:${NC}"
    echo "   • Sistema de archivos: 777/666"
    echo "   • Scripts ejecutables: 777"
    echo "   • Propietario: pi:pi"
    echo ""
    
    echo -e "${GREEN}✅ APACHE (configuración limpia):${NC}"
    echo "   • Todo configurado en: /etc/apache2/conf-available/pvcontrol-limpio.conf"
    echo "   • Alias principal: /pvcontrol/ → ${PVC_HOME}/"
    echo "   • Listado habilitado con Options +Indexes"
    echo ""
    
    # ============ ACCESOS WEB ============
    IP_ADDRESS=$(hostname -I | awk '{print $1}' | head -1)
    
    echo -e "${GREEN}🌐 ACCESO WEB DISPONIBLE:${NC}"
    echo -e "${BLUE}──────────────────────────────────────────────────────${NC}"
    echo ""
    
    echo -e "${YELLOW}📁 ACCESO A TODA LA ESTRUCTURA:${NC}"
    if [ -n "$IP_ADDRESS" ]; then
        echo "  • http://${IP_ADDRESS}/pvcontrol/"
    else
        echo "  • http://localhost/pvcontrol/"
    fi
    echo "    (Navega a html/, backBD/, etc.)"
    echo ""
    
    echo -e "${YELLOW}🚀 INTERFAZ WEB PRINCIPAL:${NC}"
    if [ -n "$IP_ADDRESS" ]; then
        echo "  • http://${IP_ADDRESS}/"
    else
        echo "  • http://localhost/"
    fi
    echo ""
        
    # ============ ADVERTENCIA ============
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                  ADVERTENCIA DE SEGURIDAD                 ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  CONFIGURACIÓN PERMISIVA - SOLO DESARROLLO SEGURO ⚠️${NC}"
    echo ""
    echo -e "${RED}Características:${NC}"
    echo "   • Permisos 777/666 en todos los archivos"
    echo "   • Listado público de directorios"
    echo "   • Acceso web a estructura completa"
    echo ""
    
    echo -e "${RED}🔒 RESTRICCIONES:${NC}"
    echo "   ✅ Solo redes privadas"
    echo "   ✅ Nunca exponer a Internet"
    echo "   ✅ Solo personal autorizado"
    echo ""
    
    echo -e "${BLUE}──────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Configuración limpia finalizada: $(date)${NC}"
    echo -e "${BLUE}──────────────────────────────────────────────────────${NC}"
    echo ""
}

# Ejecutar
main