# Cryptanalysis of 10-round SKINNY-128-128 (SKINNY 2018-2019 Competition)

This repository contains information about cryptanalysis of the tweakable block cipher SKINNY-128-128 reduced to 10 rounds. This target was suggested by [SKINNY 2018-2019 Cryptanalysis Competition](https://sites.google.com/site/skinnycipher/cryptanalysis-competition/2018-2019-competition). The competition provides an encryption of a known book containing 2<sup>20</sup> blocks. The goal is to recover the secret key.

The attack used to break the 10-round version is described in [writeup.pdf](writeup.pdf). In brief, it is a second-order truncated differential attack. Equivalently, it is an integral cryptanalysis. For particular quadruples of plaintexts differing only in the last two bytes, the 10-th byte of the state after 6 encryption rounds xor-sums to zero. This state byte can be computed from the ciphertext and 6 bytes of the master key. These bytes of the key can be found by an exhaustive search that verifies the zero-sum property for several such plaintext-ciphertext quadruples. It requires about 2<sup>48</sup> computations.

There are the following scripts in this repository:

1. `$ pypy find_2nd_diff.py data/skinny128_10_rounds.bin 2` finds all second-order differences in the plaintext pool, with at most 2 active bytes (runs in less than a minute).
2. `$ pypy find_zerosum.py data/2nd_diffs_128_10_maxactive2 6f` finds all zero-sum properties after 6 full rounds of SKINNY-128-128 by performing an empirical check with random keys. It uses the quadruples produced by the first script. It also outputs all ciphertext quadruples with zerosum at 10-th byte of the state, in a C-style format. It can be copy-pasted into the [brute.c](brute.c) file.
3. [brute.c](brute.c) performs an optimized exhaustive search with verification based on the zerosum property.
