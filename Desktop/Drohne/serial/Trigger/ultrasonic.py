from gpiozero import DistanceSensor as DS

signal = DS(echo=11, trigger=7)
print("Distance:", signal.distance)