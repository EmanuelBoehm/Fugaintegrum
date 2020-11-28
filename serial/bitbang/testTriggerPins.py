import pigpio
import time
import RPi.GPIO as GPIO
import sys


#gpin = 4 #NOT working
#gpin = 3 #NOT working

#gpin = 16 # WORKS
#gpin = 12 #WORKS
#gpin = 25 #WORKS
gpin = 24 #WORKS

pi = pigpio.pi()
pi.set_mode(gpin, pigpio.OUTPUT)
level = pi.read(gpin)
oldLevel = level
print("gpin", gpin, "is at level", level)
if level == 1:
    print("Writing a 0 to gpin", gpin)
    pi.write(gpin, 0)
    level = pi.read(gpin)
    print("gpin", gpin, "level is now", level)
else:
    print("Writing a 1 to gpin", gpin)
    pi.write(gpin, 1)
    level = pi.read(gpin)
    print("gpin", gpin, "level is now", level)

if level == oldLevel:
    print("GPIO level was NOT changed!!!!!")
    
