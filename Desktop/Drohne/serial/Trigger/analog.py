from gpiozero import MCP3008
import time

pot = MCP3008(0)
readTime = 0
while True:
    print(pot.value)
    print("Reading #", readTime, "read")
    readTime = readTime +1
    time.sleep(0.1)