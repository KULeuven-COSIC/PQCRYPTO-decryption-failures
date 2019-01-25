# -*- coding: utf-8 -*-
from proba_util import *
from proba_util2 import *
from scipy.stats import norm
from math import log

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


def Probl(n, s, sprime, e, eprime):
    # get the variance of the secrets
    varS = distvariance(s)
    varE = distvariance(e)

    # calculate the distribution of var(S^T C)_ijk
    abss = {}
    abse = {}
    for i in sprime.keys():
        abss[i**2 * varE] = abss.get(i**2 * varE, 0) + sprime[i]
    for i in eprime.keys():
        abse[i**2 * varS] = abse.get(i**2 * varS, 0) + eprime[i]

    abss = iter_law_convolution_simplify(abss, n, 2**12)
    abse = iter_law_convolution_simplify(abse, n, 2**12)
    res = law_convolution(abss, abse)
    res = simplifyDistribution2(res)

    return clean_dist(res)


def Failgivenl(variance):
    # gaussian approximation of the distribution of the error based on the variance
    return lambda thres: norm.sf(thres, loc=0, scale=sqrt(variance))


def getplot(n, n2, thres, s, sprime, e, eprime, eprimeprime, errorCorrection=False, n3=1, **args):
    # only abs of eprimeprime is important
    absepp = law_abs(eprimeprime)

    # calculate the distribution of var(S^T C)_ijk
    probl = Probl(n, s, sprime, e, eprime)

    # calculate the distribution of the failure prob for each value of var(S^T C)_ijk
    thelist = []
    for varl in probl.keys():
        eppfail = {}
        fail = Failgivenl(varl)
        for i in absepp.keys():
            eppfail[fail(thres - i) + fail(thres + i)] = absepp[i]
        eppfail = iter_law_convolution_simplify(eppfail, n2, 2**8)
        for i in eppfail.keys():
            thelist.append((eppfail[i], varl, i))

    # avarage over the values of var(S^T C)_ijk
    faildist = {}
    for pepp, l, failprob in thelist:
        faildist[failprob] = faildist.get(failprob, 0) + probl[l] * pepp

    # final convolution
    faildist = iter_law_convolution_simplify(faildist, n3, 2**13)

    # sort the list by failure probability
    thelist = sorted(faildist.keys(), reverse=True)

    # calculate alpha and beta
    alpha, beta = [], []
    alphatmp, betatmp = 0, 0

    for i in thelist:
        alphatmp += faildist[i]
        alpha.append(alphatmp)

        betatmp += i * faildist[i]
        beta.append(betatmp / alphatmp)

    # cutoff values of alpha smaller than 2**-256 (not useful)
    beta2 = [b for (b, a) in zip(beta, alpha)]
    alpha2 = [a**-1 for a in alpha]

    if errorCorrection:
        beta2 = errorCorrection[0](beta2, **errorCorrection[1])

    return alpha2, beta2


def main():
    # choose which schemes to plot
    from NISTschemes import Kyber768, Saber, LizardCat3, LAC192, LAC256, FrodoKEM640, FrodoKEM976, Kyber1024, FireSaber, LightSaber, Kyber512, LightSaber, Kyber512

    toplot = [Kyber768, FrodoKEM976, LAC256, Saber, LizardCat3]

    import pickle
    import os.path
    for i in toplot:
        if os.path.exists(i['name'] + "-2.pkl"):
            continue
        alpha, beta = getplot(**i)
        with open(i['name'] + "-2.pkl", "wb") as f:
            pickle.dump([alpha, beta], f)

    # alphabeta

    # get colors
    fig, ax = plt.subplots()
    colors = ax._get_lines.prop_cycler

    for i in toplot:
        color = colors.next()[u'color']
        with open(i['name'] + "-2.pkl", "rb") as f:
            alpha, beta = pickle.load(f)
        plt.loglog(alpha, beta,
                   color=color, label=i['name'], basex=2, basey=2)
        print i['name'], 'failure probability: 2^' + str(log(min(beta), 2))

    # plt.gca().invert_xaxis()
    plt.xlabel(u'work to generate one weak sample (1/α)')
    plt.ylabel(u'weak ciphertext failure rate (β)')
    plt.legend(loc='lower right')
    plt.gca().set_xlim(left=1)
    plt.tight_layout()
    plt.savefig('alphabeta.pdf')
    plt.show()

    # betatot

    # get colors
    fig, ax = plt.subplots()
    colors = ax._get_lines.prop_cycler

    for i in toplot:
        color = colors.next()[u'color']
        with open(i['name'] + "-2.pkl", "rb") as f:
            alpha, beta = pickle.load(f)
        plt.loglog(beta, [a * b**-1 for a, b in zip(alpha, beta)],
                   color=color, label=i['name'], basex=2, basey=2)
        print i['name'], 'failure probability: 2^' + str(log(min(beta), 2))

    plt.axvline(x=2**-64, color='r', linestyle='--')
    # plt.gca().invert_xaxis()
    plt.xlabel(u'weak ciphertext failure rate (β)')
    plt.ylabel(u'total work to generate a failure (1/αβ)')
    plt.legend(loc='upper right')
    # plt.gca().set_xlim(left=1)
    plt.tight_layout()
    plt.savefig('betatot.pdf')
    plt.show()

    # sqrtalphatot
    # get colors
    fig, ax = plt.subplots()
    colors = ax._get_lines.prop_cycler

    for i in toplot:
        color = colors.next()[u'color']
        with open(i['name'] + "-2.pkl", "rb") as f:
            alpha, beta = pickle.load(f)
        plt.loglog(np.sqrt(alpha), [sqrt(a) * b**-1 for a, b in zip(alpha, beta)],
                   color=color, label=i['name'], basex=2, basey=2)
        print i['name'], 'failure probability: 2^' + str(log(min(beta), 2))

    # plt.gca().invert_xaxis()
    plt.xlabel(u'work to generate one weak sample (1/√α)')
    plt.ylabel(u'total work to generate a failure (1/β√α)')
    plt.legend(loc='lower right')
    plt.gca().set_xlim(left=1)
    plt.tight_layout()
    plt.savefig('sqrtalphatot.pdf')
    plt.show()


if __name__ == '__main__':
    main()
