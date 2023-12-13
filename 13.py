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
        print(f"Result of note {i} is {result}\n")
        total += result

    print("total is", total)

def evaluate_candidate(readone, i, require_smudge=False):
    got_smudge = False
    first = list(reversed(readone[:i+1]))
    second = readone[i+1:]
    for row in range(min(len(first), len(second))):
        print("checking", first[row], second[row])
        if first[row] != second[row]:
            differences = [(a != b, i) for i, (a, b) in enumerate(zip(first[row], second[row]))]
            print("diffs", sum(d for d, _ in differences))
            if require_smudge and not got_smudge and sum(d for d, _ in differences) == 1:
                print("Allowing smudge on row", row)
                got_smudge = True
            else:
                print("Failed at row", row)
                return False
    if require_smudge and not got_smudge:
        print("Missing required smudge")
        return False
    print("evaluate success")
    return True

def process_one(readone, part2, verbose):
    for i in range(len(readone)-1):
        if not part2:
            if readone[i] == readone[i+1]:
                print("found potential candidate at line", i)
            else:
                continue

            if evaluate_candidate(readone, i):
                print("Success")
                return i+1
        else:
            if readone[i] == readone[i+1]:
                print("found potential candidate at line", i)

                if evaluate_candidate(readone, i, True):
                    print("Success")
                    return i+1
                continue

            print("Considering row", i, "for smudges", readone[i], readone[i+1])
            differences = [(a != b, i) for i, (a, b) in enumerate(zip(readone[i], readone[i+1]))]
            print("row diffs", sum(d for d, _ in differences))
            if sum(d for d, _ in differences) == 1:
                smudge = next(i for d, i in differences if d)
                print("possible smudge at index", smudge)
                # Two possibilities: either we need to flip it in the first half
                # or the second.
                # Wait that's dumb, we only have to try one
                temp1 = readone.copy()
                flip_map = {
                        "#": ".",
                        ".": "#",
                }
                flip_first  = [flip_map[ch] if i == smudge else ch for i, ch in enumerate(readone[i])]
                temp1[i] = flip_first

                result1 = evaluate_candidate(temp1, i, False)

                if result1:
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
