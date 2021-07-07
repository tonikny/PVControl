#!/bin/bash
######
usuario="rpi"
password="fv"
basedatos="control_solar"


echo "Creando tablas necesarias...un momento..."
#creamos tabla datos con el $usuario
echo "Creando tabla open_evse"
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE open_evse (
Fecha date NOT NULL,
kWh_evse float NOT NULL,
PRIMARY KEY Fecha)"

echo "Creando tabla open_evse_partial"
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE open_evse_partial (
Fecha datetime NOT NULL,
kWh_evse float NOT NULL,
PRIMARY KEY Fecha)"


echo
echo "Tablas OPENEVSE creadas"
