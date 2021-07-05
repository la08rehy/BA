from utility import *

sumoBinary = "H:/Program Files (x86)/Sumo/bin/sumo-gui.exe"
traciConnection = None


# general
def start(sumocfg):
    """
    Startet die übergebene Konfiguration als Sumo-Simulation und erstellt eine Verbindung zur Traci-Schnittstelle

    :param sumocfg: Auszuführende Simulation
    :return:
    """
    global traciConnection
    sumoParams = ["-Q", "-S", "-c", sumocfg, "--ignore-route-errors", "true", "--no-warnings", "true", "--no-step-log", "true", "--seed", "42"]
    traci.start([sumoBinary] + sumoParams, numRetries=10, label="environment")
    traciConnection = traci.getConnection("environment")
    return


def close():
    """
    Beendet die laufende Sumo-Simulation und die Verbindung zur Traci-Schnittstelle

    :return:
    """
    traciConnection.close(True)
    traci.switch("environment")
    traci.close()


def step(targetTime=0.0):
    """
    Simuliert bis zur übergebenen Zeit oder alternativ einen Schritt (1s)

    :param targetTime:
    :return:
    """
    traciConnection.simulation.step(targetTime)


def getTime():
    """
    Gibt die aktuelle Zeit der Simulation aus

    :return: Zeit in Sekunden
    """
    return traciConnection.simulation.getTime()


# traffic related
def addVehicle(vehicleID, routeID):
    """
    Erstellt ein Fahrzeug, welches anschließend die übergebene Route abfährt

    :param vehicleID: ID des neuen Fahrzeugs
    :param routeID: ID der abzufahrenden Route
    :return:
    """
    traciConnection.vehicle.add(vehicleID, routeID)


def changeTarget(vehicleID, edgeID):
    """
    Ändert die Zielstrecke des übergebenen Fahrzeugs und erstellt anschließend eine neue Route (alte Route wird
    überschrieben)

    :param vehicleID: Betreffendes Fahrzeug
    :param edgeID: Neue Zielstrecke
    :return:
    """
    traciConnection.vehicle.changeTarget(vehicleID, edgeID)


def addRoute(routeID, route):
    """
    Erstellt eine neue Route, die über die ID adressiert werden kann

    :param routeID: ID der neuen Route
    :param route: Liste von abzufahrenden Strecken
    :return:
    """
    traciConnection.route.add(routeID, route)


def getRoute(vehicleID):
    """
    Gibt die aktuelle Route eines Fahrzeugs zurück

    :param vehicleID: Betreffendes Fahrzeug
    :return: Route in Form eines Tupels von Strings (= gecastete Kantennummern)
    """
    return traciConnection.vehicle.getRoute(vehicleID)


def getLastStepVehicleIDs(detectorID):
    """
    Gibt alle im letzten Zeitschritt (1s) an einem bestimmten Detektor vorbeigefahrenen  Fahrzeuge in Form ihrer IDs
    zurück

    :param detectorID: Betreffende Zählstelle
    :return: Liste von Fahrzeug-IDs
    """
    return traciConnection.domain.Domain.getLastStepVehicleIDs(detectorID)


def setDisallowed(laneID):
    traciConnection.lane.setDisallowed(laneID, "passenger")


def setAllowed(laneID):
    traciConnection.lane.setAllowed(laneID, ["passenger"])

