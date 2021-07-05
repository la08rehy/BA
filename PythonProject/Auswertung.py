import math
import matplotlib.pyplot as plt
import BezirkeUndKreuzungen_100_V1 as v100_v1
import BezirkeUndKreuzungen_300_V1 as v300_v1
import BezirkeUndKreuzungen_100_V2 as v100_v2
import BezirkeUndKreuzungen_300_V2 as v300_v2
import Streckensperrung_100_mitAlternative as s100mit
import Streckensperrung_100_ohneAlternative as s100ohne
import Threshhold_Ints as t


def changeFormat(l):
    res = []
    for i in range(len(l[0])):
        temp = []
        for j in range(len(l)):
            temp.append(l[j][i])
        res.append(temp)
    return res


def convertTime(l):
    res = []
    for t in l:
        temp = str(t[0]).zfill(6)
        tempTime = sum([int(temp[0:2]) * 3600, int(temp[2:4]) * 60, int(temp[4:6]) * 1])
        res.append((tempTime, t[1]))
    return res


def countForEachTimeStep(l, timeintervall):
    res = []
    for i in range(timeintervall):
        curTimeStep = [x[1] for x in l if 3600 * i <= x[0] < 3600 * (i + 1)]
        flattened = [x for y in curTimeStep for x in y]
        counted = counts(flattened)
        res.append(counted)
    return res


def counts(a):
    b = list(set(a))
    b.sort()
    res = []
    for i in range(len(b)):
        res.append((b[i], a.count(b[i])))
    return res


def removeIrrelevantLinks(a, b):
    res = []
    for i in range(len(a)):
        temp = []
        for t in a[i]:
            if t[0] in b:
                temp.append(t)
        res.append(temp)
    return res


def take(l, n):
    return [a[n] for a in l]


# relevant = [12, 14, 16, 32, 34, 36, 64, 66]  # Links zu Sumo
def plotFahrzeugerzeugung(VOLUMEN, relevant, startDurchgang, endDurchgang):
    volumen_visum = []  # für jeden Link eine Liste aller Zeitschritte
    for LINK in relevant:
        volumen_visum.append(take(eval("v" + VOLUMEN + "_v1.d0_erzeugung_" + str(LINK)), 0))
        volumen_sumo = []
        for i in range(startDurchgang, endDurchgang):
            volumen_sumo.append(eval("v" + VOLUMEN + "_v1.d" + str(i) + "_erzeugung_" + str(LINK)))
            volumen_sumo.append(eval("v" + VOLUMEN + "_v2.d" + str(i) + "_erzeugung_" + str(LINK)))
        volumen_sumo = [take(x, 1) for x in volumen_sumo]
        # print(str(LINK), "(visum)", volumen_visum[-1])
        # print(str(LINK), "(sumo)", volumen_sumo)
        plt.figure()
        plt.plot(range(1, len(volumen_visum[-1]) + 1), volumen_visum[-1], label="Berechnete Auslastung Visum")
        plt.plot([], label="Geplante Fahrzeuge")
        plt.boxplot(changeFormat(volumen_sumo))
        plt.title("Link " + str(LINK) + " und Volumen " + VOLUMEN)
        plt.xlabel("Zeit [h]")
        plt.ylabel("# Fahrzeuge")
        plt.legend(loc="upper left")


# relevant = [-68, -67, -35, -15, 15, 35, 67, 68]  # Links in Sumo
def plotRoutenplanung(VOLUMEN, VERSION, relevant, startDurchgang, endDurchgang, timeintervall):
    volumen_visum = []
    for LINK in relevant:
        link = "m" + str(LINK)[1:] if LINK < 0 else LINK
        volumen_visum.append(take(eval("v" + VOLUMEN + "_v" + VERSION + ".visum_" + str(link)), 1))
        # print(str(LINK), "(visum)", volumen_visum[-1])

    durchgaenge = []
    for i in range(startDurchgang, endDurchgang):
        converted = convertTime(eval("v" + VOLUMEN + "_v" + VERSION + ".sumo_d" + str(i) + "_routing"))
        counted = countForEachTimeStep(converted, timeintervall)
        onlyRelevant = removeIrrelevantLinks(counted, relevant)
        links = []
        for j in range(len(relevant)):
            zeitschritte = []
            for k in range(len(onlyRelevant)):
                for e in onlyRelevant[k]:
                    if e[0] == relevant[j]:
                        zeitschritte.append(e[1])
                        break
                if len(zeitschritte) - 1 < k:
                    zeitschritte.append(0)
            links.append(zeitschritte)
        durchgaenge.append(links)
    for i in range(len(relevant)):
        oneLink = take(durchgaenge, i)
        # print(str(relevant[i]), "(sumo)", oneLink)
        plt.figure()
        plt.plot(range(1, len(volumen_visum[i]) + 1), volumen_visum[i], label="Berechnete Auslastung Visum")
        plt.plot([], label="Geplante Fahrzeuge")
        plt.boxplot(changeFormat(oneLink))
        plt.title("Link " + str(relevant[i]) + " und Volumen " + VOLUMEN)
        plt.xlabel("Zeit [h]")
        plt.ylabel("# Fahrzeuge")
        plt.legend(loc="upper left")


# relevant = [2,3,-5,(6,7,-8),9]  # Links in Sumo
def plotRoutenplanung2(alt, relevant, startDurchgang, endDurchgang, timeintervall):
    volumen_visum = []
    for LINK in relevant:
        link = "m" + str(LINK)[1:] if LINK < 0 else LINK
        volumen_visum.append(take(eval("s100" + alt + ".visum_" + str(link)), 1))
        # print(str(LINK), "(visum)", volumen_visum[-1])

    durchgaenge = []
    for i in range(startDurchgang, endDurchgang):
        converted = convertTime(eval("s100" + alt + ".sumo_d" + str(i) + "_routing"))
        counted = countForEachTimeStep(converted, timeintervall)
        onlyRelevant = removeIrrelevantLinks(counted, relevant)
        links = []
        for j in range(len(relevant)):
            zeitschritte = []
            for k in range(len(onlyRelevant)):
                for e in onlyRelevant[k]:
                    if e[0] == relevant[j]:
                        zeitschritte.append(e[1])
                        break
                if len(zeitschritte) - 1 < k:
                    zeitschritte.append(0)
            links.append(zeitschritte)
        durchgaenge.append(links)
    for i in range(len(relevant)):
        oneLink = take(durchgaenge, i)
        # print(str(relevant[i]), "(sumo)", oneLink)
        plt.figure()
        # plt.plot(range(1, len(volumen_visum[i]) + 1), volumen_visum[i], label="Berechnete Auslastung Visum")
        # plt.plot([], label="Geplante Fahrzeuge")
        plt.boxplot(changeFormat(oneLink))
        plt.title("Link " + str(relevant[i]) + " und Volumen 100")
        plt.xlabel("Zeit [h]")
        plt.ylabel("# Fahrzeuge")
        # plt.legend(loc="upper left")


def plotThreshhold(threshhold, startDurchgang, endDurchgang):
    newCalc = []
    for i in range(startDurchgang, endDurchgang):
        newCalc.append(eval("t.t"+threshhold+"_d"+str(i)))
    plt.figure()
    for i in range(len(newCalc)):
        plt.plot(newCalc[i])
    plt.yticks([0, 1], ["nein", "ja"])
    plt.title("Neue Umlegungen bei Threshhold "+str(threshhold))
    plt.xlabel("Zeit [h]")
    plt.ylabel("Neue Umlegung")
    plt.legend(loc="upper left")


if __name__ == "__main__":
    # plotFahrzeugerzeugung(str(100), [12, 14, 16, 32, 34, 36, 64, 66], 0, 20)
    # plotRoutenplanung(str(300), str(2), [-68, -67, -35, -15, 15, 35, 67, 68], 0, 20, 15)
    # plotRoutenplanung2("ohne", [2, 3, -5, 9], 0, 20, 15)
    # plotRoutenplanung2("mit", [2, 3, -5, 6, 7, -8, 9], 0, 20, 15)
    # plotThreshhold(str(10), 0, 20)
    plt.show()
