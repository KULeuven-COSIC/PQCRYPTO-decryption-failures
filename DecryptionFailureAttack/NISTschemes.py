from proba_util import *
from proba_util2 import *
from math import sqrt

# FRODOKEM
FrodoKEM640 = {}
FrodoKEM640['thres'] = (2**15) / 2**3
FrodoKEM640['s'] = {-11: 4.57763671875e-05, -10: 0.0001983642578125, -9: 0.0007171630859375, -8: 0.002197265625, -7: 0.005859375, -6: 0.013702392578125, -5: 0.02813720703125, -4: 0.0506744384765625, -3: 0.0800933837890625, -2: 0.111083984375, -1: 0.1351470947265625,
                    0: 0.144287109375, 1: 0.1351470947265625, 2: 0.111083984375, 3: 0.0800933837890625, 4: 0.0506744384765625, 5: 0.02813720703125, 6: 0.013702392578125, 7: 0.005859375, 8: 0.002197265625, 9: 0.0007171630859375, 10: 0.0001983642578125, 11: 4.57763671875e-05}
FrodoKEM640['e'] = FrodoKEM640['s']
FrodoKEM640['sprime'] = FrodoKEM640['s']
FrodoKEM640['eprime'] = FrodoKEM640['s']
FrodoKEM640['eprimeprime'] = FrodoKEM640['s']
FrodoKEM640['n'] = 640
FrodoKEM640['n2'] = 8
FrodoKEM640['n3'] = 8
FrodoKEM640['name'] = 'FrodoKEM-640'

FrodoKEM976 = {}
FrodoKEM976['thres'] = (2**16) / 2**4
FrodoKEM976['s'] = {-10: 1.52587890625e-05, -9: 9.1552734375e-05, -8: 0.0004425048828125, -7: 0.001800537109375, -6: 0.00604248046875, -5: 0.0167999267578125, -4: 0.0388336181640625, -3: 0.074493408203125, -2: 0.118621826171875, -1: 0.1568145751953125,
                    0: 0.172088623046875, 1: 0.1568145751953125, 2: 0.118621826171875, 3: 0.074493408203125, 4: 0.0388336181640625, 5: 0.0167999267578125, 6: 0.00604248046875, 7: 0.001800537109375, 8: 0.0004425048828125, 9: 9.1552734375e-05, 10: 1.52587890625e-05}
FrodoKEM976['e'] = FrodoKEM976['s']
FrodoKEM976['sprime'] = FrodoKEM976['s']
FrodoKEM976['eprime'] = FrodoKEM976['s']
FrodoKEM976['eprimeprime'] = FrodoKEM976['s']
FrodoKEM976['n'] = 976
FrodoKEM976['n2'] = 8
FrodoKEM640['n3'] = 8
FrodoKEM976['name'] = 'FrodoKEM-976'


# Kyber
Kyber512 = {}
Kyber512['thres'] = 7681 / 2**2
Kyber512['s'] = build_centered_binomial_law(5)
u = build_mod_switching_error_law(7681, 2**11)
Kyber512['e'] = law_convolution(Kyber512['s'], u)
Kyber512['sprime'] = Kyber512['s']
Kyber512['eprime'] = law_convolution(Kyber512['s'], u)
u2 = build_mod_switching_error_law(7681, 2**3)
Kyber512['eprimeprime'] = law_convolution(Kyber512['s'], u2)
Kyber512['n'] = 256 * 2
Kyber512['n2'] = 256
Kyber512['name'] = 'Kyber512'

Kyber768 = {}
Kyber768['thres'] = 7681 / 2**2
Kyber768['s'] = build_centered_binomial_law(4)
u = build_mod_switching_error_law(7681, 2**11)
Kyber768['e'] = law_convolution(Kyber768['s'], u)
Kyber768['sprime'] = Kyber768['s']
Kyber768['eprime'] = law_convolution(Kyber768['s'], u)
u2 = build_mod_switching_error_law(7681, 2**3)
Kyber768['eprimeprime'] = law_convolution(Kyber768['s'], u2)
Kyber768['n'] = 256 * 3
Kyber768['n2'] = 256
Kyber768['name'] = 'Kyber768'

Kyber1024 = {}
Kyber1024['thres'] = 7681 / 2**2
Kyber1024['s'] = build_centered_binomial_law(3)
u = build_mod_switching_error_law(7681, 2**11)
Kyber1024['e'] = law_convolution(Kyber1024['s'], u)
Kyber1024['sprime'] = Kyber1024['s']
Kyber1024['eprime'] = law_convolution(Kyber1024['s'], u)
u2 = build_mod_switching_error_law(7681, 2**3)
Kyber1024['eprimeprime'] = law_convolution(Kyber1024['s'], u2)
Kyber1024['n'] = 256 * 4
Kyber1024['n2'] = 256
Kyber1024['name'] = 'Kyber1024'

# SABER
LightSaber = {}
LightSaber['thres'] = 2**13 / 2**2
LightSaber['s'] = build_centered_binomial_law(5)
LightSaber['e'] = build_mod_switching_error_law(2**13, 2**10)
LightSaber['sprime'] = LightSaber['s']
LightSaber['eprime'] = LightSaber['e']
LightSaber['eprimeprime'] = build_mod_switching_error_law(2**13, 2**3)
LightSaber['n'] = 256 * 2
LightSaber['n2'] = 256
LightSaber['name'] = 'LightSaber'

Saber = {}
Saber['thres'] = 2**13 / 2**2
Saber['s'] = build_centered_binomial_law(4)
Saber['e'] = build_mod_switching_error_law(2**13, 2**10)
Saber['sprime'] = Saber['s']
Saber['eprime'] = Saber['e']
Saber['eprimeprime'] = build_mod_switching_error_law(2**13, 2**4)
Saber['n'] = 256 * 3
Saber['n2'] = 256
Saber['name'] = 'Saber'

FireSaber = {}
FireSaber['thres'] = 2**13 / 2**2
FireSaber['s'] = build_centered_binomial_law(3)
FireSaber['e'] = build_mod_switching_error_law(2**13, 2**10)
FireSaber['sprime'] = FireSaber['s']
FireSaber['eprime'] = FireSaber['e']
FireSaber['eprimeprime'] = build_mod_switching_error_law(2**13, 2**6)
FireSaber['n'] = 256 * 4
FireSaber['n2'] = 256
FireSaber['name'] = 'FireSaber'

# LAC
def LACprob(prob, ne, te):
    from math import factorial
    lacprob = []
    for delta in prob:
        res = 0
        for i in range(te + 1, ne + 1):
            res += factorial(ne) / factorial(i) / factorial(ne -
                                                            i) * (1 - delta)**(ne - i) * delta ** i
        lacprob.append(res)
    return lacprob


LAC256 = {}
LAC256['thres'] = 251 / 4
LAC256['s'] = {-1: 1. / 4, 0: 1. / 2, 1: 1. / 4}
LAC256['e'] = LAC256['s']
LAC256['sprime'] = LAC256['s']
LAC256['eprime'] = LAC256['s']
LAC256['eprimeprime'] = LAC256['s']
LAC256['n'] = 1024
LAC256['n2'] = 1
LAC256['errorCorrection'] = (LACprob, {'ne': 1023, 'te': 55})
LAC256['name'] = 'LAC-256'

LAC192 = {}
LAC192['thres'] = 251 / 4
LAC192['s'] = {-1: 1. / 8, 0: 3. / 4, 1: 1. / 8}
LAC192['e'] = LAC192['s']
LAC192['sprime'] = LAC192['s']
LAC192['eprime'] = LAC192['s']
LAC192['eprimeprime'] = LAC192['s']
LAC192['n'] = 1024
LAC192['n2'] = 1
LAC192['errorCorrection'] = (LACprob, {'ne': 511, 'te': 13})
LAC192['name'] = 'LAC-192'

LAC128 = {}
LAC128['thres'] = 251 / 4
LAC128['s'] = {-1: 1. / 4, 0: 1. / 2, 1: 1. / 4}
LAC128['e'] = LAC128['s']
LAC128['sprime'] = LAC128['s']
LAC128['eprime'] = LAC128['s']
LAC128['eprimeprime'] = LAC128['s']
LAC128['n'] = 512
LAC128['n2'] = 1
LAC128['errorCorrection'] = (LACprob, {'ne': 511, 'te': 29})
LAC128['name'] = 'LAC-128'

# ## Lizard --> Fixed hamming weight
LizardCat3 = {}
LizardCat3['n'] = 1024
LizardCat3['n2'] = 1024
LizardCat3['thres'] = 2048 / 4
LizardCat3['s'] = {1: 256. / (2 * 1024), -1: 256. /
                   (2 * 1024), 0: 1 - 256. / 1024}
LizardCat3['e'] = law_product({1: 0.5, -1: 0.5}, {0: 117. / 561, 1: 224. /
                                                  561, 2: 151. / 561, 3: 55. / 561, 4: 13. / 561, 5: 1. / 561})
LizardCat3['sprime'] = {sqrt(264. / 1024): 1}
LizardCat3['eprime'] = build_mod_switching_error_law(2048, 512)
LizardCat3['eprimeprime'] = build_mod_switching_error_law(2048, 512)
# LizardCat3['eprimeprime']={0: 1.}
LizardCat3['name'] = 'LizardCat3'
