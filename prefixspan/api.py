#! /usr/bin/env python3

# Uncomment for static type checking
# from typing import *
# Matches = List[Tuple[int, int]]
# Pattern = List[int]
# Results = List[Tuple[int, Pattern]]

import sys
from collections import defaultdict
from heapq import heappop, heappush


class PrefixSpan(object):
    def __init__(self, db, minlen=None, maxlen=None):
        self._db = db

        self.minlen = minlen or 1
        self.maxlen = maxlen or sys.maxsize

    def _mine(self, func):
        self._results = []  # type: Results

        func([], [(i, 0) for i in range(len(self._db))])

        return self._results

    def _scan(self, matches):
        # type: (Matches) -> DefaultDict[int, Matches]
        alloccurs = defaultdict(list)  # type: DefaultDict[int, Matches]

        for (i, pos) in matches:
            seq = self._db[i]

            occurs = set()  # type: Set[int]
            for j in range(pos, len(seq)):
                k = seq[j]
                if k not in occurs:
                    occurs.add(k)
                    alloccurs[k].append((i, j + 1))

        return alloccurs

    def frequent(self, minsup, allow_gap=True):
        def frequent_rec_with_gap(patt, matches):
            # type: (Pattern, Matches) -> None
            if len(patt) >= self.minlen:
                self._results.append((len(matches), patt))

                if len(patt) == self.maxlen:
                    return

            for (c, newmatches) in self._scan(matches).items():
                if len(newmatches) >= minsup:
                    frequent_rec_with_gap(patt + [c], newmatches)

        def frequent_rec_without_gap(patt, matches):
            # type: (Pattern, Matches) -> None
            if len(patt) >= self.minlen:
                self._results.append((len(matches), patt))

                if len(patt) == self.maxlen:
                    return

            for (c, newmatches) in self._scan(matches).items():
                newpattern = patt + [c]
                support = sum([
                    newpattern == self._db[i][j - len(patt) - 1:j]
                    for i, j in newmatches
                ])
                if support >= minsup:
                    frequent_rec_without_gap(patt + [c], newmatches)

        if allow_gap:
            return self._mine(frequent_rec_with_gap)
        else:
            return self._mine(frequent_rec_without_gap)

    def topk(self, k):
        def topk_rec(patt, matches):
            # type: (Pattern, Matches) -> None
            if len(patt) >= self.minlen:
                heappush(self._results, (len(matches), patt))
                if len(self._results) > k:
                    heappop(self._results)

                if len(patt) == self.maxlen:
                    return

            for (c, newmatches) in sorted(
                    self._scan(matches).items(),
                    key=(lambda x: len(x[1])),
                    reverse=True):
                if len(self._results
                       ) == k and len(newmatches) <= self._results[0][0]:
                    break

                topk_rec(patt + [c], newmatches)

        return self._mine(topk_rec)
