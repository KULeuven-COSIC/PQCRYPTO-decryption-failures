# -*- coding: utf-8 -*-
import numpy as np
from tqdm import tqdm
import pickle
from scipy.stats import binom
import os

# get the information from the sample file
def getsample(location):
    with open(location) as f:
        for i in range(0, 3):
            f.next()
        for line in f:
            if line[0] != "=":
                yield int(line)


def getdependency(location, errors, n):
    readout = getsample(location)
    numsamples = 0
    numfails = 0
    failnumexp = {}

    # calculate the distribution of the number of failures
    for fail in tqdm(readout):
        failnumexp[fail] = failnumexp.get(fail, 0) + 1
        numsamples += 1.
        numfails += fail

    # calculate the failure probability of an individual bit
    probfail = numfails / numsamples / n

    # theoretical failure distribution
    failnumtheo = {}
    for i in errors:
        failnumtheo[i] = binom.pmf(i, n, p=probfail)

    # parse in the right variables
    independent = [failnumtheo[i] for i in errors]
    experiment = [failnumexp[i] / numsamples for i in errors if i in failnumexp.keys()]
    errorsexp = [i for i in errors if i in failnumexp.keys()]

    return independent, errors, experiment, errorsexp


def main():
    # location and name of the algorithm
    alg = 'LAC256'
    location = 'check256.txt'
    # other parameters
    maxerrors = 25
    n = 1023
    recalculate = True

    errors = list(range(0, maxerrors))

    if os.path.exists('dependency-' + alg + ".pkl"):
        with open('dependency-' + alg + ".pkl", "rb") as f:
            independent, errorsind, experiment, errorsexp = pickle.load(f)
        if len(errors) <= len(errorsind):
            recalculate = False

    if recalculate:
        independent, errorsind, experiment, errorsexp = getdependency(location, errors, n)
        with open('dependency-' + alg + ".pkl", "wb") as f:
            pickle.dump([independent, errorsind, experiment, errorsexp], f)

    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt

    plt.xlabel(u'number of flipped bits in the message')
    plt.ylabel(u'probability')
    plt.scatter(errorsexp[:maxerrors], experiment[:maxerrors], label='experimental', color='r', marker='p')
    plt.semilogy(errorsind[:maxerrors], independent[:maxerrors], basey=2, label='theoretical', color='b', linestyle='--')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('dependency-' + alg + '.pdf')


if __name__ == '__main__':
    main()
