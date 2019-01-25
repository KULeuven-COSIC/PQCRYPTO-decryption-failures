from scipy.stats import binom, hypergeom
import numpy as np
from tqdm import tqdm
import itertools
import os
import pickle

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

# take into account error correction that can correct up to te errors
def LACprob(prob, ne, te):
    res = binom.sf(te, ne, p=prob)
    return res


# load samples
def getsample(location):
    with open(location) as f:
        for i in range(0, 3):
            f.next()
        for line in f:
            if line[0] != "=":
                yield int(line)


# get the experimental data
def checkexperiment(location, errors):
    readout = getsample(location)
    numsamples = 0
    numfails = 0
    fail2 = [0] * len(errors)
    for fail in tqdm(readout):
        for i in errors:
            if fail >= i:
                fail2[i] += 1
        numsamples += 1.
        numfails += fail

    fail2 = [i / numsamples for i in fail2 if i > 0]

    return fail2


# calculate the theoretical predictions
def checktheory(thres, n, ne, p, te, s):
    # calculate failure probability for a certain number of ones in se
    pfaildict = {}
    for se in range(0, n + 1):
        tmp = [binom.sf((thres + i + se) / 2, se, p=0.5) * s[i] for i in s]
        tmp2 = [binom.sf((thres + 1 + i + se) / 2, se, p=0.5) * s[i]
                for i in s]
        pfail = 1.5 * sum(tmp) + 0.5 * sum(tmp2)
        pfaildict[se] = pfail

    # set everything to zero
    fail = 0
    fail2 = {}
    for te1 in te:
        fail2[te1] = 0

    # loop over all norm values
    for l1, l2 in tqdm(itertools.combinations_with_replacement(range(0, n + 1), 2), leave=False, total=n * (n + 1) / 2):
        # probability of a certain norm
        pl1 = binom.pmf(l1, n=n, p=p)
        pl2 = binom.pmf(l2, n=n, p=p)
        pl = pl1 * pl2
        if l1 != l2:
            pl *= 2

        # skip if probability is too small
        if pl < 2**-200:
            continue

        # calculate the probability of a failure
        failtmp = 0
        # loop over all possible number of nonzero elements in se
        for se1 in range(max(0, l1 + l2 - n), min(l1, l2) + 1):
            # probability of number of nonzero elements in se
            pse = hypergeom.pmf(k=se1, M=n, n=l1, N=l2)
            # probability of failure for a certain se1
            pfail = pfaildict[se1]
            # weighted average share
            failtmp += pse * pfail

        # for new model, take error correction into account
        fail += pl * failtmp
        for te1 in te:
            fail2[te1] += pl * LACprob(failtmp, ne, te1)

    new = []
    old = []
    for te1 in te:
        # for old model, take error correction into account
        old.append(LACprob(fail, ne, te1))
        new.append(fail2[te1])

    return new, old


def main():
    # location of the failure files
    location = 'check256.txt'
    # maximum error correction to plot
    te = 30
    # scheme to use
    from NISTschemes import LAC256 as scheme
    # use experimental data
    doExperiment =True

    # load some parameters
    n = 2 * scheme['n']
    s = scheme['s']
    thres = scheme['thres']
    alg = scheme['name']
    ne = n / 2 - 1
    p = s[1] + s[-1]
    errors = list(range(0, te + 1))

    # get experimental data
    if doExperiment:
        if os.path.exists('modelLAC-experiment-' + alg + ".pkl"):
            print 'preload experiment'
            with open('modelLAC-experiment-' + alg + ".pkl", "rb") as f:
                experiment = pickle.load(f)[0]
        else:
            experiment = checkexperiment(location, errors)
            with open('modelLAC-experiment-' + alg + ".pkl", "wb") as f:
                pickle.dump([experiment], f)
    else:
        experiment = [1.]


    # get theoretical data
    if os.path.exists('modelLAC-theory-' + alg + ".pkl"):
        print 'preload experiment'
        with open('modelLAC-theory-' + alg + ".pkl", "rb") as f:
            new, old = pickle.load(f)
    else:
        new, old = checktheory(thres, n, ne, p, errors, s)
        with open('modelLAC-theory-' + alg + ".pkl", "wb") as f:
            pickle.dump([new, old], f)

    experiment = experiment[1:te+1]
    old = old[0:te]
    new = new[0:te]

    # remove elements that are statistically not sound
    experiment = experiment[:-2]

    
    # plot
    plt.xlabel(u'maximum number of flipped bits in the message')
    plt.ylabel(u'probability')
    plt.semilogy(old,basey=2, color='b', label='independency model', linestyle='--')
    plt.semilogy(new, basey=2, color='g', label='dependency model')
    plt.scatter(errors[0:len(experiment)], experiment, color='r', marker='p', label='experimental data')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('modelLAC-'+alg+'.pdf')


if __name__ == '__main__':
    main()
