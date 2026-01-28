#!/bin/bash
# Script principal de instalacion para PVControl+
# Compatible con Trixie y Bookworm
# Sin pausas interactivas para funcionar con curl | bash

# Colores
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
CYAN='\033[0;96m'
NC='\033[0m'

# Función para pausa automática (no interactiva)
pausa_automatica() {
    local segundos=${1:-2}
    echo ""
    echo -e "${CYAN}Continuando en ${segundos} segundos...${NC}"
    echo -e "${YELLOW}Presiona Ctrl+C para cancelar${NC}"
    sleep $segundos
    echo ""
}

# Mostrar informacion del sistema
echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}   INSTALACION PVControl+${NC}"
echo -e "${CYAN}=========================================${NC}"
echo -e "${BLUE}Sistema: ${SO}${NC}"
echo -e "${BLUE}Plataforma: $([ "$ES_RASPBERRY" = true ] && echo "Raspberry Pi" || echo "PC/Netbook")${NC}"
echo -e "${BLUE}Arquitectura: ${ARCH}${NC}"

# Variables globales
INSTALL_DIR="/home/pi/PVControl+"
ENV_DIR="$INSTALL_DIR/env"
ENV_PYTHON="$ENV_DIR/bin/python"
ACTUALIZAR_SCRIPT="$INSTALL_DIR/actualizar"

# Paso 1: Configurar Python
echo -e "${BLUE}[1/4] Configurando Python...${NC}"
chmod +x setup_python.sh

# Exportar variables para setup_python.sh
export ES_TRIXIE
export ES_BOOKWORM
export ES_RASPBERRY

./setup_python.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Fallo la configuracion de Python${NC}"
    exit 1
fi

echo -e "${GREEN}Python configurado correctamente${NC}"
echo -e "${BLUE}Entorno virtual: $ENV_DIR${NC}"
echo -e "${BLUE}Activacion permanente en .bashrc${NC}"
pausa_automatica 10

# Paso 2: Instalar servicios
echo -e "${BLUE}[2/4] Instalando servicios...${NC}"
chmod +x install_stack.sh

# Exportar variables para install_stack.sh
export ES_TRIXIE
export ES_BOOKWORM
export ES_RASPBERRY
export SO
export ARCH

./install_stack.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Fallo la instalacion de servicios${NC}"
    exit 1
fi

echo -e "${GREEN}Servicios instalados correctamente${NC}"
echo -e "${BLUE}Apache + PHP${NC}"
echo -e "${BLUE}MariaDB + PHPMyAdmin${NC}"
echo -e "${BLUE}Mosquitto MQTT${NC}"

if [ "$ES_RASPBERRY" = true ]; then
    echo -e "${BLUE}VNC Server${NC}"
else
    echo -e "${YELLOW}VNC Server opcional en PC${NC}"
fi

echo -e "${BLUE}Permisos web configurados${NC}"
pausa_automatica 10

# Paso 3: Configurar permisos
echo -e "${BLUE}[3/4] Configurando permisos...${NC}"
chmod +x setup_permisos.sh

# Exportar variables para setup_permisos.sh
export ES_RASPBERRY

./setup_permisos.sh

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}ADVERTENCIA: Problemas con permisos, continuando...${NC}"
fi

echo -e "${GREEN}Permisos configurados${NC}"
pausa_automatica 10

# Paso 4: Configuracion final
echo -e "${BLUE}[4/4] Configuracion final...${NC}"
source ~/.bashrc
echo -e "${GREEN}Configuracion final aplicada${NC}"
echo -e "${BLUE}Entorno virtual activado${NC}"
pausa_automatica 10

# Verificacion del entorno
echo -e "${BLUE}Verificando instalacion...${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   INSTALACION COMPLETADA!${NC}"
echo -e "${GREEN}     ... buscando actualizaciones....${NC}"
echo -e "${GREEN}=========================================${NC}"

if [ -f "$ENV_PYTHON" ]; then
    "$ENV_PYTHON" -c "import sys; print('✓ Python: ' + sys.version.split()[0])"
    
    # Verificación CORREGIDA - usar comillas simples y punto y coma
    "$ENV_PYTHON" -c "
try:
    import paho.mqtt
    print('✓ paho-mqtt: OK')
except ImportError:
    print('✗ paho-mqtt: Falta')
"
    
    "$ENV_PYTHON" -c "
try:
    import mysql.connector
    print('✓ mysql-connector: OK')
except ImportError:
    print('✗ mysql-connector: Falta')
"
    
    "$ENV_PYTHON" -c "
try:
    import pymodbus
    print('✓ pymodbus: OK')
except ImportError:
    print('✗ pymodbus: Falta')
"
else
    echo -e "${RED}ERROR: Entorno virtual no encontrado${NC}"
fi

# Ejecutar script de actualizacion si existe
if [ -f "$ACTUALIZAR_SCRIPT" ] && [ -f "$ENV_PYTHON" ]; then
    echo -e "${GREEN}Script actualizar encontrado${NC}"
    
    chmod +x "$ACTUALIZAR_SCRIPT"
    cd "$INSTALL_DIR"
    
    if head -n 1 "$ACTUALIZAR_SCRIPT" | grep -q "python"; then
        echo -e "${BLUE}Ejecutando actualizar (script Python)...${NC}"
        "$ENV_PYTHON" "$ACTUALIZAR_SCRIPT"
    else
        echo -e "${BLUE}Ejecutando actualizar (script shell)...${NC}"
        if [ -f "$ENV_DIR/bin/activate" ]; then
            source "$ENV_DIR/bin/activate"
        fi
        ./actualizar
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Actualizacion completada${NC}"
    else
        echo -e "${YELLOW}La actualizacion encontro problemas${NC}"
    fi
else
    echo -e "${YELLOW}Script actualizar no encontrado${NC}"
fi

# Obtener IP del sistema
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

# Mensajes finales con pasos siguientes
echo ""
echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}   RESUMEN DE INSTALACION${NC}"
echo -e "${CYAN}=========================================${NC}"
echo -e "${GREEN}✓ INSTALACION COMPLETADA${NC}"
echo ""
echo -e "${BLUE}DIRECTORIO PRINCIPAL:${NC}"
echo -e "  $INSTALL_DIR"
echo ""
echo -e "${BLUE}SERVICIOS INSTALADOS:${NC}"
echo -e "  ✓ Apache Web Server"
echo -e "  ✓ PHP ($(php --version 2>/dev/null | head -n1 | cut -d' ' -f2 || echo "instalado"))"
echo -e "  ✓ MariaDB (MySQL) - Usuario: rpi / Contraseña: fv"
echo -e "  ✓ PHPMyAdmin"
echo -e "  ✓ Mosquitto MQTT"

if [ "$ES_RASPBERRY" = true ]; then
    echo -e "  ✓ VNC Server"
fi

echo ""
echo -e "${BLUE}ACCESOS WEB:${NC}"
echo -e "  🌐 Pagina principal: ${GREEN}http://${IP_ADDRESS}/${NC}"
echo -e "  📊 PHPMyAdmin: ${GREEN}http://${IP_ADDRESS}/phpmyadmin${NC}"
echo -e "  ⚙️  Configuracion PVControl+: ${GREEN}http://${IP_ADDRESS}/configuracion.html${NC}"
echo ""
echo -e "${BLUE}CONFIGURACION PVControl+:${NC}"
echo -e "${YELLOW}⚠️  PASOS IMPORTANTES A SEGUIR:${NC}"
echo ""
echo -e "${CYAN}1. CONFIGURACION INICIAL:${NC}"
echo -e "   • Abre tu navegador web"
echo -e "   • Visita: ${GREEN}http://${IP_ADDRESS}/configuracion.html${NC}"
echo -e "   • Configura los equipos FV que tengas instalados"
echo ""
echo -e "${CYAN}2. ACCESO A BASE DE DATOS:${NC}"
echo -e "   • Usuario: ${GREEN}rpi${NC}"
echo -e "   • Contraseña: ${GREEN}fv${NC}"
echo -e "   • Base de datos: ${GREEN}control_solar${NC}"
echo ""
echo -e "${CYAN}3. ACCESO REMOTO (Raspberry Pi):${NC}"
if [ "$ES_RASPBERRY" = true ]; then
    echo -e "   • VNC: Conecta a ${GREEN}${IP_ADDRESS}:0${NC}"
    echo -e "   • SSH: ${GREEN}ssh pi@${IP_ADDRESS}${NC}"
else
    echo -e "   • SSH: ${GREEN}ssh pi@${IP_ADDRESS}${NC}"
fi
echo ""
echo ""
echo -e "${YELLOW}⚠️  NOTAS IMPORTANTES:${NC}"
echo -e "   • El entorno virtual Python se activa automaticamente"
echo -e "   • Las nuevas terminales se abriran en PVControl+"
echo -e "   • Para soporte, revisa la documentacion en ${IP_ADDRESS}/ayuda.php/"
echo ""
echo -e "${GREEN}✅ PVControl+ ESTA LISTO PARA USAR!${NC}"
echo ""
echo -e "${BLUE}Proceso completado el: $(date)${NC}"
echo -e "${CYAN}=========================================${NC}"