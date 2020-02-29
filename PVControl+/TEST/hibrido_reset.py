#!/usr/bin/python
from usb.core import find as finddev
dev = finddev(idVendor=0x0665, idProduct=0x5161)
dev.reset()
