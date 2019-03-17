import os, sys
from itertools import *
from collections import *
from random import *

fname = sys.argv[1]
max_active = int(sys.argv[2])

s = open(fname).read()
bs = 16 if "skinny128" in fname else 8
nr = int(fname.split("_")[1])

pt2ct = {}
ptct_pairs = []
for i in xrange(0, len(s), bs*2):
    pt = s[i:i+bs]
    ct = s[i+bs:i+bs+bs]
    if pt in pt2ct:
        continue
    pt2ct[pt] = ct
    ptct_pairs.append((pt, ct))

def xor(a, b):
    return "".join(chr(ord(aa) ^ ord(bb)) for aa, bb in zip(a, b))

def orr(a, b):
    return "".join(chr(ord(aa) | ord(bb)) for aa, bb in zip(a, b))

def wt(d):
    return sum(1 for c in d if c != "\x00")

fname2 = "data/2nd_diffs_%s_%s_maxactive%d" % (8*bs, nr, max_active)
fout = open(fname2, "w")

seen = set()

ntotal = 0
for indexes in combinations(range(bs), bs-max_active):
    groups = defaultdict(list)
    for pi, (pt, ct) in enumerate(ptct_pairs):
        k = tuple(pt[i] for i in indexes)
        groups[k].append(pt)

    for k, g in groups.items():
        if len(g) <= 1:
            continue

        g = sorted(g)
        by_delta = defaultdict(set)
        for pa, pb in combinations(g, 2):
            delta = xor(pa, pb)
            by_delta[delta].add((pa, pb))

        for delta, pairs in by_delta.items():
            pairs = sorted(pairs)
            if len(pairs) <= 1:
                continue
            for pair1, pair2 in combinations(pairs, 2):
                delta1 = xor(pair1[0], pair1[1])
                delta2 = xor(pair1[0], pair2[0])
                delta3 = xor(pair1[0], pair2[1])
                print "xor", delta1.encode("hex").replace("00","..")
                print "xor", delta2.encode("hex").replace("00","..")
                print "xor", delta3.encode("hex").replace("00","..")
                print
                assert xor(xor(*pair1), xor(*pair2)) == "\x00" * bs
                assert len(set(pair1 + pair2)) == 4
                pts = tuple(sorted(pair1 + pair2))
                if pts not in seen:
                    seen.add(pts)
                    for pt in pair1 + pair2:
                        fout.write(pt)
                        fout.write(pt2ct[pt])
                    ntotal += 1

print ntotal, "second order differentials found with at most 2 active input bytes"
