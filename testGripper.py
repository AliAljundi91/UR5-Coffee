from VG10Control import VG10
import time
import traceback
from datetime import datetime

GRIPPER_IP = "192.168.1.1"

LOG_FILE = "vacuum_debug_log.txt"

# Scan range
START_REGISTER = 0
END_REGISTER = 80

POLL_DELAY = 0.5


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"

    print(full_msg)

    with open(LOG_FILE, "a") as f:
        f.write(full_msg + "\n")


def safe_read_input(gripper, reg):
    try:
        result = gripper.client.read_input_registers(
            address=reg,
            count=1,
            slave=gripper.slave_id
        )

        if result.isError():
            return None

        return result.registers[0]

    except:
        return None


def safe_read_holding(gripper, reg):
    try:
        result = gripper.client.read_holding_registers(
            address=reg,
            count=1,
            slave=gripper.slave_id
        )

        if result.isError():
            return None

        return result.registers[0]

    except:
        return None


try:
    log("Starting VG10 register scan")

    gripper = VG10(GRIPPER_IP)

    log("Connecting...")
    gripper.connect()
    log("Connected")

    log("Activating vacuum")
    gripper.grip_a(60)
    gripper.grip_b(60)

    time.sleep(5)

    previous_values = {}

    log("Starting live register monitoring")
    log("PUT A BAG ON/OFF NOW")

    while True:

        for reg in range(START_REGISTER, END_REGISTER + 1):

            input_value = safe_read_input(gripper, reg)
            holding_value = safe_read_holding(gripper, reg)

            key_input = f"I_{reg}"
            key_holding = f"H_{reg}"

            # Detect changes only
            if previous_values.get(key_input) != input_value:
                log(f"INPUT Reg {reg}: {input_value}")
                previous_values[key_input] = input_value

            if previous_values.get(key_holding) != holding_value:
                log(f"HOLDING Reg {reg}: {holding_value}")
                previous_values[key_holding] = holding_value

        time.sleep(POLL_DELAY)

except Exception as e:
    log(f"FATAL ERROR: {e}")
    log(traceback.format_exc())

finally:
    try:
        log("Releasing vacuum")
        gripper.release_a()
        gripper.release_b()
    except:
        pass

    log("Script ended")