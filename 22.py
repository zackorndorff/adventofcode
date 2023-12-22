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

@dataclass(frozen=True, eq=True)
class Point3:
    x: int
    y: int
    z: int

    def __add__(self, other):
        return Point3(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z)

@dataclass
class Brick:
    end1: Point3
    end2: Point3

    def copy(self):
        return Brick(self.end1, self.end2)

    def translate(self, move):
        self.end1 += move
        self.end2 += move

    @property
    def lowest_z(self):
        return min(self.end1.z, self.end2.z)

    def contained_cubes(self):
        lowx = min(self.end1.x, self.end2.x)
        hix  = max(self.end1.x, self.end2.x)
        lowy = min(self.end1.y, self.end2.y)
        hiy  = max(self.end1.y, self.end2.y)
        lowz = min(self.end1.z, self.end2.z)
        hiz  = max(self.end1.z, self.end2.z)
        for x in range(lowx, hix+1):
            for y in range(lowy, hiy+1):
                for z in range(lowz, hiz+1):
                    yield Point3(x, y, z)

DOWN = Point3(0, 0, -1)
class World:
    def __init__(self, bricks):
        self.bricks = list(sorted(bricks, key=lambda b: b.lowest_z))
        #for brick in self.bricks:
        #    print(brick, end=" ")
        #    for cube in brick.contained_cubes():
        #        print(cube, end=" ")
        #    print()

    def occupied_set(self):
        occupied = set()
        for brick in self.bricks:
            for cube in brick.contained_cubes():
                occupied.add(cube)
        return occupied

    def fall_sim(self):
        moved = set()
        changed = True
        while changed:
            changed = False
            occupied_set = self.occupied_set()
            for brick in self.bricks:
                if self._brick_can_move(brick, occupied_set):
                    for cube in brick.contained_cubes():
                        occupied_set.remove(cube)
                    brick.translate(DOWN)
                    for cube in brick.contained_cubes():
                        occupied_set.add(cube)
                    changed = True
                    moved.add(id(brick))
        return len(moved)
            #         print(".", end="")
            # print("/")

    @staticmethod
    def _brick_can_move(brick, occupied_set):
        result = True
        for cube in brick.contained_cubes():
            occupied_set.remove(cube)
        lower = brick.copy()
        lower.translate(DOWN)
        if lower.lowest_z < 1:
            #print("hit bottom", brick)
            result = False
        result = result and set(lower.contained_cubes()).isdisjoint(occupied_set)
        for cube in brick.contained_cubes():
            occupied_set.add(cube)
        return result

    def check_disintegration(self):
        disintegrable = []
        occupied_set = self.occupied_set()
        for disbrick in self.bricks:
            yay = True
            for cube in disbrick.contained_cubes():
                occupied_set.remove(cube)
            for brick in self.bricks:
                if disbrick is brick:
                    continue
                if self._brick_can_move(brick, occupied_set):
                    yay = False
                    break
            if yay:
                disintegrable.append(disbrick)
            for cube in disbrick.contained_cubes():
                occupied_set.add(cube)
        return disintegrable


def chain_reaction(world):
    other_bricks = []
    for disbrick in tqdm(world.bricks):
        new_world = World(map(lambda b: b.copy(), filter(lambda brick: brick is not disbrick, world.bricks)))
        moved = new_world.fall_sim()
        #print(disbrick.name, moved)
        other_bricks.append(moved)
    return sum(other_bricks)


def main(realdata=False, part2=False, verbose=False, num=None):
    if realdata:
        data = open("22.txt", "r")
    else:
        data = """1,0,1~1,2,1
0,0,2~2,0,2
0,2,3~2,2,3
0,0,4~0,2,4
2,0,5~2,2,5
0,1,6~2,1,6
1,1,8~1,1,9""".splitlines()

    bricks = []
    for linenum, line in enumerate(data):
        line = line.strip()
        ends = (Point3(*(int(j) for j in i.split(','))) for i in line.split("~"))
        brick = Brick(*ends)
        if not realdata:
            brick.name = "ABCDEFGHIJKL"[linenum]
        bricks.append(brick)
    world = World(bricks)
    print("Simulating falls")
    world.fall_sim()
    if not part2:
        print("Checking disintegration")
        disintegrable = world.check_disintegration()
        print(len(disintegrable))
    else:
        print("Checking chain reaction")
        print(chain_reaction(world))


if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    num = None
    for i in lower_args:
        try:
            num = int(i)
        except Exception:
            pass
    main(real, part2, verbose, num)
