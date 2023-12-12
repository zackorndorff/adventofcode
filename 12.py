from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, List, Set, Tuple
import functools
import itertools
import json
import math
import re
import sys

from tqdm import tqdm

def matches_summary(records, summary):
    in_run = False
    run_length = 0
    run_lengths = []
    for ch in records:
        if ch == "#" and in_run:
            run_length += 1
        elif ch == "#" and not in_run:
            run_length = 1
            in_run = True
        elif ch == "." and in_run:
            run_lengths.append(run_length)
            in_run = False
            run_length = 0
    if run_length:
        run_lengths.append(run_length)
    return tuple(run_lengths) == summary, run_lengths

def handle(line, part2):
    records, summary = line.split()
    if part2:
        records = "?".join([records]*5)
        summary = ",".join([summary]*5)
    records = list(records)
    summary = tuple([int(i) for i in summary.split(",")])
    print(''.join(records), summary)

    unknowns = [i for i, ch in enumerate(records) if ch == "?"]

    total = 0
    hits = set()
    for i in range(2**len(unknowns)):
        for uidx, unknown in enumerate(unknowns):
            records[unknown] = "#" if ((i & (1 << (uidx))) >> uidx) else "."
            if records[unknown] == "#":
                hits.add(unknown)
        if matches_summary(records, summary)[0]:
            total += 1
        #print('wut', i, summary,  ''.join(records), matches_summary(records, summary))
    for i in unknowns:
        assert i in hits, f"unknown {i} not hit out of {len(unknowns)}"
    return total




def main(realdata=False, part2=False):
    if realdata:
        data = open("12.txt", "r")
    else:
        data = """???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1""".splitlines()

    total = 0
    for linenum, line in enumerate(tqdm(list(data))):
        # if linenum == 0:
        #     continue
        line = line.strip()
        result = handle(line, part2)
        print("line", linenum, line, "had", result)
        total += result
        # break
    print("part1:", total)



if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    main(real, part2)
