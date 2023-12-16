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

@dataclass(eq=True, frozen=True)
class BeamState:
    position: Tuple[int, int]
    direction: Tuple[int, int]

    def next(self):
        return coord_add(self.position, self.direction)

def coord_add(left, right):
    return tuple(i + j for i, j in zip(left, right))

class Emulator:
    def __init__(self, room_data, state=None):
        self.data = room_data
        self.states = set()
        if state is None:
            self.states.add(BeamState((0,-1), (0,1)))
        else:
            self.states.add(state)
        self._height = max(y for y, x in self.data.keys()) + 1
        self._width = max(x for y, x in self.data.keys()) + 1
        self.visited = set()

    def in_bounds(self, coord):
        y, x = coord
        if y < 0 or x < 0:
            return False
        if y >= self._height or x >= self._width:
            return False
        return True

    def stepn(self):
        for i in range(n):
            if self.step() == 0:
                return i
        return None

    def step(self):
        new_states = []
        for state in self.states:
            new_states.extend(self.state_step(state))
        self.states = set(new_states)
        for state in self.states:
            self.visited.add(state.position)
        return len(self.states)

    def state_step(self, state) -> List[BeamState]:
        new_states = []
        pos = state.next()
        if self.in_bounds(pos):
            ch = self.data[pos]
            match ch:
                case ".":
                    new_states.append(BeamState(pos, state.direction))
                case "/":
                    reflect_map = {
                            ( 0, 1): (-1, 0),
                            (0, -1): ( 1, 0),
                            (-1, 0): ( 0, 1),
                            ( 1, 0): ( 0, -1),
                    }
                    new_states.append(BeamState(pos,
                                                reflect_map[state.direction]))
                case "\\":
                    reflect_map = {
                            ( 0, 1): ( 1, 0),
                            (0, -1): (-1, 0),
                            (-1, 0): ( 0,-1),
                            ( 1, 0): ( 0, 1),
                    }
                    new_states.append(BeamState(pos,
                                                reflect_map[state.direction]))

                case "|" | "-":
                    if ch == "-" and state.direction[1] != 0:
                        new_states.append(BeamState(pos, state.direction))
                    elif ch == "|" and state.direction[0] != 0:
                        new_states.append(BeamState(pos, state.direction))
                    elif ch in "-|":
                        if ch == "-":
                            directions = [ (0, -1), (0, 1)]
                        elif ch == "|":
                            directions = [ (-1, 0), (1, 0)]
                        else:
                            raise Exception("impossible")
                        for direction in directions:
                            new_states.append(BeamState(pos, direction))
                    else:
                        raise Exception("Shouldn't get here")
                case _:
                    raise Exception(f"idk {ch}")
        return new_states

def try_one(emu):
    i = 0
    last_update = 0
    last = 0
    while emu.step() != 0:
        i += 1
        delta = i - last_update
        if delta > 100:
            break
        if len(emu.visited) != last:
            last = len(emu.visited)
            last_update = i
        if verbose:
            print("States", len(emu.states))
            print("visited", len(emu.visited))
            for y in range(emu._height):
                for x in range(emu._width):
                    ch = "#" if (y, x) in emu.visited else emu.data[(y,x)]
                    print(ch, end="")
                print()
    print(f"Stopped after step {i} with {len(emu.visited)} activated and {len(emu.states)} states")
    return len(emu.visited)


def main(realdata=False, part2=False, verbose=False, num=None):
    if realdata:
        data = open("16.txt", "r")
    else:
        data = r""".|...\....
|.-.\.....
.....|-...
........|.
..........
.........\
..../.\\..
.-.-/..|..
.|....-|.\
..//.|....""".splitlines()

    room_data = {}
    for linenum, line in enumerate(data):
        line = line.strip()
        for chnum, ch in enumerate(line):
            room_data[(linenum, chnum)] = ch

    if not part2:
        emu = Emulator(room_data)
        i = 0
        last_update = 0
        last = 0
        while emu.step() != 0:
            i += 1
            delta = i - last_update
            if delta > 100:
                break
            if len(emu.visited) != last:
                last = len(emu.visited)
                last_update = i
            if verbose:
                print("States", len(emu.states))
                print("visited", len(emu.visited))
                for y in range(emu._height):
                    for x in range(emu._width):
                        ch = "#" if (y, x) in emu.visited else emu.data[(y,x)]
                        print(ch, end="")
                    print()
        print(f"Stopped after step {i} with {len(emu.visited)} activated and {len(emu.states)} states")
    else:
        emu = Emulator(room_data)
        things_to_try = []
        for i in range(emu._width):
            things_to_try.append(BeamState((-1, i), (1, 0)))
            things_to_try.append(BeamState((emu._height, i), (-1, 0)))
        for i in range(emu._height):
            things_to_try.append(BeamState((i, -1), (0, 1)))
            things_to_try.append(BeamState((i, emu._width), (0, -1)))
        maxx = 0
        max_start = None
        for state in tqdm(things_to_try):
            print("Trying", state)
            emu = Emulator(room_data, state)
            active = try_one(emu)
            if active > maxx:
                maxx = active
                max_start = state
        print("Max was", maxx, "from", max_start)


if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    #num = next((i for i in lower_args if str(int(i)) == i), None)
    num = False
    main(real, part2, verbose, num)
