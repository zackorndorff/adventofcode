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

def transpose(lines):
    new = [([""] * len(lines)) for i in range(len(lines[0]))]
    for i, line in enumerate(lines):
        for j, ch in enumerate(line):
            new[j][i] = ch
    return new

def points(width, height):
    for i in range(height):
        for j in range(width):
            yield (i, j)

def compute_edges_for_point(point, width, height):
        # Each point has north, south, east, west edges
        y, x = point
        # north
        if y-1 >= 0:
            north = (y-1, x)
            yield (point, north)
        if y+1 < height:
            south = (y+1, x)
            yield (point, south)
        if x-1 >= 0:
            west  = (y  , x-1)
            yield (point, west)
        if x+1 < width:
            east  = (y  , x+1)
            yield (point, east)

def compute_neighbors_for_point(point, width, height):
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
    return neighbors

def compute_edges(width, height):
    for point in points(width, height):
        yield from compute_edges_for_point(point, width, height)

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

def dijkstra(data, source_point):
    width = len(data[0])
    height = len(data)
    #for edge in compute_edges(width, height):
    dist = {}
    prev = {}
    Q = []
    for point in points(width, height):
        dist[point] = 999999999
        prev[point] = None
    dist[source_point] = 0
    heapq.heappush(Q, (0, source_point))

    while Q:
        prio, u = heapq.heappop(Q)
        if prio != dist[u]:
            continue

        for v in compute_neighbors_for_point(u, width, height):
            alt = dist[u] + 1
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(Q, (alt, v))
    return dist, prev


def main(realdata=False, part2=False):
    if realdata:
        data = open("11.txt", "r")
    else:
        data = """...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....""".splitlines()

    readone = []
    for linenum, line in enumerate(data):
        line = line.strip()
        readone.append(list(line))
        if all(ch == "." for ch in line):
            readone.append(list(line))

    height = len(readone)
    # this is a list of lists of chars
    transposed = transpose(readone)
    transposed_final = []
    for line in transposed:
        transposed_final.append(line)
        if all(ch == "." for ch in line):
            transposed_final.append(line)

    final = transpose(transposed_final)
    for line in final:
        for ch in line:
            print(ch, end="")
        print()

    galaxies = []
    for point in points(len(final[0]), len(final)):
        y, x = point
        if final[y][x] == '#':
            galaxies.append(point)

    total = 0
    for i, galaxy1 in enumerate(tqdm(galaxies)):
        dist, prev = dijkstra(final, galaxy1)
        for galaxy2 in galaxies[i+1:]:
            #print(f"E({galaxy1}, {galaxy2}) = {dist[galaxy2]}")
            total += dist[galaxy2]

    print("part1 total was", total)




if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    main(real, part2)
