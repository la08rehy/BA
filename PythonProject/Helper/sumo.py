import traci

sumoBinary = "H:/Program Files (x86)/Sumo/bin/sumo-gui.exe"

sumoParams = None
traciConnection = None


# general
def start(sumocfg):
    global sumoParams, traciConnection
    sumoParams = ["-Q", "-S", "-c", sumocfg, "--no-warnings", "true", "--no-step-log", "true", "--seed", "42"]
    traci.start([sumoBinary] + sumoParams, numRetries=10, label="environment")
    traciConnection = traci.getConnection("environment")
    return


def close():
    traciConnection.close(True)
    traci.switch("environment")
    traci.close()


def step(time=0.0):
    traciConnection.simulation.step(time)


def getTime():
    return traciConnection.simulation.getTime()


# traffic related
def addVehicle(vehicleID, routeID):
    traciConnection.vehicle.add(vehicleID, routeID)


def changeTarget(vehicleID, edgeID):
    traciConnection.vehicle.changeTarget(vehicleID, edgeID)


def addRoute(routeID, route):
    traciConnection.route.add(routeID, route)


def getLastStepVehicleIDs(detectorID):
    return traciConnection.domain.Domain.getLastStepVehicleIDs(detectorID)
