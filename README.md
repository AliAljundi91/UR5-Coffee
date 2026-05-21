HX711 is split into two different scripts.
  The first script is to calibrate the load cell and HX711.
  The second script is needed when other code is to be run. 
    This script is without calibration, so it works from the get-go.
There are four different Main and Position scripts. 
  These are just iterations of the code and the corresponding positions needed in the code.
  Main4, together with Positions4, are the needed codes.
moveToPos.py is used for testing positions made and is a variation of Main4.py
scaleReader.py is what reads from the Arduino and should not be touched.
solutionTests.py is a script mainly used for testing different scenarios.
VG10Control.py is what controls the VG10 Vacuum Gripper from OnRobot. This script works as a library.
