#!/bin/bash

## Web
#sudo ln -s /home/pi/PVControl+/html /var/www/html

## Servicios basicos
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv.service /etc/systemd/system/fv.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_temp.service /etc/systemd/system/fv_temp.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_oled.service /etc/systemd/system/fv_oled.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fvbot.service /etc/systemd/system/fvbot.service

## Servicios PCB
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_mux.service /etc/systemd/system/fv_mux.service

## Sercivio crontab
sudo ln -s /home/pi/PVControl+/etc/cron.d/pvcontrol /etc/cron.d/pvcontrol 

## Servicios Utilidades
sudo ln -s /home/pi/PVControl+/etc/systemd/system/motion.service /etc/systemd/system/motion.service

## Servicios por equipamiento
sudo ln -s /home/pi/PVControl+/etc/systemd/system/hibrido.service /etc/systemd/system/hibrido.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/victron.service /etc/systemd/system/victron.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/bmv.service /etc/systemd/system/bmv.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/srne.service /etc/systemd/system/srne.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fronius.service /etc/systemd/system/fronius.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/huawei.service /etc/systemd/system/huawei.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/must.service /etc/systemd/system/must.service

sudo ln -s /home/pi/PVControl+/etc/systemd/system/sma.service /etc/systemd/system/sma.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/sma_meter.service /etc/systemd/system/sma_meter.service



