import pigpio
import time
import RPi.GPIO as GPIO
import sys


pi = pigpio.pi()
#inputGPIO = 17 #works
#inputGPIO = 27 #works
#inputGPIO = 22 #works
#inputGPIO = 6 #works
inputGPIO = 13 #works
triggerGPIO = 16
triggerTime = 20 #uS
baudRate = 9600
bitsPerWord = 8
invert = 1


def setupPins():
    closeSerialGPIO()
    print("Opening GPIO", inputGPIO, "for serial reading")
    status = pi.bb_serial_read_open(inputGPIO, baud=baudRate, bb_bits=bitsPerWord)
    if status == 0:
        print("GPIO", inputGPIO, "is ready for serial reading")
    else:
        print("Failed opening GPIO", inputGPIO, "for serial reading")
        cleanAndExit()
    if invert == 1:
        status = pi.bb_serial_invert(inputGPIO, 1)
        if status == 0:
            print("Serial signal on GPIO", inputGPIO, "is now inverted")
        else:
            print("Failed inverting serial signal on GPIO", inputGPIO)
        
    print("Setting GPIO", triggerGPIO, "as trigger pin")
    pi.set_mode(triggerGPIO, pigpio.OUTPUT)
    triggerLevel = pi.read(triggerGPIO)
    if triggerLevel == 0:
        print("Trigger GPIO", triggerGPIO, "is already set to 0 (LOW)")
    else:
        pi.write(triggerGPIO, 0)
        triggerLevel = pi.read(triggerGPIO)
        if triggerLevel == 1:
            print("Failed pulling trigger GPIO", triggerGPIO, "LOW")
            cleanAndExit()
        else:
            print("Trigger GPIO", triggerGPIO, "was set to 1 (HIGH) and is now back to", triggerLevel, "(LOW)")



def closeSerialGPIO():
    try:
        pi.bb_serial_read_close(inputGPIO)
    except:
        print("Couldn't close serial read on GPIO", inputGPIO)

def cleanAndExit():
    closeSerialGPIO()
    
    print("Program quit!")
    sys.exit()



def readRange():
    (count, data) = pi.bb_serial_read(inputGPIO)
    if count:
        print("Data:", data, "\t[Length=", (str(count)+"]"))
    else:
        print("Nothing to read!")

def trigger():
    pi.gpio_trigger(triggerGPIO, pulse_len=triggerTime, level=1)
    



setupPins()
#trigger()
while 1:
    trigger()
    readRange()
    time.sleep(1)