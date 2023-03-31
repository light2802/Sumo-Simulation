import traci
import optparse

def run(host, port):
    traci.init(host = host, port = port)
    traci.setOrder(2)

    state_up_down_green="GGGGGGGGGGGGrrrrrrrrrrrrrrrrrrrrGGGGGGGGGGGGrrrrrrrrrrrrrrrrrrrr"
    state_up_down_yellow="yyyyyyyyyyyyrrrrrrrrrrrrrrrrrrrryyyyyyyyyyyyrrrrrrrrrrrrrrrrrrrr"
    state_up_left_green="rrrrrrrrrrrrGGGGrrrrrrrrrrrrrrrrrrrrrrrrrrrrGGGGrrrrrrrrrrrrrrrr"
    state_up_left_yellow="rrrrrrrrrrrryyyyrrrrrrrrrrrrrrrrrrrrrrrrrrrryyyyrrrrrrrrrrrrrrrr"
    state_right_left_green="rrrrrrrrrrrrrrrrGGGGGGGGGGGGrrrrrrrrrrrrrrrrrrrrGGGGGGGGGGGGrrrr"
    state_right_left_yellow="rrrrrrrrrrrrrrrryyyyyyyyyyyyrrrrrrrrrrrrrrrrrrrryyyyyyyyyyyyrrrr"
    state_right_down_green="rrrrrrrrrrrrrrrrrrrrrrrrrrrrGGGGrrrrrrrrrrrrrrrrrrrrrrrrrrrrGGGG"
    state_right_down_yellow="rrrrrrrrrrrrrrrrrrrrrrrrrrrryyyyrrrrrrrrrrrrrrrrrrrrrrrrrrrryyyy"

    #Get vehicle count for the jucntion with id jId
    def getJunctionCount(jId):
        u = traci.multientryexit.getLastIntervalVehicleSum(jId + "_up")
        d = traci.multientryexit.getLastIntervalVehicleSum(jId + "_down")
        r = traci.multientryexit.getLastIntervalVehicleSum(jId + "_right")
        l = traci.multientryexit.getLastIntervalVehicleSum(jId + "_left")
        return [u, d, l, r]

    #Add delay in seconds
    def simulationDelay(delay):
        traci.simulationStep(step = traci.simulation.getTime() + delay)

    skip = 1
    #Start simulation
    while traci.simulation.getMinExpectedNumber()>0:
    	baseTimer = 120
    	timeLimits = [5, 30]
    	vehicles = getJunctionCount("j")
    	totalVehicles = sum(vehicles)
    	#TODO Make modular function for setting traffic light time
    	if(totalVehicles != 0):
    		t = [(i / totalVehicles) * baseTimer if timeLimits[0] < (i / totalVehicles) * baseTimer < timeLimits[1] else min(timeLimits, key=lambda x: abs(x - (i / totalVehicles) * baseTimer)) for i in vehicles]
    		print(t)
    		phases = []
    		phases.append(traci.trafficlight.Phase(t[0], state_up_down_green, 0, 0))
    		phases.append(traci.trafficlight.Phase(5, state_up_down_yellow, 0, 0))
    		phases.append(traci.trafficlight.Phase(t[1], state_up_left_green, 0, 0))
    		phases.append(traci.trafficlight.Phase(5, state_up_left_yellow, 0, 0))
    		phases.append(traci.trafficlight.Phase(t[2], state_right_left_green, 0, 0))
    		phases.append(traci.trafficlight.Phase(5, state_right_left_yellow, 0, 0))
    		phases.append(traci.trafficlight.Phase(t[3], state_right_down_green, 0, 0))
    		phases.append(traci.trafficlight.Phase(5, state_right_down_yellow, 0, 0))

    		logic = traci.trafficlight.Logic("0", 0, 0, phases)
    		traci.trafficlight.setProgramLogic("j", logic)
    	if skip :
    		traci.simulationStep(step=32368)
    		skip = 0
    	else:
    		#traci.simulationStep()
    		simulationDelay(130)

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--host", action="store_true",
                         default="localhost", help="Specify host on which totalVehicleso simulation is running")
    optParser.add_option("--port", action="store_true", default=8813,
                         help="simulation port")
    options, args = optParser.parse_args()
    return options

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    run(options.host, options.port)
