import serial
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class ScaleReader:
    def __init__(self, port='COM3', baudrate=115200, timeout=5):
        try:
            logging.info(f"Opening serial port {port} at {baudrate} baud...")
            self.ser = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            logging.error(f"Failed to open serial port: {e}")
            raise

        time.sleep(3)

        # wait for Arduino ready (with timeout so it doesn't hang forever)
        logging.info("Waiting for Arduino READY...")
        start = time.time()

        while True:
            if time.time() - start > timeout:
                logging.error("Timeout waiting for Arduino READY")
                raise TimeoutError("Arduino did not send READY")

            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    logging.debug(f"RX: {line}")
            except Exception as e:
                logging.error(f"Serial read error while waiting for READY: {e}")
                continue

            if line == "READY":
                logging.info("Arduino is READY")
                break

        self.ser.reset_input_buffer()

        # AUTO TARE ON STARTUP
        self.tare()

    def tare(self):
        try:
            logging.info("Sending TARE command...")
            self.ser.write(b"TARE\n")
        except Exception as e:
            logging.error(f"Failed to send TARE: {e}")
            return

        start = time.time()
        timeout = 5

        while True:
            if time.time() - start > timeout:
                logging.error("Timeout waiting for TARED response")
                raise TimeoutError("No TARED from Arduino")

            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                logging.debug(f"RX: {line}")

            if line == "TARED":
                logging.info("Scale tared successfully")
                break

        self.ser.reset_input_buffer()

    def get_weight(self):
        while True:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                logging.debug(f"RX: {line}")

                if "Weight:" in line:
                    return float(line.split("Weight:")[1].replace("g", "").strip())

            except ValueError:
                logging.warning(f"Could not parse weight from line: {line}")
            except Exception as e:
                logging.error(f"Error in get_weight: {e}")

    def get_stable_weight(self, tolerance=2.0, stable_reads=2):
        last_value = None
        stable_count = 0

        while True:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                logging.debug(f"RX: {line}")

                if "Weight:" not in line:
                    continue

                value = float(line.split("Weight:")[1].replace("g", "").strip())

                if last_value is not None and abs(value - last_value) <= tolerance:
                    stable_count += 1
                else:
                    stable_count = 0

                last_value = value

                if stable_count >= stable_reads:
                    #logging.info(f"Stable weight detected: {value} g")
                    return value

            except ValueError:
                logging.warning(f"Parse error on line: {line}")
            except Exception as e:
                logging.error(f"Error in get_stable_weight: {e}")