#!/bin/bash
# Instalador PVControl+ para Raspberry OS Trixie
# Ubicacion: https://sourceforge.net/p/pvcontrol/code/ci/trixie/tree/instalacion_pvcontrol_trixie.sh?format=raw

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
echo -e "${CYAN}    INSTALADOR PVControl+ - TRIXIE${NC}"
echo -e "${CYAN}=========================================${NC}"

# Configuracion
REPO_URL="https://git.code.sf.net/p/pvcontrol/code"
BRANCH="trixie"
INSTALL_DIR="/home/pi/PVControl+"

# Verificar usuario
if [ "$USER" != "pi" ]; then
    echo -e "${RED}ERROR: Debes ejecutar como usuario 'pi'${NC}"
    echo -e "${RED}Usuario actual: $USER${NC}"
    exit 1
fi

# Verificar que estamos en Trixie
if ! grep -q "trixie" /etc/os-release; then
    echo -e "${YELLOW}ADVERTENCIA: No estas en Raspberry OS Trixie${NC}"
    echo -e "${YELLOW}Este instalador esta especificamente para Trixie${NC}"
    read -p "Continuar de todos modos? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Funcion principal
main() {
    echo -e "${BLUE}[1/4] Descargando PVControl+...${NC}"
    cd /home/pi
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Actualizando instalacion existente...${NC}"
        cd "$INSTALL_DIR"
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
    else
        echo -e "${BLUE}Clonando repositorio desde $REPO_URL...${NC}"
        git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
        if [ $? -ne 0 ]; then
            echo -e "${RED}ERROR: No se pudo descargar PVControl+${NC}"
            echo -e "${YELLOW}Verifica:${NC}"
            echo -e "${YELLOW} - Conexion a internet${NC}"
            echo -e "${YELLOW} - Que la rama '$BRANCH' existe${NC}"
            exit 1
        fi
        cd "$INSTALL_DIR"
    fi
    
    
    echo -e "${BLUE}[2/4] Verificando estructura...${NC}"
    if [ ! -d "instalacion_trixie" ]; then
        echo -e "${RED}ERROR: No se encuentra el directorio de instalacion${NC}"
        echo -e "${YELLOW}Estructura actual:${NC}"
        ls -la
        exit 1
    fi

    echo -e "${BLUE}[3/4] Preparando scripts...${NC}"
    chmod +x instalacion_trixie/*.sh
    echo -e "${GREEN}Scripts preparados correctamente${NC}"

    echo -e "${BLUE}[4/4] Ejecutando instalacion completa...${NC}"
    cd instalacion_trixie
    ./install.sh
}

# Manejo de senales
cleanup() {
    echo ""
    echo -e "${RED}Instalacion interrumpida${NC}"
    exit 1
}

trap cleanup SIGINT SIGTERM

# Verificar conexion a internet
check_internet() {
    echo -e "${BLUE}Verificando conexion a internet...${NC}"
    if ! ping -c 1 git.code.sf.net &> /dev/null; then
        echo -e "${RED}ERROR: No hay conexion a internet${NC}"
        echo -e "${YELLOW}Conecta a internet y vuelve a intentarlo${NC}"
        exit 1
    fi
    echo -e "${GREEN}Conexion a internet OK${NC}"
}

# Verificar dependencias
check_dependencies() {
    echo -e "${BLUE}Verificando dependencias...${NC}"
    
    if ! command -v git &> /dev/null; then
        echo -e "${YELLOW}Git no encontrado, instalando...${NC}"
        sudo apt update && sudo apt install git -y
    fi
    
    if ! command -v curl &> /dev/null; then
        echo -e "${YELLOW}Curl no encontrado, instalando...${NC}"
        sudo apt install curl -y
    fi
    
    echo -e "${GREEN}Dependencias OK${NC}"
}


# Ejecutar verificaciones previas
echo -e "${CYAN}Realizando verificaciones previas...${NC}"
check_internet
check_dependencies
echo ""

# Ejecutar instalacion
main