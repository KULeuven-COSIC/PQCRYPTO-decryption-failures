# -*- coding: utf-8 -*-

from __future__ import print_function
from probabilityFunctions import delta, delta2, err, err2, est, Ptheta, PthetaMax
from sage.all import RR, ZZ, ceil, sqrt, pi, cos, arccos, floor, sin
import numpy as np
import matplotlib.pyplot as plt
from samplingfailures import normalize, rotate, sampleFailure, probij, probijvector

from tqdm import trange, tqdm
import random

TESTS = 1000
REP = 3


def plotAngleDifference(lwe_n, q, sd, B, m, name):
    points = 10000

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
    normc = norms

    K = qt / norms / normc

    #####################
    #   distributions   #
    #####################

    angle = np.linspace(0, float(pi), points)

    uniformdist = np.vectorize(Ptheta)(angle, n)
    uniformdist = np.nan_to_num(np.vectorize(float)(uniformdist))
    uniformdist = uniformdist / (sum(uniformdist) * float(pi) / points)

    if m > 1.5:
        Pthetamax2 = PthetaMax(n, 2 * (m - 1))
        maxdist = np.vectorize(Pthetamax2)(angle)
        maxdist = maxdist / (sum(maxdist) * float(pi) / points)
    else:
        maxdist = uniformdist

    posdist = np.vectorize(Ptheta)(arccos((cos(angle) - K**2) / (1 - K**2)), n - 1)
    posdist = np.nan_to_num(np.vectorize(float)(posdist))
    posdist = posdist / (sum(posdist) * float(pi) / points)

    negdist = np.vectorize(Ptheta)(arccos((cos(angle) + K**2) / (1 - K**2)), n - 1)
    negdist = np.nan_to_num(np.vectorize(float)(negdist))
    negdist = negdist / (sum(negdist) * float(pi) / points)

    prob = 0
    for y in trange(0, len(angle)):
        for x in range(0, y):
            prob += posdist[x] * maxdist[y]

    with open(name + '/findingfailurelocation.txt', 'a') as f:
        print("theoretical probability of good estimate: %f" % (prob,), file=f)

    ############
    #   plot   #
    ############

    angledivpi = angle / float(pi)
    import matplotlib.ticker as tck

    plt.rcParams.update({'font.size': 10})
    plt.plot(angledivpi, uniformdist, label=u'Θₙ')
    plt.xlim(left=0, right=1)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(tck.FormatStrFormatter('%g $\pi$'))
    ax.xaxis.set_major_locator(tck.MultipleLocator(base=0.25))
    # plt.legend(loc='upper left')
    plt.xlabel(u'θ')
    plt.ylabel(u'pdf')
    plt.tight_layout()
    plt.savefig(name + '/randomangle.pdf')
    # plt.show()
    plt.clf()

    # angle = angle/float(pi)
    cosangle = np.cos(angle)
    plt.rcParams.update({'font.size': 16})
    plt.plot(cosangle, posdist, label=u'C(δ₁,₀)')
    plt.plot(cosangle, negdist, label=u'C(δ₁,₀ + N)')
    plt.plot(cosangle, uniformdist, label=u'C(r); r ≠ (δ₁,₀ mod N)')
    if m > 1:
        plt.plot(cosangle, maxdist, label=u'maxᵣ C(r); r ≠ (δ₁,₀ mod N)')
    plt.xlim(left=-0.25, right=0.25)
    plt.legend(loc='upper left')
    plt.xlabel(u'C(r)')
    plt.ylabel(u'pdf')
    plt.tight_layout()
    plt.savefig(name + '/findingfailurelocation.pdf')
    # plt.show()


def findrotation(n, varc, m, qt):
    secret = np.random.randn(int(n)) * np.sqrt(varc)

    xi = random.randint(0, 2 * m)
    x = sampleFailure(secret, n, varc, qt)
    x = normalize(rotate(x, xi, m))

    yi = random.randint(0, 2 * m)
    y = sampleFailure(secret, n, varc, qt)
    y = normalize(rotate(y, yi, m))

    # try to retrieve highest cosine
    coslist = []
    for j in range(0, 2 * m):
        yr = rotate(y, j, m)
        coslist.append(np.dot(x, yr))

    tofind = int((xi - yi) % (2 * m))
    found = int(np.argmax(coslist))
    if(tofind == found):
        return 1.
    return 0.


def findrotation2ciphertexts(lwe_n, q, sd, B, m, name):
    n = 2 * lwe_n
    q = q
    B = B
    vars = sd**2
    varc = vars

    #####################
    #  precalculations  #
    #####################

    # qt
    qt = q / 2**(B + 1)
    # print('qt: ', qt)

    # |s| and |c*|
    norms = ZZ(ceil(sqrt(n * vars)))  # This is an approximation of the mean value
    normc = norms

    ##################
    #  calculations  #
    ##################

    import pathos
    pool = pathos.pools._ProcessPool(4, maxtasksperchild=1)
    results = pool.map(lambda x: findrotation(n, varc, m, qt), range(0, TESTS))
    pool.terminate()
    pool.join()

    numsucces = np.sum(results)

    print('experimental probability of combining 2 ciphertexts, succesprob %f' % (float(numsucces) / TESTS,))
    with open(name + '/findingfailurelocation.txt', 'a') as f:
        print('experimental probability of combining 2 ciphertexts, succesprob %f'
              % (float(numsucces) / TESTS,), file=f)


def findonemulticiphertextrotation(n, varc, CIPHERTEXTS, qt, norms):
    # create secret
    secret = np.random.randn(int(n)) * np.sqrt(varc)

    # create ciphertexts and correct answer
    correctAnswer = []
    ciphertexts = []
    xi = 0  # don't rotate first ciphertext
    for j in range(0, CIPHERTEXTS):
        x = sampleFailure(secret, n, varc, qt)
        x = normalize(rotate(x, xi, 256))
        correctAnswer.append(xi)
        ciphertexts.append(x)
        xi = random.randint(0, 512)  # rotate from second ciphertext on

    # probability from first ciphertext
    fixedciphertext = ciphertexts[0]
    f = probij(n, qt, norms, norms)
    pilist = [0] * CIPHERTEXTS
    for j in range(1, CIPHERTEXTS):
        prob = probijvector(ciphertexts[j], fixedciphertext, f, 256)
        pilist[j] = prob

    # add probability from other ciphertexts
    # numer of repetitions
    for rep in range(0, REP):
        # update all ciphertexts
        for j in range(1, CIPHERTEXTS):
            probj = pilist[j]
            # using all other ciphertexts
            for k in range(1, CIPHERTEXTS):
                if k == j:
                    continue
                # probability of kj in a certain rotation
                probkj = probijvector(ciphertexts[k], ciphertexts[j], f, 256)
                # probability of k
                probk = pilist[k]

                # calculate the message from this ciphertext
                prob = []
                for kk in range(0, 512):
                    tmp = np.dot(probk, np.roll(probkj, kk))
                    prob.append(tmp)
                prob = np.array(prob) / sum(prob)

                # apply the message to our previous belief
                probj *= prob

            # normalize the probabilities
            probj = probj / sum(probj)
            pilist[j] = probj

    # calculate guess as highest probability location
    guess = [0]
    for j in range(1, CIPHERTEXTS):
        guess.append(np.argmax(pilist[j]))

    # verify if test worked correctly
    if guess == correctAnswer:
        return 1.
    return 0.


def findrotationmulticiphertexts(lwe_n, q, sd, B, m, name):
    n = 2 * RR(lwe_n)
    q = RR(q)
    B = RR(B)
    vars = RR(sd**2)
    varc = vars

    #####################
    #  precalculations  #
    #####################

    # qt
    qt = q / 2**(B + 1)

    # |s| and |c*|
    norms = ZZ(ceil(sqrt(n * vars)))  # This is an approximation of the mean value
    normc = norms

    ##################
    #  calculations  #
    ##################
    numsucces = 0
    for CIPHERTEXTS in [3, 4, 5]:
        results = []

        import pathos
        pool = pathos.pools._ProcessPool(4, maxtasksperchild=1)
        results = pool.map(lambda x: findonemulticiphertextrotation(n, varc, CIPHERTEXTS, qt, norms), range(0, TESTS))
        pool.terminate()
        pool.join()

        numsucces = np.sum(results)

        print('experimental probability of combining %d ciphertexts in %d rounds, succesprob %f'
              % (CIPHERTEXTS, REP, numsucces / TESTS))
        with open(name + '/findingfailurelocation.txt', 'a') as f:
            print('experimental probability of combining %d ciphertexts in %d rounds, succesprob %f'
                  % (CIPHERTEXTS, REP, numsucces / TESTS), file=f)


def angleofcombination(lwe_n, q, sd, B, m, name):
    n = 2 * lwe_n
    B = B
    vars = sd**2
    varc = vars

    #####################
    #  precalculations  #
    #####################

    # qt
    qt = q / 2**(B + 1)

    # |s| and |c*|
    norms = ceil(sqrt(n * vars))  # This is an approximation of the mean value
    normc = norms

    tmp = 0
    for i in trange(0, 10):
            secret = np.random.randn(int(n)) * np.sqrt(varc)
            E = normalize(sampleFailure(secret, n, varc, qt))
            tmp += np.dot(E, normalize(secret))
    Kexperiment = np.arccos(tmp / 10)
    Ktheory = np.arccos(qt / norms / normc)

    with open(name + '/findingfailurelocation.txt', 'a') as f:
        print('theta_SE %f, theory: %f' % (Kexperiment, Ktheory), file=f)

    K = Ktheory

    # generate random failures and calculate their angle with the secret
    for numcipher in tqdm([0, 1, 2, 3, 5]):
        anglelist = []

        # calculate theta_SE approximately
        for rp in trange(0, TESTS):
            secret = np.random.randn(int(n)) * np.sqrt(varc)

            E = normalize(sampleFailure(secret, n, varc, qt))
            for i in range(1, numcipher):
                E += normalize(sampleFailure(secret, n, varc, qt))
            E = normalize(E)

            anglelist.append(np.dot(E, normalize(secret)))

        experimentalangle = np.mean(anglelist)
        theoreticalangle = cos(K) / np.sqrt(cos(K)**2 + sin(K)**2 / numcipher)

        with open(name + '/findingfailurelocation.txt', 'a') as f:
            print('ciphertexts %d, mean angle of combination with secret, theoretical: %f, experimental %f'
                  % (numcipher, theoreticalangle, experimentalangle), file=f)


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
    plotAngleDifference(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)
    findrotation2ciphertexts(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)
    findrotationmulticiphertexts(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)


import __main__
if hasattr(__main__, "__file__") and __name__ == "__main__":
    main()
