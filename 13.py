from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, List, Set, Tuple
import functools
import itertools
import inspect
import json
import math
import re
import sys

from tqdm import tqdm

def print_depth(*args, **kwargs):
    print("    " * (len(inspect.stack(0))-5), end="")
    return print(*args, **kwargs)

def transpose(lines):
    new = [([""] * len(lines)) for i in range(len(lines[0]))]
    for i, line in enumerate(lines):
        for j, ch in enumerate(line):
            new[j][i] = ch
    return new

def main(realdata=False, part2=False, verbose=False):
    if realdata:
        data = open("13.txt", "r")
    else:
        data = """#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#""".splitlines()

    notes = []
    readone = []
    for linenum, line in enumerate(data):
        line = line.strip()
        if line:
            readone.append(list(line))
        else:
            notes.append(readone)
            readone = []
    if len(readone):
        notes.append(readone)
        readone = []

    total = 0
    for i, note in enumerate(notes):
        result = process_note(note, part2, verbose)
        print(f"Result of note {i} is {result}")
        total += result

    print("total is", total)

def evaluate_candidate(first, second):
    for row in range(min(len(first), len(second))):
        print(first[row], second[row])
        if first[row] != second[row]:
            print("Failed at row", row)
            return False
    return True

def process_one(readone, part2, verbose):
    for i in range(len(readone)-1):
        if readone[i] == readone[i+1]:
            print("found potential candidate at line", i)
        else:
            continue

        first = list(reversed(readone[:i+1]))
        second = readone[i+1:]
        if evaluate_candidate(first, second):
            print("Success")
            return i+1
    return 0

def process_note(readone, part2, verbose):
    transposed = transpose(readone)

    horizontal = process_one(readone, part2, verbose)
    vertical = process_one(transposed, part2, verbose)
    return horizontal * 100 + vertical



if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    main(real, part2, verbose)
