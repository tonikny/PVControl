#!/bin/bash
# Instalador PVControl+ para Raspberry OS Trixie y Debian Bookworm (PC)
# Compatible con:
#   - Raspberry Pi con Trixie (64-bit)
#   - PC/Netbook con Bookworm (32-bit o 64-bit)
#   - PC/Netbook con Trixie (64-bit)

# Colores
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
CYAN='\033[0;96m'
NC='\033[0m'

# Funcion para pausa con mensaje
pausa() {
    echo ""
    echo -e "${CYAN}=========================================${NC}"
    echo -e "${CYAN}Pulsa Enter para continuar o Ctrl+C para cancelar${NC}"
    echo -e "${CYAN}=========================================${NC}"
    
    if read -r entrada1 < /dev/tty; then
        echo "✓ Leído: $entrada1"
    else
        echo "✗ Error con /dev/tty"
    fi
}

echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}    INSTALADOR PVControl+${NC}"
echo -e "${CYAN}=========================================${NC}"

# Configuracion
REPO_URL="https://git.code.sf.net/p/pvcontrol/code"
BRANCH="trixie"
INSTALL_DIR="/home/pi/PVControl+"
INSTALL_SUBDIR_NAME="instalacion_pvcontrol"

# Verificar usuario pi
if [ "$USER" != "pi" ]; then
    echo -e "${YELLOW}ADVERTENCIA: PVControl+ requiere usuario 'pi'${NC}"
    echo -e "${YELLOW}Usuario actual: $USER${NC}"
    echo ""
    echo -e "${BLUE}Para PC/Netbook con Debian:${NC}"
    echo -e "1. Crear usuario 'pi': ${CYAN}sudo adduser pi${NC}"
    echo -e "2. Agregar a grupos necesarios: ${CYAN}sudo usermod -aG sudo,adm,dialout pi${NC}"
    echo -e "3. Salir y entrar como 'pi'${NC}"
    echo -e "4. Ejecutar este script de nuevo${NC}"
    echo ""
    echo -e "${RED}No se puede continuar sin usuario 'pi'${NC}"
    exit 1
fi

# Detectar SO y plataforma
detectar_so() {
    # Detectar SO
    if grep -q "trixie" /etc/os-release; then
        SO="Raspberry OS Trixie"
        SO_COMPATIBLE=true
        ES_TRIXIE=true
        ES_BOOKWORM=false
    elif grep -q "bookworm" /etc/os-release || grep -q "12" /etc/os-release; then
        SO="Debian Bookworm"
        SO_COMPATIBLE=true
        ES_TRIXIE=false
        ES_BOOKWORM=true
    else
        SO="Desconocido"
        SO_COMPATIBLE=false
        ES_TRIXIE=false
        ES_BOOKWORM=false
    fi
    
    # Detectar arquitectura
    ARCH=$(uname -m)
    
    # Detectar si es Raspberry Pi
    if [ -f /proc/device-tree/model ]; then
        MODEL=$(tr -d '\0' < /proc/device-tree/model)
        if echo "$MODEL" | grep -qi "raspberry"; then
            ES_RASPBERRY=true
        else
            ES_RASPBERRY=false
        fi
    else
        ES_RASPBERRY=false
    fi
    
    # Mostrar informacion
    echo -e "${BLUE}Sistema operativo: $SO${NC}"
    echo -e "${BLUE}Arquitectura: $ARCH${NC}"
    echo -e "${BLUE}Plataforma: $([ "$ES_RASPBERRY" = true ] && echo "Raspberry Pi" || echo "PC/Netbook")${NC}"
}

# Funcion para verificar grupos del usuario actual
verificar_grupos_usuario() {
    echo -e "${BLUE}Verificando grupos del usuario $USER...${NC}"
    
    # Solo verificar si ya es usuario pi
    if [ "$USER" = "pi" ]; then
        GRUPOS_FALTANTES=()
        
        if ! groups pi | grep -q "\bsudo\b"; then
            GRUPOS_FALTANTES+=("sudo")
        fi
        
        if ! groups pi | grep -q "\badm\b"; then
            GRUPOS_FALTANTES+=("adm")
        fi
        
        if ! groups pi | grep -q "\bdialout\b"; then
            GRUPOS_FALTANTES+=("dialout")
        fi
        
        if [ ${#GRUPOS_FALTANTES[@]} -gt 0 ]; then
            echo -e "${YELLOW}ADVERTENCIA: Usuario pi no está en grupos: ${GRUPOS_FALTANTES[*]}${NC}"
            echo -e "${YELLOW}El script de instalación intentará agregarlos automáticamente${NC}"
        else
            echo -e "${GREEN}✓ Usuario pi tiene todos los grupos necesarios${NC}"
        fi
    fi
}

# Verificar compatibilidad
verificar_compatibilidad() {
    if [ "$SO_COMPATIBLE" = false ]; then
        echo -e "${YELLOW}ADVERTENCIA: Sistema no detectado como Trixie o Bookworm${NC}"
        echo -e "${YELLOW}Continuando automaticamente en 5 segundos...${NC}"
        echo -e "${YELLOW}Presiona Ctrl+C para cancelar${NC}"
        sleep 5
    fi
}

# Funcion principal
main() {
    echo -e "${BLUE}[1/4] Descargando PVControl+ (rama $BRANCH)...${NC}"
    cd /home/pi
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Actualizando instalacion existente...${NC}"
        cd "$INSTALL_DIR"
        
        if [ -d ".git" ]; then
            git checkout "$BRANCH" 2>/dev/null || echo -e "${YELLOW}No se pudo cambiar a rama $BRANCH${NC}"
            git pull origin "$BRANCH"
        else
            echo -e "${RED}No es un repositorio git valido${NC}"
            cd ..
            rm -rf "$INSTALL_DIR"
            git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
        fi
    else
        echo -e "${BLUE}Clonando repositorio...${NC}"
        git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
        if [ $? -ne 0 ]; then
            echo -e "${RED}ERROR: No se pudo descargar PVControl+${NC}"
            echo -e "${YELLOW}Intentando sin rama especifica...${NC}"
            git clone "$REPO_URL" "$INSTALL_DIR"
            if [ $? -ne 0 ]; then
                echo -e "${RED}ERROR: No se pudo clonar el repositorio${NC}"
                exit 1
            fi
        fi
        cd "$INSTALL_DIR"
    fi
    
    echo -e "${BLUE}[2/4] Verificando estructura...${NC}"
    
    if [ -d "$INSTALL_SUBDIR_NAME" ]; then
        INSTALL_SUBDIR="$INSTALL_SUBDIR_NAME"
        echo -e "${GREEN}Directorio de instalacion encontrado: $INSTALL_SUBDIR${NC}"
    else
        echo -e "${RED}ERROR: No se encuentra '$INSTALL_SUBDIR_NAME'${NC}"
        ls -la
        exit 1
    fi
    
    echo -e "${BLUE}[3/4] Preparando scripts...${NC}"
    chmod +x "$INSTALL_SUBDIR"/*.sh
    echo -e "${GREEN}Scripts preparados${NC}"

    echo -e "${BLUE}[4/4] Ejecutando instalacion completa...${NC}"
    cd "$INSTALL_SUBDIR"
    
    # Informacion antes de instalar
    echo ""
    echo -e "${CYAN}===============================================${NC}"
    echo -e "${CYAN}           RESUMEN DE INSTALACION${NC}"
    echo -e "${CYAN}===============================================${NC}"
    echo -e "${BLUE}Sistema: $SO${NC}"
    echo -e "${BLUE}Plataforma: $([ "$ES_RASPBERRY" = true ] && echo "Raspberry Pi" || echo "PC/Netbook")${NC}"
    echo -e "${BLUE}Arquitectura: $ARCH${NC}"
    echo -e "${BLUE}Rama PVControl+: $BRANCH${NC}"
    echo -e "${BLUE}Directorio: $INSTALL_DIR/$INSTALL_SUBDIR${NC}"
    echo -e "${CYAN}===============================================${NC}"
    echo ""
    
    # Pausa antes de continuar
    echo -e "${YELLOW}La instalacion comenzara en 5 segundos...${NC}"
    echo -e "${YELLOW}Presiona Ctrl+C para cancelar${NC}"
    sleep 5
    
    # Exportar variables para install.sh
    export ES_TRIXIE
    export ES_BOOKWORM
    export ES_RASPBERRY
    export SO
    export ARCH
    
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
    
    # Intentar con ping primero (no requiere curl)
    if ping -c 1 google.com &> /dev/null || ping -c 1 8.8.8.8 &> /dev/null; then
        echo -e "${GREEN}Conexion a internet OK (via ping)${NC}"
        return 0
    fi
    
    # Si curl está disponible, usarlo
    if command -v curl &> /dev/null; then
        if curl -s --connect-timeout 5 https://google.com > /dev/null 2>&1; then
            echo -e "${GREEN}Conexion a internet OK (via curl)${NC}"
            return 0
        fi
    fi
    
    # Si wget está disponible, usarlo
    if command -v wget &> /dev/null; then
        if wget -q --spider https://google.com 2>/dev/null; then
            echo -e "${GREEN}Conexion a internet OK (via wget)${NC}"
            return 0
        fi
    fi
    
    echo -e "${RED}ERROR: No se detecta conexion a internet${NC}"
    echo -e "${YELLOW}Verifica tu conexion y vuelve a intentarlo${NC}"
    exit 1
}

# Verificar e instalar dependencias basicas
check_dependencies() {
    echo -e "${BLUE}Verificando dependencias basicas...${NC}"
    
    # Primero actualizar repositorios (intentar, pero no fallar si no funciona)
    echo -e "${YELLOW}Actualizando lista de paquetes...${NC}"
    sudo apt update > /dev/null 2>&1 || echo -e "${YELLOW}Nota: No se pudo actualizar lista de paquetes${NC}"
    
    # Lista de dependencias basicas
    BASIC_DEPS=()
    
    # Git es esencial
    if ! command -v git &> /dev/null; then
        echo -e "${YELLOW}Git no encontrado, se instalará${NC}"
        BASIC_DEPS+=("git")
    else
        echo -e "${GREEN}✓ Git ya instalado${NC}"
    fi
    
    # Curl es necesario para descargar PHPMyAdmin
    if ! command -v curl &> /dev/null; then
        echo -e "${YELLOW}Curl no encontrado, se instalará${NC}"
        BASIC_DEPS+=("curl")
    else
        echo -e "${GREEN}✓ Curl ya instalado${NC}"
    fi
    
    # Instalar dependencias faltantes
    if [ ${#BASIC_DEPS[@]} -gt 0 ]; then
        echo -e "${YELLOW}Instalando dependencias faltantes: ${BASIC_DEPS[*]}...${NC}"
        
        # Intentar instalación
        if sudo apt install -y "${BASIC_DEPS[@]}"; then
            echo -e "${GREEN}✓ Dependencias instaladas correctamente${NC}"
        else
            echo -e "${RED}ERROR: No se pudieron instalar las dependencias${NC}"
            echo -e "${YELLOW}Intenta instalarlas manualmente:${NC}"
            echo -e "  sudo apt update"
            echo -e "  sudo apt install git curl"
            exit 1
        fi
    fi
    
    # Verificación final
    if ! command -v git &> /dev/null; then
        echo -e "${RED}ERROR: Git no disponible después de la instalación${NC}"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}ERROR: Curl no disponible después de la instalación${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Todas las dependencias basicas verificadas${NC}"
}

# Ejecutar verificaciones previas
echo -e "${CYAN}Realizando verificaciones previas...${NC}"
check_internet
detectar_so
verificar_grupos_usuario
verificar_compatibilidad
check_dependencies
echo ""

# Ejecutar instalacion
main