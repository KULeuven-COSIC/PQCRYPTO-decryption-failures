#/*---------------------------------------------------------------------
#This file has been adapted from the implementation
#(available at, Public Domain https://github.com/pq-crystals/kyber)
#of "CRYSTALS - Kyber: a CCA-secure module-lattice-based KEM"
#by : Joppe Bos, Leo Ducas, Eike Kiltz, Tancrede Lepoint,
#Vadim Lyubashevsky, John M. Schanck, Peter Schwabe & Damien stehle
#----------------------------------------------------------------------*/ 

from math import pi, exp, log, sqrt, ceil, floor, erfc

log_infinity = 9999


def delta_BKZ(b):
    """Computes the root hermite factor delta of BKZ-b.

    Args:
      b (integer): blocksize

    Returns:
      delta (real)
    """
    return ((pi * b)**(1. / b) * b / (2 * pi * exp(1)))**(1. / (2. * b - 2.))


def svp_plausible(b):
    """Computes the best plausible quantum cost of SVP in dimension b.

    Args:
      b (integer): blocksize

    Returns:
      log_2 of the cost.
    """
    return log(sqrt(4. / 3), 2) * b + log(b, 2)


def svp_quantum(b):
    """Computes the best known quantum cost of SVP in dimension b.

    Args:
      b (integer): blocksize

    Returns:
      log_2 of the cost.
    """
    return log(sqrt(13. / 9), 2) * b + log(b, 2)


def svp_classical(b):
    """Computes the best known classical cost of SVP in dimension b.

    Args:
      b (integer): blocksize

    Returns:
      log_2 of the cost.
    """
    return log(sqrt(3. / 2), 2) * b + log(b, 2)


def nvec_sieve(b):
    """Computes the number of vectors output by the sieving step for SVP in dimension b.

    Args:
      b (integer): blocksize

    Returns:
      log_2 of the number of vectors (proxy for the cost).
    """
    return log(sqrt(4. / 3), 2) * b


def primal_cost_LWR(q, p, n, m, s_secret, b, cost_svp=svp_classical, verbose=False):
    """Computes the cost of a primal attack using m samples and blocksize b (infinity if the attack fails).

    The attack assumes 'small secret' (i.e., the distribution of the secret is the same as errors).
    Args:
      q: LWE modulus
      n: LWE dimension
      m: number of samples
      s_secret: standard deviation of the error distribution
      b: blocksize
      cost_svp: cost function for the SVP oracle
      verbose: spill details on stdout

    Returns:
      log_2 of the number of vectors
    """
    d = n + m
    delta = delta_BKZ(b)
    s_noise = 1.*q/(sqrt(12)*p)
    omega = s_noise / s_secret
    if s_noise<s_secret:
      return 0
    
    if verbose:
        print "Primal attacks uses block-size", b, "and ", m, "samples"

    if s_secret * sqrt(b) < delta**(2. * b - d - 1) * (q/omega)**(1. * m / d):
        return cost_svp(b) # + log(n-b)/log(2)

    else:
        return log_infinity


def dual_cost_LWR(q, p, n, m, s_secret, b, cost_svp=svp_classical, verbose=False):
    """Computes the cost a dual attack using m samples and blocksize b (infinity of the attacks fails).

    The attack assume 'small secret' (i.e., the distribution of the secret is the same as errors).
    Args:
      q: LWE modulus
      n: LWE dimension
      m: number of samples
      s: standard deviation of the error distribution
      b: blocksize
      cost_svp: cost function for the SVP oracle
      verbose: spill details on stdout

    Returns:
      log_2 of the cost.
    """

    d = n + m
    delta = delta_BKZ(b)
    s_noise = 1.*q/(sqrt(12)*p)

    if s_noise<s_secret:
      return 0

    omega = s_noise / s_secret

    norm_v = delta**(m+n) * (q/omega)**(1.*n/(m+n))

    tau = norm_v*s_noise/q

    log2_eps = -0.5 + (- 2 * pi * pi * tau * tau) / log(2)

    cost = max(0, - 2 * log2_eps - nvec_sieve(b)) + \
        cost_svp(b)  # + log(d-b)/log(2)
    if verbose:
        print "Dual attacks uses block-size", b, "and ", m, "samples"
        print "log2(epsilon) = ", log2_eps, "log2 nvector per run", nvec_sieve(b)
    return cost

def optimize_attack_LWR(
        q,
        p,
        n,
        max_m,
        s,
        cost_attack=primal_cost_LWR,
        cost_svp=svp_classical,
        verbose=False):
    """ Finds optimal attack parameters against an LWE instance.

      q: LWE modulus
      n: LWE dimension
      max_m: maximum number of samples
      s: standard deviation of the error distribution
      cost_attack: primal vs dual attack
      cost_svp: cost function for the SVP oracle
      verbose: spill details on stdout

    Returns:
      Best parameters (m and b) and log_2 of their cost.
    """
    best_cost = log_infinity
    best_b = 0
    best_m = 0
    for b in range(50, n + max_m + 1):
        # Try all block-size, until just one call to SVP cost more than the
        # best attack found so far
        if cost_svp(b) > best_cost:
            break
        # Try all possible number of number of sample
        for m in range(max(1, b - n), max_m):
            cost = cost_attack(q, p, n, m, s, b, cost_svp)
            if cost < best_cost:
                best_cost = cost
                best_m = m
                best_b = b
    if verbose:
        # Re-call the cost_attack on the best params spilling extra info
        cost_attack(q, p, n, best_m, s, best_b,
                    cost_svp=svp_classical, verbose=True)
    return (best_m, best_b, best_cost)
