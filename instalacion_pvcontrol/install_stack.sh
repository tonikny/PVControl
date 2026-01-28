#!/bin/bash
# install_stack.sh - Instalacion de servicios para PVControl+
# Compatible con: 
#   - Raspberry Pi con Trixie (64-bit)
#   - PC/Netbook con Bookworm (32-bit o 64-bit)
#   - PC/Netbook con Trixie (64-bit)

# Colores
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   INSTALANDO STACK PARA PVControl+${NC}"
echo -e "${BLUE}=========================================${NC}"

# Variables desde el script principal
ES_RASPBERRY=${ES_RASPBERRY:-true}
ES_TRIXIE=${ES_TRIXIE:-true}
ES_BOOKWORM=${ES_BOOKWORM:-false}
SO=${SO:-"Desconocido"}
ARCH=${ARCH:-"desconocida"}

# Definir rutas absolutas
PVC_HOME="/home/pi/PVControl+"
PVSQL_FILE="$PVC_HOME/PVControl+.sql"
PARAM_FV_DIST="$PVC_HOME/Parametros_FV_DIST.py"
PARAM_FV="$PVC_HOME/Parametros_FV.py"
PARAM_WEB_DIST="$PVC_HOME/html/Parametros_Web_DIST.js"
PARAM_WEB="$PVC_HOME/html/Parametros_Web.js"
VERSION_INC="$PVC_HOME/html/version.inc"
PHPMA_CONF="$PVC_HOME/util/phpmyadmin.conf"
ARRANCAR_SERVICIOS="$PVC_HOME/Arrancar_servicios_PVControl+.py"
PARAR_SERVICIOS="$PVC_HOME/Parar_Servicios_PVControl+.py"
VER_PROGRAMAS="$PVC_HOME/Ver_Programas_en_Ejecucion_PVControl+.sh"

# Obtener IP para mostrar al final
get_ip() {
    if command -v hostname &> /dev/null; then
        local ip=$(hostname -I 2>/dev/null | awk '{print $1}')
        if [ -n "$ip" ]; then
            echo "$ip"
        else
            echo "localhost"
        fi
    else
        echo "localhost"
    fi
}

IP_ADDRESS=$(get_ip)

# Función para crear accesos directos web en el escritorio
crear_accesos_directos_web() {
    echo -e "${BLUE}Creando accesos directos en el escritorio...${NC}"
    
    # Crear directorio Desktop si no existe
    mkdir -p /home/pi/Desktop
    
    # Eliminar accesos antiguos si existen
    echo -e "${BLUE}Preparando escritorio...${NC}"
    rm -f /home/pi/Desktop/PVControl+.desktop \
          /home/pi/Desktop/Configuracion_PVControl+.desktop \
          /home/pi/Desktop/Arrancar_servicios.desktop \
          /home/pi/Desktop/Parar_servicios.desktop \
          /home/pi/Desktop/Ver_programas.desktop
    
    # 1. Acceso directo a PVControl+ Web
    echo -e "${BLUE}Creando acceso web principal...${NC}"
    cat > /home/pi/Desktop/PVControl+.desktop << 'EOF'
[Desktop Entry]
Name=PVControl+ Web
Exec=xdg-open http://localhost
Icon=web-browser
Terminal=false
Type=Application
EOF
    chmod 755 /home/pi/Desktop/PVControl+.desktop
    echo -e "${GREEN}✓ PVControl+ Web${NC}"
    
    # 2. Acceso directo a Configuración
    echo -e "${BLUE}Creando acceso a configuración...${NC}"
    cat > /home/pi/Desktop/Configuracion_PVControl+.desktop << 'EOF'
[Desktop Entry]
Name=Configuración PVControl+
Exec=xdg-open http://localhost/configuracion.html
Icon=preferences-system
Terminal=false
Type=Application
EOF
    chmod 755 /home/pi/Desktop/Configuracion_PVControl+.desktop
    echo -e "${GREEN}✓ Configuración${NC}"
    
    # 3. Acceso para Arrancar Servicios
    echo -e "${BLUE}Creando acceso para arrancar servicios...${NC}"
    cat > /home/pi/Desktop/Arrancar_servicios.desktop << 'EOF'
[Desktop Entry]
Name=Arrancar Servicios
Exec=lxterminal -e "python3 /home/pi/PVControl+/Arrancar_servicios_PVControl+.py && read -p 'Presiona Enter...'"
Icon=system-run
Terminal=false
Type=Application
EOF
    chmod 755 /home/pi/Desktop/Arrancar_servicios.desktop
    echo -e "${GREEN}✓ Arrancar Servicios${NC}"
    
    # 4. Acceso para Parar Servicios
    echo -e "${BLUE}Creando acceso para parar servicios...${NC}"
    cat > /home/pi/Desktop/Parar_servicios.desktop << 'EOF'
[Desktop Entry]
Name=Parar Servicios
Exec=lxterminal -e "python3 /home/pi/PVControl+/Parar_Servicios_PVControl+.py && read -p 'Presiona Enter...'"
Icon=system-shutdown
Terminal=false
Type=Application
EOF
    chmod 755 /home/pi/Desktop/Parar_servicios.desktop
    echo -e "${GREEN}✓ Parar Servicios${NC}"
    
    # 5. Acceso para Ver Programas
    echo -e "${BLUE}Creando acceso para ver programas...${NC}"
    cat > /home/pi/Desktop/Ver_programas.desktop << 'EOF'
[Desktop Entry]
Name=Ver Programas
Exec=lxterminal -e "/home/pi/PVControl+/Ver_Programas_en_Ejecucion_PVControl+.sh && read -p 'Presiona Enter...'"
Icon=utilities-system-monitor
Terminal=false
Type=Application
EOF
    chmod 755 /home/pi/Desktop/Ver_programas.desktop
    echo -e "${GREEN}✓ Ver Programas${NC}"
    
    # Forzar actualización del escritorio (método simple)
    echo -e "${BLUE}Actualizando vista del escritorio...${NC}"
    sleep 1
    
    echo -e "${GREEN}✓ Accesos creados${NC}"
    echo -e "${YELLOW}Si aparece diálogo, haga clic derecho → Propiedades → Permisos → Marcar 'Permitir ejecutar'${NC}"
}

# Función para verificar y configurar grupos del usuario pi
setup_user_groups() {
    echo -e "${BLUE}Configurando grupos del usuario pi...${NC}"
    echo -e "${YELLOW}Grupos necesarios: sudo, adm, dialout${NC}"
    
    # Variable para trackear si se hicieron cambios
    GRUPOS_MODIFICADOS=false
    
    # 1. Grupo SUDO (permisos administrativos)
    if ! groups pi | grep -q "\bsudo\b"; then
        echo -e "${YELLOW}Agregando pi al grupo sudo...${NC}"
        sudo usermod -a -G sudo pi
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ pi agregado a grupo sudo${NC}"
            GRUPOS_MODIFICADOS=true
        else
            echo -e "${RED}✗ Error agregando pi a grupo sudo${NC}"
        fi
    else
        echo -e "${GREEN}✓ pi ya está en grupo sudo${NC}"
    fi
    
    # 2. Grupo ADM (acceso a logs del sistema)
    if ! groups pi | grep -q "\badm\b"; then
        echo -e "${YELLOW}Agregando pi al grupo adm...${NC}"
        sudo usermod -a -G adm pi
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ pi agregado a grupo adm${NC}"
            GRUPOS_MODIFICADOS=true
        else
            echo -e "${YELLOW}⚠ No se pudo agregar pi a grupo adm${NC}"
        fi
    else
        echo -e "${GREEN}✓ pi ya está en grupo adm${NC}"
    fi
    
    # 3. Grupo DIALOUT (acceso a puertos serie)
    if ! groups pi | grep -q "\bdialout\b"; then
        echo -e "${YELLOW}Agregando pi al grupo dialout...${NC}"
        sudo usermod -a -G dialout pi
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ pi agregado a grupo dialout${NC}"
            GRUPOS_MODIFICADOS=true
        else
            echo -e "${YELLOW}⚠ No se pudo agregar pi a grupo dialout${NC}"
        fi
    else
        echo -e "${GREEN}✓ pi ya está en grupo dialout${NC}"
    fi
    
    # 4. Grupo WWW-DATA (compartir con Apache)
    if id www-data &>/dev/null; then
        if ! groups pi | grep -q "\bwww-data\b"; then
            echo -e "${YELLOW}Agregando pi al grupo www-data...${NC}"
            sudo usermod -a -G www-data pi
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ pi agregado a grupo www-data${NC}"
                GRUPOS_MODIFICADOS=true
            fi
        else
            echo -e "${GREEN}✓ pi ya está en grupo www-data${NC}"
        fi
    fi
    
    # Mostrar grupos actuales
    echo -e "${BLUE}Grupos actuales de pi:${NC}"
    groups pi
    
    # Advertencia si se hicieron cambios
    if [ "$GRUPOS_MODIFICADOS" = true ]; then
        echo -e "${YELLOW}⚠ Se modificaron grupos. Puede requerir reiniciar sesión${NC}"
        echo -e "${YELLOW}Para aplicar inmediatamente: newgrp sudo${NC}"
    fi
}

# Función para detectar version de PHP disponible
detectar_php_version() {
    echo -e "${BLUE}Detectando version de PHP disponible...${NC}"
    
    # Para Trixie (PC o Raspberry Pi)
    if [ "$ES_TRIXIE" = true ]; then
        if apt-cache show php8.4 &> /dev/null; then
            PHP_VERSION="php8.4"
            PHP_MODULE="php8.4"
            echo -e "${GREEN}Trixie detectado - usando PHP 8.4${NC}"
        elif apt-cache show php8.3 &> /dev/null; then
            PHP_VERSION="php8.3"
            PHP_MODULE="php8.3"
            echo -e "${YELLOW}Trixie con PHP 8.3 (fallback)${NC}"
        else
            PHP_VERSION="php8.2"
            PHP_MODULE="php8.2"
            echo -e "${YELLOW}Trixie con PHP 8.2 (ultimo recurso)${NC}"
        fi
    
    # Para Bookworm (siempre PC)
    elif [ "$ES_BOOKWORM" = true ]; then
        if apt-cache show php8.2 &> /dev/null; then
            PHP_VERSION="php8.2"
            PHP_MODULE="php8.2"
            echo -e "${GREEN}Bookworm detectado - usando PHP 8.2${NC}"
        elif apt-cache show php8.1 &> /dev/null; then
            PHP_VERSION="php8.1"
            PHP_MODULE="php8.1"
            echo -e "${YELLOW}Bookworm con PHP 8.1 (fallback)${NC}"
        else
            PHP_VERSION="php"
            PHP_MODULE="php"
            echo -e "${YELLOW}Bookworm con PHP default${NC}"
        fi
    
    # Por defecto
    else
        PHP_VERSION="php"
        PHP_MODULE="php"
        echo -e "${YELLOW}Usando PHP por defecto del sistema${NC}"
    fi
    
    echo -e "${BLUE}Version PHP seleccionada: $PHP_VERSION${NC}"
}

# Función para detectar y configurar zona horaria
configurar_zona_horaria() {
    echo -e "${BLUE}Configurando zona horaria para PHP...${NC}"
    
    # 1. Detectar zona horaria del sistema
    if [ -f /etc/timezone ]; then
        SYSTEM_TIMEZONE=$(cat /etc/timezone)
    elif command -v timedatectl &> /dev/null; then
        SYSTEM_TIMEZONE=$(timedatectl show --property=Timezone --value)
    else
        SYSTEM_TIMEZONE="UTC"
    fi
    
    # Validar que no esté vacía
    [ -z "$SYSTEM_TIMEZONE" ] && SYSTEM_TIMEZONE="UTC"
    
    echo -e "${GREEN}Zona horaria detectada: $SYSTEM_TIMEZONE${NC}"
    
    # 2. Función para configurar un archivo php.ini específico
    configurar_php_ini() {
        local php_ini="$1"
        
        if [ ! -f "$php_ini" ]; then
            echo -e "${YELLOW}Archivo no encontrado: $php_ini${NC}"
            return 1
        fi
        
        echo -e "${BLUE}Procesando: $(basename $(dirname $(dirname "$php_ini")))/$(basename $(dirname "$php_ini"))/php.ini${NC}"
        
        # Crear backup
        if [ ! -f "${php_ini}.backup-timezone" ]; then
            sudo cp "$php_ini" "${php_ini}.backup-timezone"
        fi
        
        # Crear archivo temporal con awk (evita problemas con caracteres especiales)
        local temp_file=$(mktemp)
        
        sudo awk -v tz="$SYSTEM_TIMEZONE" '
            # Buscar línea [Date]
            /^\[Date\]/ {
                print $0
                # Insertar date.timezone después de [Date]
                found_date_section = 1
                date_section_printed = 1
                next
            }
            
            # Si estamos en sección [Date] y encontramos la primera opción después del encabezado
            found_date_section && /^[a-zA-Z]/ && !tz_set_in_date {
                print "date.timezone = \"" tz "\""
                tz_set_in_date = 1
                found_date_section = 0
            }
            
            # Reemplazar date.timezone existente (comentada o no)
            /^[;]*\s*date\.timezone/ {
                print "date.timezone = \"" tz "\""
                tz_set = 1
                next
            }
            
            # Imprimir línea normal
            { print }
            
            # Al final del archivo, si no se encontró [Date] ni date.timezone
            END {
                if (!date_section_printed && !tz_set && !tz_set_in_date) {
                    print "\n[Date]"
                    print "date.timezone = \"" tz "\""
                } else if (date_section_printed && !tz_set && !tz_set_in_date) {
                    # Si se imprimió [Date] pero no se agregó date.timezone
                    print "date.timezone = \"" tz "\""
                }
            }
        ' "$php_ini" > "$temp_file"
        
        # Verificar si hay cambios y reemplazar
        if ! sudo diff -q "$php_ini" "$temp_file" > /dev/null 2>&1; then
            sudo mv "$temp_file" "$php_ini"
            sudo chmod 644 "$php_ini"
            echo -e "${GREEN}✓ Zona horaria configurada${NC}"
            
            # Verificar que se configuró
            if sudo grep -q "date.timezone = \"$SYSTEM_TIMEZONE\"" "$php_ini"; then
                echo -e "${GREEN}  Verificado: $SYSTEM_TIMEZONE${NC}"
            fi
        else
            sudo rm "$temp_file"
            echo -e "${YELLOW}⚠ Ya estaba configurada${NC}"
        fi
    }
    
    # 3. Buscar y configurar TODOS los archivos php.ini
    echo -e "${BLUE}Buscando archivos php.ini...${NC}"
    
    # Buscar en todas las versiones de PHP
    for php_dir in /etc/php/*; do
        if [ -d "$php_dir" ]; then
            for ini_type in apache2 cli fpm; do
                local php_ini="$php_dir/$ini_type/php.ini"
                if [ -f "$php_ini" ]; then
                    configurar_php_ini "$php_ini"
                fi
            done
        fi
    done
    
    # Buscar también en ubicaciones específicas para la versión detectada
    if [ -n "$PHP_VERSION" ] && [ "$PHP_VERSION" != "php" ]; then
        local php_num=$(echo "$PHP_VERSION" | sed 's/php//')
        for ini_type in apache2 cli fpm; do
            local specific_ini="/etc/php/$php_num/$ini_type/php.ini"
            if [ -f "$specific_ini" ]; then
                configurar_php_ini "$specific_ini"
            fi
        done
    fi
    
    # 4. Configurar zona horaria del sistema
    echo -e "${BLUE}Configurando zona horaria del sistema...${NC}"
    
    # Configurar /etc/timezone
    echo "$SYSTEM_TIMEZONE" | sudo tee /etc/timezone > /dev/null
    echo -e "${GREEN}✓ /etc/timezone configurado${NC}"
    
    # Configurar /etc/localtime si la zona existe
    if [ -f "/usr/share/zoneinfo/$SYSTEM_TIMEZONE" ]; then
        sudo ln -sf "/usr/share/zoneinfo/$SYSTEM_TIMEZONE" /etc/localtime
        echo -e "${GREEN}✓ /etc/localtime configurado${NC}"
    else
        echo -e "${YELLOW}⚠ Zona horaria $SYSTEM_TIMEZONE no encontrada en /usr/share/zoneinfo/${NC}"
        echo -e "${YELLOW}  Listando zonas disponibles similares...${NC}"
        find /usr/share/zoneinfo -type f -name "*$(echo "$SYSTEM_TIMEZONE" | sed 's/.*\///')*" 2>/dev/null | head -5
    fi
    
    # 5. Verificar configuración
    echo -e "${BLUE}Verificando configuración...${NC}"
    
    # Reiniciar Apache para aplicar cambios
    sudo systemctl restart apache2 2>/dev/null || true
    
    # Esperar un momento
    sleep 2
    
    # Probar con diferentes versiones de PHP
    for php_cmd in php "$PHP_VERSION"; do
        if command -v "$php_cmd" &> /dev/null; then
            local php_tz=$("$php_cmd" -r "echo ini_get('date.timezone');" 2>/dev/null || echo "ERROR")
            echo -e "${BLUE}$php_cmd zona horaria: $php_tz${NC}"
            
            if [ "$php_tz" = "$SYSTEM_TIMEZONE" ]; then
                echo -e "${GREEN}✓ $php_cmd configurado correctamente${NC}"
            elif [ "$php_tz" = "ERROR" ]; then
                echo -e "${YELLOW}⚠ $php_cmd no pudo leer configuración${NC}"
            else
                echo -e "${YELLOW}⚠ $php_cmd muestra: $php_tz (esperado: $SYSTEM_TIMEZONE)${NC}"
            fi
        fi
    done
    
    # Mostrar información del sistema
    if command -v timedatectl &> /dev/null; then
        echo -e "${BLUE}Sistema zona horaria: $(timedatectl show --property=Timezone --value)${NC}"
    fi
    
    echo -e "${GREEN}✓ Configuración de zona horaria completada${NC}"
}

# Funcion para instalar paquetes
instalar_paquete() {
    local paquete=$1
    local descripcion=$2
    
    echo -e "${BLUE}Instalando $descripcion...${NC}"
    if sudo apt install -y "$paquete"; then
        echo -e "${GREEN}$descripcion instalado${NC}"
        return 0
    else
        echo -e "${YELLOW}Error instalando $descripcion, intentando continuar...${NC}"
        return 1
    fi
}

# 1. ACTUALIZAR SISTEMA
echo -e "${BLUE}[1/16] Actualizando sistema...${NC}"
sudo apt update
sudo apt full-upgrade -y
echo -e "${GREEN}Sistema actualizado${NC}"

# 2. CONFIGURAR GRUPOS DEL USUARIO
echo -e "${BLUE}[2/16] Configurando grupos del usuario...${NC}"
setup_user_groups

# 3. DETECTAR VERSION DE PHP
detectar_php_version

# 4. PARA PC: INSTALAR HERRAMIENTAS BASICAS
if [ "$ES_RASPBERRY" = false ]; then
    echo -e "${BLUE}[3/16] Configurando PC/Netbook...${NC}"
    echo -e "${BLUE}Plataforma: PC con $SO ($ARCH)${NC}"
    
    # Herramientas basicas para cualquier PC
    BASIC_TOOLS="curl wget git htop net-tools"
    for tool in $BASIC_TOOLS; do
        if ! command -v "$tool" &> /dev/null; then
            instalar_paquete "$tool" "$tool"
        else
            echo -e "${GREEN}$tool ya instalado${NC}"
        fi
    done
    
    # Instalar Python completo si no esta
    if ! command -v python3 &> /dev/null; then
        instalar_paquete "python3" "Python 3"
        instalar_paquete "python3-pip" "pip para Python 3"
        instalar_paquete "python3-venv" "Virtual environments"
    else
        echo -e "${GREEN}Python ya instalado${NC}"
    fi
    
    # Instalar Geany (editor) - automatico para PC
    echo -e "${YELLOW}Instalando Geany (editor) para PC...${NC}"
    if ! command -v geany &> /dev/null; then
        instalar_paquete "geany" "Editor Geany"
        instalar_paquete "geany-plugins" "Plugins para Geany"
    fi
    
    # Herramientas graficas basicas
    instalar_paquete "lxterminal" "Terminal grafica ligera"
    instalar_paquete "pcmanfm" "Gestor de archivos ligero"
    
    # VNC Server - NO instalar automaticamente (opcional)
    echo -e "${YELLOW}VNC Server omitido (instala manualmente si es necesario)${NC}"
    echo -e "${YELLOW}Para instalar VNC manualmente: sudo apt install tigervnc-standalone-server${NC}"
    
    echo -e "${GREEN}Configuracion PC completada${NC}"
else
    echo -e "${BLUE}[3/16] Raspberry Pi detectada - usando configuracion optimizada${NC}"
fi

# 5. INSTALAR MARIADB
echo -e "${BLUE}[4/16] Instalando MariaDB...${NC}"
instalar_paquete "mariadb-server" "MariaDB Server"
instalar_paquete "mariadb-client" "MariaDB Client"
instalar_paquete "python3-mysqldb" "MySQL para Python 3"

# Configurar MariaDB
echo -e "${BLUE}Configurando MariaDB...${NC}"
sudo mysql -e "CREATE USER IF NOT EXISTS 'rpi'@'localhost' IDENTIFIED BY 'fv';" 2>/dev/null || true
sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'rpi'@'localhost' WITH GRANT OPTION;" 2>/dev/null || true
sudo mysql -e "CREATE DATABASE IF NOT EXISTS control_solar;" 2>/dev/null || true

# Importar BD si existe
if [ -f "$PVSQL_FILE" ]; then
    echo -e "${BLUE}Importando base de datos...${NC}"
    sudo mysql control_solar < "$PVSQL_FILE"
    echo -e "${GREEN}Base de datos importada${NC}"
else
    echo -e "${YELLOW}PVControl+.sql no encontrado, saltando importacion${NC}"
fi

# 6. INSTALAR APACHE
echo -e "${BLUE}[5/16] Instalando Apache...${NC}"
instalar_paquete "apache2" "Apache Web Server"

# 7. INSTALAR PHP Y MODULOS
echo -e "${BLUE}[6/16] Instalando PHP y modulos...${NC}"

# Lista de modulos PHP comunes
PHP_PACKAGES="$PHP_VERSION $PHP_VERSION-cli $PHP_VERSION-common $PHP_VERSION-mysql $PHP_VERSION-curl $PHP_VERSION-gd $PHP_VERSION-mbstring $PHP_VERSION-xml $PHP_VERSION-zip"

for pkg in $PHP_PACKAGES; do
    # Verificar si el paquete existe antes de instalarlo
    if apt-cache show "$pkg" &> /dev/null; then
        instalar_paquete "$pkg" "$pkg"
    else
        echo -e "${YELLOW}$pkg no disponible, omitiendo...${NC}"
    fi
done

# Instalar modulo PHP para Apache
if apt-cache show "libapache2-mod-$PHP_MODULE" &> /dev/null; then
    instalar_paquete "libapache2-mod-$PHP_MODULE" "Modulo Apache para $PHP_VERSION"
else
    # Intentar modulo generico
    instalar_paquete "libapache2-mod-php" "Modulo Apache para PHP"
fi

# 8. CONFIGURAR PAGINA WEB PVControl+
echo -e "${BLUE}[7/16] Configurando pagina web PVControl+...${NC}"
sudo rm -rf /var/www/html
sudo ln -sf "$PVC_HOME/html" /var/www/html

# Dar permisos basicos
sudo chmod 755 /home/pi
sudo chmod 755 "$PVC_HOME"
sudo chmod -R 755 "$PVC_HOME/html"

# Configurar Apache para permitir enlaces simbolicos
echo -e "${BLUE}Configurando Apache para enlaces simbolicos...${NC}"

sudo tee /etc/apache2/conf-available/pvcontrol-enlaces.conf > /dev/null << EOF
# Configuracion para permitir enlaces simbolicos a PVControl+
<Directory /home/pi/PVControl+/html>
    Options FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
EOF

sudo a2enconf pvcontrol-enlaces

# Configurar Virtual Host
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

# Habilitar modulos necesarios
sudo a2enmod rewrite
sudo systemctl restart apache2
echo -e "${GREEN}Pagina web configurada${NC}"

# 9. CREAR ARCHIVOS DE CONFIGURACION
echo -e "${BLUE}[8/16] Creando archivos de configuracion...${NC}"

# Parametros_FV.py
if [ -f "$PARAM_FV_DIST" ] && [ ! -f "$PARAM_FV" ]; then
    cp "$PARAM_FV_DIST" "$PARAM_FV"
    echo -e "${GREEN}Parametros_FV.py creado${NC}"
else
    echo -e "${YELLOW}Parametros_FV_DIST.py no encontrado o Parametros_FV.py ya existe${NC}"
fi

# html/Parametros_Web.js
if [ -f "$PARAM_WEB_DIST" ] && [ ! -f "$PARAM_WEB" ]; then
    cp "$PARAM_WEB_DIST" "$PARAM_WEB"
    echo -e "${GREEN}html/Parametros_Web.js creado${NC}"
else
    echo -e "${YELLOW}html/Parametros_Web_DIST.js no encontrado o html/Parametros_Web.js ya existe${NC}"
fi

# html/version.inc
echo -e "${BLUE}Creando archivo version.inc...${NC}"
sudo tee "$VERSION_INC" > /dev/null << 'EOF'
<?php
// Version de la web para la pagina de "relojes"
// SC = bat sin celdas, CC = bat con celdas, RD = sin bat
$version = "SC";

// Archivo por defecto que se carga al iniciar la web
$archivo_inicio = "fv.html";
?>
EOF
echo -e "${GREEN}html/version.inc creado${NC}"

# 10. INSTALAR MOSQUITTO
echo -e "${BLUE}[9/16] Instalando Mosquitto...${NC}"
instalar_paquete "mosquitto" "Mosquitto MQTT Broker"
instalar_paquete "mosquitto-clients" "Clientes Mosquitto"

# Configurar Mosquitto
echo -e "${BLUE}Configurando Mosquitto...${NC}"

sudo tee /etc/mosquitto/conf.d/default.conf > /dev/null << EOF
allow_anonymous false

# Puerto estandar MQTT 
listener 1883

# Puerto para WebSockets
listener 9001 0.0.0.0
protocol websockets
 
# Autenticacion
password_file /etc/mosquitto/passwd_mosquitto
EOF

# Copiar archivo de contrasenas
if [ -f "/home/pi/PVControl+/passwd_mosquitto" ]; then
    sudo cp "/home/pi/PVControl+/passwd_mosquitto" /etc/mosquitto/passwd_mosquitto
    echo -e "${GREEN}Archivo de contrasenas copiado${NC}"
else
    echo -e "${YELLOW}Archivo passwd_mosquitto no encontrado${NC}"
fi

# Reiniciar Mosquitto
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto

if sudo systemctl is-active --quiet mosquitto; then
    echo -e "${GREEN}Mosquitto funcionando correctamente${NC}"
else
    echo -e "${YELLOW}Problema al iniciar Mosquitto${NC}"
fi

# 11. INSTALAR PHPMYADMIN
echo -e "${BLUE}[10/16] Instalando PHPMyAdmin...${NC}"

# Crear directorio util si no existe
mkdir -p "$PVC_HOME/util"

# Descargar PHPMyAdmin
echo -e "${BLUE}Descargando PHPMyAdmin...${NC}"
wget -q https://www.phpmyadmin.net/downloads/phpMyAdmin-latest-all-languages.zip -O /tmp/phpmyadmin.zip
if [ $? -eq 0 ]; then
    unzip -q /tmp/phpmyadmin.zip -d /tmp/
    sudo rm -rf /usr/share/phpmyadmin
    sudo mv /tmp/phpMyAdmin-*-all-languages /usr/share/phpmyadmin
    sudo chmod -R 0755 /usr/share/phpmyadmin
    echo -e "${GREEN}PHPMyAdmin instalado${NC}"
else
    echo -e "${YELLOW}Error descargando PHPMyAdmin, omitiendo...${NC}"
fi

# Configurar PHPMyAdmin si se descargo
if [ -d "/usr/share/phpmyadmin" ]; then
    echo -e "${BLUE}Configurando PHPMyAdmin...${NC}"
    
    if [ -f "$PHPMA_CONF" ]; then
        echo -e "${GREEN}Archivo de configuracion encontrado${NC}"
    else
        echo -e "${YELLOW}Creando configuracion de PHPMyAdmin...${NC}"
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
        echo -e "${GREEN}Archivo de configuracion creado${NC}"
    fi

    # Copiar y activar configuracion
    sudo cp "$PHPMA_CONF" /etc/apache2/conf-available/phpmyadmin-pvcontrol.conf
    sudo a2enconf phpmyadmin-pvcontrol

    # Crear directorio temporal para PHPMyAdmin
    sudo mkdir -p /usr/share/phpmyadmin/tmp
    sudo chown -R www-data:www-data /usr/share/phpmyadmin/tmp

    echo -e "${GREEN}PHPMyAdmin configurado y activado${NC}"
fi

sudo systemctl reload apache2

# 12. CONFIGURAR PHP PARA BACKUPS (Max 200MB, 300seg)
echo -e "${BLUE}[11/16] Configurando PHP para backups grandes...${NC}"

# Buscar php.ini segun version detectada
find_php_ini() {
    # Buscar en rutas comunes
    local posibles_rutas=(
        "/etc/php/${PHP_VERSION##php}/apache2/php.ini"
        "/etc/php/${PHP_VERSION##php}/cli/php.ini"
        "/etc/php/$(echo $PHP_VERSION | sed 's/php//')/apache2/php.ini"
        "/etc/php/$(echo $PHP_VERSION | sed 's/php//')/cli/php.ini"
        "/etc/php/apache2/php.ini"
        "/etc/php/cli/php.ini"
    )
    
    for ruta in "${posibles_rutas[@]}"; do
        if [ -f "$ruta" ]; then
            echo "$ruta"
            return 0
        fi
    done
    
    echo ""
    return 1
}

PHP_INI=$(find_php_ini)

if [ -n "$PHP_INI" ] && [ -f "$PHP_INI" ]; then
    # Backup
    sudo cp "$PHP_INI" "${PHP_INI}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Modificar valores
    sudo sed -i "s/^\(;\s*\)\?upload_max_filesize.*/upload_max_filesize = 200M/" "$PHP_INI"
    sudo sed -i "s/^\(;\s*\)\?post_max_size.*/post_max_size = 210M/" "$PHP_INI"
    sudo sed -i "s/^\(;\s*\)\?memory_limit.*/memory_limit = 512M/" "$PHP_INI"
    sudo sed -i "s/^\(;\s*\)\?max_execution_time.*/max_execution_time = 300/" "$PHP_INI"
    sudo sed -i "s/^\(;\s*\)\?max_input_time.*/max_input_time = 300/" "$PHP_INI"
    
    echo -e "${GREEN}php.ini configurado ($PHP_INI)${NC}"
    
    # Reiniciar Apache
    sudo systemctl restart apache2
    echo -e "${GREEN}Apache reiniciado con nueva configuracion${NC}"
else
    echo -e "${YELLOW}php.ini no encontrado${NC}"
    echo -e "${YELLOW}La configuracion de backups grandes puede no funcionar${NC}"
fi

# 13. CONFIGURAR ZONA HORARIA EN PHP
echo -e "${BLUE}[12/16] Configurando zona horaria en PHP...${NC}"
configurar_zona_horaria

# 14. CREAR ACCESOS DIRECTOS EN EL ESCRITORIO
echo -e "${BLUE}[13/16] Preparando accesos directos...${NC}"
echo -e "${BLUE}Los accesos se crearán ahora...${NC}"

# 15. CREAR ACCESOS DIRECTOS WEB
echo -e "${BLUE}[14/16] Creando accesos directos web en el escritorio...${NC}"
crear_accesos_directos_web

# 16. CONFIGURAR VNC (solo Raspberry Pi)
echo -e "${BLUE}[15/16] Configurando acceso remoto...${NC}"

if [ "$ES_RASPBERRY" = true ]; then
    # Para Raspberry Pi
    echo -e "${BLUE}Configurando VNC Server (Raspberry Pi)...${NC}"
    
    if command -v raspi-config &> /dev/null; then
        if sudo raspi-config nonint get_vnc | grep -q "1"; then
            echo -e "${YELLOW}VNC no esta activado, activando...${NC}"
            
            if ! command -v vncserver &> /dev/null; then
                echo -e "${YELLOW}Instalando VNC Server...${NC}"
                sudo apt update
                sudo apt install realvnc-vnc-server -y
            fi

            sudo raspi-config nonint do_vnc 0
            sudo systemctl enable vncserver-x11-serviced.service
            sudo systemctl start vncserver-x11-serviced.service
            sudo raspi-config nonint do_resolution 2 16
            
            echo -e "${GREEN}VNC Server activado y configurado${NC}"
        else
            echo -e "${GREEN}VNC ya estaba activado${NC}"
        fi
    else
        echo -e "${YELLOW}raspi-config no disponible${NC}"
    fi
fi

# 17. ACTIVAR SERVICIOS
echo -e "${BLUE}[16/16] Activando servicios...${NC}"
sudo systemctl enable apache2
sudo systemctl enable mariadb
sudo systemctl enable mosquitto

sudo systemctl restart apache2
sudo systemctl restart mariadb
sudo systemctl restart mosquitto

# CONFIGURAR PERMISOS (se ejecutara desde install.sh)

# VERIFICACION FINAL
echo -e "${BLUE}Realizando verificacion final...${NC}"
sleep 2

if curl -s -I http://localhost > /dev/null; then
    echo -e "${GREEN}Web funcionando correctamente${NC}"
    echo -e "${BLUE}Web disponible en: http://$IP_ADDRESS${NC}"
else
    echo -e "${YELLOW}La web podria tener problemas${NC}"
fi

# Verificar permisos web
if sudo -u www-data ls -la "$PVC_HOME" > /dev/null 2>&1; then
    echo -e "${GREEN}Apache tiene acceso a PVControl+${NC}"
else
    echo -e "${YELLOW}Problema con los permisos de Apache${NC}"
fi

# Verificar zona horaria PHP
echo -e "${BLUE}Verificando zona horaria PHP...${NC}"
if command -v php &> /dev/null; then
    PHP_TIMEZONE_FINAL=$(php -r "echo ini_get('date.timezone');")
    if [ -n "$PHP_TIMEZONE_FINAL" ] && [ "$PHP_TIMEZONE_FINAL" != "" ]; then
        echo -e "${GREEN}Zona horaria PHP configurada: $PHP_TIMEZONE_FINAL${NC}"
    else
        echo -e "${YELLOW}Advertencia: Zona horaria PHP no configurada${NC}"
    fi
fi

# Verificar accesos directos
echo -e "${BLUE}Verificando accesos directos creados...${NC}"
ACCESOS_CREADOS=0
if [ -f "/home/pi/Desktop/PVControl+.desktop" ]; then
    echo -e "${GREEN}✓ PVControl+.desktop creado${NC}"
    ACCESOS_CREADOS=$((ACCESOS_CREADOS+1))
fi
if [ -f "/home/pi/Desktop/Configuracion_PVControl+.desktop" ]; then
    echo -e "${GREEN}✓ Configuracion_PVControl+.desktop creado${NC}"
    ACCESOS_CREADOS=$((ACCESOS_CREADOS+1))
fi
if [ -f "/home/pi/Desktop/PHPMyAdmin.desktop" ]; then
    echo -e "${GREEN}✓ PHPMyAdmin.desktop creado${NC}"
    ACCESOS_CREADOS=$((ACCESOS_CREADOS+1))
fi
echo -e "${GREEN}Total accesos directos creados: $ACCESOS_CREADOS${NC}"

# RESUMEN FINAL
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   STACK INSTALADO CORRECTAMENTE${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${BLUE}Plataforma: $([ "$ES_RASPBERRY" = true ] && echo "Raspberry Pi" || echo "PC")${NC}"
echo -e "${BLUE}Sistema: $SO ($ARCH)${NC}"
echo -e "${BLUE}PHP Version: $PHP_VERSION${NC}"
if command -v php &> /dev/null; then
    PHP_TZ=$(php -r "echo ini_get('date.timezone');" 2>/dev/null || echo "No detectada")
    echo -e "${BLUE}Zona Horaria PHP: $PHP_TZ${NC}"
fi
echo ""
echo -e "${BLUE}Servicios instalados:${NC}"
echo -e "${BLUE}- Apache Web Server${NC}"
echo -e "${BLUE}- PHP ($PHP_VERSION)${NC}"
echo -e "${BLUE}- MariaDB (MySQL)${NC}"
echo -e "${BLUE}- PHPMyAdmin${NC}"
echo -e "${BLUE}- Mosquitto MQTT${NC}"

if [ "$ES_RASPBERRY" = true ]; then
    echo -e "${BLUE}- VNC Server${NC}"
    echo -e "${BLUE}VNC disponible en: $IP_ADDRESS${NC}"
elif command -v geany &> /dev/null; then
    echo -e "${BLUE}Programas PC instalados:${NC}"
    [ -x "$(command -v geany)" ] && echo -e "${BLUE}- Geany (editor)${NC}"
fi

echo ""
echo -e "${BLUE}Archivos de configuracion creados:${NC}"
echo -e "${BLUE}- Parametros_FV.py${NC}"
echo -e "${BLUE}- html/Parametros_Web.js${NC}"
echo -e "${BLUE}- html/version.inc${NC}"
echo -e "${BLUE}Zona horaria configurada automaticamente${NC}"
echo ""
echo -e "${BLUE}Accesos directos creados en el escritorio:${NC}"
echo -e "${BLUE}- PVControl+ Web (http://localhost)${NC}"
echo -e "${BLUE}- Configuración PVControl+ (http://localhost/configuracion.html)${NC}"
echo -e "${BLUE}- PHPMyAdmin (http://localhost/phpmyadmin)${NC}"
echo -e "${BLUE}- Arrancar/Parar servicios${NC}"
echo -e "${BLUE}- Ver programas en ejecución${NC}"
echo ""
echo -e "${BLUE}Accesos web:${NC}"
echo -e "${BLUE}Web principal: http://$IP_ADDRESS${NC}"
echo -e "${BLUE}Configuración: http://$IP_ADDRESS/configuracion.html${NC}"
echo -e "${BLUE}PHPMyAdmin: http://$IP_ADDRESS/phpmyadmin${NC}"
echo -e "${BLUE}Usuario BD: rpi | Contrasena: fv${NC}"
echo -e "${GREEN}=========================================${NC}"