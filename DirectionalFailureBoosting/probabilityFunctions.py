# -*- coding: utf-8 -*-

from sage.all import *
import numpy as np
import tqdm
import itertools
from scipy.stats import norm

ACCURACY = 2**-300

#######################
#  error computation  #
#######################

delta = lambda n, q, sd: 1 - erf(round(q / 4) / (sqrt(2) * sd**2 * sqrt(2 * n)))
err = lambda n, q, sd, m: (1 - (1 - delta(n, q, sd))**m).n().log(2)

delta2 = lambda n, q, sd, B: norm.logsf(float(round(q / 2 / 2**B)), scale=float(sd**2 * sqrt(2 * n))) / np.log(2) + 1
err2 = lambda n, q, sd, B, m: delta2(n, q, sd, B) + np.log2(m)

#########################
# security estimation   #
#########################

try:
    load('https://bitbucket.org/malb/lwe-estimator/raw/HEAD/estimator.py')

    def est(n, q, sd):
        alpha = sqrt(2 * pi) * sd / RR(q)
        m = n
        secret_distribution = "normal"
        success_probability = 0.99
        reduction_cost_model = lambda beta, d, B: ZZ(2)**RR(0.265 * beta)
        print(primal_usvp(n, alpha, q, secret_distribution=secret_distribution,
                          m=m, success_probability=success_probability,
                          reduction_cost_model=reduction_cost_model))
        print(dual_scale(n, alpha, q, secret_distribution=secret_distribution,
                         m=m, success_probability=success_probability,
                         reduction_cost_model=reduction_cost_model))
        reduction_cost_model = lambda beta, d, B: ZZ(2)**RR(0.292 * beta)
        print(primal_usvp(n, alpha, q, secret_distribution=secret_distribution,
                          m=m, success_probability=success_probability,
                          reduction_cost_model=reduction_cost_model))
        print(dual_scale(n, alpha, q, secret_distribution=secret_distribution,
                         m=m, success_probability=success_probability,
                         reduction_cost_model=reduction_cost_model))
except IOError:
    print("WARNING: failed to retrieve lwe-estimator.")


###################
#  distributions  #
###################

# uniform angle distribution in N dimensions
var('angle, N')
assume(N > 2)
uniformAngle = sin(angle)**(N - 2)  # not normalized

# calculate probability of a certain norm of |c|
var('x', 'k')
chidist = x**(k - 1) * exp(-x**2 / 2) / 2**(k / 2 - 1) / gamma(k / 2) * unit_step(x)

#############################################
#  calculations of ciphertext distribution  #
#############################################


# calculate probability of |c|
def Pnormc(x, varc, n):
    return chidist(x=x / sqrt(varc), k=n)


# calculate probability of theta
def Ptheta(theta, n):
    return uniformAngle(N=n)(angle=theta)  # not normalized!


# calculate probability of max(theta)
def PthetaMax(n, m):
    if m == 1:
        return lambda theta: Ptheta(theta, n)

    points = 1000
    yrange = np.linspace(0, float(pi), points)

    f = []
    F = []
    Fm = []

    # generate f (probability function)
    # generate F (1 - cumulative function)
    sum = 0
    for theta in yrange:
        prob = Ptheta(theta, n)
        f.append(prob)
        F.append(sum)
        sum += prob

    # generate Fm (cumulative function)
    # sum = 0
    # for theta in reversed(yrange):
    #     prob = Ptheta(theta, n)
    #     Fm.append(sum)
    #     sum += prob

    f = [i / sum for i in f]
    F = [i / sum for i in F]
    # Fm = [i / sum for i in reversed(Fm)]

    fmax = []
    for i, theta in enumerate(yrange):
        fmax.append(m * f[i] * abs(F[i] - 1)**(m - 1))

    fmax = np.array([float(i) for i in fmax])

    return lambda angle: np.interp(float(angle), yrange, fmax)


#############################################################
#  calculations of failure probability without information  #
#############################################################
# calculate failure probability of ciphertext given C*
def calcFailgivennormctNoInfo(normc, norms, qt, n, m):
    thres1 = (qt / normc / norms)

    # deal with out of scope values
    if thres1 > 1:
        return 0

    # calcalate failure probability
    # failure if cos(angle)>thres1 or -cos(angle)<-thres1
    var('x')
    Pcosalpha = uniformAngle(angle=arccos(x), N=n)
    prob = 2 * numerical_integral(Pcosalpha, thres1, 1)[0]
    normalizer = numerical_integral(Pcosalpha, -1, 1)[0]

    prob = prob / normalizer
    # take into account m failure locations
    if prob > 2**-10:
        return 1 - (1 - prob)**m
    else:
        return prob * m


##########################################################
#  calculations of failure probability with information  #
##########################################################
# calculate failure probability of ciphertext given C*
def calcFailgivennormct(theta, normc, thetaSE, norms, qt, n):
    # filter out the zero case
    if (normc * norms * sin(theta) * sin(thetaSE)) == 0:
        if abs(normc * norms * cos(theta) * cos(thetaSE)) > qt:
            return 1
        else:
            return 0

    # calculate thresholds
    thres1 = (qt - normc * norms * cos(theta) * cos(thetaSE)) / (normc * norms * sin(theta) * sin(thetaSE))
    thres2 = (qt + normc * norms * cos(theta) * cos(thetaSE)) / (normc * norms * sin(theta) * sin(thetaSE))

    # deal with out of scope values
    if thres1 > 1:
        thres1 = 1
    if thres2 > 1:
        thres2 = 1
    if thres1 < -1 or thres2 < -1:
        return 1

    # get Pcosalpha
    var('x')
    Pcosalpha = uniformAngle(angle=arccos(x), N=n - 1)

    # calcalate failure probability
    normalizer = numerical_integral(Pcosalpha, -1, 1)[0]
    prob = numerical_integral(Pcosalpha, thres1, 1)[0] + numerical_integral(Pcosalpha, thres2, 1)[0]

    prob = prob / normalizer
    return prob


###########################################
#  Calculate the normal failure boosting  #
###########################################
def failureboosting(xrange, yrange, n, qt, varc, norms, m):
    # get the probability of ciphertexts over the grid
    Pcipher = []
    sumprob = 0

    for tmp in tqdm.tqdm(itertools.product(xrange, yrange), total=len(xrange) * len(yrange), desc='P[ciphertext]: '):
        normc, theta = tmp
        prob = Ptheta(theta, n) * Pnormc(normc, varc, n)
        Pcipher.append(prob)
        sumprob += prob

    # normalize the probability
    Pcipher = [i / sumprob for i in Pcipher]

    # make a list of ciphertext probability and failure probability
    thelist = []
    for i, tmp in tqdm.tqdm(enumerate(itertools.product(xrange, yrange)),
                            total=len(xrange) * len(yrange), desc='make list: '):
        normc, theta = tmp
        if Pcipher[i] > ACCURACY:
            fail = calcFailgivennormctNoInfo(normc, norms, qt, n, m)
            thelist.append((Pcipher[i], fail))

    # sort the list in descending failure probability
    thelist.sort(key=lambda x: x[1], reverse=True)

    # calculate alpha and beta
    alpha2, beta2 = [], []
    alphatmp, betatmp = 0, 0

    for i in thelist:
        alphatmp += i[0]
        alpha2.append(alphatmp)

        betatmp += i[0] * i[1]
        beta2.append(betatmp / alphatmp)

    # get into same form as plots from decryption failure paper
    beta = [float(b) for (b, a) in zip(beta2, alpha2)]
    alpha = [float(a**-1) for a in alpha2]

    return alpha, beta


############################################################
#  Calculate the normal failure boosting with information  #
############################################################
def failureboostingWithInfo(xrange, yrange, thetaSE, n, qt, varc, norms, m):
    # calculate failure probability if |cos(theta_j)| < |cos(theta_i)|
    failOther = {}
    for normc in tqdm.tqdm(xrange, desc='P[F | |cos(theta_j)| < |cos(theta_i)|]: '):
        sumthetaprob = 0
        sumfailprob = 0
        for theta in sorted(yrange, key=lambda x: abs(x - pi / 2)):
            ptheta = Ptheta(theta, n)
            sumthetaprob += ptheta
            sumfailprob += ptheta * calcFailgivennormct(theta, normc, thetaSE, norms, qt, n)
            if sumthetaprob > 0:
                failOther[(normc, theta)] = float(sumfailprob / sumthetaprob)
            else:
                failOther[(normc, theta)] = 0

    # failure boosting
    # get the probability of ciphertexts over the grid
    Pcipher = []
    sumprob = 0
    Pthetamax = PthetaMax(n, m)
    for i, tmp in tqdm.tqdm(enumerate(itertools.product(xrange, yrange)),
                            total=len(xrange) * len(yrange), desc='calc probability: '):
        normc, theta = tmp
        prob = Pthetamax(theta) * Pnormc(normc, varc, n)
        Pcipher.append(prob)
        sumprob += prob

    # normalize the probability
    Pcipher = [i / sumprob for i in Pcipher]

    # make a list of ciphertext probability and failure probability
    thelist = []
    var('pFAIL', 'pFAILother')
    failcalc = 1 - (1 - pFAIL) * (1 - pFAILother)**(m - 1)
    failcalc = failcalc.expand()

    for i, tmp in tqdm.tqdm(enumerate(itertools.product(xrange, yrange)), desc='make list: '):
        normc, theta = tmp
        if Pcipher[i] > ACCURACY:
            Pfailmaxcosine = calcFailgivennormct(theta, normc, thetaSE, norms, qt, n)
            Pfailothercosine = failOther[(normc, theta)]
            thelist.append((Pcipher[i], float(failcalc(pFAIL=Pfailmaxcosine, pFAILother=Pfailothercosine))))

    # sort the list in descending failure probability
    thelist.sort(key=lambda x: x[1], reverse=True)

    # calculate alpha and beta
    alpha, beta = [], []
    alphatmp, betatmp = 0, 0

    for i in thelist:
        alphatmp += i[0]
        alpha.append(alphatmp)

        betatmp += i[0] * i[1]
        beta.append(betatmp / alphatmp)

    # get into same form as plots from decryption failure paper
    beta = [float(b) for (b, a) in zip(beta, alpha)]
    alpha = [float(a**-1) for a in alpha]

    return alpha, beta
