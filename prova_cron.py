import subprocess

print('######## Activando Procesos CRONTAB #########')
res = subprocess.run(['sudo','cp', '-n', '/home/pi/PVControl+/etc/cron.d/pvcontrol.DIST','/home/pi/PVControl+/etc/cron.d/pvcontrol'])
res = subprocess.run(['sudo','chown', 'root','/home/pi/PVControl+/etc/cron.d/pvcontrol'])
res = subprocess.run(['sudo','ln', '-s','/home/pi/PVControl+/etc/cron.d/pvcontrol','/etc/cron.d/pvcontrol'], capture_output=True)
print ('  ---- OK -----')