from sumo_visum import *
from utility import *


def simulateTime(visum, procedurePath, sumo_nodes, simulation_startTime=0, simulation_endTime=230000, visumStep=10000,
                 simulationStep=1, procedure_threshhold=0, generate_option=2, inLinksSumo=None):
    """
    Simulation der Zeit der Simulatorenkopplung

    :param visum: instance of the macroscopic simulation
    :param procedurePath: path of the matching procedureParameters.xml
    :param sumo_nodes: relevant nodes in microskopic simulation model sumo
    :param simulation_startTime: start time of the simulation in seconds
    :param simulation_endTime: end time of the simulation in seconds (e.g. 230000 means 23:00:00)
    :param visumStep: calculation steps in macroskopic simulation model visum in seconds (e.g. 10000 means 1:00:00)
    :param simulationStep: steps of the script in seconds (default 1)
    :param procedure_threshhold: defines the acceptable difference between counted and estimated
    :param generate_option: use of complete path (1) or only destination link (2)
    :param inLinksSumo: all ingoing links to sumo, for statistic purposes
    :return:
    """
    if inLinksSumo is None:
        inLinksSumo = []
    # Relevante Turns rausfiltern (außer U-Turns)
    noReturns = visum.Net.Turns.FilteredBy("[FromNodeNo] != [ToNodeNo]")
    logicTurns = ""
    for i in range(len(sumo_nodes)):
        logicTurns += "[ViaNodeNo] = " + str(sumo_nodes[i]) + " | "
    sumo_turns = noReturns.FilteredBy(logicTurns[:-3])
    # Relevante Übergangsstrecken Visum-Sumo rausfiltern
    logicLinks = "("
    for i in range(len(sumo_nodes)):
        logicLinks += "[ToNodeNo] = " + str(sumo_nodes[i]) + " | "
    logicLinks = logicLinks[:-3] + ") & "
    for i in range(len(sumo_nodes)):
        logicLinks += "[FromNodeNo] != " + str(sumo_nodes[i]) + " & "
    links_to_sumo = visum.Net.Links.FilteredBy(logicLinks[:-3])
    nDetectors = links_to_sumo.Count
    originCaps = getVolAndCap_Visum(visum, links_to_sumo, 0)
    gesamteAuslastung = 0

    # Plotting for Evaluation
    dataInLinksSumo, plannedVehs = [], []
    for i in range(len(inLinksSumo)):
        dataInLinksSumo.append([])
        plannedVehs.append([])
    registratedVehs = []
    neueUmlegung = []
    recordLinkVolumes = []
    rec = []
    volumenInSumo = []
    sumoLinksTuples = [(13, 14), (13, 18), (14, 13), (14, 19), (18, 13), (18, 19), (19, 18), (19, 14)]  # BezirkeUndKreuzungen
    # sumoLinksTuples = [(2, 3), (2, 5), (2, 6), (3, 2), (3, 4), (3, 7), (4, 3), (4, 5), (5, 2), (5, 4), (6, 2), (6, 7), (7, 3), (7, 6)]  # Streckensperrung
    volumenInVisum = [[] for _ in range(len(sumoLinksTuples))]

    generatedVehicles = []  # Liste mit allen erzeugten Fahrzeugen (ID, path_nodes)
    generatedVehicleCounter = 0
    allEvents_flat, allPaths_links = [], []
    for curTime in range(simulation_startTime, simulation_endTime, simulationStep):
        # überspringe ungültige Zeiten
        if curTime % 100 > 59 or ((curTime % 10000) / 5900 > 1 and (curTime % 10000) % 5900 > 59):
            continue
        # Simulationsschritt in Visum (-> neue Daten)
        if curTime % visumStep == 0:
            print(str(convertToTime(str(curTime).zfill(6))))
            if curTime == 80000:
                sumo.setDisallowed("2_0")
            if curTime == 120000:
                sumo.setAllowed("2_0")
            if curTime != simulation_startTime:
                # Zählen, Anpassungen der Kapazitätsbeschränkungen, neue Umlegung
                transfer_links_visum = getVolAndCap_Visum(visum, links_to_sumo, curTime)
                transfer_links_sumo = getVol_Sumo(allPaths_links)
                print("[INFO: transfer Visum-Sumo]:", transfer_links_visum, "\n", transfer_links_sumo)
                modified = capacityModification(visum, transfer_links_visum, transfer_links_sumo, procedure_threshhold,
                                                originCaps)
                allPaths_links = []
                if modified:
                    # Umlegung neu starten
                    visum.Procedures.Open(os.path.abspath(procedurePath), True, True, True)
                    visum.Procedures.Execute()
                    print("Umlegung ausgeführt")
                    neueUmlegung.append(True)
                else:
                    neueUmlegung.append(False)
                # Für Statistik Daten der letzten Stunde auslesen (nach ggf neuer Umlegung)
                # Tupel aus Zeit und Liste der Auslastungen des letzten Zeitschritts (als Tupel: No, Sumo, Visum)
                print("curVolumes:", (curTime, record(transfer_links_sumo, transfer_links_visum)))
                recordLinkVolumes.append((curTime, record(transfer_links_sumo, transfer_links_visum)))

                # Für letzten Schritt neu berechnete Daten aus Visum abspeichern
                for i in range(len(sumoLinksTuples)):
                    volumenInVisum[i].append((curTime, getDataFromVisum(
                        visum.Net.Links.ItemByKey(sumoLinksTuples[i][0], sumoLinksTuples[i][1]), curTime - visumStep)))

                # Kapazitätsbeschränkungen entfernen und neue Umlegung für nächste Stunde
                if modified:
                    capacityModification(visum, transfer_links_visum, transfer_links_sumo, procedure_threshhold,
                                         originCaps, True)
                    visum.Procedures.Open(os.path.abspath(procedurePath), True, True, True)
                    visum.Procedures.Execute()
            else:
                visum.Procedures.Open(os.path.abspath(procedurePath), True, True, True)
                visum.Procedures.Execute()
                neueUmlegung.append(False)

            allEvents = []
            for link in links_to_sumo:
                temp_curFlowRate = getDataFromVisum(link, curTime)
                gesamteAuslastung += temp_curFlowRate
                visumIntervall = visumStep % 100 + int((visumStep % 10000) / 100) * 60 + int(visumStep / 10000) * 3600
                if temp_curFlowRate != 0:
                    eventList_oneLink = sampleAbsoluteArrivalTimes(curTime, temp_curFlowRate, visumIntervall,
                                                                   int(link.AttValue("No")),
                                                                   int(link.AttValue("FromNodeNo")),
                                                                   int(link.AttValue("ToNodeNo")))
                    rec.append((curTime, temp_curFlowRate, len(eventList_oneLink), eventList_oneLink))
                    allEvents.append(eventList_oneLink)
                    temp = str(curTime).zfill(6)
                    tempTime = sum([int(temp[0:2]) * 3600, int(temp[2:4]) * 60, int(temp[4:6]) * 1])
                    plannedVehs[inLinksSumo.index(link.AttValue("No"))].append(
                        len([e for e in eventList_oneLink if e[0] < tempTime]))
                else:
                    plannedVehs[inLinksSumo.index(link.AttValue("No"))].append(0)
                dataInLinksSumo[inLinksSumo.index(link.AttValue("No"))].append(temp_curFlowRate)
            allEvents_flat = flatten(allEvents)
            allEvents_flat.sort()  # Sortierung der Events aller Links nach Eventzeit

        # Anstehende Events abarbeiten (Erstellung von Fahrzeugen), bis die nächsten Daten in Visum bereit stehen
        if len(allEvents_flat) != 0:
            while allEvents_flat[0][0] == sumo.getTime():
                path_nodes, path_links = planPath(visum, curTime, allEvents_flat[0], sumo_turns, sumo_nodes, visumStep)
                if path_nodes is None:
                    del allEvents_flat[0]
                    continue
                generatedVehicleCounter = generateVehicle(path_links, generatedVehicleCounter, generate_option)
                volumenInSumo.append((curTime, list(sumo.getRoute("newVeh" + str(generatedVehicleCounter - 1)))))
                generatedVehicles.append((generatedVehicleCounter, path_nodes, path_links))
                print("new vehicle" + str(generatedVehicleCounter - 1) + " @",
                      str(convertToTime(str(curTime).zfill(6))),
                      "(sumoTime:", int(sumo.getTime()), "seconds) on link", allEvents_flat[0][1],
                      "with path_nodes", path_nodes, "which means path_links", path_links)
                time.sleep(0.5)
                del allEvents_flat[0]
                if len(allEvents_flat) == 0:
                    break

        # Alle angekommenen Fahrzeuge registrieren
        vehIDs = []
        for i in range(nDetectors):
            temp = traci.inductionloop.getLastStepVehicleIDs("e1Detector_" + str(i))
            vehIDs.append(temp)
        # Duplikate entfernen (doppelt gezählte Fahrzeuge)
        vehIDs_flat = list(set(flatten(vehIDs)))
        registratedVehs += [e for e in vehIDs_flat]
        if len(vehIDs_flat) != 0:
            print(vehIDs_flat, "arrived @ sumotime", sumo.getTime(), "seconds")
        for vid in vehIDs_flat:
            allPaths_links.append(generatedVehicles[int(vid[6:])][2])
        # Sumo eine Sekunde weitersimulieren lassen
        sumo.step()
    print("Gesamte Auslastung:", gesamteAuslastung)
    print("Summe erzeugter Fahrzeuge:", generatedVehicleCounter)
    print("-> Fahrzeuge verloren:", gesamteAuslastung - generatedVehicleCounter)
    print("Neue Umlegungen nötig:", neueUmlegung)

    gesamtRec = []
    for i in range(len(inLinksSumo)):
        gesamtRec.append([])
    for i in range(len(rec)):
        temp = [x[0] for x in rec[i][3]]
        count = len(temp) - 1
        count2 = rec[i][1]
        if len(temp) <= 1:
            count = -1
        if rec[i][1] == 0:
            count2 = -1
        gesamtRec[inLinksSumo.index(rec[i][3][0][1])].append(
            (rec[i][1], rec[i][2], int(3600 / count2), int((temp[-1] - temp[0]) / count)))
    print("Tupel bestehend aus: VolVisum, geplantesVolSumo, avgArrTimeVisum, avgArrTimeSumo")
    for i in range(len(links_to_sumo)):
        print("Link:", inLinksSumo[i], "->", gesamtRec[i])
    print("VolumenInSumo:", volumenInSumo)
    for i in range(len(sumoLinksTuples)):
        print(sumoLinksTuples[i][0], "->", sumoLinksTuples[i][1], ":", volumenInVisum[i])


def sampleAbsoluteArrivalTimes(curTime, curFlowRate, visumInterval, linkNo, fromNode, toNode):
    """
    Erstellt mithilfe einer Exponentialverteilung Abfahrtszeiten von curFlowRate Fahrzeugen (t)

    :param curTime:
    :param curFlowRate:
    :param visumInterval:
    :param linkNo: Nummer des Links (no)
    :param fromNode: Startknoten des Links (from)
    :param toNode: Zielknoten des Links (to)
    :return: Liste mit Tupeln (t, no, from, to)
    """
    res = []
    temp = str(curTime).zfill(6)
    tempTime = sum([int(temp[0:2]) * 3600, int(temp[2:4]) * 60, int(temp[4:6]) * 1])
    endTime = tempTime + visumInterval
    mean_headway = visumInterval / curFlowRate

    # Durchschnittliche Zeit zwischen 2 Fahrzeugankünften (z.B. 3600s/15=240s)
    while tempTime < endTime:
        nextInterval = doubleToInt(exponential_distributed_arrival_intervals(mean_headway))  # mean_headway als Argument
        # Tupel aus Eventzeit, Link-Nummer und beiden Knoten des Links
        res.append((int(tempTime + nextInterval), int(linkNo), int(fromNode), int(toNode)))
        tempTime += nextInterval
    return res


def planPath(visum, curTime, event, sumo_turns, sumo_nodes, visumStep):
    """
    Erstellt eine Route für ein neues Fzg in Sumo \n
    from via to
        from via to
            ...

    :param visum:
    :param curTime: Aktuelle Zeit = Zeit der Fahrzeugerzeugung
    :param event: Gesampletes Tupel (t, linkNo, from, to) mit Informationen über Erzeugung
    :param sumo_turns: Von Sumo simulierte Abbieger außer U-Turns
    :param sumo_nodes: Knoten in Sumo
    :param visumStep: Schrittweite in Visum zur Bestimmung des letzten Visumschritts
    :return: Tupel aus Liste der Knoten und Liste der Links
    """
    path_nodes = [event[2], event[3]]
    while len(path_nodes) == 2 or (path_nodes[-1] in sumo_nodes):
        # Alle möglichen nächsten Turns bestimmen
        tempTurns = sumo_turns.FilteredBy("[FromNodeNo] = " + str(path_nodes[-2]) +
                                          " & [ViaNodeNo] = " + str(path_nodes[-1]))
        # Alle Turns durchgehen und einen Abbieger auswählen
        flowRatesTurns = []
        it = tempTurns.Iterator
        while it.Valid:
            curTurn = it.Item
            # Daten von letztem Visum-Step holen
            lastVisumStep = int(curTime / visumStep) * visumStep
            flowRate = getDataFromVisum(curTurn, lastVisumStep)
            t = (int(curTurn.AttValue("ToNodeNo")), flowRate)
            flowRatesTurns.append(t)
            it.Next()
        # Unter Einbeziehung der flowrates zufällig (gewichtet) einen Abbieger wählen und zum Pfad hinzufügen
        toNodeNo = weighted_choice_turns(flowRatesTurns)
        if toNodeNo is None:
            return None, None
        toNodeNo = int(toNodeNo)
        # Vermeidung von Zyklen (Erneutes Einfügen führt zur Entfernung des Zyklus)
        if toNodeNo not in path_nodes:
            path_nodes.append(toNodeNo)
        else:
            path_nodes = path_nodes[:path_nodes.index(toNodeNo) + 1]

    # Aus den Knoten die Links des gewählten Pfades bestimmen
    path_links = []
    for i in range(len(path_nodes) - 1):
        link = visum.Net.Links.ItemByKey(path_nodes[i], path_nodes[i + 1])
        linkNo = int(link.AttValue("No"))
        if not link.AttValue("isForward"):
            linkNo = linkNo * (-1)
        path_links.append(linkNo)

    return path_nodes, path_links


def generateVehicle(path_links, generatedVehicleCounter, option):
    """
    Erstellt ein neues Fahrzeug in Sumo

    :param path_links: Pfad der Links des neuen Fahrzeugs
    :param generatedVehicleCounter: Nummer des neuen Fahrzeugs
    :param option: Variante 1 (Route aus Visum nehmen) oder 2 (Route von Sumo bestimmen lassen)
    :return:
    """
    path_links_strings = [str(n) for n in path_links]

    if option == 1:
        # Variante 1: Route komplett übergeben (über Visum-Abbiegewahrscheinlichkeiten bestimmt)
        sumo.addRoute("curRoute" + str(generatedVehicleCounter), path_links_strings)
        sumo.addVehicle("newVeh" + str(generatedVehicleCounter), "curRoute" + str(generatedVehicleCounter))
    else:
        # Variante 2: DummyRoute übergeben und dann Route mit changeTarget von Sumo bestimmen lassen
        # Achtung: alle nicht-Sumo-Straßen müssen gesperrt oder aus dem Sumo-Netz entfernt werden
        sumo.addRoute("curRoute" + str(generatedVehicleCounter), path_links_strings[0:1])
        sumo.addVehicle("newVeh" + str(generatedVehicleCounter), "curRoute" + str(generatedVehicleCounter))
        sumo.changeTarget("newVeh" + str(generatedVehicleCounter), str(path_links_strings[-1]))

    generatedVehicleCounter += 1
    return generatedVehicleCounter
