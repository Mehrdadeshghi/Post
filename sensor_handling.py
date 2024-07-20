import time
import threading
from datetime import datetime
from gpio_handling import GPIOHandler

class StateMachine:
    def __init__(self):
        self.state = "INIT"
        self.lock = threading.Lock()

    def set_state(self, state):
        with self.lock:
            print(f"Transitioning to {state} state.")
            self.state = state

    def get_state(self):
        with self.lock:
            return self.state

class SensorHandler:
    def __init__(self, gpio_handler, state_machine, no_motion_threshold=60, power_check_interval=10, power_check_window=30):
        self.gpio_handler = gpio_handler
        self.state_machine = state_machine
        self.no_motion_threshold = no_motion_threshold
        self.power_check_interval = power_check_interval
        self.power_check_window = power_check_window
        self.last_power_check_time = time.time()
        self.status = {
            "message": "Waiting for motion...",
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "movements": {pin: [] for pin in self.gpio_handler.SENSOR_PINS},
            "cpu_temperature": 0,
            "system_uptime": 0,
            "network_activity": {"upload": 0, "download": 0},
            "active_processes": 0
        }

    def log_message(self, message, sensor=None):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.status["last_update"] = current_time
        if sensor:
            self.status["movements"][sensor].append(current_time)
        print(f"{current_time} - {message}")

    def monitor_sensors(self):
        while True:
            current_state = self.state_machine.get_state()
            current_time = time.time()

            if current_state == "WAITING_FOR_MOTION":
                for pin in self.gpio_handler.SENSOR_PINS:
                    sensor_input = self.gpio_handler.get_sensor_input(pin)

                    if sensor_input == GPIO.HIGH:
                        self.gpio_handler.movement_detected_times[pin].append(current_time)
                        self.gpio_handler.movement_detected_times[pin] = [t for t in self.gpio_handler.movement_detected_times[pin] if current_time - t <= 10]

                        if len(self.gpio_handler.movement_detected_times[pin]) >= 2:
                            self.log_message(f"Motion detected on GPIO {pin}! There is mail.", sensor=pin)
                            self.gpio_handler.movement_detected_times[pin] = []
                            self.gpio_handler.last_motion_time[pin] = current_time
                            self.state_machine.set_state("MOTION_DETECTED")
                            self.update_display(pin)
                    else:
                        if self.gpio_handler.last_motion_time[pin] and current_time - self.gpio_handler.last_motion_time[pin] > self.no_motion_threshold:
                            self.log_message(f"Mailbox is open. (No motion detected for threshold period on GPIO {pin})")
                            self.gpio_handler.last_motion_time[pin] = None
                            self.state_machine.set_state("MAILBOX_OPEN")

            elif current_state == "MOTION_DETECTED":
                time.sleep(2)  # Simulate processing time
                self.state_machine.set_state("WAITING_FOR_MOTION")

            elif current_state == "MAILBOX_OPEN":
                time.sleep(2)  # Simulate processing time
                self.state_machine.set_state("WAITING_FOR_MOTION")

            time.sleep(1)

    def update_display(self, pin):
        if pin == 25:
            # Code to update Mehrdad's display
            print("Updating display for Mehrdad")
        elif pin == 24:
            # Code to update Rezvaneh's display
            print("Updating display for Rezvaneh")
