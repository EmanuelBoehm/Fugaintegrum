import serial
import time

con = serial.Serial('/dev/ttyS0', 57600, timeout=10)

print ("created con and is reading..")
while 1:
    s = con.read(1)
    print ("read the following:", ~int.from_bytes(s, byteorder='little'))
    print ("read the following:", s)

