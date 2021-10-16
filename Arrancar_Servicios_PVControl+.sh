#!/bin/bash

## Web
#sudo ln -s /home/pi/PVControl+/html /var/www/html


## Servicios basicos ######
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv.service /etc/systemd/system/fv.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_temp.service /etc/systemd/system/fv_temp.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_oled.service /etc/systemd/system/fv_oled.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fvbot.service /etc/systemd/system/fvbot.service
## Activar 
sudo systemctl enable fv
sudo systemctl enable fvbot
sudo systemctl enable fv_temp
sudo systemctl enable fv_oled
## Reiniciar
sudo systemctl restart fv
sudo systemctl restart fvbot
sudo systemctl restart fv_temp
sudo systemctl restart fv_oled
## Status 
sudo systemctl status fv
sudo systemctl status fvbot
sudo systemctl status fv_temp
sudo systemctl status fv_oled

## Servicios PCB
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_mux.service /etc/systemd/system/fv_mux.service
sudo systemctl enable fv_mux
sudo systemctl restart fv_mux
sudo systemctl status fvmux


## Sercivio crontab
sudo chown root /home/pi/PVControl+/etc/cron.d/pvcontrol
sudo ln -s /home/pi/PVControl+/etc/cron.d/pvcontrol /etc/cron.d/pvcontrol 

## Servicios Utilidades
sudo ln -s /home/pi/PVControl+/etc/systemd/system/motion.service /etc/systemd/system/motion.service


## Servicios por equipamiento
sudo ln -s /home/pi/PVControl+/etc/systemd/system/hibrido.service /etc/systemd/system/hibrido.service
sudo systemctl enable hibrido
sudo systemctl restart hibrido
sudo systemctl status hibrido

sudo ln -s /home/pi/PVControl+/etc/systemd/system/victron.service /etc/systemd/system/victron.service
sudo systemctl enable victron
sudo systemctl restart victron
sudo systemctl status victron

sudo ln -s /home/pi/PVControl+/etc/systemd/system/bmv.service /etc/systemd/system/bmv.service
sudo systemctl enable bmv
sudo systemctl restart bmv
sudo systemctl status bmv

sudo ln -s /home/pi/PVControl+/etc/systemd/system/srne.service /etc/systemd/system/srne.service
sudo systemctl enable srne
sudo systemctl restart srne
sudo systemctl status srne
sudo systemctl enable fronius

sudo ln -s /home/pi/PVControl+/etc/systemd/system/fronius.service /etc/systemd/system/fronius.service
sudo systemctl restart fronius
sudo systemctl status fronius

sudo ln -s /home/pi/PVControl+/etc/systemd/system/huawei.service /etc/systemd/system/huawei.service
sudo systemctl enable huawei
sudo systemctl restart huawei
sudo systemctl status huawei

sudo ln -s /home/pi/PVControl+/etc/systemd/system/goodwe.service /etc/systemd/system/goodwe.service
sudo systemctl enable goodwe
sudo systemctl restart goodwe
sudo systemctl status goodwe

sudo ln -s /home/pi/PVControl+/etc/systemd/system/must.service /etc/systemd/system/must.service
sudo systemctl enable must
sudo systemctl restart must
sudo systemctl status must

sudo ln -s /home/pi/PVControl+/etc/systemd/system/sma.service /etc/systemd/system/sma.service
sudo systemctl enable sma
sudo systemctl restart sma
sudo systemctl status sma

sudo ln -s /home/pi/PVControl+/etc/systemd/system/sma_meter.service /etc/systemd/system/sma_meter.service
sudo systemctl enable sma_meter
sudo systemctl restart sma_meter
sudo systemctl status sma_meter

sudo ln -s /home/pi/PVControl+/etc/systemd/system/daikin.service /etc/systemd/system/daikin.service
sudo systemctl enable daikin
sudo systemctl restart daikin
sudo systemctl status daikin

sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_mqtt.service /etc/systemd/system/fv_mqtt.service
sudo systemctl enable fv_mqtt
sudo systemctl restart fv_mqtt
sudo systemctl status fv_mqtt


echo press Enter
read reply


