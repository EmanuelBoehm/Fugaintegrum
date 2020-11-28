from bitstring import BitArray
import serial

ser = serial.Serial('/dev/ttyS0', 9600, timeout=10)

s = BitArray(bytes=b'\x00\x00\x00\x00\x00\x00', length = 28, offset=1)
print("yo:", s.uint)

