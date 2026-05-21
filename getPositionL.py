import time
from rtde_receive import RTDEReceiveInterface

robot_ip = "192.168.1.10"
rtde_r = RTDEReceiveInterface(robot_ip)

print("Starting TCP pose logger... Move robot freely.")

try:
    
    tcp = rtde_r.getActualTCPPose()

    tcp_rounded = [round(v, 4) for v in tcp]

    print(f"TCP Pose: {tcp_rounded}")

except KeyboardInterrupt:
    print("Stopped logging.")