# -*- coding: utf-8 -*-
from __future__ import print_function
import os

import matplotlib.pyplot as plt
import numpy as np
import itertools
import tqdm

from probabilityFunctions import calcFailgivennormct, calcFailgivennormctNoInfo, Pnormc, Ptheta, PthetaMax, failureboosting, failureboostingWithInfo, err, delta, est, delta2, err2

# from sage.all import *
from sage.all import RR, ZZ, ceil, sqrt, arccos, cos, pi, log, exp,\
    var, sin, numerical_integral, gamma, unit_step, erf, round, load, find_root, solve

ACCURACY = 2**-300
GRIDPOINTS = 300
CIPHERTEXTS = 30


# calculate failure boosting when x ciphertexts are known and save in txt file
def precalc(lwe_n, q, sd, B, m, name):
    name2 = name
    name = name + '/tmp'
    if not os.path.exists(name):
        os.mkdir(name)

    n = 2 * RR(lwe_n)
    q = RR(q)
    B = RR(B)
    vars = RR(sd**2)
    m = RR(m)

    #####################
    #  precalculations  #
    #####################

    # qt
    qt = q / 2**(B + 1)

    # |s| and |c*|
    norms = ZZ(ceil(sqrt(n * vars)))  # This is an approximation of the mean value
    normc2 = norms

    ################################################
    #  Calculate the grid and failure probability  #
    ################################################

    # make a grid of possible ciphertext points
    points = GRIDPOINTS
    xrange = np.linspace(0, normc2 * 3, points)
    yrange = np.linspace(0, float(pi), points)

    xrange = [RR(i) for i in xrange]
    yrange = [RR(i) for i in yrange]

    # calculate the usual failure boosting
    if not os.path.isfile(name + '/beta0.txt'):
        alpha, beta = failureboosting(xrange, yrange, n, qt, vars, norms, m)
        np.savetxt(name + '/alpha0.txt', alpha)
        np.savetxt(name + '/beta0.txt', beta)
        del alpha, beta

    # make a list of theta_SE
    thetaSE = arccos(qt / norms / normc2)  # Considering the worst case scenario for an attacker
    var('N')
    meanangle = arccos(cos(thetaSE) / sqrt(cos(thetaSE)**2 + sin(thetaSE)**2 / N))
    thetaSE_list = [(meanangle(N=i).n(), i) for i in list(range(1, CIPHERTEXTS))]

    # calculate alpha beta for each theta_SE
    def generate_alphabeta(thetaSE, i, name, xrange, yrange, n, qt, vars, norms, m):
        if not os.path.isfile('%s/beta%d.txt' % (name, i)):
            alphac, betac = failureboostingWithInfo(xrange, yrange, thetaSE, n, qt, vars, norms, m)
            np.savetxt('%s/alpha%d.txt' % (name, i), alphac)
            np.savetxt('%s/beta%d.txt' % (name, i), betac)
        return i

    f = lambda i: generate_alphabeta(i[0], i[1], name, xrange, yrange, n, qt, vars, norms, m)

    # import multiprocessing as mp
    # import pathos
    # pool = pathos.pools._ProcessPool(4, maxtasksperchild=1)
    # pool.map(f, thetaSE_list )
    # pool.close()
    # pool.join()
    # pool.clear()

    # TODO: fix memory leak in this map operation
    map(f, thetaSE_list)

    alphabetalist = []
    for i in range(0, 4):
        alpha = np.loadtxt('%s/alpha%d.txt' % (name, i))
        beta = np.loadtxt('%s/beta%d.txt' % (name, i))
        alphabetalist.append((alpha, beta, i))

    ################
    #  Let's plot  #
    ################
    alpha, beta, ciphertexts = alphabetalist[0]
    plt.loglog(alpha, beta, basex=2, basey=2, color='r', label='no extra info')
    for i in alphabetalist[1:]:
        alphac, betac, ciphertexts = i
        plt.loglog(alphac, betac, basex=2, basey=2, color='b', label=str(ciphertexts) + ' ciphertext')
    plt.xlabel(u'work to generate one weak sample (1/α)')
    plt.ylabel(u'weak ciphertext failure rate (β)')
    plt.legend(loc='lower right')
    plt.gca().set_xlim(left=1)
    plt.tight_layout()
    plt.savefig(name2 + '/alphabeta.pdf')
    # plt.show()
    plt.clf()

    plt.rcParams.update({'font.size': 16})
    plt.loglog(beta, [np.sqrt(a) * b**-1 for a, b in zip(alpha, beta)],
               basex=2, basey=2, color='r', label='no extra info')
    for i in alphabetalist[1:]:
        alphac, betac, ciphertexts = i
        plt.loglog(betac, [np.sqrt(a) * b**-1 for a, b in zip(alphac, betac)],
                   basex=2, basey=2, color='b', label=str(ciphertexts) + ' ciphertext')
    plt.axvline(x=2**-64, color='r', linestyle='--')
    plt.xlabel(u'weak ciphertext failure rate (β)')
    plt.ylabel(u'total work to generate a failure (1/β√α)')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(name2 + '/betatot.pdf')
    # plt.show()
    plt.clf()

    plt.rcParams.update({'font.size': 10})
    plt.loglog(np.sqrt(alpha), [np.sqrt(a) * b**-1 for a, b in zip(alpha, beta)],
               basex=2, basey=2, color='r', label='no extra info')
    # print("normal failprob: %f" % -np.log2(float(np.min(b))))
    tmp = min([(np.sqrt(a) * b**-1, b**-1) for a, b in zip(alpha, beta)], key=lambda x: x[0])
    # print("min failureboosting: (%f, %f)" % (np.log2(float(tmp[0])), np.log2(float(tmp[1]))))
    # print("min failureboosting: %f" % np.log2(float(np.min([np.sqrt(a) * b**-1 for a, b in zip(alpha, beta)]))))
    for i in alphabetalist[1:]:
        alphac, betac, ciphertexts = i
        plt.loglog(np.sqrt(alphac), [np.sqrt(a) * b**-1 for a, b in zip(alphac, betac)],
                   basex=2, basey=2, color='b', label=str(ciphertexts) + ' ciphertext')
        # print out cost of attack
        tmp = min([(np.sqrt(a) * b**-1, b**-1) for a, b in zip(alphac, betac)], key=lambda x: x[0])
        # print("min failureboosting with %d ciphertexts: (%f, %f)"
        #       % (ciphertexts, np.log2(float(tmp[0])), np.log2(float(tmp[1]))))
        # print("min failureboosting with %d ciphertexts: (%f, %f)"
        #       % (ciphertexts, np.log2(float(np.min([np.sqrt(a) * b**-1 for a, b in zip(alphac, betac)]))), numfailures))
    plt.xlabel(u'work to generate one weak sample (1/√α)')
    plt.ylabel(u'total work to generate a failure (1/β√α)')
    plt.legend(loc='lower right')
    plt.gca().set_xlim(left=1)
    plt.tight_layout()
    plt.savefig(name2 + '/sqrtalphatot.pdf')
    # plt.show()
    plt.clf()


def directionalFailureboosting(lwe_n, q, sd, B, m, name, limitedqueries=False, multitarget=False):
    alphabetalist = []
    for i in range(0, CIPHERTEXTS):
        alpha = np.loadtxt('%s/tmp/alpha%d.txt' % (name, i))
        beta = np.loadtxt('%s/tmp/beta%d.txt' % (name, i))
        alphabetalist.append((alpha, beta, i))

    # save the work needed to get x ciphertexts
    worklist = []
    querylist = []
    problist = []

    # save the work needed to get x ciphertexts (old method)
    workoldlist = []
    queryoldlist = []
    proboldlist = []

    # save the work needed to get the next ciphertext
    worknextciphertext = []
    querynextciphertext = []

    # number of ciphertexts x
    ciphertextlist = []

    # list of optimal alpha beta values
    ablist = []

    # set by hand
    if multitarget and limitedqueries:
        LMT = 59.5

    if not multitarget and limitedqueries:
        LMT = 57.2

    firstmt = not multitarget  # if multitarget attack: don't restrict first sample
    for alphabetavalues in alphabetalist:
        # add new ciphertext
        alphac, betac, ciphertexts = alphabetavalues
        optimalab = min([(np.sqrt(a) * b**-1, b**-1, a) for a, b in zip(alphac, betac)], key=lambda x: x[0])
        if limitedqueries and firstmt and optimalab[1] > 2**LMT:
            if max(betac) <= 2**-LMT:
                with open(name + '/attackcost.txt', 'a') as f:
                    print('attack not possible for: limited queries: %r,  multitarget %r'
                          % (limitedqueries, multitarget))
                    print('attack not possible for: limited queries: %r,  multitarget %r'
                          % (limitedqueries, multitarget), file=f)
                return 0
            idx = np.where(betac > 2**-LMT)[0][-1]
            optimalab = (np.sqrt(alphac[idx]) * betac[idx]**-1, betac[idx]**-1, alphac[idx])
        firstmt = True
        ablist.append(optimalab)
        ciphertextlist.append(len(ablist))

        worknextciphertext.append(optimalab[0])
        querynextciphertext.append(optimalab[1])

        # calculate the best attack strategy
        # setup the lagrange function and solve
        vlam = var('vlam')
        eq = 1
        normalizer = ablist[0][0]
        for ab, b, a in ablist:
            eq *= vlam + (ab / normalizer)

        eq -= vlam**len(ablist) / (1 - exp(-1))
        lam = find_root(eq, 0.001, 500000)

        # calculate the amount of work to get the next failure and sum
        work = 0
        prob = 1
        queries = 0

        ab, b, a = ablist[0]
        l = np.log(lam * (normalizer / ab) + 1)
        if multitarget:
            queries += l * b / 2**64
        else:
            queries = l * b
        work += l * ab
        prob *= 1 - exp(-l)
        for ab, b, a in ablist[1:]:
            l = np.log(lam * (normalizer / ab) + 1)
            queries += l * b
            work += l * ab
            prob *= 1 - exp(-l)

        # traditional method
        ab, b, a = ablist[0]
        queriesold = b * len(ablist)
        workold = ab * len(ablist)
        probold = 1 - exp(-1)

        # save all our results
        worklist.append(work)
        querylist.append(queries)
        problist.append(prob)

        workoldlist.append(workold)
        queryoldlist.append(queriesold)
        proboldlist.append(prob)

        # and print
        with open(name + '/attackcost.txt', 'a') as f:
            print('\n limited queries: %r,  multitarget %r' % (limitedqueries, multitarget), file=f)
            print('work to obtain %d ciphertexts with same probability:' % len(ablist), file=f)
            print('queries: %f, total work:%f, probability: %f'
                  % (np.log2(float(queries)), np.log2(float(work)), prob), file=f)

    ################
    #  Let's plot  #
    ################
    plt.loglog(ciphertextlist, worklist, label='work', basex=2, basey=2)
    if not multitarget:
        plt.loglog(ciphertextlist, workoldlist, label='work - traditional', basex=2, basey=2)
    plt.loglog(ciphertextlist, querylist, label='queries', basex=2, basey=2)
    if not multitarget:
        plt.loglog(ciphertextlist, queryoldlist, label='queries - traditional', basex=2, basey=2)
    plt.title('work/queries to obtain n ciphertexts')
    plt.xlabel(u'ciphertexts')
    plt.ylabel(u'total work/queries')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(name + '/workqueriesforxciphertexts-LQ%r,MT%r.pdf' % (limitedqueries, multitarget))
    # plt.show()
    plt.clf()

    plt.rcParams.update({'font.size': 16})
    plt.loglog(ciphertextlist, worklist, label='work', basex=2, basey=2)
    if not multitarget:
        plt.loglog(ciphertextlist, workoldlist, label='work - traditional', basex=2, basey=2, linestyle='dashed')
    plt.title('work to obtain n ciphertexts')
    plt.xlabel(u'ciphertexts')
    plt.ylabel(u'total work')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(name + '/workforxciphertexts-LQ%r,MT%r.pdf' % (limitedqueries, multitarget))
    # plt.show()
    plt.clf()

    plt.rcParams.update({'font.size': 16})
    plt.loglog(ciphertextlist, querylist, label='queries', basex=2, basey=2)
    if not multitarget:
        plt.loglog(ciphertextlist, queryoldlist, label='queries - traditional', basex=2, basey=2, linestyle='dashed')
    plt.title('queries to obtain n ciphertexts')
    plt.xlabel(u'ciphertexts')
    plt.ylabel(u'total queries')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(name + '/queriesforxciphertexts-LQ%r,MT%r.pdf' % (limitedqueries, multitarget))
    # plt.show()
    plt.clf()

    plt.rcParams.update({'font.size': 16})
    plt.loglog(ciphertextlist, worknextciphertext, label='work', basex=2, basey=2)
    plt.loglog(ciphertextlist, querynextciphertext, label='query', basex=2, basey=2)
    plt.title('work/queries to obtain next ciphertexts')
    plt.xlabel(u'available failing ciphertexts')
    plt.ylabel(u'total work/queries')
    plt.legend(loc='lower left')
    plt.tight_layout()
    plt.savefig(name + '/worknextciphertext-LQ%r,MT%r.pdf' % (limitedqueries, multitarget))
    # plt.show()
    plt.clf()

    plt.rcParams.update({'font.size': 10})


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=150)
    parser.add_argument("-q", type=int, default=100)
    parser.add_argument("-sd", type=float, default=0.65)
    parser.add_argument("-B", type=int, default=1)
    parser.add_argument("-m", type=int, default=1)
    parser.add_argument("-name", type=str, default="search", help="plot output filename")
    args = parser.parse_args()

    n, q, sd, B, m = args.n, args.q, args.sd, args.B, args.m
    print("n = %d, q = %d, sd = %.2f, B = %d, m=%d" % (n, q, sd, B, m))
    print("single bit error log: %f, low prob: %f" % (delta(n, q, sd), delta2(n, q, sd, B)))
    print("failure prob log: %f, low prob: %f" % (err(n, q, sd, m), err2(n, q, sd, B, m)))
    est(n, q, sd)
    precalc(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)
    onetarget(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)
    multitarget(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)


import __main__
if hasattr(__main__, "__file__") and __name__ == "__main__":
    main()
