#!/bin/bash

# ping router.
SERVER=192.168.0.1

#wlan interface
WLANINTERFACE=wlan0

# Envia dos pings, salida a /    dev/null
ping -I ${WLANINTERFACE} -c2 ${SERVER} > /dev/null

# If the return code from ping ($?) is not 0 (meaning there was an error)
if [ $? != 0 ]
then
# Restart the wireless interface
ifdown --force ${WLANINTERFACE}
ifup ${WLANINTERFACE}
fi
