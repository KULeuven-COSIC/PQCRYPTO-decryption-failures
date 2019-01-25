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
LAC128['thres'] = 251 / 4.
LAC128['s'] = {-1: 1. / 4, 0: 1. / 2, 1: 1. / 4}
LAC128['e'] = LAC128['s']
LAC128['sprime'] = LAC128['s']
LAC128['eprime'] = LAC128['s']
LAC128['eprimeprime'] = LAC128['s']
LAC128['n'] = 512
LAC128['n2'] = 1
LAC128['errorCorrection'] = (LACprob, {'ne': 511, 'te': 29})
LAC128['name'] = 'LAC-128'