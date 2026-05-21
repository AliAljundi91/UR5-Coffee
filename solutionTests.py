from rtde_control import RTDEControlInterface
from rtde_receive import RTDEReceiveInterface
from rtde_io import RTDEIOInterface
import time
from positions3 import POSITIONS
from VG10Control import VG10
from scaleReader import ScaleReader

robot_ip = "192.168.1.10"
gripper_ip = "192.168.1.1"

gripper = VG10(gripper_ip)
gripper.connect()

rtde_c = RTDEControlInterface(robot_ip)
rtde_r = RTDEReceiveInterface(robot_ip)
rtde_io = RTDEIOInterface(robot_ip)

scale = ScaleReader('COM3', 115200)

time.sleep(2.5)

NORMAL_SPEED_J = 3.14
NORMAL_ACCEL_J = 3.14

NORMAL_SPEED_L = 3
NORMAL_ACCEL_L = 3

MOVING_SPEED = 1*NORMAL_SPEED_J
MOVING_ACCEL = 0.10*NORMAL_ACCEL_J

PICKUP_SPEED = 1*NORMAL_SPEED_L
PICKUP_ACCEL = 0.45*NORMAL_ACCEL_L

payload = 2.29  # Initial payload of the gripper

def moveJ(coordinate, speed=NORMAL_SPEED_J, accel=NORMAL_ACCEL_J):
    success = rtde_c.moveJ(coordinate, speed=speed, acceleration=accel)
    #print("Move executed:", coordinate)

def moveL(coordinate, speed=NORMAL_SPEED_L, accel=NORMAL_ACCEL_L):
    success = rtde_c.moveL(coordinate, speed=speed, acceleration=accel)
    #print("Move executed:", coordinate)

def moveP(coordinate, speed=NORMAL_SPEED_L, accel=NORMAL_ACCEL_L):
    success = rtde_c.moveP(coordinate, speed=speed, acceleration=accel)
    #print("Move executed:", coordinate)

def wait(seconds):
    time.sleep(seconds)

def moveHome():
    rtde_c.setPayload(payload, [0.0, 0.0, 0.0])
    moveJ(POSITIONS["homeJ"]) # Move to home position
    print("Robot initialized and moved to home position.")

def moveCrude():
    moveL(POSITIONS["boxCrude"], 3, 3*0.3) # Move to crude box position



def waitForBag():
    scale.ser.reset_input_buffer()

    while True:
        weight = scale.get_stable_weight()
        #print(f"Current Weight: {weight:.2f} g")

        EMPTY_THRESHOLD = 50  # adjust after testing

        if weight < EMPTY_THRESHOLD:
            continue
        elif 900 < weight < 1100:
            return "1000g"
    
def moveToPickUp(bagType, bagNr):
    if bagType == "1000g":
        moveL(POSITIONS[bagType]["semipickup"]) # Move to semi-pickup position
        #gripper.grip_a(70) # Grip the bag with 70% vacuum
        gripper.grip_b(70) # Grip the bag with 70% vacuum
        moveL(POSITIONS[bagType]["pickup"], PICKUP_SPEED, PICKUP_ACCEL) # Move to 1000g bag position
        wait(0.2) # Short wait to ensure the bag is gripped
        moveL(POSITIONS["home"], PICKUP_SPEED, PICKUP_ACCEL) # Move back to angled home position
        ensureGrip(bagType, bagNr)
    else:
        print("Unknown bag type in moveToPickUp")

def ensureGrip(bagType, bagNr):
    scale.ser.reset_input_buffer()
    weight = scale.get_stable_weight()
    print(f"Weight after gripping: {weight:.2f} g")
    if bagType == "1000g":
        if weight < 50:
            print("Grip successful.")
            #set bagType as extra payload in kg
            rtde_c.setPayload(payload + 1.0, [0.0, 0.0, 0.0]) # Set payload for the gripper
        else:
            print("Grip unsuccessful. Trying again...")
            #gripper.release_a()
            gripper.release_b()
            moveToPickUp(bagType, bagNr)



def boxNotFilled(bagType, bagNr):
    if bagType == "1000g" and bagNr > 8:
        return False
    else:
        return True

def sameBagType(bagType, prevBagType):
    return bagType == prevBagType

def packBag(bagType, bagNr, speed, accel):
    bagKey = f"bag{bagNr}"

    moveCrude()
    moveJ(POSITIONS[bagType]["bags"][bagKey]["placeFineJ"], MOVING_SPEED, MOVING_ACCEL)
    moveL(POSITIONS[bagType]["bags"][bagKey]["dropOff"], PICKUP_SPEED, PICKUP_ACCEL)

    #gripper.release_a()
    gripper.release_b()
    rtde_c.setPayload(payload, [0.0, 0.0, 0.0]) # Reset payload after releasing the bag

    moveL(POSITIONS[bagType]["bags"][bagKey]["placeFine"], speed, accel)
    moveJ(POSITIONS["boxCrudeJ"])

def pushNeeded(bagType, bagNr):
    if bagType == "1000g" and bagNr in [3, 7]:
        return True
    else:
        return False

def pushBag(bagType, bagNr):
    bagKey = f"bag{bagNr}"
    moveL(POSITIONS[bagType]["push3"][bagKey]["quarter"])
    moveL(POSITIONS[bagType]["push3"][bagKey]["half"])
    moveL(POSITIONS[bagType]["push3"][bagKey]["full"])
    moveL(POSITIONS[bagType]["push3"][bagKey]["down"])
    moveL(POSITIONS[bagType]["push3"][bagKey]["orient"])
    moveL(POSITIONS[bagType]["push3"][bagKey]["pushb"], PICKUP_SPEED, PICKUP_ACCEL)
    moveL(POSITIONS[bagType]["push3"][bagKey]["pushf"], PICKUP_SPEED, PICKUP_ACCEL)
    moveL(POSITIONS[bagType]["push3"][bagKey]["pushb"], PICKUP_SPEED, PICKUP_ACCEL)
    moveL(POSITIONS[bagType]["push3"][bagKey]["full"])
    moveL(POSITIONS[bagType]["push3"][bagKey]["half"])
    moveL(POSITIONS[bagType]["push3"][bagKey]["quarter"])
    moveCrude()


# Main loop
bagNr = 1
bagType = "1000g"

factor = 0.5

Test_Speed_L = 1*NORMAL_SPEED_L
Test_Accel_L = factor*NORMAL_ACCEL_L

Test_Speed_J = 1*NORMAL_SPEED_J
Test_Accel_J = factor*NORMAL_ACCEL_J

#moveHome()
moveCrude()
#scenario = input("Enter scenario number: ")
scenario = "8"
if scenario == "1": # Move back and forth with L (long side)
    waitForBag()
    moveToPickUp("1000g", 1)
    moveCrude()
    for i in range(50):
        moveL([0.1217, -0.471, 0.5259, 1.3497, -1.1631, 1.3187], Test_Speed_L, Test_Accel_L)
        moveL([-0.3685, -0.4759, 0.5259, 1.3495, -1.1633, 1.3187], Test_Speed_L, Test_Accel_L)
        print(f"Iteration {i+1} completed.")
elif scenario == "2": # Move back and forth with J (long side)
    waitForBag()
    moveToPickUp("1000g", 1)
    moveCrude()
    for i in range(50):
        moveJ([1.5, -1.81, 1.48, 0.36, 1.34, -4.7], Test_Speed_J, Test_Accel_J)
        moveJ([0.39, -1.29, 0.95, 0.46, 0.23, -4.81], Test_Speed_J, Test_Accel_J)
        print(f"Iteration {i+1} completed.")
elif scenario == "3": # Move back and forth with L (short side)
    waitForBag()
    moveToPickUp("1000g", 1)
    moveCrude()
    for i in range(50):
        moveL([-0.2923, -0.6819, 0.5259, 1.3495, -1.1635, 1.3187], Test_Speed_L, Test_Accel_L)
        moveL([-0.2952, -0.3851, 0.5259, 1.3496, -1.1632, 1.3187], Test_Speed_L, Test_Accel_L)
        print(f"Iteration {i+1} completed.")
elif scenario == "4": # Move back and forth with J (short side)
    waitForBag()
    moveToPickUp("1000g", 1)
    moveCrude()
    for i in range(50):
        moveJ([0.79, -0.99, 0.51, 0.53, 0.63, -4.73], Test_Speed_J, Test_Accel_J)
        moveJ([0.23, -1.53, 1.25, 0.63, 0.08, -5.05], Test_Speed_J, Test_Accel_J)
        print(f"Iteration {i+1} completed.")
elif scenario == "5": # Move up and down with L
    waitForBag()
    moveToPickUp("1000g", 1)
    moveCrude()
    for i in range(50):
        moveL([-0.1311, -0.4162, 0.6929, 1.3495, -1.1633, 1.3187], Test_Speed_L, Test_Accel_L)
        moveL([-0.1311, -0.4162, 0.4365, 1.3495, -1.1633, 1.3186], Test_Speed_L, Test_Accel_L)
        print(f"Iteration {i+1} completed.")
elif scenario == "6": # Move up and down with J
    waitForBag()
    moveToPickUp("1000g", 1)
    moveCrude()
    for i in range(50):
            moveJ([0.53, -1.61, 0.81, 0.88, 0.36, -4.77], Test_Speed_J, Test_Accel_J)
            moveJ([0.53, -1.88, 1.77, 0.19, 0.37, -4.77], Test_Speed_J, Test_Accel_J)
            print(f"Iteration {i+1} completed.")
elif scenario == "7": # Pick up bag loop
    for i in range(50):
        moveHome()
        waitForBag()
        moveToPickUp(bagType, bagNr)
        moveCrude()
        gripper.release_b()
        print(f"Dropped off bag nr: {bagNr + i}.")
elif scenario == "8": # Scale speed test
    timeMatrix = []
    weightMatrix = []
    for i in range(50):
        print(f"Running iteration {i+1}/50.")
        weight = None
        print("Place bag.")
        while weight is None or weight < 50:
            timeStart = time.time()
            weight = scale.get_stable_weight()
            #print(f"Current Weight: {weight:.2f} g")
        timeEnd = time.time()
        timeElapsed = timeEnd - timeStart
        timeMatrix.append(timeElapsed)
        weightMatrix.append(weight)
        print(f"Bag detected with weight: {weight:.2f} g in {timeElapsed:.2f} s.")
        print("Remove bag.")
        while weight is not None and weight > 50:
            weight = scale.get_stable_weight()
    averageTime = sum(timeMatrix) / len(timeMatrix)
    averageWeight = sum(weightMatrix) / len(weightMatrix)
    print(f"Average time to detect bag: {averageTime:.2f} seconds")
    print(f"Average weight of detected bags: {averageWeight:.2f} g")
    
else:    print("Invalid scenario number. Please enter a valid scenario number.")

moveCrude()
    