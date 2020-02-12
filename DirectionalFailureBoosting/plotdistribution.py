# -*- coding: utf-8 -*-

from __future__ import print_function
import os

import matplotlib.pyplot as plt
import numpy as np
import itertools
import tqdm

from probabilityFunctions import calcFailgivennormct, calcFailgivennormctNoInfo, Pnormc, Ptheta, err, delta, est

from sage.all import RR, ZZ, ceil, sqrt, arccos, cos, pi, log, exp,\
    var, sin, numerical_integral, gamma, unit_step, erf, round, load

ACCURACY = 2**-300
GRIDPOINTS = 100


def plot_profiles(lwe_n, q, sd, B, name):
    n = 2 * RR(lwe_n)
    q = RR(q)
    B = RR(B)
    vars = RR(sd**2)

    #####################
    #  precalculations  #
    #####################

    qt = q / 2**(B + 1)

    # |s| and |c*|
    norms = ZZ(ceil(sqrt(n * vars)))  # This is an approximation of the mean value
    normc2 = norms

    # thetaSE
    thetaSE = arccos(qt / norms / normc2)  # Considering the worst case scenario for an attacker

    #####################################
    #  calculate probability functions  #
    #####################################

    # make a discrete grid
    xrange = np.linspace(normc2 * 0.5, normc2 / 0.5, GRIDPOINTS)
    yrange = np.linspace(float(pi / 4), float(3 * pi / 4), GRIDPOINTS)
    plotNormC, plotTheta = np.meshgrid(xrange, yrange)

    # calculate failure probability of ciphertext given C* (log2)
    vcalcFailgivennormct = np.vectorize(lambda theta, normc: calcFailgivennormct(theta, normc, thetaSE, norms, qt, n))
    plotFailprob = np.log2(vcalcFailgivennormct(plotTheta, plotNormC))

    # calculate ciphertext probability (log2)
    calcNormC = np.vectorize(lambda x: float(log(Pnormc(x, vars, n), 2)))
    plotCiphertextprob = calcNormC(plotNormC)

    calcT = np.vectorize(lambda theta: float(log(Ptheta(theta, n), 2)))
    plotCiphertextprob += calcT(plotTheta)

    ######################
    #  plot the results  #
    ######################

    if not os.path.exists(name):
        os.mkdir(name)

    # Plot the distribution of failing ciphertexts
    plt.title('distribution of failing ciphertexts')
    plt.xlabel('NormC')
    plt.ylabel('theta (angle C - C*)')
    plt.pcolormesh(plotNormC, plotTheta, plotFailprob + plotCiphertextprob)
    plt.savefig(name + '/failingciphertextsdistribution.pdf')
    # plt.show()
    plt.clf()

    # Plot the distribution of successfull ciphertexts
    plt.title('distribution of ciphertexts')
    plt.xlabel('NormC')
    plt.ylabel('theta (angle C - C*)')
    plt.pcolormesh(plotNormC, plotTheta, plotCiphertextprob)
    plt.savefig(name + '/succesciphertextsdistribution.pdf')
    # plt.show()
    plt.clf()

    # Plot the failure probability of ciphertexts
    plt.title('failure probability of ciphertexts')
    plt.xlabel(u'||C||₂')
    plt.ylabel('theta (angle C - C*)')
    plt.pcolormesh(plotNormC, plotTheta, plotFailprob)
    plt.savefig(name + '/failprobability.pdf')
    # plt.show()
    plt.clf()

    # Plot the failure probability of ciphertexts using contours
    fig, ax = plt.subplots()
    # somewhat bigger text to fit paper size
    plt.rcParams.update({'font.size': 16})
    plt.title('failure probability of ciphertexts')
    plt.xlabel(u'||C||₂')
    plt.ylabel(u'θ_CE')
    # select some grid points
    levels = [-i * 20 for i in list(range(12, 6, -2)) + list(range(6, -1, -1))]
    CS = ax.contour(plotNormC, plotTheta, plotFailprob, levels=levels)
    ax.clabel(CS, inline=1, fontsize=10, fmt='2^%d')
    plt.savefig(name + '/failprobabilitycontour.pdf')
    # plt.show()
    plt.clf()
    plt.rcParams.update({'font.size': 10})

    # Plot the failure probability of ciphertexts using contours (cos(theta) on y axis)
    fig, ax = plt.subplots()
    plt.rcParams.update({'font.size': 16})
    plt.title('failure probability of ciphertexts')
    plt.xlabel(u'||C||₂')
    plt.ylabel(u'cos(θ_CE)')
    levels = [-i * 20 for i in list(range(12, 6, -2)) + list(range(6, -1, -1))]
    CS = ax.contour(plotNormC, np.cos(plotTheta), plotFailprob, levels=levels)
    ax.clabel(CS, inline=1, fontsize=10, fmt='2^%d')
    plt.savefig(name + '/failprobabilitycontourcos.pdf')
    # plt.show()
    plt.clf()

    # Plot the failure probability of ciphertexts using contours (cos(theta) on y axis)
    fig, ax = plt.subplots()
    plt.rcParams.update({'font.size': 16})
    plt.title('failure probability of ciphertexts')
    plt.ylim(bottom=-0.15, top=0.15)
    plt.xlim(left=75, right=87)
    plt.xlabel(u'||C||₂')
    plt.ylabel(u'cos(θ_CE)')
    levels = list(range(-135, -95, 10))
    CS = ax.contour(plotNormC, np.cos(plotTheta), plotFailprob, levels=levels)
    ax.clabel(CS, inline=1, fontsize=10, fmt='2^%d')
    plt.savefig(name + '/failprobabilitycontourcosmini.pdf')
    # plt.show()
    plt.clf()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=150)
    parser.add_argument("-q", type=int, default=100)
    parser.add_argument("-sd", type=float, default=0.65)
    parser.add_argument("-B", type=int, default=1)
    parser.add_argument("-name", type=str, default="search", help="plot output filename")
    args = parser.parse_args()

    n, q, sd, B = args.n, args.q, args.sd, args.B
    print("n = %d, q = %d, sd = %.2f, B = %d" % (n, q, sd, B))
    print("single bit error log: %f" % err(n, q, sd, 1))
    est(n, q, sd)
    plot_profiles(lwe_n=n, q=q, sd=sd, B=B, name=args.name)


import __main__
if hasattr(__main__, "__file__") and __name__ == "__main__":
    main()
