#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
from itertools import islice

def get_sec(time_str):
    """Get seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

def add_vehicles(inFileName, outFileName, vehNr):
    car_count = 0
    bike_count = 0
    bus_count = 0
    truck_count = 0

    with open(inFileName, "r") as datFile:
        for line in datFile.readlines()[1:]:
            time, dir, car_curr, bike_curr, bus_curr, truck_curr = line.split(",")
            if not time:
                continue
            time = get_sec(time)
            car_curr = int(car_curr)
            bike_curr = int(bike_curr)
            bus_curr = int(bus_curr)
            truck_curr = int(truck_curr)

            if car_curr - car_count:
                print('    <vehicle id="%i" type="car" route="%s" depart="%i" />' % (
                    vehNr, dir, time), file=outFileName)
                vehNr += 1
                car_curr = car_count
            if bike_curr - bike_count:
                print('    <vehicle id="%i" type="bike" route="%s" depart="%i" />' % (
                    vehNr, dir, time), file=outFileName)
                vehNr += 1
                bike_curr = bike_count
            if bus_curr - bus_count:
                print('    <vehicle id="%i" type="bus" route="%s" depart="%i" />' % (
                    vehNr, dir, time), file=outFileName)
                vehNr += 1
                bus_curr = bus_count
            if truck_curr - truck_count:
                 print('    <vehicle id="%i" type="truck" route="%s" depart="%i" />' % (
                     vehNr, dir, time), file=outFileName)
                 vehNr += 1
                 truck_curr = truck_count
    return vehNr
        


def generate_networkfile():
    os.system("netconvert -W --node-files=./data/cross.nod.xml --edge-files=./data/cross.edg.xml --output-file=./new/cross.net.xml")
    print("Network created\n")

def generate_routefile():
    routefile = "new/cross.rou.xml"
    os.makedirs(os.path.dirname(routefile), exist_ok=True)
    with open(routefile, "w") as routes:
        print("""<routes>
        <vType id="car" width="10" accel="0.8" decel="4.5" sigma="0.5" length="1" minGap="2.5" maxSpeed="60" guiShape="passenger"/>
        <vType id="bike" accel="0.8" decel="4.5" sigma="0.5" length="2" minGap="2.5" maxSpeed="80" guiShape="passenger"/>
        <vType id="bus" accel="0.8" decel="4.5" sigma="0.5" length="6" minGap="3" maxSpeed="40" guiShape="bus"/>
        <vType id="truck" accel="0.8" decel="4.5" sigma="0.5" length="8" minGap="3" maxSpeed="40" guiShape="bus"/>
        <route id="RIGHT" edges="51o 1i 2o 52i" />
        <route id="LEFT" edges="52o 2i 1o 51i" />
        <route id="UP" edges="53o 3i 4o 54i" />
        <route id="DOWN" edges="54o 4i 3o 53i" />""", file=routes)

        vehNr = 0
        vehNr =  add_vehicles("proj/Jehangir final_timed/j1/j1_11_one.csv", routes, vehNr)
        
#        for i in range(N):
#            if random.uniform(0, 1) < pWE:
#                print('    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
#                    vehNr, i), file=routes)
#                vehNr += 1
#            if random.uniform(0, 1) < pEW:
#                print('    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" />' % (
#                    vehNr, i), file=routes)
#                vehNr += 1
#            if random.uniform(0, 1) < pNS:
#                print('    <vehicle id="down_%i" type="typeNS" route="down" depart="%i" color="1,0,0"/>' % (
#                    vehNr, i), file=routes)
#                vehNr += 1
        print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>
    print("Routes created\n")


def run():
    """execute the TraCI control loop"""
    step = 0
    # we start with phase 2 where EW has green
    traci.trafficlight.setPhase("0", 2)
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if traci.trafficlight.getPhase("0") == 2:
            # we are not already switching
            if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
                # there is a vehicle from the north, switch
                traci.trafficlight.setPhase("0", 3)
            else:
                # otherwise try to keep green for EW
                traci.trafficlight.setPhase("0", 2)
        step += 1
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()
    generate_networkfile()
    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "--lanechange.duration", "0.1", "-c", "data/cross.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
