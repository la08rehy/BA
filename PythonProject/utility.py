import os
import sys
import win32com.client
import traci
import math
import random
import time
import matplotlib.pyplot as plt
from Helper import sumo_old
from Helper import sumo


def start_and_load(filePath):
    visum = win32com.client.Dispatch("Visum.Visum")
    visum.LoadVersion(filePath)
    return visum


def save(visum, filePath):
    visum.SaveVersion(filePath)


def doubleToInt(n):
    return math.floor(n + 0.5)


def convertToTime(tempTime):
    timeConv = ""
    for i in range(0, len(tempTime), 2):
        timeConv = timeConv + tempTime[i:i + 2]
        timeConv = timeConv + ":"
    return timeConv[:-1]


def getDataFromVisum(obj, curTime):
    """ obj could be link or turn """
    tempTime = str(curTime).zfill(6)  # fuellt auf 4 Stellen auf: z.B. X -> 000X
    attName = "VOLVEHPRT(" + tempTime[:4] + ")"
    curFlowRate = doubleToInt(obj.AttValue(attName))
    return curFlowRate


def weighted_choice_turns(items):
    weight_total = sum(j for i, j in items)
    r = random.uniform(1, weight_total)
    for i in range(len(items)):
        if r > items[i][1]:
            r -= items[i][1]
        else:
            return items[i][0]
    print("ERROR!!!", items)


def flatten(list_2d):
    flatList = []
    for element in list_2d:
        if type(element) is not list and type(element) is not tuple:
            flatList.append(element)
            continue
        for e in element:
            flatList.append(e)
    return flatList


def exponential_distributed_arrival_intervals(mean_headway):
    """
    Mit Exponentialverteilung zufällig erstellte Zeitintervalle zwischen zwei Fahrzeug-Ankünften

    :param mean_headway: Durchschnittliche Ankunftsrate von Fahrzeugen
    :return:
    """
    X = random.random()
    return -1 * mean_headway * math.log(X, math.e)
