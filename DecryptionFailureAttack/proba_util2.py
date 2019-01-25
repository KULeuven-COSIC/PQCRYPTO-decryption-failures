from math import factorial as fac
from math import *
from proba_util import *
import numpy as np


def simplifyDistribution(dist, amount):
    """ approximate distribution dist with amount entries in the dictionary
    :param dist: distribution (dictionnary)
    :param amount: number of entries(integer)
    """
    result = {}
    x = sorted(dist.keys())
    length = len(x)
    if amount >= length:
        return dist
    step = float(length) / amount
    for j in range(0, amount):
        tmp = x[int(round(j * step)): int(round((j + 1) * step))]
        prob = sum([dist[i] for i in tmp])
        mean = sum([dist[i] * float(i) for i in tmp]) / prob
        result[mean] = result.get(mean, 0) + prob

    return result


def simplifyDistribution2(dist):
    """ approximate distribution dist with only integer keys in the dictionary
    :param dist: distribution (dictionnary)
    """
    result = {}
    for i in dist.keys():
        result[round(i)] = result.get(round(i), 0) + dist[i]
    return result


def law_abs(A):
    """ take absolute value of all entries in distribution A
    :param A: distribution (dictionnary)
    """
    res = {}
    for i in A.keys():
        res[abs(i)] = res.get(abs(i), 0) + A[i]
    return res


def iter_law_convolution_simplify(A, i, simpl):
    """ compute the -ith forld convolution of a distribution (using double-and-add), and simplify in the process
    :param A: first input law (dictionnary)
    :param i: (integer)
    """
    D = {0: 1.0}
    i_bin = bin(i)[2:]  # binary representation of n
    for ch in i_bin:
        D = law_convolution(D, D)
        D = clean_dist(D)
        D = simplifyDistribution(D, simpl)
        if ch == '1':
            D = law_convolution(D, A)
            D = clean_dist(D)
            D = simplifyDistribution(D, simpl)
    D = simplifyDistribution(D, simpl)
    return D


def tail_probability(D):
    """ Compute survival function of D """
    ma = max(D.keys())
    s = {ma + 1: 0.0}
    # Summing in reverse for better numerical precision (assuming tails are decreasing)
    for i in reversed(range(0, ma + 1)):
        s[i] = D.get(i, 0) + s[i + 1]
    return s


## distribution analytics

def distmean(dist):
    # get mean of a distribution dist
    res = 0.
    for i in dist.keys():
        res += dist[i] * i
    return res


def distvariance(dist):
    # get variance of a distribution dist
    mean = distmean(dist)
    res = 0.
    for i in dist.keys():
        res += dist[i] * (i - mean)**2

    return res
