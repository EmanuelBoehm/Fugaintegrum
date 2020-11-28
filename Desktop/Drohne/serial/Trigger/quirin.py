import RPi.GPIO as GPIO
import time

echoPinNum = 11
#triggerPin = 7
#triggerResponseTime = 0.00002

def readRange():
    c = 0
    result = ""
    #GPIO.output(triggerPin, GPIO.HIGH)
    #time.sleep(triggerResponseTime)
    #GPIO.output(triggerPin, GPIO.LOW)
    while c < 50:
        if GPIO.input(echoPinNum) == 0:
            result = result + "0"
        else:
            result = result + "1"
        c = c + 1
        
    print("Range:", result)
    
    

        
        
def setup():
    print("Setting up pins")
    GPIO.setmode(GPIO.BOARD) # BCM
    

    GPIO.setup(echoPinNum, GPIO.IN)
    #GPIO.setup(triggerPin, GPIO.OUT)
    #GPIO.output(triggerPin, GPIO.LOW)
    time.sleep(2);
    #print("Trigger pin1:", triggerPinNum1, "\nEcho pin1:", echoPinNum1, "\n\nTrigger pin2:", triggerPinNum2, "\nEcho pin2:", echoPinNum2)
    print("Pin:", echoPinNum)
try:
    setup()
    while 1:
        readRange()
        time.sleep(0.1)
    #trigger(triggerPinNum2)
    #readRange(echoPinNum2)
except Exception as e:
    print("Aborted! Error:", e)
finally:
    GPIO.cleanup()
    
    

