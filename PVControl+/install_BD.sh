#!/bin/bash

clear

unset password
unset password1
unset rootpass

echo
echo "Bienvenido al programa de instalación de la BD y tablas,"
echo "para: RPi: Control Sistema Fotovoltaico"
echo
#usuario
echo -n "Introduce nombre de usuario: "
read usuario

echo
PROMPT="Introduce contraseña: "
while IFS= read -p "$PROMPT" -r -s -n 1 char; do
    if [[ $char == $'\0' ]]; then
        break
    fi
    PROMPT='*'
    password+="$char"
done
echo

echo
PROMPT="Vuelve a introducir la contraseña: "
while IFS= read -p "$PROMPT" -r -s -n 1 char; do
    if [[ $char == $'\0' ]]; then
        break
    fi
    PROMPT='*'
    password1+="$char"
done
echo

if [ "$password" != "$password1" ]; then
	echo
        echo "Error, la contraseña no coincide. Vuelve a empezar."
        exit 0

fi
echo


#base de datos
#echo -n "Introduce nombre de la base de datos: "
#read basedatos
#echo
basedatos="control_solar"

echo
PROMPT="Introduzca contraseña de root: "
while IFS= read -p "$PROMPT" -r -s -n 1 char; do
    if [[ $char == $'\0' ]]; then
        break
    fi
    PROMPT='*'
    rootpass+="$char"
done
echo


#crear base de datos

echo "Creando base de datos y otorgando permisos a $usuario..."

sudo mysql -h localhost -u root -p$rootpass $basedatos < control_solar.sql

#mysql -h localhost -u root -p$rootpass -e "CREATE DATABASE $basedatos"
#creamos usuario para conectar al servidor desde localhost con su contraseña


#sudo mysql -h localhost -u root -p$rootpass -e "GRANT USAGE ON *.* to $usuario@localhost identified by $password"
#otorgamos todos los privilegios al usuario para la base de datos
sudo mysql -h localhost -u root -p$rootpass -e "GRANT ALL PRIVILEGES on $basedatos.* to $usuario@localhost"
echo

echo "Creando valores por defecto de la Tabla Parametros..."
sudo mysql -h localhost -u $usuario -p$password $basedatos -e "INSERT INTO parametros (grabar_datos,grabar_reles,t_muestra,n_muestras_grab,id_parametros) VALUES ('S','N',5,1,1)"


#creamos tabla datos con el $usuario



echo
echo "Hecho"
