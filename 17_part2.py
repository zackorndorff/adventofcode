from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, List, Set, Tuple
import functools
import itertools
import heapq
import json
import math
import re
import sys

from tqdm import tqdm

import contextlib
# https://stackoverflow.com/a/42424890
@contextlib.contextmanager
def redirect_to_tqdm():
    old_print = print
    def new_print(*args, **kwargs):
        try:
            tqdm.write(*args, **kwargs)
        except Exception:
            old_print(*args, **kwargs)
    try:
        inspect.builtins.print = new_print
        yield
    finally:
        inspect.builtins.print = old_print


NORTH = (-1, 0)
SOUTH = ( 1, 0)
WEST  = ( 0,-1)
EAST  = ( 0, 1)


# left is (y, x, direction, times_in_a_row)
# right is a (y, x) direction
def coord_add(left, right):
    assert len(left) == 4
    assert len(right) == 2
    assert right in (NORTH, SOUTH, WEST, EAST)

    ly, lx, ldir, ltimes = left
    ry, rx = right

    # initial point has no direction
    assert ldir in (None, NORTH, SOUTH, WEST, EAST)
    # initial point has 0 times in a row
    assert ltimes >= 0
    #assert ltimes < 5

    # Compute newdirection and newtimes
    newtimes = 1
    newdirection = right
    if ldir == newdirection:
        newtimes = ltimes + 1

    # Sanity checks
    #assert newtimes < 5
    assert newtimes > 0
    assert newdirection in (NORTH, SOUTH, WEST, EAST)
    
    return (ly + ry, lx + rx, newdirection, newtimes)


def transpose(lines):
    new = [([""] * len(lines)) for i in range(len(lines[0]))]
    for i, line in enumerate(lines):
        for j, ch in enumerate(line):
            new[j][i] = ch
    return new

MAX_STRAIGHT = 10
def points(width, height):
    for i in range(height):
        for j in range(width):
            for direction in (NORTH, SOUTH, WEST, EAST):
                for k in range(1, MAX_STRAIGHT+1):
                    yield (i, j, direction, k)

#def compute_edges_for_point(point, width, height):
#        # Each point has north, south, east, west edges
#        y, x, count = point
#        # TODO: do count logic here if this is needed
#        # north
#        if y-1 >= 0:
#            north = coord_add(point, NORTH)
#            yield (point, north)
#        if y+1 < height:
#            south = coord_add(point, SOUTH)
#            yield (point, south)
#        if x-1 >= 0:
#            west  = coord_add(point, WEST)
#            yield (point, west)
#        if x+1 < width:
#            east  = coord_add(point, EAST)
#            yield (point, east)

# Compute "layered" graph as suggested here:
# https://math.stackexchange.com/questions/889418/constrained-shortest-path-dijkstra/3327906#3327906
# Namely, we just add extra graph nodes to track the constraint on number of
# consecutive moves in the same direction.
def compute_neighbors_for_point(point, width, height):
    neighbors = []
    # Each point has north, south, east, west edges
    y, x, direction, count = point # TODO do count logic here

    # it needs to move a minimum of four blocks in that direction before it can turn
    if direction is not None and count < 4:
        maybe = coord_add(point, direction)
        newy, newx, _, _ = maybe
        if newy < 0 or newy >= width or newx < 0 or newx >= height:
            return []
        else:
            return [maybe]

    # north
    if y-1 >= 0 and not (direction == NORTH and count >= MAX_STRAIGHT) and not direction == SOUTH:
        north = coord_add(point, NORTH)
        neighbors.append(north)
    if y+1 < height and not (direction == SOUTH and count >= MAX_STRAIGHT) and not direction == NORTH:
        south = coord_add(point, SOUTH)
        neighbors.append(south)
    if x-1 >= 0 and not (direction == WEST and count >= MAX_STRAIGHT) and not direction == EAST:
        west  = coord_add(point, WEST)
        neighbors.append(west)
    if x+1 < width and not (direction == EAST and count >= MAX_STRAIGHT) and not direction == WEST:
        east  = coord_add(point, EAST)
        neighbors.append(east)
    return neighbors

#def compute_edges(width, height):
#    for point in points(width, height):
#        yield from compute_edges_for_point(point, width, height)

# Too slow
#def floyd_warshall(data):
#    # number of vertices is width times height
#    width = len(data[0])
#    height = len(data)
#    dist = defaultdict(lambda: defaultdict(lambda: 9999999999))
#    for edge in compute_edges(width, height):
#        u, v = edge
#        dist[u][v] = 1
#    for point in points(width, height):
#        dist[point][point] = 0
#    for k in tqdm(points(width, height)):
#        for i in points(width, height):
#            for j in points(width, height):
#                if dist[i][j] > dist[i][k] + dist[k][j]:
#                    dist[i][j] = dist[i][k] + dist[k][j]
#    return dist

INFINITY = 999999999
# data is dict from point2 to weight as char
# source_point is (y, x, direction, times_in_a_row)
def dijkstra(data, source_point):
    height = max(y for y, x in data.keys()) + 1
    width = max(x for y, x in data.keys()) + 1

    dist = {}
    prev = {}
    Q = []
    for point in points(width, height):
        dist[point] = INFINITY
        prev[point] = None
    dist[source_point] = 0
    heapq.heappush(Q, (0, source_point))

    while Q:
        prio, u = heapq.heappop(Q)
        if prio != dist[u]:
            continue

        #uy, ux, udirection, ucount = u
        for v in compute_neighbors_for_point(u, width, height):
            vy, vx, vdirection, vcount = v
            value = data[(vy, vx)]

            alt = dist[u] + value
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(Q, (alt, v))
    return dist, prev


def main(realdata=False, part2=False):
    if realdata:
        data = open("17.txt", "r")
    else:
        data = """2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533""".splitlines()

    graph_data = {}
    for linenum, line in enumerate(data):
        line = line.strip()
        for chnum, ch in enumerate(line):
            graph_data[(linenum, chnum)] = int(ch)

    height = max(y for y, x in graph_data.keys()) + 1
    width = max(x for y, x in graph_data.keys()) + 1

    start_point = (0, 0, None, 0)
    dist, prev = dijkstra(graph_data, start_point)

    # it needs to move a minimum of four blocks in that direction before it can turn (or even before it can stop at the end).
    exit_point_template = [height-1, width-1, None, None]
    exit_points = set()
    for direction in (NORTH, SOUTH, WEST, EAST):
        for count in range(4, MAX_STRAIGHT+1):
            exit_point_template[2] = direction
            exit_point_template[3] = count
            exit_points.add(tuple(exit_point_template))

    mindist, minpoint = INFINITY, None
    for p in exit_points:
        if dist[p] < mindist:
            mindist, minpoint = dist[p], p

    direction_map = {}
    cur = minpoint
    while cur in prev:
        y, x, direction, _ = cur
        #y, x, _, _ = prev[cur]

        direction_map[(y, x)] = direction
        cur = prev[cur]

    direction_ch = {
            #None: "!",
            NORTH: "^",
            SOUTH: "v",
            WEST: "<",
            EAST: ">",
    }
    for y in range(height):
        for x in range(width):
            point = (y, x)
            if point in direction_map:
                print(direction_ch[direction_map[point]], end="")
            else:
                print(graph_data[point], end="")
        print()


    print(f"part2: {mindist=} {minpoint=}")
    #import pdb; pdb.set_trace()


if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    main(real, part2)
