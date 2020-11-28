import pigpio
import time
import RPi.GPIO as GPIO


pi = pigpio.pi()
bitbangPin = 18
triggerPin = 3
triggerDurationMicroSeconds = 20


try:
    pi.bb_serial_read_close(bitbangPin)
except:
    print("Couldn't close serial read on GPIO", bitbangPin)

#pi.set_mode(triggerPin, pigpio.OUTPUT)
#triggerLevel = pi.read(triggerPin)
#print("Trigger is", triggerLevel)
#print("Trigger pin is at level", triggerLevel)
#if triggerLevel == 1:
#    pi.write(triggerPin, 0)
#    triggerLevel = pi.read(triggerPin)
#    print("GPIO", triggerPin, "is set to", triggerLevel, "-> chill!")


GPIO.setmode(GPIO.BCM)
GPIO.setup(triggerPin, GPIO.OUT)



status = pi.bb_serial_read_open(bitbangPin, baud=9600, bb_bits=8)
print("GPIO", bitbangPin, "is now used for serial input | Status:", status)

status = pi.bb_serial_invert(bitbangPin, 1)
print("Inverted signal on GPIO", bitbangPin, " | status:", status)

#print("Triggering GPIO", triggerPin, "for", triggerDurationMicroSeconds, "uS")

#pi.write(triggerPin, 1)
#if pi.wait_for_edge(triggerPin):
#    print("pin is high")
#else:
#    print("pin is low")
#print("trigger level is ", pi.read(triggerPin))
#time.sleep(0.00002)
#pi.write(triggerPin, 0)

#pi.gpio_trigger(triggerPin, pulse_len=20, level=1)
#print("Triggered! Will start reading now")



c=0
while c < 100 or True:
    #pi.write(triggerPin, 1)
    #GPIO.output(triggerPin, GPIO.HIGH)
    #time.sleep(0.00002)
    #pi.write(triggerPin, 0)
    #GPIO.output(triggerPin, GPIO.LOW)
    time.sleep(0.05)
    (count, data) = pi.bb_serial_read(bitbangPin)
    print("Read data:", data, "count:", count)
    
    c = c + 1
    

