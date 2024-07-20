from gpiozero import MotionSensor
from signal import pause

pir_24 = MotionSensor(24)
pir_25 = MotionSensor(25)

pir_24.when_motion = lambda: print("Bewegung erkannt: Rezvaneh")
pir_25.when_motion = lambda: print("Bewegung erkannt: Mehrdad")

pause()
