import time
import math

"""
Uso desde cualquier archivo:

from utils import Utils
...
...
Utils().pausa(x,y)
"""

class Utils:

    @staticmethod
    def pausa(x,y):
        t=time.time()
        resto=round(30000*(t/30-math.floor(t/30)),2)%x
        if resto<y:time.sleep((y-resto)/1000)
        else:time.sleep((x+y-resto)/1000)
