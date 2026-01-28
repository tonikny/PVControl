#!/bin/bash

# Definir colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Impedir ejecución como root
if [ "$(id -u)" -eq 0 ]; then
    echo -e "${RED}Error: Este script no se debe ejecutar como root.${NC}" >&2
    exit 1
fi

# Nombre del entorno virtual
venv_name="env"

# Paths
pi_path="/home/pi"
pvcontrol_path="$pi_path/PVControl+"
venv_path="$pvcontrol_path/$venv_name"
venv_bin_path="$venv_path/bin"
bashrc_file="$pi_path/.bashrc"
pyenv_path="$venv_path/pyvenv.cfg"
desktop_path=$(xdg-user-dir DESKTOP)

# Git
git_repo="https://git.code.sf.net/p/pvcontrol/code"
git_branch="bookworm"

# Datos Bd
bd_user="rpi"
bd_pass="fv"
bd_host="localhost"
bd_name="control_solar"
bd_data="$pvcontrol_path/PVControl+.sql"

# Comandos base
comandos_base=(
    "######### Instalando comandos base #########"
    "sudo apt update"
    "sudo apt-get full-upgrade"
    "sudo chmod 755 $pi_path"
    "sudo apt install php8.2 php8.2-cli php8.2-common php8.2-curl php8.2-gd php8.2-intl php8.2-mbstring php8.2-mysql php8.2-opcache php8.2-readline php8.2-xml php8.2-xsl php8.2-zip php8.2-bz2 libapache2-mod-php8.2 -y"

    "######### Instalando MariaDB #########"
    "sudo apt install mariadb-server mariadb-client -y"
    "sudo mysql -uroot -e \"CREATE USER IF NOT EXISTS '$bd_user'@'$bd_host' IDENTIFIED BY '$bd_pass';\""
    "sudo mysql -uroot -e \"GRANT ALL PRIVILEGES ON *.* TO '$bd_user'@'$bd_host' WITH GRANT OPTION;\""
    "sudo mysql -uroot -e \"DROP DATABASE IF EXISTS $bd_name;\""
    "sudo mysql -uroot -e \"CREATE DATABASE $bd_name;\""
    "sudo mysql -uroot control_solar < $bd_data"

    "######### Instalando Phpmyadmin #########"
    "echo 'phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2' | sudo debconf-set-selections"
    "sudo DEBIAN_FRONTEND=noninteractive apt install phpmyadmin -y"
    "sudo cp /usr/share/phpmyadmin/config.sample.inc.php /usr/share/phpmyadmin/config.inc.php"
    "sudo sed -i 's/\$cfg\['\''blowfish_secret'\''\] = '\'''\'';/\$cfg['\''blowfish_secret'\''\] = '\''clave_secreta%PVControl+'\'';/' /usr/share/phpmyadmin/config.inc.php"
    "sudo a2enconf phpmyadmin"
    "sudo systemctl reload apache2"

    "######### Instalando Mosquitto MQTT #########"
    "sudo apt install mosquitto mosquitto-clients python3-paho-mqtt -y"
    "sudo bash -c 'echo \"allow_anonymous false\" > /etc/mosquitto/conf.d/default.conf'"
    "sudo bash -c 'echo \"listener 1883\" >> /etc/mosquitto/conf.d/default.conf'"
    "sudo bash -c 'echo \"password_file $pvcontrol_path/passwd_mosquitto\" >> /etc/mosquitto/conf.d/default.conf'"
    "sudo systemctl restart mosquitto"
    ""
)

# Instalar paquetes Python en entorno virtual
paquetes_python=(
    "######### Instalando paquetes Python #########"
    "sudo apt install python3-full python3-mysqldb -y"
    "python3 -m venv $venv_path" # Crear entorno virtual
    "source $venv_bin_path/activate" # Activar entorno virtual
    "pip install wheel"
    "pip install colorama click"
    "pip install pymodbus"
    "pip install pymodbusTCP"
    "pip install minimalmodbus"
    "pip install rpi.gpio"
    "pip install adafruit-ads1x15"
    "pip install timeout_decorator"
    "pip install libscrc"
    "pip install esptool"
    "pip install smbus"
    "pip install luma.core luma.oled"
    "pip install pyTelegramBotAPI"
    "pip install pyautogui"
    "pip install pynput"
    #"pip install clarifai"
    #"pip install clarifai-grpc" # parece no necesaria
    "pip install bleak"  # JK
    "pip install goodwe"
    "pip install pysolarmanv5" # DEYE
    "pip install can cantools" # Pylontech
    "pip install broadlink"
    "pip install requests xmltodict" #Aemet

    # Ruta del entorno virtual
    "sed -i '/#PVControl+/d' $bashrc_file"  # Eliminar #PVControl+ de .bashrc
    "echo \"export VIRTUAL_ENV=$venv_path #PVControl+\" >> $bashrc_file"
    # Eliminar y añadir en primera posicion la ruta del entorno virtual
    'echo "export PATH=\$(echo \$PATH | tr \":\" \"\\n\" | awk -v p=\"$venv_path\" '\''!x[\$0]++ && \$0 != p'\'' | paste -sd \":\" -)  #PVControl+" >> "$bashrc_file"'
    'echo "export PATH=\"$venv_path:\$PATH\"" >> "$bashrc_file"  #PVControl+'

    # Modificar o incluir include-system-site-packages en pyvenv.cfg
    "if [ ! -e \"$pyenv_path\" ]; then touch \"$pyvenv_path\"; fi"
    "sed -i '/include-system-site-packages/d' $pyenv_path"
    "echo \"include-system-site-packages = true\" >> \"$pyenv_path\""

    "deactivate" # Desactivar entorno virtual
    ""
)

# Clonar repositorio PVControl+
clonar_repositorio=(
    "cd $pi_path"
    "sudo rm -rf $pvcontrol_path"
    "######### Clonando repositorio PVControl+ #########"
    "git clone -b $git_branch $git_repo $pvcontrol_path"
    ""
)

web=(
    "######### Creando enlaces de la web #########"
    "sudo rm -R /var/www/html"
    "sudo ln -s $pvcontrol_path/html /var/www"
    ""
)

enlaces_escritorio=(
    "######### Creando enlaces escritorio #########"
    "ln -sf $pvcontrol_path/PVControl_Configuracion_Inicial.py $desktop_path/PVControl_Configuracion_Inicial.py"
    "ln -sf $pvcontrol_path/Arrancar_servicios_PVControl+.py $desktop_path/Arrancar_servicios_PVControl+.py"
    "ln -sf $pvcontrol_path/Parar_Servicios_PVControl+.py $desktop_path/Parar_Servicios_PVControl+.py"
    "ln -sf $pvcontrol_path/Ver_Programas_en_Ejecucion_PVControl+.sh $desktop_path/Ver_Programas_en_Ejecucion_PVControl+.sh"
    ""
)

docker_HA=(
    "######### Instalando Docker y Home Assistant #########"
    # Docker
    #"sudo apt install raspberrypi-kernel raspberrypi-kernel-headers"
    "curl -sSL https://get.docker.com | sh"
    "sudo usermod -aG docker pi"
    "newgrp docker"
    # Home Assistant
    "docker run -d --name homeassistant --privileged --restart=unless-stopped -e TZ=Europe/Madrid -v $pvcontrol_path/HA:/config --network=host ghcr.io/home-assistant/home-assistant:stable"
    "ln -sf $pvcontrol_path/PVControl+/PVControl_Instalacion_HomeAssistant.py $desktop_path/PVControl_Instalacion_HomeAssistant.py"
    ""
)

# Función para ejecutar comandos
ejecutar_comando() {
    if [[ $1 == "#"* ]]; then
        echo -e "${YELLOW}$1${NC}"
    elif [ -n "$1" ]; then
        echo -e "${GREEN}-> $1${NC}"
        eval "$1"
        return_code=$?
        if [ $return_code -ne 0 ]; then
            echo -e "${RED}Error al ejecutar comandos. Saliendo.${NC}"
            exit $return_code
        else
            echo -e "${GREEN}<- Ok${NC}"
            echo ""
        fi
    else
        echo ""
    fi
}

# Función de ayuda
mostrar_ayuda() {
    echo -e "Uso: $0 [opciones]"
    echo -e "Opciones:"
    echo -e "  -a: Ejecutar todos los comandos (excepto -d y -h)"
    echo -e "  -c: Clonar repositorio PVControl+ (${RED}se eliminará el directorio $pvcontrol_path si existe!${NC})"
    echo -e "  -b: Ejecutar comandos base (${RED}si ya existe la base de datos se eliminará y se perderán los datos!${NC})"
    echo -e "  -p: Crear, activar y desactivar el entorno virtual, instalar paquetes Python"
    echo -e "  -w: Crear enlace para la web de PVControl+"
    echo -e "  -l: Crear enlaces en el escritorio"
    echo -e "  -d: Instalar Docker y Home Assistant"
    echo -e "  -h: Mostrar esta ayuda"
    echo -e "Ejemplo de uso: $0 -b -p"
}

# Manejar opciones de comandos
while getopts ":cbpwldah" opt; do
    case $opt in
        c) comandos_a_ejecutar=("${clonar_repositorio[@]}");;
        b) comandos_a_ejecutar=("${comandos_base[@]}");;
        p) comandos_a_ejecutar=("${paquetes_python[@]}");;
        w) comandos_a_ejecutar=("${web[@]}");;
        l) comandos_a_ejecutar=("${enlaces_escritorio[@]}");;
        d) comandos_a_ejecutar=("${docker_HA[@]}");;
        a) comandos_a_ejecutar=(
            "${clonar_repositorio[@]}"
            "${comandos_base[@]}"
            "${paquetes_python[@]}"
            "${web[@]}"
            "${enlaces_escritorio[@]}"
        );;
        h|*) mostrar_ayuda; exit 0;;
    esac
done

# Verificar si no se proporcionaron opciones
if [ $OPTIND -eq 1 ]; then
    echo -e "${RED}No se proporcionaron opciones.${NC}"
    mostrar_ayuda
    exit 0
fi

# Ejecutar comandos seleccionados
for comando in "${comandos_a_ejecutar[@]}"; do
    ejecutar_comando "$comando"
done

echo -e "${YELLOW}######## Proceso Completado #####################${NC}"
echo ""
