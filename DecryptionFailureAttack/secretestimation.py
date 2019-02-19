from proba_util import *
from proba_util2 import *
import numpy as np
import itertools
from math import ceil
import pickle
import os.path

f= open("estimateLWE/__init__.py","w+")
f.close() 
from estimateLWE.estimates import para_cost_scheme, flatten

def security_failure(scheme, entropy, name):
    sd = scheme["params"][0]["sd"]
    primal = []
    dual = []
    for i in entropy:
        try:
            scheme["params"][0]["sd"] = sd * sqrt(i)
            lwe_estimates = para_cost_scheme([[scheme]])
            estimates_list = flatten([x[1] for x in lwe_estimates])
            primal.append(estimates_list[0]['cost']['Q\xe2\x80\x91Core\xe2\x80\x91Sieve']['n']['rop'])
            dual.append(estimates_list[1]['cost']['Q\xe2\x80\x91Core\xe2\x80\x91Sieve']['n']['rop'])
        except:
            break
    return primal, dual

def getestimator(thres, s, sprime, e, eprime, offset, n, **args):
    '''
    determine the estimator of s_i given e'_i
    Notation: s_i -> s, e'_i -> sp
    '''
    svalues = sorted(s.keys())
    evalues = sorted(eprime.keys())

    sgivensp = {i: 1. for i in itertools.product(svalues, evalues)}
    spgivens = {i: 1. for i in itertools.product(svalues, evalues)}

    norms = {}
    normsp = {}

    # make the error distribution without s_i, eprime_i
    seprime = law_product(s, eprime)
    esprime = law_product(sprime, e)

    tmp1 = iter_law_convolution(seprime, n - 1)
    tmp2 = iter_law_convolution(esprime, n)
    tmp = law_convolution(tmp1, tmp2)
    tmp = tail_probability(tmp)

    # calcualte the probabilities
    for (si, epi) in itertools.product(svalues, evalues):
        # P[si'] (this could be improved with extra information)
        spgivens[(si, epi)] *= eprime[epi]
        # P[si]
        sgivensp[(si, epi)] *= s[si]
        # P[fail | si]
        sgivensp[(si, epi)] *= tmp[thres + 1 - epi * si - offset]
        spgivens[(si, epi)] *= tmp[thres + 1 - epi * si - offset]
        # compute norm
        norms[si] = norms.get(si, 0) + spgivens[(si, epi)]
        normsp[epi] = normsp.get(epi, 0) + sgivensp[(si, epi)]

    # normalize
    for (si, epi) in itertools.product(svalues, evalues):
        spgivens[(si, epi)] /= norms[si]
        sgivensp[(si, epi)] /= normsp[epi]

    # determine information about si from epi
    estimator = {}
    for si in svalues:
        estimator[si] = {
            epi: eprime[epi] + (spgivens[si, epi] - eprime[epi]) for epi in evalues}

    # normalize estimator for better numeric accuracy
    norms = {}
    for (si, epi) in itertools.product(svalues, evalues):
        norms[epi] = norms.get(epi, 1) * (estimator[si]
                                          [epi]**(1. / len(evalues)))

    for (si, epi) in itertools.product(svalues, evalues):
        estimator[si][epi] /= norms[epi]

    return estimator, spgivens, sgivensp


def theoreticentropyInner(thres, s, sprime, e, eprime, eprimeprime, n, samples, failures, **args):
    # determine some useful values
    svalues = sorted(s.keys())
    evalues = sorted(eprime.keys())
    offset = int(ceil(max(eprimeprime.keys())))
    estimator, spgivens, sgivensp = getestimator(
        thres=thres, s=s, sprime=sprime, e=e, eprime=eprime, offset=offset, n=n)

    
    # propare our result list
    entropy = [0] * failures
    # get a baseline
    entropyzero = sum([si**2 * s[si] for si in svalues])

    # for every possible si: calculate how good the approximation is
    # sp: realization of spi given si
    # ap: non normalized estimation of p[si]
    # a: optimal guess for value of si
    for si in svalues:
        # get pdf of e given s and of e without knowledge of s
        prob = [spgivens[(si, epi)] for epi in evalues]
        # perform  samples number of tests
        for j in range(0, samples):
            # generate a random test
            ep = np.random.choice(evalues, size=(failures), p=prob)
            # refresh the estimate for si
            ap = {i: s[i] for i in svalues}
            # loop over all values in ep and estimate si
            for k in range(0, ep.shape[0]):
                # estimate a from ap
                a = sum([ap[i] * i for i in svalues]) / sum(ap.values())
                entropy[k] += (a - si)**2 / entropyzero * (s[si] / (samples))
                # update estimates
                tmp = ep[k]
                for i in svalues:
                    ap[i] *= estimator[i][tmp]

    return entropy


def theoreticentropy(thres, s, sprime, e, eprime, eprimeprime, n, samples, failures, **args):
    # calculate entropy reduction for e' -> s and for s' -> e, 
    tmp = theoreticentropyInner(
        thres, s, sprime, e, eprime, eprimeprime, n, samples, failures)
    tmp2 = theoreticentropyInner(
        thres, e, eprime, s, sprime, eprimeprime, n, samples, failures)
    # take the mean
    return [(i + j) / 2. for i, j in zip(tmp, tmp2)]


def main():
    # choose which schemes to plot
    from NISTschemes import Kyber768, Saber, LAC192, LAC256, Kyber512, Kyber1024, LightSaber, FireSaber, FrodoKEM976, LizardCat3, Kyber1024, FireSaber
    from NISTschemesSEC import SCHEMES

    toplot = [Saber, Kyber768, FrodoKEM976]

    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt


    for i in toplot:
        if os.path.exists(i['name'] + "-entropy.pkl"):
            continue
        ecc = 1
        if i.get('errorCorrection', 0):
            ecc = i['errorCorrection'][1]['te'] + 1
        entropy = theoreticentropy(
            samples=int(2**14), failures=2**10*ecc, **i)
        with open(i['name'] + "-entropy.pkl", "wb") as f:
            pickle.dump([entropy], f)

    for i in toplot:
        if os.path.exists(i['name'] + "-sec.pkl"):
            continue
        with open(i['name'] + "-entropy.pkl", "rb") as f:
            entropy, = pickle.load(f)
        scheme = SCHEMES[i['name']]
        primal, dual = security_failure(scheme, entropy, i['name'])
        with open(i['name'] + "-sec.pkl", "wb") as f:
            pickle.dump([primal, dual, entropy], f)

    # get colors
    fig, ax = plt.subplots()
    colors = ax._get_lines.prop_cycler

    for i in toplot:
        with open(i['name'] + "-sec.pkl", "rb") as f:
            primal, dual, entropy = pickle.load(f)
        color = colors.next()[u'color']
        plt.semilogx(primal[0:256], color=color, label=i['name'], basex=2)
        # plt.plot(dual, color=color, linestyle='.')

    plt.xlabel(r'positive failure vectors')
    plt.ylabel(r'security')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('secreduction.pdf')
    plt.show()

    # get colors
    fig, ax = plt.subplots()
    colors = ax._get_lines.prop_cycler

    for i in toplot:
        with open(i['name'] + "-sec.pkl", "rb") as f:
            primal, dual, entropy = pickle.load(f)
        color = colors.next()[u'color']

        with open(i['name'] + "-2.pkl", "rb") as f:
            alpha, beta = pickle.load(f)
        workforonefailure = np.log2([ sqrt(a) * b**-1 for a,b in zip(alpha, beta)])
        minwork = min(workforonefailure)

        ecc = 1
        if i.get('errorCorrection', 0):
            ecc = i['errorCorrection'][1]['te'] + 1

        security = primal
        security = np.array(security)
        samples = np.array(range(0,len(security)))
        idx = samples * ecc
        tmp = idx<security.shape[0]

        idx = idx[tmp]
        samples = samples[tmp]
        security = security[idx]


        security = np.logaddexp2(security, (np.log2(samples) + minwork))

        print i['name'], minwork, np.log2(alpha[np.argmin(workforonefailure)]**-1)
        print np.argmin(security), np.log2(np.argmin(security)*beta[np.argmin(workforonefailure)]**-1)
        print min(security), security[0]

        plt.semilogx(samples, security, color=color, label=i['name'], basex=2)
        # plt.semilogx(primal[0:256], color=color, label=i['name'])
        # plt.plot(dual, color=color, linestyle='.')

    plt.xlabel(r'positive failure vectors')
    plt.ylabel(r'attack cost')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('secreduction2.pdf')
    plt.show()

    # get colors
    fig, ax = plt.subplots()
    colors = ax._get_lines.prop_cycler

    for i in toplot:
        with open(i['name'] + "-sec.pkl", "rb") as f:
            primal, dual, entropy = pickle.load(f)
        color = colors.next()[u'color']
        plt.semilogx(entropy[0:256], color=color, label=i['name'], linestyle='--', basex=2)
        # plt.plot(dual, color=color, linestyle='.')

    plt.xlabel(r'positive failure vectors')
    plt.ylabel(r'relative variance')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('entropyreduction.pdf')
    plt.show()


if __name__ == '__main__':
    main()
