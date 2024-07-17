import busio
import digitalio
import board
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn

# SPI-Bus initialisieren
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)  # Chip select des ADC
mcp = MCP3008(spi, cs)

# Analogeingangspins erstellen
power_monitor = AnalogIn(mcp, MCP3008.P0)  # An welchem Pin des ADC der Spannungsteiler angeschlossen ist

def get_voltage(analog_input):
    return (analog_input.voltage * 3.3) / 4096

try:
    while True:
        voltage = get_voltage(power_monitor)
        if voltage > 1.0:  # Grenze einstellen, ab wann man annimmt, dass der PIR-Sensor Strom hat
            print("PIR-Sensor ist eingeschaltet.")
        else:
            print("PIR-Sensor ist ausgeschaltet.")
        time.sleep(1)
except KeyboardInterrupt:
    print("Programm wurde vom Benutzer gestoppt.")
