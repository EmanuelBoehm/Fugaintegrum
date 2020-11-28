#!/usr/bin/env python
import time
import serial

ser = serial.Serial('/dev/ttyS0', 9600, timeout=10)
word = []
ser.read(1) # skip first byte
while 1:
    readByte = ser.read(1)
    if readByte == b'\r':
        i = (word[0] << 16) | (word[1] << 8) | word[2]
        print(i)
        word = []
        ser.read(1)
    else:
        word.append(int(readByte))
