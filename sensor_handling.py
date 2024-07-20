import time
from datetime import datetime, timedelta

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
        self.status["message"] = message
        self.status["last_update"] = current_time
        if "motion detected" in message.lower() and sensor is not None:
            self.status["movements"][sensor].append(current_time)
        print(f"{current_time} - {message}")

    def check_sensor(self):
        while True:
            current_state = self.state_machine.get_state()
            current_time = time.time()

            if current_state == "INIT":
                self.log_message("Initializing...")
                self.state_machine.set_state("WAITING_FOR_MOTION")

            elif current_state == "WAITING_FOR_MOTION":
                for pin in self.gpio_handler.SENSOR_PINS:
                    sensor_input = self.gpio_handler.get_sensor_input(pin)

                    # Update power check status
                    if current_time - self.last_power_check_time > self.power_check_interval:
                        self.last_power_check_time = current_time
                        self.gpio_handler.power_check_status[pin].append((current_time, sensor_input))
                        self.gpio_handler.power_check_status[pin] = [status for status in self.gpio_handler.power_check_status[pin] if current_time - status[0] <= self.power_check_window]

                        # Check if PIR has no power
                        if len(self.gpio_handler.power_check_status[pin]) > 0 and all(status[1] == 0 for status in self.gpio_handler.power_check_status[pin]):
                            self.log_message(f"Mailbox is open. (PIR on GPIO {pin} has no power)")
                            self.state_machine.set_state("MAILBOX_OPEN")

                    if sensor_input == GPIO.HIGH:
                        self.gpio_handler.movement_detected_times[pin].append(current_time)
                        self.gpio_handler.movement_detected_times[pin] = [t for t in self.gpio_handler.movement_detected_times[pin] if current_time - t <= 10]

                        if len(self.gpio_handler.movement_detected_times[pin]) >= 2:
                            self.log_message(f"Motion detected on GPIO {pin}! There is mail.", sensor=pin)
                            self.gpio_handler.movement_detected_times[pin] = []
                            self.gpio_handler.last_motion_time[pin] = current_time
                            self.state_machine.set_state("MOTION_DETECTED")
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
