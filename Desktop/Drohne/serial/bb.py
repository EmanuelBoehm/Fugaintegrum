import pigpio
import time
import RPi.GPIO as GPIO
import sys
import time


pi = pigpio.pi()
sensorPositions = {"front" : 0, "back" : 1, "left" : 2, "right" : 3}
sensorKeys = sensorPositions.keys()

#inputPins   = [13, 6, 23, 17]
inputPins   = [13, 22, 23, 6]#, 22, 22]
#triggerPins = [16, 12, 24, 5]
triggerPins = [16, 17, 12, 24]#, 27, 18] #16
#invert      = [0, 0, 0, 0]
invert      = [1 for _ in inputPins]

triggerTime = 20 #uS
baudRate = 9600
bitsPerWord = 8
error = False
readingTrys = 3


def setupPins():
    print("########### BEGIN: setup() ###########")
    c = 0
    for input in inputPins:
        closeSerialGPIO(input)
        openSerialGPIO(input)
        if error:
            cleanAndExit()
        if invert[c] == 1:
            invertSerialGPIO(input)
            if error:
                cleanAndExit()
        c = c + 1
    
    for trig in triggerPins:
        setPinAsTrigger(trig)
        if error:
            cleanAndExit()
            
    time.sleep(2)
    print("########### END: setup() ###########")



def closeSerialGPIO(pin):
    try:
        pi.bb_serial_read_close(pin)
    except:
        print("Couldn't close serial read on GPIO", pin)

def openSerialGPIO(pin):
    status = pi.bb_serial_read_open(pin, baud=baudRate, bb_bits=bitsPerWord)
    if status == 0:
        print("GPIO", pin, "is ready for serial reading")
    else:
        print("Failed opening GPIO", pin, "for serial reading")
        error = True
        

def invertSerialGPIO(pin):
    status = pi.bb_serial_invert(pin, 1)
    if status == 0:
        print("Serial signal on GPIO", pin, "is now inverted")
    else:
        print("Failed inverting serial signal on GPIO", pin)
        error = True

def setPinAsTrigger(pin):
    pi.set_mode(pin, pigpio.OUTPUT)
    level = pi.read(pin)
    if level == 1:
        pi.write(pin, 0)
    else:
        print("GPIO", pin, "is set as trigger pin and is already pulled LOW")
        return None
        
    level = pi.read(pin)
    if level == 1:
        print("Failed at pulling pin", pin, "LOW")
        error = True
    else:
        print("GPIO", pin, "is set as trigger pin and is now pulled LOW")
    
        
def cleanAndExit():
    print("Quitting...")
    for pin in inputPins:
        closeSerialGPIO(pin)
    
    for pin in triggerPins:
        pi.write(pin, 0)
    
    print("Program quit!")
    sys.exit()



def readRange(sensorId):
    (count, data) = pi.bb_serial_read(inputPins[sensorId])
    if count and count == 5:
         dist = getRangeCM(data)
         return dist
    else:
        return None

def trigger(sensorId):
    pi.gpio_trigger(triggerPins[sensorId], pulse_len=triggerTime, level=1)
    
def getRangeCM(input):
    inches = 0
    try:
        inches = int(input[1:4])
    except:
        print("Failed converting to cm:", input)
        return None
        
    return round(inches * 2.54)

def getDist(position):
    if not position in sensorKeys:
        print("Given sensor position not valid: ", position)
        return None
        
    id = sensorPositions[position]
    c = 0
    while c < readingTrys:
        trigger(id)
        r = readRange(id)
        if r:
            print("range read " + position + " is: ", r, "cm")
            return r
        else:
            time.sleep(0.1)
        c = c + 1
    print("Failed reading range from " + position + " sensor")
    return None



setupPins()
getDist("front")



