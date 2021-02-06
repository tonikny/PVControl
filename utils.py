import time

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
        a=round(t*1000,3)
        b=round(t,)*1000
        c=(a-b)%x
        if c < y: time.sleep((y-c)/1000)
        else: time.sleep((x+y-c)/1000)
    
