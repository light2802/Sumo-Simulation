import traci
import optparse
import pandas as pd
import datetime
import numpy as np
import random

def fog_control(host, port, jId, prob):
    traci.init(host = host, port = port)
    traci.setOrder(random.randint(2, 100))

    states = {
            "GGGGGGGGGGGGrrrrrrrrrrrrrrrrrrrrGGGGGGGGGGGGrrrrrrrrrrrrrrrrrrrr" : 0,
            "yyyyyyyyyyyyrrrrrrrrrrrrrrrrrrrryyyyyyyyyyyyrrrrrrrrrrrrrrrrrrrr" : 1,
            "rrrrrrrrrrrrGGGGrrrrrrrrrrrrrrrrrrrrrrrrrrrrGGGGrrrrrrrrrrrrrrrr" : 2,
            "rrrrrrrrrrrryyyyrrrrrrrrrrrrrrrrrrrrrrrrrrrryyyyrrrrrrrrrrrrrrrr" : 3,
            "rrrrrrrrrrrrrrrrGGGGGGGGGGGGrrrrrrrrrrrrrrrrrrrrGGGGGGGGGGGGrrrr" : 4,
            "rrrrrrrrrrrrrrrryyyyyyyyyyyyrrrrrrrrrrrrrrrrrrrryyyyyyyyyyyyrrrr" : 5,
            "rrrrrrrrrrrrrrrrrrrrrrrrrrrrGGGGrrrrrrrrrrrrrrrrrrrrrrrrrrrrGGGG" : 6,
            "rrrrrrrrrrrrrrrrrrrrrrrrrrrryyyyrrrrrrrrrrrrrrrrrrrrrrrrrrrryyyy" : 7,
            }

    # Convert seconds to h:m:s format
    def secToHMS(time):
        h = int(time // 3600)
        time = time % 3600
        m = int(time // 60)
        time = time % 60
        s = time
        return "{:02d}:{:02d}".format(h, m)

    #Get vehicle count for the jucntion with id jId
    def getJunctionCount(jId):
        simulationDelay(3)
        u = traci.multientryexit.getLastIntervalVehicleSum(jId + "_up")
        d = traci.multientryexit.getLastIntervalVehicleSum(jId + "_down")
        r = traci.multientryexit.getLastIntervalVehicleSum(jId + "_right")
        l = traci.multientryexit.getLastIntervalVehicleSum(jId + "_left")
        return [u + d, l + r]

    #Add delay in seconds
    def simulationDelay(delay):
        traci.simulationStep(step = traci.simulation.getTime() + delay)

    def updateSignalTimes(j, times = None, vehicleCount = None):
        if times:
            phases = [traci.trafficlight.Phase(times[states[state]], state, 0, 0) for state in states]
            logic = traci.trafficlight.Logic("0", 0, states[traci.trafficlight.getRedYellowGreenState(j)], phases)
            traci.trafficlight.setProgramLogic(j, logic)
    #TODO predict contains 4 elements, add U/D R/L based on structure in SUMO to keep 2 values in vehicles
        if vehicleCount:
            vehicles = vehicleCount
        else:
            vehicles = getJunctionCount(j) 
        baseTimer = 120
        timeLimits = [10, 30]
        totalVehicles = sum(vehicles)
        
        if(totalVehicles != 0):
            t = [(i / totalVehicles) * baseTimer if timeLimits[0] < (i / totalVehicles) * baseTimer < timeLimits[1] else min(timeLimits, key=lambda x: abs(x - (i / totalVehicles) * baseTimer)) for i in vehicles]
            print("Vehicles:", vehicles)
            print("Corresponsing times:", t)
            phases = [traci.trafficlight.Phase(5, state, 0, 0) for state in states]
            phases[0].duration = t[0]
            phases[4].duration = t[1]
            logic = traci.trafficlight.Logic("0", 0, states[traci.trafficlight.getRedYellowGreenState(j)], phases)
            traci.trafficlight.setProgramLogic(j, logic)
 
    def getFailureTime():
        #[date, hour]
        #traci.simulation.getTime()

        #TODO Fix date
        curDate = '01-11-2023'#datetime.datetime.now().strftime('%m-%d-%Y') 
        curHour = secToHMS(traci.simulation.getTime())
        curHour += ":00"
        value = [curDate, curHour]
        return value
    
    def getFailureNode(ID):
        if ID == "j":
            #[(id, dir), (id, dir), ...]
            return [(4,4), (3,1), (2,2), (3,2)]
        elif ID == "a":
            return [(1,4), (0,2), (1,3), (0,1)]
        else:
            return [(7,4), (6,1), (5,2), (6,4)]
    
    def getPredictions(IDS, times):
        pred = []
        for i in range(4):
            vehicles = data.loc[(data['Junction'] == IDS[i][0]) & (data['Direction'] == IDS[i][1]) &
                                (data['Date'] == times[0]) & (data['Time'] == times[1])]
            if vehicles.empty :
                simulationDelay(60)
                return pred
            predicted = vehicles.iloc[0]['predicted']
            pred.append(predicted)
        return pred

    skip = 1
    probability = prob
    data = pd.read_csv("./predictions/BTPROJ_predictions_knn.csv")
    #Start simulation
    while traci.simulation.getMinExpectedNumber() > 0:
        # Skip to when vehicles come
        #if skip :
        #    updateSignalTimes(jId, times = [30,5,5,5,30,5,5,5])
        #    traci.simulationStep(step=32368)
        #    skip = 0

        # Add prob. of downing a fog instead of a flag
        if probability and random.randint(1, 10000) % int(1 / probability) == 0:
            downtime = np.random.poisson(600)   #Random downtime with average downtime of 10s
            while downtime > 0:
                print("Fog down for ", downtime, "s", "at",
                      secToHMS(traci.simulation.getTime()), "(", traci.simulation.getTime(), ")")
                IDS = getFailureNode(jId)
                predict = []
                while traci.simulation.getMinExpectedNumber() > 0:
                    times = getFailureTime()
                    predict = getPredictions(IDS, times)
                    if len(predict) < 4 :
                        print("Couldn't predict at time ",
                          secToHMS(traci.simulation.getTime()), "(",
                        traci.simulation.getTime(), ")")
                    else :
                        break
                if len(predict) == 4:
                    updateSignalTimes(jId, vehicleCount = predict)
                    downtime -= 300
                    simulationDelay(300)
                else:
                    break
        else:
    		#traci.simulationStep()
            updateSignalTimes(jId)
            simulationDelay(300)
    traci.close()
    print("Simulation over")

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--host", action="store",
                         default="localhost", help="Specify host on which totalVehicles simulation is running")
    optParser.add_option("--port", action="store", default=8813,
                         help="simulation port")
    optParser.add_option("--jId", action="store", default="j",
                         help="Junction Id")
    optParser.add_option("--prob", action="store", default=0.0,
                         help="Downtime probability")

    options, args = optParser.parse_args()
    return options

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()
    fog_control(options.host, options.port, options.jId, float(options.prob))
