#!/bin/bash
# Script para instalar los servicios systemd para ADS

echo "=== Instalando servicios systemd para ADS ==="

# Copiar archivo de plantilla
sudo cp /home/pi/PVControl+/etc/systemd/system/fv_ads@.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar ADS1
echo "Habilitando ADS1..."
sudo systemctl enable fv_ads@ADS1.service
sudo systemctl start fv_ads@ADS1.service

# Habilitar e iniciar ADS4
echo "Habilitando ADS4..."
sudo systemctl enable fv_ads@ADS4.service
sudo systemctl start fv_ads@ADS4.service

# Mostrar estado
echo ""
echo "=== Estado de los servicios ==="
sudo systemctl status fv_ads@ADS1.service --no-pager
echo ""
sudo systemctl status fv_ads@ADS4.service --no-pager

# Mostrar logs recientes
echo ""
echo "=== Logs recientes ==="
sudo journalctl -u fv_ads@ADS1.service --no-pager -n 10
echo ""
sudo journalctl -u fv_ads@ADS4.service --no-pager -n 10

echo ""
echo "=== Instalación completada ==="
echo ""
echo "Comandos útiles:"
echo "  Ver estado:     sudo systemctl status fv_ads@ADS1.service"
echo "  Ver logs:       sudo journalctl -u fv_ads@ADS1.service -f"
echo "  Reiniciar:      sudo systemctl restart fv_ads@ADS1.service"
echo "  Detener:        sudo systemctl stop fv_ads@ADS1.service"
echo "  Habilitar:      sudo systemctl enable fv_ads@ADS1.service"
