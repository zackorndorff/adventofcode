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

direction_map = {
        "U": ( 0, 1),
        "D": ( 0,-1),
        "L": (-1, 0),
        "R": ( 1, 0),
}

def coord_add(left, right):
    assert len(left) == 2
    assert len(right) == 2
    return tuple(i + j for i, j in zip(left, right))

def scalar_multiple(coord, scalar):
    return tuple(i * scalar for i in coord)

class Turtle:
    def __init__(self):
        self.vertices = []
        self.current = (0,0)
        self.last_direction = None
        self.perimeter = 0

    def go(self, direction, length):
        next_point = coord_add(self.current, scalar_multiple(direction, length))
        self.current = next_point
        self.vertices.append(self.current)
        self.perimeter += length

    def area(self):
        # Shoelace / surveyor's formula
        # https://en.wikipedia.org/wiki/Shoelace_formula
        # This is the "trapezoid formula"
        accum = 0
        for i in range(len(self.vertices)):
            nxt = i + 1
            if nxt == len(self.vertices):
                nxt = 0
            x, y = self.vertices[i]
            nx, ny = self.vertices[nxt]
            accum += (y + ny) * (x - nx)
        accum *= 0.5
        return accum



def main(realdata=False, part2=False, verbose=False, num=None):
    if realdata:
        data = open("18.txt", "r")
    else:
        data = """R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)""".splitlines()

    turtle = Turtle()
    for linenum, line in enumerate(data):
        line = line.strip()
        direction, count, color = line.split()
        color = color.split("#")[1].replace(")", "")
        print(direction, count, color)
        if not part2:
            turtle.go(direction_map[direction], int(count))
        else:
            # decode color
            print(color)
            assert len(color) == 6
            direction = int(color[-1:])
            distance = int(color[:-1], 16)
            dirmap2 = {
                    0: "R",
                    1: "D",
                    2: "L",
                    3: "U",
            }
            turtle.go(direction_map[dirmap2[direction]], distance)
    area = abs(turtle.area())
    # Correct for the fact that we're missing the area around the outside
    # Someone on reddit suggested this a few days ago
    result = area + (turtle.perimeter + 2)/2
    print(result)



if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    #num = next((i for i in lower_args if str(int(i)) == i), None)
    num = None
    main(real, part2, verbose, num)
