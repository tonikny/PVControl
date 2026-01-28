#!/bin/bash
# Configuracion Python para Trixie

# Colores brillantes y definidos
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
CYAN='\033[0;96m'
NC='\033[0m'

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}   CONFIGURANDO PYTHON PARA TRIXIE${NC}"
echo -e "${BLUE}=============================================${NC}"

# Limpiar configuraciones anteriores
echo -e "${BLUE}[INFO] Limpiando configuraciones anteriores...${NC}"
sed -i '/PVControl+ Permanent Activation/d' ~/.bashrc
sed -i '/PVControl+ Auto Activation/d' ~/.bashrc

# Crear entorno virtual
echo -e "${BLUE}[INFO] Creando entorno virtual...${NC}"
python -m venv /home/pi/PVControl+/env

# Configurar pyvenv.cfg para incluir paquetes del sistema
echo -e "${BLUE}[INFO] Configurando pyvenv.cfg...${NC}"
cat > /home/pi/PVControl+/env/pyvenv.cfg << 'EOF'
home = /usr/bin
include-system-site-packages = true
version = 3.13.5
executable = /usr/bin/python3.13
command = /home/pi/PVControl+/env/bin/python -m venv /home/pi/PVControl+/env
EOF

# Configurar activacion PERMANENTE
echo -e "${BLUE}[INFO] Configurando activacion permanente...${NC}"
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
echo -e "${BLUE}[INFO] Activando entorno...${NC}"
source /home/pi/PVControl+/env/bin/activate
export PATH="/home/pi/PVControl+/env/bin:$PATH"

# Instalar dependencias en el entorno virtual
echo -e "${BLUE}[INFO] Instalando dependencias Python...${NC}"
pip install "paho-mqtt<2.0.0"
pip install colorama pymodbus luma.core luma.oled bleak
pip install smbus adafruit-ads1x15 pymodbusTCP minimalmodbus esptool
pip install pyTelegramBotAPI pyautogui pynput timeout_decorator crc16
pip install clarifai goodwe pysolarmanv5 can cantools libscrc
pip install psutil packaging tinytuya pyhOn

# Verificar configuracion
echo -e "${BLUE}[INFO] Verificando configuracion...${NC}"
echo -e "${YELLOW}Contenido de pyvenv.cfg:${NC}"
cat /home/pi/PVControl+/env/pyvenv.cfg

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}   PYTHON CONFIGURADO CORRECTAMENTE${NC}"
echo -e "${GREEN}=============================================${NC}"
echo -e "${BLUE}NOTA: Entorno virtual activado permanentemente${NC}"
echo -e "${BLUE}NOTA: include-system-site-packages = true${NC}"