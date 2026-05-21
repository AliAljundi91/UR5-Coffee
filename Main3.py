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
PICKUP_ACCEL = 0.15*NORMAL_ACCEL_L

payload = 2.29  # Initial payload of the gripper

def moveJ(coordinate, speed=NORMAL_SPEED_J, accel=NORMAL_ACCEL_J):
    success = rtde_c.moveJ(coordinate, speed=speed, acceleration=accel)
    #print("Move executed:", coordinate)

def moveL(coordinate, speed=NORMAL_SPEED_L, accel=NORMAL_ACCEL_L):
    success = rtde_c.moveL(coordinate, speed=speed, acceleration=accel)
    #print("Move executed:", coordinate)

def wait(seconds):
    time.sleep(seconds)

def moveHome():
    rtde_c.setPayload(payload, [0.0, 0.0, 0.0])
    moveJ(POSITIONS["homeJ"]) # Move to home position
    print("Robot initialized and moved to home position.")

def moveCrude():
    moveL(POSITIONS["boxCrude"]) # Move to crude box position



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

def packBag(bagType, bagNr):
    bagKey = f"bag{bagNr}"

    moveCrude()
    moveJ(POSITIONS[bagType]["bags"][bagKey]["placeFineJ"], MOVING_SPEED, MOVING_ACCEL)
    moveL(POSITIONS[bagType]["bags"][bagKey]["dropOff"], PICKUP_SPEED, PICKUP_ACCEL)

    #gripper.release_a()
    gripper.release_b()
    rtde_c.setPayload(payload, [0.0, 0.0, 0.0]) # Reset payload after releasing the bag

    moveL(POSITIONS[bagType]["bags"][bagKey]["placeFine"])
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

def errorPresent():
    if boxNotFilled(bagType, bagNr) and (sameBagType(bagType, prevBagType) or bagNr == 1):
        return False
    elif not boxNotFilled(prevBagType, bagNr):
        print("Box is filled. Please replace the box.")
        return True
    elif boxNotFilled(bagType, bagNr) and not sameBagType(bagType, prevBagType) and bagNr > 1:
        print("Bag type is changed but box is not filled.")
        return True
    else:
        print("Unexpected case. Please check the logic.")
        return True


# Main loop
bagNr = 0
bagMax = 8
bagType = "1000g"
prevBagType = "None"
timeMatrix = []
timeLoopStart = None
while True:
    if timeLoopStart is not None:
        timeLoopStart = time.time()
    moveHome()
    bagNr += 1
    if bagNr > bagMax:
        break
    prevBagType = bagType if 'bagType' in locals() else "None"
    print("Waiting for bag placement...")
    bagType = waitForBag()
    if timeLoopStart is None:
        timeLoopStart = time.time()
    print(f"Detected Bag Type: {bagType}")
    if not errorPresent():
        moveToPickUp(bagType, bagNr)
        print(f"Moving Bag Number: {bagNr}")
        packBag(bagType, bagNr)
        if pushNeeded(bagType, bagNr):
            pushBag(bagType, bagNr)
    else:
        print("Error detected. Please check the system.")
        break
    timeLoopEnd = time.time()
    print(f"It took: {timeLoopEnd - timeLoopStart:.2f} seconds to pack bag number {bagNr}.")
    timeMatrix.append(timeLoopEnd - timeLoopStart)
print(f"Average time per bag: {sum(timeMatrix)/len(timeMatrix):.2f} seconds.")
print(f"Total time: {sum(timeMatrix):.2f} seconds.")

    