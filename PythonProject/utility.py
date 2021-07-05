import os
import sys
import win32com.client
import traci
import math
import random
import time
import matplotlib.pyplot as plt
import sumo


def start_and_load(filePath):
    """
    Startet eine Instanz des makroskopischen Simulators Visum und öffnet die übergebene Datei

    :param filePath: Versions-Datei
    :return: Instanz von Visum
    """
    visum = win32com.client.Dispatch("Visum.Visum")
    visum.LoadVersion(filePath)
    return visum


def save(visum, filePath):
    """
    Speichert eine laufende Simulation am übergebenen Pfad ab

    :param visum: Instanz des Simulators
    :param filePath: Speicherpfad
    :return:
    """
    visum.SaveVersion(filePath)


def doubleToInt(n):
    """
    Rundet eine Kommazahl kaufmännisch (0-4 abrunden, 5-9 aufrunden)

    :param n: Zu rundende Zahl
    :return: Gerundete Zahl als Integer
    """
    return math.floor(n + 0.5)


def convertToTime(tempTime):
    """
    Wandelt die übergebene Zeit in das Format hh:mm:ss um

    :param tempTime: Umzuwandelnde Zeit
    :return: Zeit im anderen Format
    """
    timeConv = ""
    for i in range(0, len(tempTime), 2):
        timeConv = timeConv + tempTime[i:i + 2]
        timeConv = timeConv + ":"
    return timeConv[:-1]


def getDataFromVisum(obj, curTime):
    """
    Liest die aktuelle Auslastung eines Objekts aus Visum aus. Falls curTime nicht mit einem Visum-Schritt
    übereinstimmt, wird die Daten zum Zeitpunkt des letzten Schrittes abgefragt

    :param obj: Betroffenes Objekt (z.B. Strecke oder Abbieger)
    :param curTime: Aktuelle Zeit
    :return:
    """
    tempTime = str(curTime).zfill(6)  # fuellt auf 4 Stellen auf: z.B. X -> 000X
    attName = "VOLVEHPRT(" + tempTime[:4] + ")"
    curFlowRate = doubleToInt(obj.AttValue(attName))
    return curFlowRate


def weighted_choice_turns(items):
    """
    Wählt abhängig von den Gewichtungen der Abbieger einen dieser aus

    :param items: Liste von Tupeln, in denen der Zu-Knoten und die CurFlowRate aus Visum gespeicher sind
    :return: Ausgewählter Zu-Knoten
    """
    weight_total = sum(j for i, j in items)
    r = random.uniform(1, weight_total)
    for i in range(len(items)):
        if r > items[i][1]:
            r -= items[i][1]
        else:
            return items[i][0]
    return None
    # print("ERROR!!!", items)


def flatten(list_2d):
    """
    Wandelt eine 2-dimensionale (oder gemischte) Liste in eine 1-dimensionale um

    :param list_2d: 2-dimensionale Liste
    :return:
    """
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
    Erstellung eines exponential verteilten Zeitintervalls zwischen zwei Fahrzeugabfahrten

    :param mean_headway: Durchschnittliche Abfahrtsrate von Fahrzeugen (# / Zeiteinheit)
    :return: Zeitintervall zwischen zwei Abfahrten
    """
    X = random.random()
    return -1 * mean_headway * math.log(X, math.e)
