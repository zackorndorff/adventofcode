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

@dataclass
class Field:
    data: Dict[Tuple[int, int], str]

    _width: int = field(init=False)
    _height: int = field(init=False)

    def __post_init__(self):
        max_x = 0
        max_y = 0
        for y, x in self.data.keys():
            max_x = max(max_x, x)
            max_y = max(max_y, y)
        self._width = max_x + 1
        self._height = max_y + 1

    def in_bounds(self, coord):
        y, x = coord
        if y < 0 or x < 0:
            return False
        if y >= self._height or x >= self._width:
            return False
        return True

    def print(self):
        for i in range(self._height):
            for j in range(self._width):
                print(self.data[(i, j)], end="")
            print()

def coord_add(left, right):
    return tuple(i + j for i, j in zip(left, right))

def simulate_roll(field, direction, verbose=False):
    def funrange(direction, length):
        if direction <= 0:
            return range(length)
        else:
            return range(length-1, -1, -1)
    invdirection = -direction[0], -direction[1]
    changed = True
    while changed:
        if verbose:
            print()
            field.print()
        changed = False
        for y in funrange(direction[0], field._height):
            for x in funrange(direction[1], field._width):
                northy = coord_add((y, x), direction)
                if not field.in_bounds(northy):
                    continue
                ch = field.data[(y, x)]
                northy_ch = field.data[northy]
                if ch == "O" and northy_ch == ".":
                    cur = (y, x)
                    while True:
                        if not field.in_bounds(cur) or field.data[cur] == "#":
                            field.data[coord_add(cur, direction)] = "."
                            break
                        changed = True
                        field.data[coord_add(cur, direction)] = field.data[cur]
                        cur = coord_add(cur, invdirection)


def compute_load(field):
    total = 0
    for y in range(field._height):
        for x in range(field._width):
            ch = field.data[(y, x)]
            if ch == "O":
                total += field._height - y
    return total

def check_history(history):
    best_slide = (0, 0, -1, "")
    for history_len in range(5, min(200, len(history))):
        crib = history[-history_len:]
        assert len(crib) == history_len, f"{len(crib)=}, {history_len=}"
        for count in range(1, len(history)):
            end = len(history) - (history_len)*count
            if end-history_len < 0:
                break
            potential_match = history[end-history_len:end]
            assert len(potential_match) == len(crib), f"{len(potential_match)=} {len(crib)=}"
            if all(i == j for i, j in zip(potential_match, crib)):
                slide = (count * history_len, count, history_len, crib)
                if slide > best_slide:
                    best_slide = slide
            else:
                break
    ratio, count, best_len, s = best_slide
    near = len(history) - count * best_len
    print(f"check_history: {ratio=} {best_len=}, {count=}, {near=} {s=}")
    return count, best_len, s




def main(realdata=False, part2=False, verbose=False):
    if realdata:
        data = open("14.txt", "r")
    else:
        data = """O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#....""".splitlines()

    field_data = {}
    for linenum, line in enumerate(data):
        line = line.strip()
        for chnum, ch in enumerate(line):
            field_data[(linenum, chnum)] = ch

    field = Field(field_data)
    north = (-1,  0)
    west  = ( 0, -1)
    south = ( 1,  0)
    east  = ( 0,  1)

    if not part2:
        simulate_roll(field, north)
        print("part1:", compute_load(field))
        return


    history = []
    final = 1000000000
    for cycles in range(1, 1001):
        for i in (north, west, south, east):
            simulate_roll(field, i)
            #print()
            #print(i)
            #field.print()
        load = compute_load(field)
        history.append(load)
        print(f"after {cycles} cycles, load is {load}")


        count, best_len, s = check_history(history)
        if count > 10:
            print("Solution primed")
        if not count:
            continue
        multiplier = (final-cycles) // (best_len)
        leftbound = cycles + (best_len) * multiplier
        rightbound = leftbound + best_len
        print(f"{leftbound=} {rightbound=} {multiplier=}")
        if leftbound <= final <= rightbound:
            idx = final - leftbound - 1
            if idx < 0:
                idx += len(s)
            print("part2 guess:", s[idx], "in", cycles, "iterations")
            if count > 1:
                break



if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    main(real, part2, verbose)
