#!/bin/bash
# Script principal de instalacion para Trixie

# Colores brillantes y definidos
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
CYAN='\033[0;96m'
NC='\033[0m'

# Funcion para pausa
pausa() {
    echo -e "${CYAN}"
    read -p "   ⏎ Pulse Enter para continuar..."
    echo -e "${NC}"
}

echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}   INSTALACION PVControl+ - TRIXIE${NC}"
echo -e "${CYAN}=========================================${NC}"

# Paso 1: Configurar Python
echo -e "${BLUE}[1/4] Configurando Python...${NC}"
chmod +x setup_python.sh
./setup_python.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Fallo la configuracion de Python${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python configurado correctamente${NC}"
echo -e "${BLUE}● Entorno virtual: /home/pi/PVControl+/env${NC}"
echo -e "${BLUE}● Activación permanente en .bashrc${NC}"
echo -e "${BLUE}● Dependencias Python instaladas${NC}"
pausa


# Paso 2: Instalar servicios
echo -e "${BLUE}[2/4] Instalando servicios...${NC}"
chmod +x install_stack.sh
./install_stack.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Fallo la instalacion de servicios${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Servicios instalados correctamente${NC}"
echo -e "${BLUE}● Apache + PHP 8.4${NC}"
echo -e "${BLUE}● MariaDB + PHPMyAdmin${NC}"
echo -e "${BLUE}● Mosquitto MQTT${NC}"
echo -e "${BLUE}● VNC Server${NC}"
echo -e "${BLUE}● Permisos web configurados${NC}"
pausa

# Paso 3: Configuracion final
echo -e "${BLUE}[3/4] Configuracion final...${NC}"
source ~/.bashrc
echo -e "${GREEN}✅ Configuración final aplicada${NC}"
echo -e "${BLUE}● Entorno virtual activado${NC}"
echo -e "${BLUE}● Variables de entorno cargadas${NC}"
pausa

# Paso 4: Verificacion
echo -e "${BLUE}[4/4] Verificando instalacion...${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   INSTALACION COMPLETADA!${NC}"
echo -e "${GREEN}     ... buscando actualizaciones....${NC}"
echo -e "${GREEN}=========================================${NC}"


ENV_PYTHON="/home/pi/PVControl+/env/bin/python"
if [ -f "$ENV_PYTHON" ]; then
    "$ENV_PYTHON" -c "import paho.mqtt, MySQLdb; print('✓ Entorno virtual funcionando')"
else
    echo -e "${RED}ERROR: Entorno virtual no encontrado${NC}"
fi

# Ejecutar script de actualización SI EXISTE
echo -e "${BLUE}[INFO] Buscando script de actualización...${NC}"
ACTUALIZAR_SCRIPT="/home/pi/PVControl+/actualizar"

if [ -f "$ACTUALIZAR_SCRIPT" ] && [ -f "$ENV_PYTHON" ]; then
    echo -e "${GREEN}[OK] Script actualizar encontrado${NC}"
    
    # Hacer el script ejecutable
    chmod +x "$ACTUALIZAR_SCRIPT"
    
    # Cambiar al directorio
    cd "/home/pi/PVControl+"
    
    # Verificar si actualizar es Python o shell
    if head -n 1 "$ACTUALIZAR_SCRIPT" | grep -q "python"; then
        echo -e "${BLUE}[INFO] Ejecutando actualizar (script Python)...${NC}"
        # Es un script Python - ejecutar directamente con el Python del entorno
        "$ENV_PYTHON" "$ACTUALIZAR_SCRIPT"
    else
        echo -e "${BLUE}[INFO] Ejecutando actualizar (script shell)...${NC}"
        # Es un script shell - usar source para activar entorno
        source "/home/pi/PVControl+/env/bin/activate"
        ./actualizar
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK] Actualización completada${NC}"
    else
        echo -e "${YELLOW}[AVISO] La actualización encontró problemas${NC}"
    fi
else
    echo -e "${YELLOW}[AVISO] Script actualizar no encontrado${NC}"
fi

ACTUALIZAR_SCRIPT="/home/pi/PVControl+/actualizar"

if [ -f "$ACTUALIZAR_SCRIPT" ]; then
    echo -e "${GREEN}[OK] Script actualizar encontrado${NC}"
    
    # Dar permisos de ejecucion
    chmod +x "$ACTUALIZAR_SCRIPT"
    
    # Ejecutar desde el directorio correcto
    cd /home/pi/PVControl+
    
    echo -e "${BLUE}[INFO] Ejecutando ./actualizar...${NC}"
    ./actualizar
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK] Script actualizar ejecutado correctamente${NC}"
    else
        echo -e "${YELLOW}[AVISO] Script actualizar termino con errores${NC}"
    fi
else
    echo -e "${YELLOW}[AVISO] Script actualizar no encontrado en $ACTUALIZAR_SCRIPT${NC}"
fi

# Mensajes finales
echo ""
echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}   RESUMEN DE INSTALACIÓN${NC}"
echo -e "${CYAN}=========================================${NC}"
echo -e "${GREEN}✅ INSTALACIÓN COMPLETADA${NC}"
echo ""
echo -e "${BLUE}● Directorio: /home/pi/PVControl+${NC}"
echo -e "${BLUE}● Python: entorno virtual activado permanentemente${NC}"
echo -e "${BLUE}● Servicios: MariaDB, Apache, PHP, Mosquitto, VNC${NC}"
echo -e "${BLUE}● Web: http://$(hostname -I | awk '{print $1}')${NC}"
echo -e "${BLUE}● VNC: activado - conecta a la IP de la Raspberry${NC}"
echo -e "${BLUE}● PHPMyAdmin: http://$(hostname -I | awk '{print $1}')/phpmyadmin${NC}"
echo ""
echo -e "${YELLOW}Las nuevas terminales se abriran en PVControl+${NC}"
echo -e "${YELLOW}El entorno virtual se activará automáticamente${NC}"
echo ""
echo -e "${GREEN}¡PVControl+ está listo para usar!${NC}"
echo -e "${CYAN}=========================================${NC}"