#!/bin/bash


## Web
#sudo ln -s /home/pi/PVControl+/html /var/www/html

## Links Servicios
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv.service /etc/systemd/system/fv.service

sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_temp.service /etc/systemd/system/fv_temp.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_oled.service /etc/systemd/system/fv_oled.service

sudo ln -s /home/pi/PVControl+/etc/systemd/system/fvbot.service /etc/systemd/system/fvbot.service

sudo ln -s /home/pi/PVControl+/etc/systemd/system/motion.service /etc/systemd/system/motion.service

sudo ln -s /home/pi/PVControl+/etc/systemd/system/hibrido.service /etc/systemd/system/hibrido.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/victron.service /etc/systemd/system/victron.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/bmv.service /etc/systemd/system/bmv.service
sudo ln -s /home/pi/PVControl+/etc/systemd/system/srne.service /etc/systemd/system/srne.service

sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_mux.service /etc/systemd/system/fv_mux.service

## Cron
sudo ln -s /home/pi/PVControl+/etc/cron.d/pvcontrol /etc/cron.d/pvcontrol 



## Activar servicios
sudo systemctl enable fv
sudo systemctl enable fvbot
sudo systemctl enable fv_temp
sudo systemctl enable fv_oled
sudo systemctl enable hibrido
sudo systemctl enable victron
sudo systemctl enable bmv
sudo systemctl enable srne
sudo systemctl enable fv_mux

sudo systemctl restart fv
sudo systemctl restart fvbot
sudo systemctl restart fv_temp
sudo systemctl restart fv_oled
sudo systemctl restart hibrido
sudo systemctl restart victron
sudo systemctl restart bmv
sudo systemctl restart srne
sudo systemctl restart fv_mux


sudo systemctl status fv
sudo systemctl status fvbot
sudo systemctl status fv_temp
sudo systemctl status fv_oled
sudo systemctl status hibrido
sudo systemctl status victron
sudo systemctl status bmv
sudo systemctl status srne
sudo systemctl status fvmux


echo press Enter
read reply




