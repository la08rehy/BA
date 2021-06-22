"""
# Start von Visum (neuste Version)
visum = win32com.client.Dispatch("Visum.Visum")

# Versions-Datei laden (Absoluten Path der Versions-Datei verwenden)
visum.LoadVersion(os.path.abspath("H:/Benutzer/Joshua/git/bachelorarbeit/Visum/GeradeStraße.ver"))

# Versionsdatei speichern
visum.SaveVersion(os.path.abspath("H:/Benutzer/Joshua/git/bachelorarbeit/Visum/GeradeStraße.ver"))


# Auswahl eines Knoten über ID: ItemByKey(ID)
existingNode = visum.Net.Nodes.ItemByKey(1)

# Hinzufügen eines Knoten: AddNode(ID, x, y)
newNode = visum.Net.AddNode(15, 2, 3)

# Auswahl einer Strecke über Knoten-IDs: ItemByKey(node1, node2)
link1 = visum.Net.Links.ItemByKey(1, 2)

# Hinzufügen einer Strecke: AddLink(ID, node1, node2)
newLink = visum.Net.AddLink(220, newNode, existingNode)

# Ändern eines Attributwertes: SetAttValue(Attributname, neuerWert)
existingNode.SetAttValue("NAME", "newName")

# Ausgeben eines Attributwertes: AttValue(Attributname)
print(newLink.AttValue("NAME"))

# Werte in einer Matrix ändern
matrix = visum.Net.Matrices.ItemByKey(1)
matrix.SetValue(1, 2, 10)

# Verfahrensablauf mit bestimmten Parametern starten
visum.Procedures.Open(os.path.abspath("H:/Benutzer/Joshua/git/bachelorarbeit/Visum/procedureParameters.xml"), True, True, True)
visum.Procedures.Execute()

# Sperren bzw Freigeben von Links
links_sumo = visum.Net.Links.FilteredBy("[ToNodeNo] = 13 | [ToNodeNo] = 14 | "
                                        "[ToNodeNo] = 18 | [ToNodeNo] = 19")
visum.Net.Links.SetAllAttValues("TSysSet", "", False, False)
links_sumo.SetAllAttValues("TSysSet", "B,F,L,P", False, False)

# Abrufen und Ändern eines Werts einer Matrix
matrix = visum.Net.Matrix.ItemByKey(2)
x = matrix.GetValue(row, col)
matrix.SetValue(row, col, newValue)
"""

import os
import sys
import win32com.client
import traci
import math
import random
import time
import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt
from Helper import sumo_old
from Helper import PoissonProcess as pp
from lxml import etree
# import xml.etree.ElementTree as ET


def start_and_load(filePath):
    visum = win32com.client.Dispatch("Visum.Visum")
    visum.LoadVersion(filePath)
    return visum


def save(visum, filePath):
    visum.SaveVersion(filePath)


def roundDoubleToInt(n):
    return math.floor(n + 0.5)


def convertToTime(tempTime):
    time = ""
    for i in range(0, len(tempTime), 2):
        time = time + tempTime[i:i+2]
        time = time + ":"
    return time[0:len(time)-1]


def getDataFromVisum(obj, curTime):
    """ obj could be link or turn """
    tempTime = str(curTime).zfill(6)  # fuellt auf 4 Stellen auf: z.B. X -> 000X
    attName = "VOLVEHPRT(" + tempTime[0:4] + ")"
    curFlowRate = roundDoubleToInt(obj.AttValue(attName))
    return curFlowRate


def weighted_choice_turns(items):
    weights = []
    curWeight = 0
    for i in items:
        curWeight += i[1]
        weights.append(curWeight)
    r = random.uniform(0, curWeight)
    for i in range(len(items)):
        if r <= weights[i]:
            return items[i][0]


"""-----------not needed anymore-----------"""


def vehiclesLost(eventList_allLinks):
    for eventList_oneLink in eventList_allLinks:
        if len(eventList_oneLink) != 0:
            print("-> [INFO]", len(eventList_oneLink), "vehicles lost on link", eventList_oneLink[0][1])
    return


def sumSymbol(start, end, summing):
    """ Summenzeichen: sum_{i=start}^{end} summing """
    tempsum = 0
    for i in range(start, end + 1):
        tempsum += summing
    return tempsum


def printLinks(links):
    print("Links: ", end="")
    for l in links:
        print(int(l.AttValue("No")), end=" ")
    print()
    return


# Sumo-Funktionen
traciConnection = None  # nur um Fehler zu ignorieren
sumoParams = None  # nur um Fehler zu ignorieren


def reset():
    traciConnection.load(sumoParams)


def getPositionVeh(vehicleID):
    return traciConnection.vehicle.getPosition(vehicleID)


def getArrivedIDList():
    return traciConnection.simulation.getArrivedIDList()
