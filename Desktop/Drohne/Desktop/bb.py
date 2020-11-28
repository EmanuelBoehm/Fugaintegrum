import pigpio
import time
import RPi.GPIO as GPIO
import sys
import time

# this lib allows reading the ultra sonic sensors' distances

pi = pigpio.pi() # communicates with the proces pigpiod, which automatically starts with system

# positions of ultra sonic sensorts mounted onto the drone
sensorPositions = {"front" : 0, "back" : 1, "left" : 2, "right" : 3}
sensorKeys = sensorPositions.keys()

#inputPins   = [13, 6, 23, 17]
# inputPins is the list of GIPO pins for serial input into the pi
inputPins   = [13, 22, 23, 6]#, 22, 22]
#triggerPins = [16, 12, 24, 5]
# triggerPins is the list of pins for triggering the ultra sonic sensors before reading
triggerPins = [16, 17, 12, 24]#, 27, 18] #16
#invert      = [0, 0, 0, 0]

# invert pins (=1) when no inverter is used on tx pins of ultra sonic sensors
invert      = [1 for _ in inputPins]

# trigger duration for a sensor
triggerTime = 20 #uS

# reading baudrate
baudRate = 9600

# receiving bits to encode for one word
bitsPerWord = 8

# error while setting up
error = False

# reading attempts on a sensor before returns obstacle found
readingTrys = 3


# do not touch this method
# it sets up the specified GPIO pins in inputPins and triggerPins lists
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


# do not touch this method
# closes serial reading on specified GPIO pin
def closeSerialGPIO(pin):
    try:
        pi.bb_serial_read_close(pin)
    except:
        print("Couldn't close serial read on GPIO", pin)

# do not touch this method
# opens serial reading on specified GPIO pin
def openSerialGPIO(pin):
    status = pi.bb_serial_read_open(pin, baud=baudRate, bb_bits=bitsPerWord)
    if status == 0:
        print("GPIO", pin, "is ready for serial reading")
    else:
        print("Failed opening GPIO", pin, "for serial reading")
        error = True
        
# do not touch this method
# inverts receiving signal (from sensor into the pi) on specified GPIO pin
def invertSerialGPIO(pin):
    status = pi.bb_serial_invert(pin, 1)
    if status == 0:
        print("Serial signal on GPIO", pin, "is now inverted")
    else:
        print("Failed inverting serial signal on GPIO", pin)
        error = True


# do not touch this method
# sets specified GPIO pin as trigger pin
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
    
       
# is called if an error while setup occured
# tries closing and resetting GPIO pins
def cleanAndExit():
    print("Quitting...")
    for pin in inputPins:
        closeSerialGPIO(pin)
    
    for pin in triggerPins:
        pi.write(pin, 0)
    
    print("Program quit!")
    sys.exit()

# do !!!!NOT!!!! use this method to obtain a measured distance of specified sensor
# returns the measured range in cm of specified sensor
def readRange(sensorId):
    (count, data) = pi.bb_serial_read(inputPins[sensorId])
    if count and count == 5:
         dist = getRangeCM(data)
         return dist
    else:
        return None

# triggers specified sensor to perform a single measurement
def trigger(sensorId):
    pi.gpio_trigger(triggerPins[sensorId], pulse_len=triggerTime, level=1)


# converts serial signal obtained into integer (in cm)
def getRangeCM(input):
    inches = 0
    try:
        inches = int(input[1:4])
    except:
        print("Failed converting to cm:", input)
        return None
        
    return round(inches * 2.54)

# use this method to obtain a measured distance of specified sensor
# returns measured distance (in cm) of specified sensor
# if read distance was "None", will repeat "readingTrys" times to read distance
# if last reading is "None", it returns "None"
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
            #print("range read " + position + " is: ", r, "cm")
            return r
        else:
            time.sleep(0.1)
        c = c + 1
    print("Failed reading range from " + position + " sensor")
    return None



#setupPins()



