# -*- coding: utf-8 -*-
from __future__ import print_function

import matplotlib
# matplotlib.use('pdf')

from probabilityFunctions import est, delta, delta2, err, err2
from findingfailurelocation import plotAngleDifference, findrotation2ciphertexts, findrotationmulticiphertexts, angleofcombination
from failureboosting import precalc, directionalFailureboosting
from plotdistribution import plot_profiles

import os
import sys


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=768)
    parser.add_argument("-q", type=int, default=8192)
    parser.add_argument("-sd", type=float, default=2)
    parser.add_argument("-B", type=int, default=1)
    parser.add_argument("-m", type=int, default=256)
    parser.add_argument("-name", type=str, default="ourscheme", help="plot output filename")
    args = parser.parse_args()

    if not os.path.exists(args.name):
        os.mkdir(args.name)

    print("WARNING: there is still a memory leak in precalc (to be fixed). You can either:\n \
 - use the enclosed precalculated files in ourparams/tmp/ (only if you are calculating the parameters of this scheme) \n \
 - kill the process if when RAM is flooded and restart. The calculation will resume as intermediate values are stored\n \
This will be fixed as soon as possible \n\n")

    # general information about scheme
    print('\ngeneral information\n')
    n, q, sd, B, m = args.n, args.q, args.sd, args.B, args.m
    print("n = %d, q = %d, sd = %.2f, B = %d, m=%d" % (n, q, sd, B, m))
    print("single bit error log: %f, low prob: %f" % (delta(n, q, sd), delta2(n, q, sd, B)))
    print("failure prob log: %f, low prob: %f" % (err(n, q, sd, m), err2(n, q, sd, B, m)))
    est(n, q, sd)

    # failure boosting success probability
    print('\ndirectional failure boosting precalculation\n')
    precalc(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)
    print('\ncalculate various flavours of directional failure boosting\n')
    directionalFailureboosting(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)
    directionalFailureboosting(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name, limitedqueries=True)
    directionalFailureboosting(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name, limitedqueries=True, multitarget=True)

    # plot distribution
    print('\nplot distributions\n')
    plot_profiles(lwe_n=n, q=q, sd=sd, B=B, name=args.name)

    # plot the angle distribution for 2 ciphertexts
    print('\nestimate direction of secret\n')
    plotAngleDifference(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)
    print('\nangle with secret after combination\n')
    angleofcombination(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)
    print('\ncombination success probability\n')
    findrotation2ciphertexts(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)
    findrotationmulticiphertexts(lwe_n=n, q=q, sd=sd, B=B, m=m, name=args.name)


import __main__
if hasattr(__main__, "__file__") and __name__ == "__main__":
    main()
