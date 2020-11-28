#!/usr/bin/env python
import time
import serial

ser = serial.Serial('/dev/ttyS0', 9600, timeout=10)
word = []
while 1:
    ser.read(1)
    readByte = ser.read(3)
    print("read: ", readByte, " -> Converted: ", int(readByte))
    ser.read(1)                     