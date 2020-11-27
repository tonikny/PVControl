#!/bin/bash

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




