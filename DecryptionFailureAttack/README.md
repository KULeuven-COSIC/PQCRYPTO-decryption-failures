This folder contains the analysis of the decryption failure attack described in https://eprint.iacr.org/2018/1089

# to import necessary submodules
git submodule init
git submodule update
cd estimateLWE
git submodule init
git submodule update
cd ..


# to estimate failure boosting
sage failureboost.py
# to run the 
sage secretestimation.py
