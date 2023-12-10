from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, List, Set, Tuple
import functools
import itertools
import json
import math
import re
import sys

@dataclass
class Pipes:
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


    def adj(self, coord: Tuple[int, int]) -> Iterable[Tuple[int, int]]:
        return clamped_adj(coord, self.data[coord], self._height, self._width)

def clamped_adj(point, ch, height, width) -> Iterable[Tuple[int, int]]:
    for coord in adj(point, ch):
        y, x = coord
        if y < 0 or x < 0:
            continue
        if y >= height or x >= width:
            continue
        yield coord

def adj(point: Tuple[int, int], ch: str) -> Iterable[Tuple[int, int]]:
    y, x = point
    north = (y-1, x)
    south = (y+1, x)
    west = (y, x-1)
    east = (y, x+1)

    if ch == "|":
        yield north
        yield south
    elif ch == "-":
        yield west
        yield east
    elif ch == "L":
        yield north
        yield east
    elif ch == "J":
        yield north
        yield west
    elif ch == "7":
        yield south
        yield west
    elif ch == "F":
        yield south
        yield east
    elif ch == ".":
        pass
    elif ch == "S":
        yield north
        yield south
        yield west
        yield east
        # HAX

def halfpoint_dumb_adj(coord) -> Iterable[Tuple[int, int]]:
    y, x = coord
    yield y-0.5, x
    yield y+0.5, x
    yield y, x-0.5
    yield y, x+0.5

def halfpoint_filter(iterator, pipes):
    height, width = pipes._height, pipes._width
    for point in iterator:
        y, x = point
        if x < 0 or y < 0:
            continue
        if x >= width or y >= height:
            continue
        yield point

def halfpoint_adj(coord, pipes) -> Iterable[Tuple[int, int]]:
    return halfpoint_filter(halfpoint_dumb_adj(coord), pipes)

def compute_halfwalls(walls, pipes):
    for wall in walls:
        y, x = wall
        ch = pipes.data[wall]
        north = (y-0.5, x)
        south = (y+0.5, x)
        west = (y, x-0.5)
        east = (y, x+0.5)
        if ch == "|":
            yield north
            yield south
        elif ch == "-":
            yield west
            yield east
        elif ch == "L":
            yield north
            yield east
        elif ch == "J":
            yield north
            yield west
        elif ch == "7":
            yield south
            yield west
        elif ch == "F":
            yield south
            yield east


def find_halfpoints_reachable_from(coord, pipes, walls, dimensions) -> Set[Tuple[int, int]]:
    reachable = set()
    queue = [coord]

    halfwalls = halfpoint_filter(compute_halfwalls(walls, pipes), pipes)
    walls = set(walls)
    for i in halfwalls:
        walls.add(i)

    # BFS
    while queue:
        current = queue[0]
        queue = queue[1:] # TODO: optimize
        for adj_coord in halfpoint_adj(current, pipes):
            if adj_coord in reachable:
                continue
            if adj_coord in walls:
                continue
            reachable.add(adj_coord)
            queue.append(adj_coord)
    return reachable

def main(realdata=False, part2=False):
    if realdata:
        data = open("10.txt", "r")
    else:
        data = """.....
.S-7.
.|.|.
.L-J.
.....""".splitlines()
        data2 = """..F7.
.FJ|.
SJ.L7
|F--J
LJ...""".splitlines()
        data = data2

    pipe_data = {}
    for linenum, line in enumerate(data):
        line = line.strip()
        for chnum, ch in enumerate(line):
            pipe_data[(linenum, chnum)] = ch

    starting = None
    for point, ch in pipe_data.items():
        if ch == "S":
            starting = point
    if starting is None:
        raise Exception("no starting")

    pipes = Pipes(pipe_data)

    print("Found starting location", starting)

    # https://stackoverflow.com/a/3908454
    # Do a DFS to find the cycle
    # We want to walk until we find S again
    # Then walk backwards following the parent chain to make a list of nodes in
    # the chain
    positions = [(starting, None)]
    dfs_visited = set()
    end = None
    while positions:
        cur_pos, parent = positions[-1]
        prev_len = len(positions)
        positions = positions[:-1]
        assert len(positions) < prev_len
        if cur_pos in dfs_visited:
            continue
        dfs_visited.add(cur_pos)
        for adj_coord in pipes.adj(cur_pos):
            if pipes.data[adj_coord] == "S" and adj_coord != parent[0]:
                print(f"Found other end at ({cur_pos})")
                end = (cur_pos, parent)
                positions = []
                break
            if adj_coord in dfs_visited:
                continue
            positions.append((adj_coord, (cur_pos, parent)))
    chain = []
    current = end
    while current is not None:
        chain.append(current[0])
        current = current[1]
    print("end before parent was", chain[-2])
    print(len(chain))
    assert len(chain) % 2 == 0
    print("part1:", len(chain) // 2)

    # As to this shenanigans with going between pipes
    # I'm going to implement an autofill algorithm on half-grid boundaries
    # Since it seems hard to determine which side is inside and which side is
    # outside, I'm going to just do it twice, and if I hit the outside wall then
    # I know that side is the outside.
    # I take the assumption that diagonal moves don't exist.
    outside_points = find_halfpoints_reachable_from((0,0), pipes, walls=chain,
                                   dimensions=(pipes._height, pipes._width))

    # Wait if I assume no weird inside-out stuff if it's not outside it's
    # inside. Just count 'em.
    inside_cell_count = 0
    for i in range(pipes._height):
        for j in range(pipes._width):
            if (i, j) not in outside_points and (i, j) not in chain:
                print(i, j)
                inside_cell_count += 1

    print("part2:", inside_cell_count)
    chainset = set(chain)
    for i in range(pipes._height):
        for j in range(pipes._width):
            if (i, j) in outside_points:
                print(".", end="")
            elif (i, j) in chainset:
                print("W", end="")
            else:
                print(" ", end="")
        print()

    #visited = {}
    #while positions:
    #    next_positions = []
    #    for coord, count, parent in positions:
    #        if coord in visited:
    #            continue
    #        visited[coord] = count
    #        for adj_coord in pipes.adj(coord):
    #            if pipes.data[adj_coord] == "S" and adj_coord != parent:
    #                print(f"Found other end at ({coord})")
    #            if adj_coord in visited:
    #                assert visited[adj_coord] < count+1
    #                continue
    #            next_positions.append((adj_coord, count+1, coord))
    #    positions = next_positions



    #maxx = starting
    #for coord, count in visited.items():
    #    if count > visited[maxx]:
    #        # need 2 paths back to be in a loop? (this is a cheat but might work if they were nice)
    #        # It fails if any of the rabbit trails have loops
    #        num = 0
    #        for adj_coord in pipes.adj(coord):
    #            adj_dist = visited.get(adj_coord, None)
    #            if adj_dist is None:
    #                continue
    #            if adj_dist == count-1:
    #                num += 1
    #        assert num < 3
    #        if num != 2:
    #            continue

    #        maxx = coord
    #print(f"Found max of {visited[maxx]} at {maxx}")

    #if real:
    #    return
    #for i in range(pipes._height):
    #    for j in range(pipes._width):
    #        print(f"{visited.get((i, j), '.'):5}", end="")
    #    print()



if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    main(real, part2)
