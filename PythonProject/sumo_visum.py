from utility import *


def getVolAndCap_Visum(visum, links_to_sumo, curTime):
    """
    Liest die Kapazitäten und Volumen der von Sumo nach Visum verlaufenden Übergangsstrecken zur aktuellen Zeit aus

    :param visum: Instanz von Visum
    :param links_to_sumo: Übergangsstrecken nach Sumo (werden anschließend negiert)
    :param curTime: Aktuelle Zeit
    :return: Liste von Tupeln, die jeweils die ID, Kapazität, aktuelle Auslastung sowie die IDs der beiden
    angrenzenden Knoten enthalten
    """
    links_in_visum = []
    it = links_to_sumo.Iterator
    while it.Valid:
        curLink = it.Item
        # links_to_sumo -> links_in_visum: Richtung umdrehen
        fromNode = curLink.AttValue("ToNodeNo")
        toNode = curLink.AttValue("FromNodeNo")
        link_rightDirection = visum.Net.Links.ItemByKey(toNode, fromNode)
        no = link_rightDirection.AttValue("no")
        if not link_rightDirection.AttValue("isForward"):
            no = no * (-1)
        cap = link_rightDirection.AttValue("CapPrt")
        curVol = link_rightDirection.AttValue("VOLVEHPRT(" + str(curTime).zfill(6)[0:4] + ")")
        links_in_visum.append((no, cap, curVol, fromNode, toNode))
        it.Next()
    return links_in_visum


def getVol_Sumo(allPaths_links):
    """
    Zählt das Vorkommen jeder Strecke in einer Liste aus Routen

    :param allPaths_links: Routen aller Fahrzeuge, die im letzten Zeitschritt von einem Detektor registriert wurden
    (also an ihrem jeweiligen Ziel angekommen sind)
    :return: Liste aus Tupeln, die jeweils die ID eines Links und die entsprechende gezählte Auslastung enthalten
    """
    lastLinks = flatten([[x[-1]] for x in allPaths_links])
    links_in_sumo = [(x, lastLinks.count(x)) for x in set(lastLinks)]
    return links_in_sumo


def capacityModification(visum, transfer_links_visum, transfer_links_sumo, threshhold, originCaps, reset=False):
    """
    Passt die Kapazitäten aller Übergangsstrecken nach Visum im makroskopischen Simulator an, sofern sie außerhalb des
    Threshholds liegen. Über den Parameter reset können alle Kapazitäten auf ihre Anfangswerte zurückgesetzt werden

    :param visum: Instanz von Visum zur Bearbeitung der Streckenkapazitäten
    :param transfer_links_visum: Kapazitätswerte aus Visum
    :param transfer_links_sumo: Kapazitätszählungen aus Sumo
    :param threshhold: Toleranzbereich, in dem keine Anpassung der Kapazitätsbeschränkung nötig ist
    :param originCaps: Ursprüngliche Streckenkapazitäten am Anfang der Simulation
    :param reset: Ermöglicht das Zurücksetzen der Streckenkapazitäten auf die Anfangswerte
    :return: boolean, der angibt, ob mindestens eine Beschränkung angepasst wurde
    """
    modified = False
    for sumo_link in transfer_links_sumo:
        visum_link = [item for item in transfer_links_visum if abs(item[0]) == abs(sumo_link[0])][0]
        # Berechne Differenz zwischen gezählter und erwarteter Anzahl Fahrzeuge
        if abs(sumo_link[1] - visum_link[2]) > threshhold:
            # Außerhalb Toleranz -> neue Umlegung notwendig
            if sumo_link[1] < visum_link[2]:
                # kleiner als erwartet -> Begrenzung einrichten
                newCap = sumo_link[1]
            else:
                # größer als erwartet -> Begrenzung erhöhen oder auf Initialwert zurücksetzen
                visum_link_origin = [item for item in originCaps if abs(item[0]) == abs(sumo_link[0])][0]
                if sumo_link[1] < visum_link_origin[1]:
                    newCap = sumo_link[1]
                else:
                    newCap = visum_link_origin[1]
            if reset:
                # Alle Kapazitätsbeschränkungen auf Initialwert zurücksetzen
                visum_link_origin = [item for item in originCaps if abs(item[0]) == abs(sumo_link[0])][0]
                newCap = visum_link_origin[1]
            link = visum.Net.Links.FilteredBy("[FromNodeNo] = " + str(visum_link[3]) +
                                              " & [ToNodeNo] = " + str(visum_link[4]))
            link.SetAllAttValues("Capprt", newCap, False, False)
            modified = True
    return modified


def record(transfer_links_sumo, transfer_links_visum):
    """
    Ordnet die Auslastungswerte von Visum und Sumo einander zu

    :param transfer_links_sumo: Auslastungszählungen aus Sumo
    :param transfer_links_visum: Auslastungswerte aus Visum
    :return: Liste aus Tupeln, die die ID, Sumo- und Visum-Auslastung enthalten
    """
    recordList = []
    for sumo_link in transfer_links_sumo:
        visum_link = [item for item in transfer_links_visum if abs(item[0]) == abs(sumo_link[0])][0]
        recordList.append((sumo_link[0], sumo_link[1], doubleToInt(visum_link[2])))
    return recordList
