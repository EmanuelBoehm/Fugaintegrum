import RPi.GPIO as GPIO
import time


duration_in_sec_per_inch = 147 * 10**(-6)
triggerResponseTime = 0.00002
echoPinNum1 = 12
triggerPinNum1 = 5

#echoPinNum2 = 5
#triggerPinNum2 = 11


def readRange(echoPinNum):
    pulse_start_time = 0
    pulse_end_time = 0
    print("Pulse is 0")
    while GPIO.input(echoPinNum) == 0:
        pulse_start_time = time.time()
    print("pule has switched to 1")
    while GPIO.input(echoPinNum) == 1:
        pulse_end_time = time.time()
    
    pulse_duration = pulse_end_time - pulse_start_time
    distance = round(pulse_duration / duration_in_sec_per_inch, 2)
    print("Distance in inch: ", distance)
    
def trigger(triggerPinNum):
    t1 = time.time()
    GPIO.output(triggerPinNum, GPIO.HIGH)
    time.sleep(triggerResponseTime)
    GPIO.output(triggerPinNum, GPIO.LOW)
    t2 = time.time()
    print("Triggerd pin", triggerPinNum, "for", (t2-t1)*10**(6), "uS")

        
        
def setup():
    print("Setting up pins")
    GPIO.setmode(GPIO.BOARD) # BCM
    
    #GPIO.setup(triggerPinNum1, GPIO.OUT)
    #GPIO.output(triggerPinNum1, GPIO.LOW)
    GPIO.setup(echoPinNum1, GPIO.IN)
    
    
    #GPIO.setup(triggerPinNum2, GPIO.OUT)
    #GPIO.output(triggerPinNum2, GPIO.LOW)
    #GPIO.setup(echoPinNum2, GPIO.IN)
    time.sleep(2);
    #print("Trigger pin1:", triggerPinNum1, "\nEcho pin1:", echoPinNum1, "\n\nTrigger pin2:", triggerPinNum2, "\nEcho pin2:", echoPinNum2)
    print("Pin:", echoPinNum1)
try:
    setup()
    #trigger(triggerPinNum1)
    while 1:
        readRange(echoPinNum1)
        time.sleep(1)
    
    #trigger(triggerPinNum2)
    #readRange(echoPinNum2)
except Exception as e:
    print("Aborted! Error:", e)
finally:
    GPIO.cleanup()
    
    
