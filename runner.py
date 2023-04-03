from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
from itertools import islice
from sumolib import checkBinary  # noqa
import traci  # noqa

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

def add_vehicles(inFileName, junction, outFileName, vehNr):
    #[u, d, l, r]
    car_count = {"UP" : 0, "DOWN" : 0, "LEFT" : 0, "RIGHT" : 0}
    bike_count = {"UP" : 0, "DOWN" : 0, "LEFT" : 0, "RIGHT" : 0}
    bus_count = {"UP" : 0, "DOWN" : 0, "LEFT" : 0, "RIGHT" : 0}
    truck_count = {"UP" : 0, "DOWN" : 0, "LEFT" : 0, "RIGHT" : 0}

    if not os.path.exists(inFileName):
        return vehNr
    with open(inFileName, "r") as datFile:
        for line in datFile.readlines()[1:]:
            time, direction, car_curr, bike_curr, bus_curr, truck_curr = line.split(",")
            if not time:
                continue
            time = get_sec(time)
            car_curr = int(car_curr)
            bike_curr = int(bike_curr)
            bus_curr = int(bus_curr)
            truck_curr = int(truck_curr)

            while car_curr - car_count[direction] > 0:
                print('    <vehicle id="%i" type="car" route="%s_%s" depart="%i" />' % (
                    vehNr, junction, direction, time), file=outFileName)
                vehNr += 1
                car_count[direction] += 1
            while bike_curr - bike_count[direction] > 0:
                print('    <vehicle id="%i" type="bike" route="%s_%s" depart="%i" />' % (
                    vehNr, junction, direction, time), file=outFileName)
                vehNr += 1
                bike_count[direction] += 1
            while bus_curr - bus_count[direction] > 0:
                print('    <vehicle id="%i" type="bus" route="%s_%s" depart="%i" />' % (
                    vehNr, junction, direction, time), file=outFileName)
                vehNr += 1
                bus_count[direction] += 1
            while truck_curr - truck_count[direction] > 0:
                 print('    <vehicle id="%i" type="truck" route="%s_%s" depart="%i" />' % (
                     vehNr, junction, direction, time), file=outFileName)
                 vehNr += 1
                 truck_count[direction] += 1
    print(truck_count)
    print("Added %i vehicles from" % (vehNr), inFileName)
    return vehNr

def generate_networkfile():
    os.system("netconvert -W --node-files=./data/cross.nod.xml --edge-files=./data/cross.edg.xml --output-file=./new/cross.net.xml")
    print("Network created\n")

def generate_routefile(date):
    routefile = "new/cross.rou.xml"
    if os.path.exists(routefile):
        os.remove(routefile)
    os.makedirs(os.path.dirname(routefile), exist_ok=True)
    with open(routefile, "w") as routes:
        print("""<routes>
        <vType id="car" accel="0.8" decel="4.5" sigma="0.5" length="1" minGap="2.5" maxSpeed="60" guiShape="passenger"/>
        <vType id="bike" accel="0.8" decel="4.5" sigma="0.5" length="2" minGap="2.5" maxSpeed="80" guiShape="passenger"/>
        <vType id="bus" accel="0.8" decel="4.5" sigma="0.5" length="6" minGap="3" maxSpeed="40" guiShape="bus"/>
        <vType id="truck" accel="0.8" decel="4.5" sigma="0.5" length="8" minGap="3" maxSpeed="40" guiShape="bus"/>

        <route id="J_LEFT" edges="a_j_j_right j_right_j j_j_left j_left_j_left_exit" />
        <route id="J_RIGHT" edges="j_left_exit_j_left j_left_j j_j_right j_right_a_j" />
        <route id="J_DOWN" edges="j_up_exit_j_up j_up_j j_j_down j_down_j_r" />
        <route id="J_UP" edges="j_r_j_down j_down_j j_j_up j_up_j_up_exit" />

        <route id="A_LEFT" edges="a_right_exit_a_right a_right_a a_a_left a_left_a_j" />
        <route id="A_RIGHT" edges="a_j_a_left a_left_a a_a_right a_right_a_right_exit" />
        <route id="A_DOWN" edges="a_up_exit_a_up a_up_a a_a_down a_down_a_down_exit" />
        <route id="A_UP" edges="a_down_exit_a_down a_down_a a_a_up a_up_a_up_exit" />

        <route id="R_LEFT" edges="r_right_exit_r_right r_right_r r_r_left r_left_r_left_exit" />
        <route id="R_RIGHT" edges="r_left_exit_r_left r_left_r r_r_right r_right_r_right_exit" />
        <route id="R_DOWN" edges="j_r_r_up r_up_r r_r_down r_down_r_down_exit" />
        <route id="R_UP" edges="r_down_exit_r_down r_down_r r_r_up r_up_j_r" />""", file=routes)

        vehNr = 0
        for c in ["J", "A", "R"]:
            for n in range(1, 4):
                vehNr =  add_vehicles("proj/%s/%s%i/%s%i_%i_one.csv" % (c,
                                                                        c.lower(),
                                                                        n,
                                                                        c.lower(),
                                                                        n, date), c, routes, vehNr)
                vehNr =  add_vehicles("proj/%s/%s%i/%s%i_%i.csv" % (c, c.lower(), n, c.lower(), n, date), c, routes, vehNr)
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
    os.system("python $SUMO_HOME/tools/route/sort_routes.py new/cross.rou.xml")
    os.system("mv new/cross.rou.xml.sorted new/cross.rou.xml")
    print("Routes sorte\n")

def run():
    """execute the TraCI control loop"""
    # we start with phase 2 where EW has green
    traci.setOrder(1)
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("--date", action="store", default=11,
                            help="give date for simulation")
    optParser.add_option("--numClients", action="store", default="1",
                            help="Number of clients in simulation")
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

    date = options.date
    # first, generate the route file for this simulation
    generate_networkfile()
    generate_routefile(int(date))

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "--lanechange.duration", "0.1", "-c", "data/cross.sumocfg",
                             "--tripinfo-output", "tripinfo.xml",
    #                         "--full-output", "sumo.log",
                            "--duration-log.statistics",
                            "--num-clients", options.numClients], port = 8813)
    run()
