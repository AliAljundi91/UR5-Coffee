import time
from rtde_receive import RTDEReceiveInterface

robot_ip = "192.168.1.10"
rtde_r = RTDEReceiveInterface(robot_ip)

print("Starting TCP logger... Move robot freely.")

try:
    while True:
        tcp = rtde_r.getActualQ()
        tcp_rounded = [round(v, 2) for v in tcp]

        print(f"Joint Positions: {tcp_rounded}")
        time.sleep(5)

except KeyboardInterrupt:
    print("Stopped logging.")