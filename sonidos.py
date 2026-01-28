import subprocess
import sys


subprocess.call("omxplayer /opt/vc/src/hello_pi/hello_video/test.h264",shell=True)
subprocess.call("omxplayer --win 0,0,640,480 /opt/vc/src/hello_pi/hello_video/test.h264",shell=True)
subprocess.call("omxplayer ./sonidos/example.mp3",shell=True)
#subprocess.call("  ",shell=True)

"""
#result = subprocess.run([sys.executable, "-c", "import time; time.sleep(2)"], timeout=1)

result = subprocess.run(
    [sys.executable, "-c", "print('hola');raise ValueError('oops')"], capture_output=True, text=True
)
print("stdout:", result.stdout)
print("stderr:", result.stderr)
"""