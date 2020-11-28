from time import time
from serial import Serial

serialDevice = "/dev/ttyS0" # default for RaspberryPi
maxwait = 3 # seconds to try for a good reading before quitting

def measure(portName):
    sensorData = None
    ser = Serial(portName, 9600, 8, 'N', 1, timeout=1)
    timeStart = time()
    valueCount = 0
    mm = 0

    while time() < timeStart + maxwait:
        if ser.inWaiting():
            bytesToRead = ser.inWaiting()
            valueCount += 1
            if valueCount < 2: # 1st reading may be partial number; throw it out
                continue
            testData = ser.read(bytesToRead)
            if testData.startswith(b'R'):
                # data received did not start with R
                #print("Read data didn't start with R! Read data: ", testData)
                #continue
                try:
                    sensorData = testData.decode('utf-8').lstrip('R')
                except UnicodeDecodeError:
                # data received could not be decoded properly
                    print ("Wasn't UNICODE!")
                    continue
                try:
                    print ("HERE", sensorData)
                    mm = int(sensorData)
                except ValueError:
                # value is not a number
                #print("Data read was not int-like!")
                    continue
            ser.close()
            return(mm)

    ser.close()
    raise RuntimeError("Expected serial data not received")

if __name__ == '__main__':
    measurement = measure(serialDevice)
    print("distance =",measurement)