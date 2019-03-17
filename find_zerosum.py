import os, sys
from itertools import *
from collections import *
from random import *

from skinny import skinny128128

fname = sys.argv[1]
assert sys.argv[2][-1] in "fh"
halfround = sys.argv[2][-1] == "h"
checknr = int(sys.argv[2][:-1])

s = open(fname).read()
bs = 16 if "128_" in fname else 8

pt2ct = {}
ptct_pairs = []
for i in xrange(0, len(s), bs*2):
    pt = s[i:i+bs]
    ct = s[i+bs:i+bs+bs]
    pt2ct[pt] = ct
    ptct_pairs.append((pt, ct))

def xor(a, b):
    return "".join(chr(ord(aa) ^ ord(bb)) for aa, bb in zip(a, b))

def xorlist(a, b):
    return [aa ^ bb for aa, bb in zip(a, b)]

def orlist(a, b):
    return [aa | bb for aa, bb in zip(a, b)]

print "ROUNDS", checknr
seen = set()
groups = [tuple(ptct_pairs[i:i+4]) for i in xrange(0, len(ptct_pairs), 4)]
assert len(set(groups)) == len(groups)
ntotal = 0
groups_by_pos = defaultdict(list)
for igroup, group in enumerate(groups):
    mask = [0] * bs
    masks = {(i, j): [0] * bs for i, j in combinations(range(4), 2)}
    # masks[0,1,2,3] = [0] * bs
    for itr in xrange(50):
        k = [randint(0, 255) for _ in xrange(16)]
        xorsum = [0] * bs
        xorsums = {(i, j): [0] * bs for i, j in combinations(range(4), 2)}
        # xorsums[0,1,2,3] = [0] * bs
        for ipt, (pt, ct) in enumerate(group):
            pt = map(ord, pt)
            mid = skinny128128(pt, k, checknr, skip_last_MC=halfround)
            xorsum = xorlist(xorsum, mid)
            for inds in xorsums:
                if ipt in inds:
                    xorsums[inds] = xorlist(xorsums[inds], mid)
        mask = orlist(mask, xorsum)
        for inds in xorsums:
            masks[inds] = orlist(masks[inds], xorsums[inds])
        if min(mask):
            break
    else:
        print "group", igroup, ":", mask
        for pt, ct in group:
            print "   ", pt.encode("hex"), xor(group[0][0], pt).encode("hex").replace("00", "..")
        ntotal += 1
        for i, v in enumerate(mask):
            if v == 0:
                groups_by_pos[i].append(group)

        for inds, mask in sorted(masks.items()):
            if min(mask) == 0:
                print "   ", inds, mask
        print

print "total", ntotal, "zero sums"
print "by pos"
for i in xrange(bs):
    print i, ":", len(groups_by_pos[i])

for group in groups_by_pos[9]:
    pt0 = group[0][0]
    for pt, ct in group:
        print "{",
        print ", ".join("0x%02x" % c for c in map(ord, ct)),
        print "},", "// pt: %s diff: %s" % (`pt`, xor(pt, pt0).encode("hex").replace("00", ".."))
    print

