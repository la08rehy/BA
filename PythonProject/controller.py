from visum_sumo import *
from sumo_visum import *


def run():
    folder = "H:/Benutzer/Joshua/git/bachelorarbeit/"
    fileName = "BezirkeUndKreuzungen"
    # fileName = "Streckensperrung"
    # fileName = "2xSumo_sequentiell"
    # Starten von Visum
    visumPath = os.path.abspath(folder + "Visum/Verwendet/" + fileName + ".ver")
    visum = win32com.client.Dispatch("Visum.Visum")
    visum.LoadVersion(visumPath)

    # Starten von Sumo
    sumoPath = os.path.abspath(folder + "Sumo/Verwendet/" + fileName + ".sumocfg")
    sumo.start(sumoPath)

    # Kopplung der Simulatoren (verwendete Beispiele)
    procedurePath = folder + "Visum/Verwendet/" + fileName + "_procedureParameters.xml"
    simulateTime(visum, procedurePath, [13, 14, 18, 19], 0, 150000, 10000, 1, 5, 2, [12, 14, 16, 32, 34, 36, 64, 66])  # BezirkeUndKreuzungen
    # simulateTime(visum, procedurePath, [2, 3, 5, 6, 7], 0, 150000, 10000, 1, 0, 2, [1, 3, 5])  # Strassensperre
    # simulateTime(visum, procedurePath, [2, 4], 0, 100000, 10000, 1, 0, 2, [1, 2, 3, 4])  # 2xSumo_sequentiell

    # Speichern und schließen
    sumo.close()
    # visum.SaveVersion(visumPath)


if __name__ == '__main__':
    run()
