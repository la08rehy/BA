from visum_sumo import *
from sumo_visum import *

visum = None


if __name__ == '__main__':
    folder = "H:/Benutzer/Joshua/git/bachelorarbeit/"
    fileName = "MehrereKreuzungen_hierarchisch"
    # fileName = "Beispiel_von_Moritz"
    # fileName = "Achteck2xSumo"
    # Starten von Visum
    visumPath = os.path.abspath(folder + "Visum/" + fileName + ".ver")
    visum = win32com.client.Dispatch("Visum.Visum")
    visum.LoadVersion(visumPath)

    # Starten von Sumo
    fileName += "_nurSumo"
    sumoPath = os.path.abspath(folder + "Sumo/" + fileName + ".sumocfg")
    sumo.start(sumoPath)

    # Kopplung der Simulatoren
    simulateTime(visum, folder, [13, 14, 18, 19], 0, 230000, 10000, 1, 5, 2, [12, 14, 16, 32, 34, 36, 64, 66])
    # simulateTime(visum, folder, [3, 4, 8, 9, 13, 14, 18, 19, 23, 24, 36, 37], 0, 230000)
    # simulateTime(visum, folder, [2, 3, 6, 7], 0, 10000)
    # simulateTime(visum, folder, [3, 4, 7, 8], 0, 10000)
    # bezirkeUndKreuzungen inLinks: [12, 14, 17, 19, 42, 44, 47, 49]

    # Speichern und schließen
    sumo.close()
    # visum.SaveVersion(visumPath)  # TODO evtl später einkommentieren
