#!/bin/bash

sudo systemctl disable fv
sudo systemctl disable fvbot
sudo systemctl disable fv_temp
sudo systemctl disable fv_oled

sudo systemctl disable fv_mux

sudo systemctl disable hibrido
sudo systemctl disable victron
sudo systemctl disable bmv
sudo systemctl disable srne
sudo systemctl disable fronius
sudo systemctl disable huawei
sudo systemctl disable sma
sudo systemctl disable sma_meter
sudo systemctl disable daikin


sudo systemctl disable fv_mqtt

echo press Enter
read reply




