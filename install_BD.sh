#!/bin/bash

echo
echo "Bienvenido al programa de instalación de la BD de PVControl"
echo


#crear base de datos

echo "Creando base de datos..."
sudo mysql -h localhost -u root -p$PVControl+ < /home/pi/PVControl+/PVControl+.sql
echo "Base de datos control_solar creada"

echo "Creando usuario rpi"
sudo mysql -h localhost -u root -p$PVControl+ -e "CREATE USER 'rpi'@'%' IDENTIFIED BY 'fv';"
echo "Usuario creado"


echo "otorgamos todos los privilegios al usuario rpi para la base de datos"
sudo mysql -h localhost -u root -p$PVControl+ -e "GRANT ALL PRIVILEGES ON *.* TO 'rpi'@'%' WITH GRANT OPTION;"

echo
sudo mysql -h localhost -u root -p$PVControl+ -e "FLUSH PRIVILEGES;"


echo
echo "Hecho"
