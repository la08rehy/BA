from utility import *


def getVolAndCap_Visum(links_to_sumo, curTime):
    links_in_visum = []
    it = links_to_sumo.Iterator
    while it.Valid:
        curLink = it.Item
        no = curLink.AttValue("no")
        if not curLink.AttValue("isForward"):
            no = no * (-1)
        cap = curLink.AttValue("CapPrt")
        curVol = curLink.AttValue("VOLVEHPRT(" + str(curTime).zfill(6)[0:4] + ")")
        # links_to_sumo -> links_in_visum: Richtung umdrehen
        fromNode = curLink.AttValue("ToNodeNo")
        toNode = curLink.AttValue("FromNodeNo")
        no = no * (-1)
        links_in_visum.append((no, cap, curVol, fromNode, toNode))
        it.Next()
    return links_in_visum


def getVol_Sumo(allPaths_links):
    lastLinks = flatten([[x[-1]] for x in allPaths_links])
    links_in_sumo = [(x, lastLinks.count(x)) for x in set(lastLinks)]
    return links_in_sumo


def capacityModification(visum, links_in_visum, links_in_sumo, threshhold, originCaps):
    modified = False
    for sumo_link in links_in_sumo:
        # print(sumo_link, links_in_visum)
        visum_link = [item for item in links_in_visum if abs(item[0]) == abs(sumo_link[0])][0]
        if abs(sumo_link[1] - visum_link[2]) > threshhold:
            # Außerhalb Toleranz -> neue Umlegung notwendig
            if sumo_link[1] < visum_link[2]:
                # kleiner als erwartet -> Begrenzung einrichten
                newCap = sumo_link[1]
            else:
                # größer als erwartet -> Begrenzung erhöhen oder entfernen
                visum_link_origin = [item for item in originCaps if abs(item[0]) == abs(sumo_link[0])][0]
                if sumo_link[1] < visum_link_origin[1]:
                    newCap = sumo_link[1]
                else:
                    newCap = visum_link_origin[1]
            link = visum.Net.Links.FilteredBy("[FromNodeNo] = " + str(visum_link[3]) +
                                              " & [ToNodeNo] = " + str(visum_link[4]))
            link.SetAllAttValues("Capprt", newCap, False, False)
            modified = True
    return modified
