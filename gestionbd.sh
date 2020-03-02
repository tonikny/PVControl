#!/bin/bash

usuario="rpi"
password="fv"
basedatos="control_solar"

DATE=`date +%Y-%m-%d`
SQLFILE=$basedatos-${DATE}.sql.gz

### creamos copia de la base de datos
mysqldump -u $usuario -p$password --opt --single-transaction --quick $basedatos  | gzip > /home/pi/PVControl+/backBD/$SQLFILE

### eliminamos las copias de seguridad con mas de 10 dias de antiguedad
find /home/pi/PVControl+/backBD/$basedatos* -mtime +10 -exec rm {} \;
