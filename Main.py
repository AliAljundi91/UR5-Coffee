from rtde_control import RTDEControlInterface
from rtde_receive import RTDEReceiveInterface
from rtde_io import RTDEIOInterface
import time
from positions import POSITIONS
from sequence import SEQUENCE
from VG10Control import VG10
from scaleReader import ScaleReader

robot_ip = "192.168.1.10"
gripper_ip = "192.168.1.1"

gripper = VG10(gripper_ip)
gripper.connect()

rtde_c = RTDEControlInterface(robot_ip)
rtde_r = RTDEReceiveInterface(robot_ip)
rtde_io = RTDEIOInterface(robot_ip)

scale = ScaleReader('COM3', 9600)

def move(coordinate):
    success = rtde_c.moveJ(coordinate)
    print("Move executed:", success)
    wait(1) # Wait for the robot to stabilize after movement

def tool(action):
    if action == "open":
        value = False
    elif action == "close":
        value = True
    rtde_io.setToolDigitalOut(0, value)

def wait(seconds):
    time.sleep(seconds)

wait(2) # Wait for the robot to connect

def initialize():
    move(POSITIONS["home"]) # Move to home position
    print("Robot initialized and moved to home position.")

def waitForBag():
    bagType = "0g"
    
    last_valid_type = None
    stable_count = 0

    while True:
        weight = scale.get_stable_weight()
        print(f"Current Weight: {weight:.2f} g")

        # Determine current classification
        EMPTY_THRESHOLD = 50  # adjust after testing

        if weight < EMPTY_THRESHOLD:
            current_type = None
        elif 900 < weight < 1100:
            current_type = "1000g"
        else:
            current_type = None

        # Stability check (2 consecutive same classifications)
        if current_type is not None and current_type == last_valid_type:
            stable_count += 1
        else:
            stable_count = 1  # reset counter when it changes
            last_valid_type = current_type

        # Accept only after 2 stable readings
        if stable_count >= 2 and current_type is not None:
            return current_type
    
def moveToPickUp(bagType):
    if bagType == "1000g":
        move(POSITIONS["pickUp"]["1000g"]) # Move to 1000g bag position
        gripper.grip(60) # Grip the bag with 60% vacuum
        move(POSITIONS["home"]) # Move back to home position
    else:
        print("Unknown bag type in moveToPickUp")

def boxNotFilled(bagType, bagNr):
    if bagType == "1000g" and bagNr < 8:
        return True
    return False

def sameBagType(bagType, prevBagType):
    return bagType == prevBagType

def packBag(bagType, bagNr):
    move(POSITIONS["boxCrude"]) # Move to crude box
    if bagType == "1000g":
        move(POSITIONS["placeFine"]["1000g"]) # Move to 1000g place position
        move(POSITIONS["dropOff"]["1000g"]) # Move to 1000g drop off position
        gripper.release() # Release the bag
        move(POSITIONS["placeFine"]["1000g"]) # Move back to place position
        move(POSITIONS["boxCrude"]) # Move back to crude box
    



# Main loop
bagNr = 0
while True:
    initialize()
    print("Waiting for bag placement...")
    prevBagType = bagType if 'bagType' in locals() else "None"
    bagType = waitForBag()
    print(f"Detected Bag Type: {bagType}")
    if boxNotFilled(bagType, bagNr) and (sameBagType(bagType, prevBagType) or bagNr == 0):
        moveToPickUp(bagType)
        bagNr += 1
        print(f"Moving Bag Number: {bagNr}")
        packBag(bagType, bagNr)
    elif boxNotFilled(bagType, bagNr) and not sameBagType(bagType, prevBagType) and bagNr > 0:
        print("Bag type is changed but box is not filled.")
        break
    elif not boxNotFilled(bagType, bagNr):
        print("Box is filled. Please replace the box.")
        break
    else:
        print("Unexpected case. Please check the logic.")
        break


    