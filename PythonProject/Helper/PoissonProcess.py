import math
from random import random


def probability_density_function(x, flowRate):
    """
    Wahrscheinlichkeitsdichtefunktion

    :param x: p(x) ist die Wsk, dass x Events im Zeitintervall auftreten
    :param flowRate: erwartete durchschnittliche Eventauftrittsrate (mue)
    :return:
    """
    return (pow(flowRate, x) / math.factorial(x)) * pow(math.e, (-1 * flowRate))


def vehicles_between_a_and_b(a, b, flowRate):
    """
    Wsk, dass bei erwarteter flowrate zwischen a und b Fzgs im Zeitintervall ankommen

    :param a: untere Grenze Fzg (einschließlich)
    :param b: obere Grenze Fzg (einschließlich)
    :param flowRate:
    :return:
    """
    tempSum = 0
    for i in range(a, b + 1):
        tempSum += probability_density_function(i, flowRate)
    return tempSum


def poisson_distribution_for_a_point_in_time(arrivalRate):
    """
    Poisson-verteilte zufällige Anzahl von ankommenden Fzgs pro Zeitschritt \n
    Bsp.: arrivalRate=2 (pro Minute)
        -> z.B. X=0.201 -> p(0) < X < p(1) -> 1 arrivingVeh im Zeitschritt

    :param arrivalRate: Ankunftsrate von Fzgs
    :return:
    """
    # TODO is flowRate equal arrivalRate?
    # 13.5 in cete_13.pdf
    X = random()  # between 0 and 1
    counter = 0
    tempval = vehicles_between_a_and_b(0, counter, arrivalRate)
    while tempval <= X:
        counter += 1
        tempval = vehicles_between_a_and_b(0, counter, arrivalRate)
    return counter


def exponential_distribution_for_arrival_intervals(mean_headway):
    """
    Mit Exponentialverteilung zufällig erstellte Zeitintervalle zwischen zwei Fahrzeug-Ankünften

    :param mean_headway: Durchschnittliche Ankunftsrate von Fahrzeugen
    :return:
    """
    X = random()
    return -1 * mean_headway * math.log(X, math.e)


if __name__ == '__main__':
    # Testing
    print(probability_density_function(0, 2))
    print(probability_density_function(1, 2))

    print(vehicles_between_a_and_b(0, 0, 2))
    print(vehicles_between_a_and_b(0, 1, 2))
    print(vehicles_between_a_and_b(2, 4, 2))

    print("no vehicle in one hour: " + str(probability_density_function(0, 2) * 60))

    print(poisson_distribution_for_a_point_in_time(2))
    print(exponential_distribution_for_arrival_intervals(30))
