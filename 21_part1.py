from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, List, Set, Tuple
import functools
import heapq
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

def points(width, height):
    for i in range(height):
        for j in range(width):
            yield (i, j)

def compute_neighbors_for_point(point, graph, width, height):
    neighbors = []
    # Each point has north, south, east, west edges
    y, x = point
    # north
    if y-1 >= 0:
        north = (y-1, x)
        #yield (point, north)
        neighbors.append(north)
    if y+1 < height:
        south = (y+1, x)
        #yield (point, south)
        neighbors.append(south)
    if x-1 >= 0:
        west  = (y  , x-1)
        #yield (point, west)
        neighbors.append(west)
    if x+1 < width:
        east  = (y  , x+1)
        #yield (point, east)
        neighbors.append(east)
    return [n for n in neighbors if graph[n] != "#"]


INFINITY = 999999999
# data is dict from point2 to weight as int
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
            vy, vx = v
            value = data[(vy, vx)]

            alt = dist[u] + value
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(Q, (alt, v))
    return dist, prev

def main(realdata=False, part2=False, verbose=False, num=None):
    if realdata:
        data = open("21.txt", "r")
        count = 64
    else:
        count = 6
        data = """...........
.....###.#.
.###.##..#.
..#.#...#..
....#.#....
.##..S####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
...........""".splitlines()

    graph_data = {}
    for linenum, line in enumerate(data):
        line = line.strip()
        for chnum, ch in enumerate(line):
            graph_data[(linenum, chnum)] = ch

    height = max(y for y, x in graph_data.keys()) + 1
    width = max(x for y, x in graph_data.keys()) + 1

    start_point = next(point for point, value in graph_data.items() if value == "S")

    print("start point", start_point)
    #dist, prev = dijkstra(graph_data, start_point)

    positions = set([start_point])
    for _ in range(count):
        new_positions = set()
        for position in positions:
            for neighbor in compute_neighbors_for_point(position, graph_data, width, height):
                new_positions.add(neighbor)
        positions = new_positions
    print(len(positions))



if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    #@num = next((i for i in lower_args if str(int(i)) == i), None)
    num = None
    main(real, part2, verbose, num)
