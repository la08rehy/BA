import os
import sys
import controller


def runHybridSimulation(start, end):
    for i in range(start, end):
        file_name = "D" + str(i) + ".out"
        sys.stdout = open(file_name, "w")
        controller.run()
        print("Durchgang", str(i+1), "done!", file=sys.stderr)


# Kopiert ein .data-File ohne eingefügte Daten (nur Variablengerüst etc)
def copySceleton(fromPath, toPath):
    f1 = open(fromPath, "r")
    f2 = open(toPath, "w")
    lines = f1.readlines()
    for i in range(len(lines)):
        if len(lines[i]) == 1 or lines[i][0] == "#":
            print(lines[i], end="")
            f2.write(lines[i])
        else:
            print(lines[i][:lines[i].index("=") + 2])
            f2.write(lines[i][:lines[i].index("=") + 2] + "\n")


# Korrigiert fehlerhafte Variablennamen (mit Zahl am Anfang) durch Verschiebung ans Ende des Namens (IN COPY!)
def changeNames(fromPath, toPath):
    f1 = open(fromPath, "r")
    f2 = open(toPath, "w")
    lines = f1.readlines()
    for i in range(len(lines)):
        if len(lines[i]) == 1 or lines[i][0] == "#":
            print(lines[i], end="")
            f2.write(lines[i])
        elif lines[i][:2].isnumeric():
            n = int(lines[i][:2])
            index = lines[i].index(" ")
            print((lines[i][:index] + "_" + str(n) + lines[i][index:])[3:])
            f2.write((lines[i][:index] + "_" + str(n) + lines[i][index:])[3:])
        else:
            print(lines[i])
            f2.write(lines[i])


# Kopiert alle relevanten Zeilen (die letzten 18) einer DX.out Datei in DX_cutted.out
def cutRelevantOutput(folder, fromFile, toFile):
    for i in range(fromFile, toFile):
        f1 = open(folder + "D" + str(i) + ".out", "r")
        f2 = open(folder + "D" + str(i) + "_cutted.out", "w")
        lines = f1.readlines()
        lines_cutted = lines[-18:]
        for j in range(len(lines_cutted)):
            print(lines_cutted[j])
            f2.write(lines_cutted[j])


# Kopiert alle relevanten Zeilen (Threshhold) einer DX.out Datei in DX_cutted.out
def cutRelevantOutput2(folder, fromFile, toFile):
    for i in range(fromFile, toFile):
        f1 = open(folder + "D" + str(i) + ".out", "r")
        f2 = open(folder + "D" + str(i) + "_cutted.out", "w")
        lines = f1.readlines()
        print(lines[-20][:-2])
        f2.write(lines[-20])


if __name__ == '__main__':
    # runHybridSimulation(0, 20)
    # copySceleton("Streckensperrung_100_ohneAlternative.py", "Streckensperrung_100_OhneAlternative.py")
    # changeNames("BezirkeUndKreuzungen_100_V1.py", "temp.data")
    # cutRelevantOutput("../DATA/Streckensperrung/OhneAlternative/", 0, 20)
    cutRelevantOutput2("../DATA/Streckensperrung_Threshhold/0/", 0, 20)
