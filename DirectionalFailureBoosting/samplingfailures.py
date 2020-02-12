# -*- coding: utf-8 -*-

from sage.all import *
import numpy as np
import tqdm
from tqdm import trange
import itertools
import matplotlib.pyplot as plt
import random
from probabilityFunctions import Ptheta, PthetaMax

ACCURACY = 2**-300
POINTS = 2**12

##################################################
#  calculations of ciphertext norm distribution  #
##################################################

# calculate probability of |c|
var('x', 'k', 'angle')
alphadist = x**(k - 1) * exp(-x**2 / 2) / 2**(k / 2 - 1) / gamma(k / 2) * unit_step(x)


# probability of the norm of C
def Pnormc(x, varc, n):
    return alphadist(x=x / sqrt(varc), k=n)


# cumulative distribution of the angle
def PcumulTheta(n, normc, norms, qt):
    if norms * normc == 0:
        return 0
    if (qt / norms / normc) > 1:
        return 0
    # not normalized!
    return numerical_integral(sin(arccos(angle))**(n - 2), qt / norms / normc, RealNumber(1))[0]


def getNormProbability(normclist, varc, n, norms, qt):
    prob = []
    for normc in normclist:
        normc = RealNumber(normc)
        prob.append(Pnormc(normc, varc, n) * PcumulTheta(n, normc, norms, qt))
    prob = np.array(prob, dtype=np.float) / float(sum(prob))
    normclist = np.array(normclist, dtype=np.float)
    return normclist, prob


###################################################
#  calculations of ciphertext angle distribution  #
###################################################
def getAngleProbability(n, norms, normc, qt):
    """
    NOTE n is always even, so we can replace a generall probangle with a marginally faster one
    """
    anglelist = np.linspace(qt / normc / norms, 1, num=POINTS)
    # general probangle
    # def probangle(angle): return sin(arccos(angle))**(n-2)

    def probangle(angle):
        return (1 - angle**2)**(n / 2 - 1)
    prob = [probangle(i) for i in anglelist]
    prob = np.array(prob, dtype=np.float) / float(sum(prob))
    anglelist = np.array(anglelist, dtype=np.float)
    anglelist = np.arccos(anglelist)
    return anglelist, prob


########################
#  get norm and angle  #
########################


def getRandomNormAngle(n, varc, norms, qt):
    maxvalue = int((n**0.5) * varc * 3)
    if (n**0.5) * varc * 3 > POINTS:
        normclist = range(0, maxvalue, maxvalue / POINTS)
    else:
        normclist = range(0, maxvalue)
    normclist, prob = getNormProbability(normclist, varc, n, norms, qt)
    normc = np.random.choice(normclist, p=prob)

    anglelist, prob = getAngleProbability(n, norms, normc, qt)
    angle = np.random.choice(anglelist, p=prob)

    return normc, angle


###################
#  rotate vector  #
###################


def rotate(vector, pos, N):
    output = np.zeros(shape=vector.shape)
    n = vector.shape[0]
    pos = (-pos) % (2 * N)
    for i in range(0, int(n / N)):
        tmp = vector[N * i:N * (i + 1)]
        tmp = np.concatenate([tmp, -tmp, tmp])
        output[N * i:N * (i + 1)] = tmp[pos:pos + N]
    return output


def normalize(vector):
    return vector / np.linalg.norm(vector)


##################################
#  correct rotation probability  #
##################################
def probij(n, qt, norms, normc):
    points = 10000
    angle = np.linspace(0, float(pi), points)
    K = qt / norms / normc

    uniformdist = np.vectorize(Ptheta)(angle, n)
    uniformdist = np.nan_to_num(np.vectorize(float)(uniformdist))
    uniformdist = uniformdist / sum(uniformdist)

    posdist = np.vectorize(Ptheta)(arccos((cos(angle) - K**2) / sqrt(1 - K**2)), n - 1)
    posdist = np.nan_to_num(np.vectorize(float)(posdist))
    posdist = posdist / sum(posdist)

    f = lambda x: np.interp(x, np.cos(angle)[::-1], posdist[::-1]) / (np.interp(x, np.cos(angle)[::-1], uniformdist[::-1]) + 0.00001)

    return f


def probijvector(x, y, f, N):
    prob = []
    for k in range(0, 2 * N):
        tmp = rotate(y, k, 256)
        cosij = np.dot(tmp, x)
        prob.append(f(cosij))
    prob = np.array(prob) / sum(prob)
    return prob


#################################
#  sample a failing ciphertext  #
#################################

# sample a random vector
# - secret: starting vector
# - theta: angle with secret
# - normc: norm of returned vector
def sampleFailureFromThetaNorm(secret, theta, normc):
    y = np.random.randn(secret.shape[0])
    y = y / np.linalg.norm(y)
    secret = secret / np.linalg.norm(secret)

    phi = np.arccos(np.dot(y, secret))
    b = sin(theta) / sin(phi)
    a = cos(theta) - sin(theta) / tan(phi)

    x = float(a) * secret + float(b) * y
    x = x * normc

    return x


# sample a random failure around secret
# secret vector and created vector are still aligned
def sampleFailure(secret, n, varc, qt):
    norms = np.linalg.norm(secret)
    normc, theta = getRandomNormAngle(n, varc, norms, qt)
    x = sampleFailureFromThetaNorm(secret, theta, normc)

    return x
