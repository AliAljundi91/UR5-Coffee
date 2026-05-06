import serial
import time

class ScaleReader:
    def __init__(self, port='COM3', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # allow Arduino reset

        # flush startup noise
        for _ in range(5):
            self.ser.readline()

    def get_weight(self):
        while True:
            line = self.ser.readline().decode('utf-8').strip()

            if "Weight:" in line:
                try:
                    value = float(line.split("Weight:")[1].replace("g", "").strip())
                    return value
                except:
                    continue

    def get_stable_weight(self, samples=5):
        values = []

        while len(values) < samples:
            line = self.ser.readline().decode('utf-8').strip()

            if "Weight:" in line:
                try:
                    val = float(line.split("Weight:")[1].replace("g", "").strip())
                    values.append(val)
                except:
                    continue

        return sum(values) / len(values)
    
""""
# Example usage
scale = ScaleReader('COM3', 9600)
while True:
    weight = scale.get_stable_weight()
    print(f"Stable Weight: {weight:.2f} g")
    time.sleep(1)
"""
