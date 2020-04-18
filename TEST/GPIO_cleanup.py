import RPi.GPIO as GPIO  
GPIO.setmode(GPIO.BCM)

GPIO.setup(15, GPIO.IN)

# the rest of your code would go here 

# when your code ends, the last line before the program exits would be...  
GPIO.cleanup() 

# remember, a program doesn't necessarily exit at the last line! 
