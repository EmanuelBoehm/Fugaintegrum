import pigpio
import time
import RPi.GPIO as GPIO
import sys


pi = pigpio.pi()


sensor_N = 0
sensor_NO = 1
sensor_SO = 2
sensor_O = 3
sensor_SW = 4
sensor_S = 5


names = {sensor_N : "North", sensor_NO : "North East", sensor_SO : "SE", sensor_O : "East", sensor_SW : "SW", sensor_S : "SS"}

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

# initializes and sets up the given input and trigger pins
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
            
    print("########### END: setup() ###########")


# closes a GPIO pin
def closeSerialGPIO(pin):
    try:
        pi.bb_serial_read_close(pin)
    except:
        print("Couldn't close serial read on GPIO", pin)

# opens a GPIO pin for serial reading
def openSerialGPIO(pin):
    status = pi.bb_serial_read_open(pin, baud=baudRate, bb_bits=bitsPerWord)
    if status == 0:
        print("GPIO", pin, "is ready for serial reading")
    else:
        print("Failed opening GPIO", pin, "for serial reading")
        error = True
        
# inverts the serial signal obtained from the given pin
def invertSerialGPIO(pin):
    status = pi.bb_serial_invert(pin, 1)
    if status == 0:
        print("Serial signal on GPIO", pin, "is now inverted")
    else:
        print("Failed inverting serial signal on GPIO", pin)
        error = True

# initializes given pin to be used as a trigger pin
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
    
# exit program on error and closes pins     
def cleanAndExit():
    print("Quitting...")
    for pin in inputPins:
        closeSerialGPIO(pin)
    
    for pin in triggerPins:
        pi.write(pin, 0)
    
    print("Program quit!")
    sys.exit()


# reads the serial signal on given sensor id and converts it to cm
def readRange(sensorId):
    (count, data) = pi.bb_serial_read(inputPins[sensorId])
    if count and count == 5:
        #if id < 5:
          #  print("[" + names.get(sensorId) + "]", "\tRange:", getRangeCM(data), "cm  ", end='')
        #else:
          #print("[" + names.get(sensorId) + "]", "\tRange:", getRangeCM(data), "cm  ", end='')  print("[" + names.get(sensorId) + "]", "\tRange:", getRangeCM(data), "cm", " \r", end='')
         dist = getRangeCM(data)
         print("[" + str(sensorId) + "]", "\tRange:", dist, "cm ")
         return dist
    else:
        print("[" + str(sensorId) + "]", "\tNothing to read!")
        return None

# triggers the given sensor id
def trigger(sensorId):
    pi.gpio_trigger(triggerPins[sensorId], pulse_len=triggerTime, level=1)

# parses serial signal and returns corresponding cm measured
def getRangeCM(input):
    inches = 0
    try:
        inches = int(input[1:4])
    except:
        print("Failed reading range from input:", input)
        return -1
        
    return round(inches * 2.54)

# triggers sensor id then reads the distance
def getDist(id):
    trigger(id)
    return readRange(id)
    

setupPins()
time.sleep(1)

while 1:
    for t in [0]:
        x = getDist(t)
        print("d=", x)
        #trigger(t)
        #readRange(t)
        time.sleep(1.0/15)
    time.sleep(0.5)
    print("")

