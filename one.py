import traci

traci.init(host="10.100.108.174", port=8000)
traci.setOrder(2)
state_up_down_green="GGGGGGGGGGGGrrrrrrrrrrrrrrrrrrrrGGGGGGGGGGGGrrrrrrrrrrrrrrrrrrrr"
state_up_down_yellow="yyyyyyyyyyyyrrrrrrrrrrrrrrrrrrrryyyyyyyyyyyyrrrrrrrrrrrrrrrrrrrr"
state_up_left_green="rrrrrrrrrrrrGGGGrrrrrrrrrrrrrrrrrrrrrrrrrrrrGGGGrrrrrrrrrrrrrrrr"
state_up_left_yellow="rrrrrrrrrrrryyyyrrrrrrrrrrrrrrrrrrrrrrrrrrrryyyyrrrrrrrrrrrrrrrr"
state_right_left_green="rrrrrrrrrrrrrrrrGGGGGGGGGGGGrrrrrrrrrrrrrrrrrrrrGGGGGGGGGGGGrrrr"
state_right_left_yellow="rrrrrrrrrrrrrrrryyyyyyyyyyyyrrrrrrrrrrrrrrrrrrrryyyyyyyyyyyyrrrr"
state_right_left_green="rrrrrrrrrrrrrrrrrrrrrrrrrrrrGGGGrrrrrrrrrrrrrrrrrrrrrrrrrrrrGGGG"
state_right_down_yellow="rrrrrrrrrrrrrrrrrrrrrrrrrrrryyyyrrrrrrrrrrrrrrrrrrrrrrrrrrrryyyy"

flag = 1
while traci.simulation.getMinExpectedNumber()>0:
	ju = traci.multientryexit.getLastIntervalVehicleSum("j_up")
	jd = traci.multientryexit.getLastIntervalVehicleSum("j_down")
	jr = traci.multientryexit.getLastIntervalVehicleSum("j_right")
	jl = traci.multientryexit.getLastIntervalVehicleSum("j_left")
	baseTimer = 120
	timeLimits = [5, 30]
	vehicles = [ju, jd, jl, jr]
	sum = (ju+jd+jr+jl)
	step = 0
	if(sum != 0):
		t = [(i / sum) * baseTimer if timeLimits[0] < (i / sum) * baseTimer < timeLimits[1] else min(timeLimits, key=lambda x: abs(x - (i / sum) * baseTimer)) for i in vehicles]
		print(t)
		phases = []
		phases.append(traci.trafficlight.Phase(t[1], state_up_down_green, 0, 0))
		phases.append(traci.trafficlight.Phase(t[3], state_right_left_green, 0, 0))
		logic = traci.trafficlight.Logic("0", 0, 0, phases)
		traci.trafficlight.setProgramLogic("j", logic)
	if flag :
		traci.simulationStep(step=32368)
		flag = 0
		step = 32368
	else:
		traci.simulationStep()
		#traci.simulationStep(step = step+9000)
		#step += 9000

