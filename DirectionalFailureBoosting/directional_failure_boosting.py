# -*- coding: utf-8 -*-

from samplingfailures import getRandomNormAngle as getFailingNormAngle
from samplingfailures import sampleFailureFromThetaNorm
from samplingfailures import getAngleProbability, getNormProbability, POINTS
from sage.all import seed, vector, floor, sqrt, RR, cos, NaN, ceil, save, load
from sage.crypto.lwe import DiscreteGaussianDistributionIntegerSampler
import numpy as np


print "NOTE: P[S]/P[F] odds currently hardcoded"


class Roster:
    def __init__(self, rows, columns, bounds):
        """
        :params rows:       number of rows
        :params columns:    number of columns
        :params bounds:     dictionary {'row': (a, b), 'col': (c, d)} indicating entries in y axis live in [a, b] and
                              entries in x axis live in [c, d]
        """
        self.size = {'row': rows, 'col': columns}
        self.bounds = bounds
        self.step = {}

        # row is fractional numbers
        self.step['row'] = (self.bounds['row'][1] - self.bounds['row'][0]) / self.size['row']

        # column is integer step
        # make the steps coincide with integers
        step = (self.bounds['col'][1] - self.bounds['col'][0]) / self.size['col']
        self.step['col'] = ceil(step)
        # adjust the size to take into account the increased step
        size = (self.bounds['col'][1] - self.bounds['col'][0]) / self.step['col']
        self.size['col'] = ceil(size)
        # adjust the bounds
        lowerbound = floor(self.bounds['col'][0]) + 0.5
        self.bounds['col'] = (lowerbound, lowerbound + self.step['col'] * self.size['col'])

        self.grid = [[0 for c in range(self.size['col'])] for r in range(self.size['row'])]

    def index(self, axis, entry):
        if axis not in self.bounds:
            raise ValueError('Axis %s not defined.' % axis)
        ind = floor((entry - self.bounds[axis][0]) * self.size[axis] / (self.bounds[axis][1] - self.bounds[axis][0]))
        if ind == self.size[axis]:
            ind -= 1  # deal with unlikely upper bound
        return ind

    def add_entry(self, entry, value=1):
        """
        Add to roster the provided entry at the right index.
        Could overload [][], or [,].

        :params entry:  tuple (row, col) with raw row and column values (index assigned automatically).
        """
        row, col = entry
        self.grid[self.index('row', row)][self.index('col', col)] += value

    def get_entry(self, entry):
        row, col = entry
        return self.grid[self.index('row', row)][self.index('col', col)]

    def __repr__(self):
        s = ""
        for row in range(self.size['row']):
            for col in range(self.size['col']):
                s += "%s, " % self.grid[row][col]
            if row < self.size['row'] - 1:
                s += '\n'
        return s

    def getgridsize(self):
        return self.size['row'], self.size['col']

    def cleanupgrid(self):
        # restrict the grid to sensible values

        # find the rows/columns with only NaN
        rowsum = [0 for c in range(self.size['row'])]
        colsum = [0 for c in range(self.size['col'])]
        for r in range(self.size['row']):
            for c in range(self.size['col']):
                rowsum[r] += 1 - np.isnan(self.grid[r][c])
                colsum[c] += 1 - np.isnan(self.grid[r][c])

        # find first/last empty values
        def f(list, reverse=False):
            if reverse:
                list = list[::-1]
            for i, r in enumerate(list):
                if r > 0 and reverse is False:
                    return i - 1
                if r > 0 and reverse is True:
                    return len(list) - i + 1

        limits = (f(rowsum), f(rowsum, True), f(colsum), f(colsum, True))

        # change grid
        self.grid = self.grid[limits[0]:limits[1]]
        self.size['row'] = limits[1] - limits[0]

        for i in range(self.size['row']):
            self.grid[i] = self.grid[i][limits[2]:limits[3]]
        self.size['col'] = limits[3] - limits[2]

        # change bounds
        underbound = self.bounds['row'][0] + self.step['row'] * limits[0]
        self.bounds['row'] = (underbound, underbound + self.step['row'] * self.size['row'])
        underbound = self.bounds['col'][0] + self.step['col'] * limits[2]
        self.bounds['col'] = (underbound, underbound + self.step['col'] * self.size['col'])

    def heatmap(self, filename='', colormap='brg'):  # , factor=1):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()

        cs = ax.imshow(self.grid, cmap=colormap, interpolation='none', aspect='auto', extent=[
            self.bounds['col'][0], self.bounds['col'][1],
            self.bounds['row'][0], self.bounds['row'][1]
        ])

        fig.colorbar(cs)

        plt.rcParams.update({'font.size': 16})
        plt.title('experimental failure probability')
        plt.xlabel(u'$\\|\\|C\\|\\|_2$')
        plt.ylabel(u'$\\cos(\\theta_{CE})$')

        if filename == "":
            plt.show()
        else:
            plt.savefig(filename)


def getFailingNormDist(n, varc, norms, qt):
    maxvalue = int((n ** 0.5) * varc * 3)
    if (n ** 0.5) * varc * 3 > POINTS:
        normclist = range(0, maxvalue, maxvalue / POINTS)
    else:
        normclist = range(0, maxvalue)
    normclist, prob = getNormProbability(normclist, varc, n, norms, qt)
    return normclist, prob


def populate_grid(lwe, failures, successes, num_estimates, filename="", cache=""):
    # parse lwe parameters into our paper's setting (dimension doubles)
    n = 2 * RR(lwe['n'])
    varc = RR(lwe['sd']) ** 2
    q = RR(lwe['q'])

    # compute P[S]/P[F] odds
    odds = 2**119  # NOTE: hardcoded value!

    if cache != "":
        secret, cached_estimates, cached_failures, cached_successes = load(cache)
    else:
        # sample a concatenated secret and error vectors in normal form
        D = DiscreteGaussianDistributionIntegerSampler(lwe['sd'])
        secret = np.array([D() for _ in range(n)])
        norms = np.linalg.norm(secret)

        # distribution of norms of failures given s
        normclist, probnormc = getFailingNormDist(n, varc, norms, q)

    # sample estimates
    print "Sampling estimates"
    if cache != "":
        estimates = cached_estimates
    else:
        estimates = []
        for _ in range(num_estimates):
            normc = np.random.choice(normclist, p=probnormc)
            anglelist, prob = getAngleProbability(n, norms, normc, q)
            theta = np.random.choice(anglelist, p=prob)

            E = sampleFailureFromThetaNorm(secret, theta, normc)
            E = E / np.linalg.norm(E)
            estimates.append(E)

    # allocate rosters
    rows = cols = 100
    failure_roster = Roster(rows, cols, {'row': (-.4, .4), 'col': (0.8 * sqrt(n * varc), 1.2 * sqrt(n * varc))})
    success_roster = Roster(rows, cols, {'row': (-.4, .4), 'col': (0.8 * sqrt(n * varc), 1.2 * sqrt(n * varc))})
    failure_pmf_roster = Roster(rows, cols, {'row': (-.4, .4), 'col': (0.8 * sqrt(n * varc), 1.2 * sqrt(n * varc))})

    # size might be changed due to alignment with integers
    rows, cols = failure_roster.getgridsize()

    # generate failures
    print "Generating failures"

    failures_list = []
    for _ in xrange(failures):
        if cache != "":
            normc, theta_SC = cached_failures[_]
        else:
            normc = np.random.choice(normclist, p=probnormc)
            anglelist, prob = getAngleProbability(n, norms, normc, q)
            theta_SC = np.random.choice(anglelist, p=prob)
            failures_list.append((normc, theta_SC))
        x = sampleFailureFromThetaNorm(secret, theta_SC, normc)
        # failure can also be negative
        sign = np.random.choice([1, -1])
        x = x * sign
        for E in estimates:
            costheta_CE = np.dot(x, E) / normc
            failure_roster.add_entry((costheta_CE, normc))

    # # failure roster colormap
    # if filename != "":
    #     failure_roster.heatmap(filename="fails_" + filename)

    # generate successes
    print "Generating successes"

    successes_list = []
    for _ in xrange(successes):
        if cache != "":
            c, normc = cached_successes[_]
        else:
            c = np.array([D() for _ in range(n)])
            normc = np.linalg.norm(c)
            successes_list.append((c, normc))

        for E in estimates:
            costheta_CE = np.dot(c, E) / normc
            success_roster.add_entry((costheta_CE, normc))

    # # successes roster colormap
    # if filename != "":
    #     success_roster.heatmap(filename="success_" + filename)

    # combine grids using Bayes to get P[ decryption failure | ||C||_2 == normc and cos(angle_{C,S}) == theta ]
    for angle in range(rows):
        for norm in range(cols):
            F_in_roster = failure_roster.grid[angle][norm]
            S_in_roster = success_roster.grid[angle][norm]
            p_F_given_normc_angle = RR(F_in_roster) / (F_in_roster + S_in_roster * odds * failures / successes)
            failure_pmf_roster.grid[angle][norm] = np.log2(p_F_given_normc_angle)

    # print(failure_pmf_roster.grid)
    # failure_pmf_roster.heatmap(filename=("pmf_" if filename != "" else "") + filename)

    return (failure_roster, success_roster, failure_pmf_roster), (secret, estimates, failures_list, successes_list)


def genPlots(lwe, failures, successes, loc, folder, filename=""):
    # parse lwe parameters into our paper's setting (dimension doubles)
    n = 2 * RR(lwe['n'])
    varc = RR(lwe['sd']) ** 2
    q = RR(lwe['q'])

    # compute P[S]/P[F] odds
    odds = 2 ** 119  # NOTE: hardcoded value!

    (failure_roster, success_roster, pmf) = load(loc)

    # regen clean failure_pmf_roster to experiment with
    rows = cols = 100
    failure_pmf_roster = Roster(rows, cols, {'row': (-.4, .4), 'col': (0.8 * sqrt(n * varc), 1.2 * sqrt(n * varc))})
    rows, cols = failure_roster.getgridsize()

    # recalculate failure_pmf_roster
    for angle in range(rows):
        for norm in range(cols):
            F_in_roster = failure_roster.grid[angle][norm]
            S_in_roster = success_roster.grid[angle][norm]
            if F_in_roster > 3 and S_in_roster > 3:
                p_F_given_normc_angle = RR(F_in_roster) / (F_in_roster + S_in_roster * odds * failures / successes)
            else:
                p_F_given_normc_angle = float('nan')
            failure_pmf_roster.grid[angle][norm] = p_F_given_normc_angle

    # take into account failures at other location with cos(angle)<cos(theta)
    for norm in range(cols):
        F_in_roster = 0
        S_in_roster = 0
        for angle in sorted(range(rows), key=lambda x: abs(x - rows / 2)):
            F_in_roster += failure_roster.grid[angle][norm]
            S_in_roster += success_roster.grid[angle][norm]
            p_F_otherlocations = RR(F_in_roster) / (F_in_roster + S_in_roster * odds * failures / successes)
            p_F = failure_pmf_roster.grid[angle][norm] + 255 * p_F_otherlocations
            failure_pmf_roster.grid[angle][norm] = np.log2(p_F)

    # print
    failure_pmf_roster.cleanupgrid()
    failure_pmf_roster.heatmap(filename=(folder + "/pmf_" if filename != "" else "") + filename)
    if filename != "":
        success_roster.heatmap(filename=folder + "/success_" + filename)
        failure_roster.heatmap(filename=folder + "/fails_" + filename)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', type=int, default=1, help="PRNG seed")
    parser.add_argument('-n', type=int, default=768, help="(R)LWE dimension n")
    parser.add_argument('-q', type=int, default=8192 / 4, help="Error threshold  q/4")
    parser.add_argument('-sd', type=float, default=2., help="Standard deviation")
    parser.add_argument('-f', type=int, default=10000, help="Number of failures to generate")
    parser.add_argument('-s', type=int, default=10000, help="Number of successes to generate")
    parser.add_argument('-e', type=int, default=10000, help="Number of secret estimates")
    parser.add_argument('-fn', type=str, default="tmp",
                        help="Filename, if passed, the PMF colormaps and rosters are saved with names based on it")
    parser.add_argument('-load', type=str, default="", help="Load previously generated data and generate image")
    parser.add_argument('-cache', type=str, default="", help="Load previously generated lists and recreate rosters")
    parser.add_argument('-name', type=str, default="ourscheme",
                        help="Load previously generated lists and recreate rosters")
    args = parser.parse_args()

    if not args.load:
        np.random.seed(seed=args.k)
        with seed(args.k):
            rosters, cache = populate_grid({'n': args.n, 'q': args.q, 'sd': args.sd},
                                           args.f, args.s, args.e, filename=args.fn, cache=args.cache)
            if args.fn != "":
                save(rosters, args.name + '/rosters_' + args.fn)
                if args.cache == "":
                    save(cache, args.name + '/cache_' + args.fn)
            # import pdb; pdb.set_trace()
        args.load = args.name + '/rosters_' + args.fn
    genPlots({'n': args.n, 'q': args.q, 'sd': args.sd}, args.f,
             args.s, args.load, folder=args.name, filename=args.fn)
