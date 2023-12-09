from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List
import functools
import itertools
import json
import math
import re
import sys

def layer_diffs(layer):
    diffs = []
    for i in range(len(layer)-1):
        diffs.append(layer[i+1] - layer[i])
    return diffs

def predict_next_part1(item: List[int]):
    layers = [item]
    while not all(i == 0 for i in layers[-1]):
        layers.append(layer_diffs(layers[-1]))
    print(layers)
    last_diff = 0
    for layer in reversed(layers[:-1]):
        last_diff = layer[-1] + last_diff
    return last_diff

def predict_next(item: List[int]):
    layers = [item]
    while not all(i == 0 for i in layers[-1]):
        layers.append(layer_diffs(layers[-1]))
    print(layers)
    last_diff = 0
    for layer in reversed(layers[:-1]):
        last_diff = layer[0] - last_diff
    return last_diff


def main(realdata=False, part2=False):
    if realdata:
        data = open("09.txt", "r")
    else:
        data = """0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45""".splitlines()

    items = []
    for linenum, line in enumerate(data):
        line = line.strip()
        print(line)
        items.append(list(int(i) for i in line.split()))

    predictor = predict_next if part2 else predict_next_part1
    return sum(predictor(item) for item in items)



if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    print(main(real, part2))
