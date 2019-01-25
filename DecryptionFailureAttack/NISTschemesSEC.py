# -*- coding: utf-8 -*-
"""
This is an adaptation to the schemes.py file in https://github.com/estimate-all-the-lwe-ntru-schemes/

NOTATION:

    LWE
    n       lwe secret dimension (d*n for module lwe)
    q       lwe modulo
    sd      lwe error standard deviation 
            (if secret is normal form, also the secret standard devation)
    m       number of lwe samples

    NTRU-like
    n       dimension of f,g,h
    q       modulus
    norm_f  expected norm of f  -- we can swap norm_f and norm_g such that norm_g <= norm_f for a potentially better attack
    norm_g  expected norm of g  -- we can swap norm_f and norm_g such that norm_g <= norm_f for a potentially better attack
    m       number of lwe samples

ORIGINAL AUTHORS:

    Ben Curtis - 2017, 2018
    Alex Davidson - 2017, 2018
    Amit Deo - 2018
    Rachel Player - 2017, 2018
    Eamonn Postlethwaite - 2018
    Fernando Virdia - 2017, 2018
    Thomas Wunderer - 2018

"""

from sage.all import sqrt, ln, floor, RR, ZZ

SCHEMES = {'Kyber768':
            {
            "name": "CRYSTALS‑Kyber",
            "params": [
                {
                    "n": 256*3,
                    "sd": sqrt(4/ZZ(2)),
                    "q": 7681,
                    "k": 3,
                    "secret_distribution": "normal",
                    "m": 256*4,
                    "claimed": 161,
                    "category": [
                        3,
                    ],
                    "ring": "x^{n/k}+1",
                },
            ],
            "assumption": [
                "MLWE",
            ],
            "primitive": [
                "KEM",
                "PKE",
            ],
        },'Kyber1024':
            {
            "name": "CRYSTALS‑Kyber",
            "params": [
                {
                    "n": 256*4,
                    "sd": sqrt(3/ZZ(2)),
                    "q": 7681,
                    "k": 4,
                    "secret_distribution": "normal",
                    "m": 256*5,
                    "claimed": 218,
                    "category": [
                        5,
                    ],
                    "ring": "x^{n/k}+1",
                },
            ],
            "assumption": [
                "MLWE",
            ],
            "primitive": [
                "KEM",
                "PKE",
            ],
        },'Saber': 
            {
            "name": "Saber",
            "params": [
                {
                    "n": 3*256,
                    "sd": sqrt(16/ZZ(3)),
                    "q": 2**13,
                    "k": 3,
                    "secret_distribution": "normal",
                    "m": 4*256,
                    "claimed": 180,
                    "category": [
                        3,
                    ],
                    "ring": "x^{n/k} + 1",
                },
            ],
            "assumption": [
                "MLWR",
            ],
            "primitive": [
                "PKE",
                "KEM"
            ],
        },
            'FireSaber': 
            {
            "name": "FireSaber",
            "params": [
                {
                    "n": 4*256,
                    "sd": sqrt(16/ZZ(3)),
                    "q": 2**13,
                    "k": 4,
                    "secret_distribution": "normal",
                    "m": 5*256,
                    "claimed": 245,
                    "category": [
                        5,
                    ],
                    "ring": "x^{n/k} + 1",
                },
            ],
            "assumption": [
                "MLWR",
            ],
            "primitive": [
                "PKE",
                "KEM"
            ],
        },
            'FrodoKEM-976':
            {
            "name": "Frodo",
            "params": [
                {
                    "n": 976,
                    "sd": 2.3,
                    "q":2**16,
                    "secret_distribution": "normal",
                    "claimed": 150,
                    "category": [
                        3,
                    ],
                },
            ],
            "assumption": [
                "LWE",
            ],
            "primitive": [
                "KEM",
                "PKE",
            ],
        },
            "LAC-256":
            {
            "name": "LAC",
            "params": [
                {
                    "n": 1024,
                    "sd": 1/sqrt(2),
                    "q": 251,
                    "secret_distribution": "normal",
                    "m": 2*1024,
                    "claimed": 256,
                    "category": [
                        5,
                    ],
                    "ring": "x^n+1",
                }
            ],
            "assumption": [
                "PLWE",
            ],
            "primitive": [
                "PKE",
                "KEM",
                "KE",
            ],
        },

    }
