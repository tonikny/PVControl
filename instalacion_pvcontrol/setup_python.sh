#!/bin/bash
# Configuracion Python para PVControl+
# Compatible con Trixie y Bookworm

# Colores
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   CONFIGURANDO PYTHON PARA PVControl+${NC}"
echo -e "${BLUE}=========================================${NC}"

# Variables desde el script principal
ES_TRIXIE=${ES_TRIXIE:-true}
ES_BOOKWORM=${ES_BOOKWORM:-false}
ES_RASPBERRY=${ES_RASPBERRY:-true}

PVC_HOME="/home/pi/PVControl+"
VENV_DIR="$PVC_HOME/env"

# Instalar Thonny para PC (trae herramientas de desarrollo)
instalar_thonny_si_es_pc() {
    # Solo para PC, no para Raspberry Pi
    if [ "$ES_RASPBERRY" = false ]; then
        echo -e "${BLUE}[1/9] PC detectado - instalando Thonny...${NC}"
        echo -e "${YELLOW}Thonny incluye herramientas de desarrollo Python${NC}"
        
        if ! command -v thonny &> /dev/null; then
            echo -e "${YELLOW}Instalando Thonny...${NC}"
            sudo apt update
            if sudo apt install -y thonny; then
                echo -e "${GREEN}✓ Thonny instalado correctamente${NC}"
                echo -e "${YELLOW}Thonny trae: Python3, pip, setuptools, wheel y herramientas de compilacion${NC}"
            else
                echo -e "${YELLOW}⚠ No se pudo instalar Thonny, instalando herramientas manualmente...${NC}"
                instalar_herramientas_manualmente
            fi
        else
            echo -e "${GREEN}✓ Thonny ya instalado${NC}"
        fi
    else
        echo -e "${BLUE}[1/9] Raspberry Pi detectada - omitiendo Thonny${NC}"
        echo -e "${YELLOW}Para Raspberry Pi, instalando herramientas especificas...${NC}"
        instalar_herramientas_raspberry
    fi
}

# Instalar herramientas manualmente (si Thonny falla)
instalar_herramientas_manualmente() {
    echo -e "${YELLOW}Instalando herramientas de desarrollo manualmente...${NC}"
    
    DEPS_DEVELOPMENT="build-essential make gcc g++ python3-dev python3-setuptools python3-wheel"
    DEPS_DEVELOPMENT="$DEPS_DEVELOPMENT libffi-dev libssl-dev"
    
    sudo apt install -y $DEPS_DEVELOPMENT
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Herramientas de desarrollo instaladas${NC}"
    else
        echo -e "${RED}ERROR: No se pudieron instalar herramientas de desarrollo${NC}"
        echo -e "${YELLOW}Los paquetes que requieren compilacion pueden fallar${NC}"
    fi
}

# Instalar herramientas para Raspberry Pi
instalar_herramientas_raspberry() {
    echo -e "${YELLOW}Instalando herramientas para Raspberry Pi...${NC}"
    
    # Herramientas basicas de compilacion
    sudo apt install -y build-essential python3-dev
    
    # Para i2c/smbus en Raspberry Pi
    sudo apt install -y i2c-tools libi2c-dev python3-smbus
    
    # Otras dependencias comunes
    sudo apt install -y python3-setuptools python3-wheel
    
    echo -e "${GREEN}✓ Herramientas para Raspberry Pi instaladas${NC}"
}

# Determinar version de Python disponible
detectar_python() {
    echo -e "${BLUE}[2/9] Detectando Python disponible...${NC}"
    
    # Buscar versiones de Python disponibles
    if command -v python3.13 &> /dev/null; then
        PYTHON_BIN="python3.13"
        PYTHON_VERSION="3.13"
        PYTHON_VENV_PKG="python3.13-venv"
    elif command -v python3.12 &> /dev/null; then
        PYTHON_BIN="python3.12"
        PYTHON_VERSION="3.12"
        PYTHON_VENV_PKG="python3.12-venv"
    elif command -v python3.11 &> /dev/null; then
        PYTHON_BIN="python3.11"
        PYTHON_VERSION="3.11"
        PYTHON_VENV_PKG="python3.11-venv"
    elif command -v python3.10 &> /dev/null; then
        PYTHON_BIN="python3.10"
        PYTHON_VERSION="3.10"
        PYTHON_VENV_PKG="python3.10-venv"
    elif command -v python3.9 &> /dev/null; then
        PYTHON_BIN="python3.9"
        PYTHON_VERSION="3.9"
        PYTHON_VENV_PKG="python3.9-venv"
    elif command -v python3 &> /dev/null; then
        PYTHON_BIN="python3"
        PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1-2)
        
        # Determinar paquete venv segun version
        case $PYTHON_VERSION in
            "3.13") PYTHON_VENV_PKG="python3.13-venv" ;;
            "3.12") PYTHON_VENV_PKG="python3.12-venv" ;;
            "3.11") PYTHON_VENV_PKG="python3.11-venv" ;;
            "3.10") PYTHON_VENV_PKG="python3.10-venv" ;;
            "3.9")  PYTHON_VENV_PKG="python3.9-venv" ;;
            *)      PYTHON_VENV_PKG="python3-venv" ;;
        esac
    else
        echo -e "${RED}ERROR: Python3 no encontrado${NC}"
        echo -e "${YELLOW}Instalando Python3...${NC}"
        sudo apt update && sudo apt install python3 python3-venv -y
        PYTHON_BIN="python3"
        PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1-2)
        PYTHON_VENV_PKG="python3-venv"
    fi
    
    echo -e "${GREEN}Python detectado: $PYTHON_BIN (version $PYTHON_VERSION)${NC}"
    echo -e "${BLUE}Paquete venv requerido: $PYTHON_VENV_PKG${NC}"
}

# Verificar e instalar python3-venv si es necesario
verificar_venv() {
    echo -e "${BLUE}[3/9] Verificando paquete venv...${NC}"
    
    # Verificar si el paquete venv especifico esta instalado
    if ! dpkg -l | grep -q "$PYTHON_VENV_PKG"; then
        echo -e "${YELLOW}Paquete $PYTHON_VENV_PKG no encontrado, instalando...${NC}"
        sudo apt update
        if sudo apt install -y "$PYTHON_VENV_PKG"; then
            echo -e "${GREEN}✓ $PYTHON_VENV_PKG instalado correctamente${NC}"
        else
            # Intentar con python3-venv generico
            echo -e "${YELLOW}Intentando con python3-venv generico...${NC}"
            if sudo apt install -y python3-venv; then
                echo -e "${GREEN}✓ python3-venv instalado${NC}"
            else
                echo -e "${RED}ERROR: No se pudo instalar paquete venv${NC}"
                echo -e "${YELLOW}Instala manualmente: sudo apt install $PYTHON_VENV_PKG${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${GREEN}✓ $PYTHON_VENV_PKG ya instalado${NC}"
    fi
}

# Limpiar configuraciones anteriores
echo -e "${BLUE}[4/9] Limpiando configuraciones anteriores...${NC}"
sed -i '/PVControl+ Permanent Activation/d' ~/.bashrc
sed -i '/PVControl+ Auto Activation/d' ~/.bashrc

# Instalar Thonny/herramientas primero
instalar_thonny_si_es_pc

# Detectar Python
detectar_python

# Verificar e instalar venv
verificar_venv

# Crear directorio si no existe
echo -e "${BLUE}[5/9] Preparando entorno...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Entorno virtual existente detectado, eliminando...${NC}"
    rm -rf "$VENV_DIR"
fi

# Crear entorno virtual
echo -e "${BLUE}[6/9] Creando entorno virtual...${NC}"
$PYTHON_BIN -m venv "$VENV_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: No se pudo crear el entorno virtual${NC}"
    echo -e "${YELLOW}Intentando solucionar problemas...${NC}"
    
    # Verificar si es problema de permisos
    if [ ! -w "$(dirname "$VENV_DIR")" ]; then
        echo -e "${YELLOW}Problema de permisos, ajustando...${NC}"
        sudo chown -R pi:pi "$PVC_HOME"
    fi
    
    # Intentar de nuevo
    echo -e "${YELLOW}Intentando crear entorno virtual de nuevo...${NC}"
    $PYTHON_BIN -m venv "$VENV_DIR" --clear
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Fallo critico al crear entorno virtual${NC}"
        echo -e "${YELLOW}Solucion manual:${NC}"
        echo -e "1. sudo apt install $PYTHON_VENV_PKG"
        echo -e "2. python3 -m venv $VENV_DIR"
        exit 1
    fi
fi

# Configurar pyvenv.cfg dinamicamente
echo -e "${BLUE}[7/9] Configurando pyvenv.cfg...${NC}"

# Obtener ruta real de Python
PYTHON_HOME=$(dirname $(which $PYTHON_BIN))

cat > "$VENV_DIR/pyvenv.cfg" << EOF
home = $PYTHON_HOME
include-system-site-packages = true
version = $PYTHON_VERSION
executable = $(which $PYTHON_BIN)
command = $PYTHON_BIN -m venv $VENV_DIR
EOF

# Configurar activacion PERMANENTE
echo -e "${BLUE}[8/9] Configurando activacion permanente...${NC}"
cat >> ~/.bashrc << 'EOF'

# ======= PVControl+ Permanent Activation =======
# Activar entorno virtual siempre
if [ -f "/home/pi/PVControl+/env/bin/activate" ]; then
    source /home/pi/PVControl+/env/bin/activate
fi

# Cambiar al directorio PVControl+ al abrir terminal
if [ -d "/home/pi/PVControl+" ]; then
    cd "/home/pi/PVControl+"
fi

# Configurar PATH para usar Python del entorno virtual
export PATH="/home/pi/PVControl+/env/bin:$PATH"
alias python="/home/pi/PVControl+/env/bin/python"
alias python3="/home/pi/PVControl+/env/bin/python3"
alias pip="/home/pi/PVControl+/env/bin/pip"
alias pip3="/home/pi/PVControl+/env/bin/pip3"
EOF

# Activar ahora
echo -e "${BLUE}[9/9] Activando e instalando dependencias...${NC}"
source "$VENV_DIR/bin/activate"
export PATH="$VENV_DIR/bin:$PATH"

# Actualizar pip y herramientas
echo -e "${BLUE}Actualizando pip y setuptools...${NC}"
pip install --upgrade pip setuptools wheel

# Instalar dependencias con manejo de errores mejorado
echo -e "${BLUE}Instalando dependencias Python...${NC}"

# Lista de dependencias principales (deberian funcionar con Thonny/herramientas)
DEPENDENCIAS_PRINCIPALES=(
    "paho-mqtt<2.0.0"
    "colorama"
    "pymodbus"
    "luma.core"
    "luma.oled"
    "bleak"
    "pymodbusTCP"
    "minimalmodbus"
    "esptool"
    "pyTelegramBotAPI"
    "pyautogui"
    "timeout_decorator"
    "clarifai"
    "goodwe"
    "pysolarmanv5"
    "can"
    "cantools"
    "psutil"
    "packaging"
    "tinytuya"
    "pyhOn"
)

# Dependencias que requieren compilacion (ahora deberian funcionar)
DEPENDENCIAS_COMPILACION=(
    "smbus"           
    "smbus2"           # Alternativa mejor a smbus
    "adafruit-ads1x15"
    "adafruit-circuitpython-ads1x15"
    "keyboard"         # Alternativa ligera a pynput
    
    "crc16"
    "crcmod"           # Alternativa a crc16
)

# Para Bookworm
if [ "$ES_BOOKWORM" = true ]; then
    echo -e "${YELLOW}Bookworm detectado - añadiendo mysql-connector-python${NC}"
    DEPENDENCIAS_PRINCIPALES+=("mysql-connector-python")
fi

# Para Raspberry Pi
if [ "$ES_RASPBERRY" = true ]; then
    echo -e "${YELLOW}Raspberry Pi detectada - añadiendo RPi.GPIO${NC}"
    DEPENDENCIAS_PRINCIPALES+=("RPi.GPIO")
    
    # Intentar smbus original para Raspberry Pi
    DEPENDENCIAS_COMPILACION+=("smbus")
fi

echo -e "${BLUE}Instalando dependencias principales...${NC}"
for dep in "${DEPENDENCIAS_PRINCIPALES[@]}"; do
    echo -e "${BLUE}Instalando: $dep${NC}"
    if pip install "$dep" --quiet; then
        echo -e "${GREEN}✓ $dep instalado${NC}"
    else
        echo -e "${YELLOW}⚠ Problema con $dep, intentando sin version especifica...${NC}"
        dep_name=$(echo "$dep" | sed 's/[<>=!].*//')
        if pip install "$dep_name" --quiet; then
            echo -e "${GREEN}✓ $dep_name instalado (sin version especifica)${NC}"
        else
            echo -e "${YELLOW}⚠ No se pudo instalar $dep_name - se omitirá${NC}"
        fi
    fi
    echo "-----"
done

echo -e "${BLUE}Instalando dependencias que requieren compilacion...${NC}"
for dep in "${DEPENDENCIAS_COMPILACION[@]}"; do
    echo -e "${BLUE}Intentando: $dep${NC}"
    
    if pip install "$dep" --quiet 2>/dev/null; then
        echo -e "${GREEN}✓ $dep instalado (compilacion exitosa)${NC}"
    else
        echo -e "${YELLOW}⚠ No se pudo compilar $dep${NC}"
        
        # Sugerencias especificas
        case "$dep" in
            "smbus")
                if [ "$ES_RASPBERRY" = true ]; then
                    echo -e "${YELLOW}  Para Raspberry Pi, usa: sudo apt install python3-smbus${NC}"
                fi
                ;;
            "adafruit-circuitpython-ads1x15")
                echo -e "${YELLOW}  Alternativa: pip install adafruit-ads1x15${NC}"
                ;;
        esac
    fi
    echo "-----"
done

# Verificar configuracion
echo -e "${BLUE}Verificando configuracion...${NC}"
echo -e "${YELLOW}Python detectado: $PYTHON_BIN${NC}"
echo -e "${YELLOW}Version Python: $PYTHON_VERSION${NC}"
echo -e "${YELLOW}Ruta Python: $(which $PYTHON_BIN)${NC}"
echo -e "${YELLOW}Entorno virtual: $VENV_DIR${NC}"

# Verificar que el entorno funciona
if [ -f "$VENV_DIR/bin/python" ]; then
    echo -e "${GREEN}Verificando Python...${NC}"
    "$VENV_DIR/bin/python" -c "import sys; print(f'✓ Python {sys.version.split()[0]} en entorno virtual')"
    
    # Verificar paquetes criticos
    echo -e "${GREEN}Verificando paquetes criticos...${NC}"
    
    "$VENV_DIR/bin/python" -c "
paquetes_criticos = [
    ('paho.mqtt', 'paho-mqtt'),
    ('mysql.connector', 'mysql-connector-python'),
    ('pymodbus', 'pymodbus'),
    ('psutil', 'psutil'),
]

for modulo, nombre in paquetes_criticos:
    try:
        __import__(modulo)
        print(f'✓ {nombre}: OK')
    except ImportError:
        print(f'✗ {nombre}: FALLO')
"
    
    # Verificar paquetes de compilacion
    echo -e "${GREEN}Verificando paquetes compilados...${NC}"
    
    "$VENV_DIR/bin/python" -c "
paquetes_compilados = [
    ('smbus2', 'smbus2'),
    ('keyboard', 'keyboard'),
    ('crcmod', 'crcmod'),
]

for modulo, nombre in paquetes_compilados:
    try:
        __import__(modulo)
        print(f'✓ {nombre}: OK (compilado)')
    except ImportError:
        print(f'✗ {nombre}: No compilado')
"
else
    echo -e "${RED}ERROR: Entorno virtual no creado correctamente${NC}"
fi

# Resumen
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   PYTHON CONFIGURADO CORRECTAMENTE${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${BLUE}Plataforma: $([ "$ES_RASPBERRY" = true ] && echo "Raspberry Pi" || echo "PC")${NC}"
echo -e "${BLUE}Python: $PYTHON_BIN ($PYTHON_VERSION)${NC}"
echo -e "${BLUE}Entorno virtual: $VENV_DIR${NC}"
echo -e "${BLUE}include-system-site-packages: true${NC}"
echo ""
echo -e "${YELLOW}RESUMEN INSTALACION:${NC}"
if [ "$ES_RASPBERRY" = false ]; then
    echo -e "${YELLOW}• Thonny instalado (trae herramientas de desarrollo)${NC}"
fi
echo -e "${YELLOW}• Entorno virtual Python creado${NC}"
echo -e "${YELLOW}• Dependencias principales instaladas${NC}"
echo -e "${YELLOW}• Paquetes que requieren compilacion intentados${NC}"
echo ""
echo -e "${YELLOW}Entorno virtual activado permanentemente${NC}"
echo -e "${YELLOW}Terminal cambiara automaticamente a PVControl+${NC}"
echo -e "${GREEN}=========================================${NC}"