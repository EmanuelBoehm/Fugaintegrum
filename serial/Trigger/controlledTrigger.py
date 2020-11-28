import RPi.GPIO as GPIO
import time
import serial

RXPinOnSensor1 = 5
RXPinOnSensor2 = 3
triggerResponseTime = 0.00002
ser = serial.Serial('/dev/ttyS0', 9600, timeout=10)

def setup():
    GPIO.setmode(GPIO.BOARD)  
    GPIO.setup(RXPinOnSensor1, GPIO.OUT)
    GPIO.output(RXPinOnSensor1, GPIO.LOW)
    
    GPIO.setup(RXPinOnSensor2, GPIO.OUT)
    GPIO.output(RXPinOnSensor2, GPIO.LOW)
    time.sleep(2)
    print("pins", RXPinOnSensor1, ",", RXPinOnSensor2, "are held low")
    
def trigger(sensorId):
    t1 = time.time()
    GPIO.output(sensorId, GPIO.HIGH)
    time.sleep(triggerResponseTime)
    GPIO.output(sensorId, GPIO.LOW)
    t2 = time.time()
    print("Triggerd pin", sensorId, "for", (t2-t1)*10**(6), "uS")

def readCurrentRange():
    ser.read(1)
    readByte = ser.read(3)
    print("read: ", readByte)#, " -> Converted: ", int(readByte))
    ser.read(1)


setup()

while 1:
    #trigger(RXPinOnSensor2)
    readCurrentRange()
    ser.read(10)
    time.sleep(0.05)