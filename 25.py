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

import networkx as nx

from tqdm import tqdm

def print_depth(*args, **kwargs):
    print("    " * (len(inspect.stack(0))-5), end="")
    return print(*args, **kwargs)

def main(realdata=False, part2=False, verbose=False, num=None):
    if realdata:
        data = open("25.txt", "r")
    else:
        data = """jqt: rhn xhk nvd
rsh: frs pzl lsr
xhk: hfx
cmg: qnr nvd lhk bvb
rhn: xhk bvb hfx
bvb: xhk hfx
pzl: lsr hfx nvd
qnr: nvd
ntq: jqt hfx bvb xhk
nvd: lhk
lsr: lhk
rzs: qnr cmg lsr rsh
frs: qnr lhk lsr""".splitlines()

    G = nx.Graph()
    for linenum, line in enumerate(data):
        line = line.strip()
        this, rest = line.split(": ")
        for connection in rest.split():
            G.add_edge(this, connection)

    # Min k-cut problem for k=2
    # https://www.geeksforgeeks.org/gomory-hu-tree-introduction/
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.flow.gomory_hu_tree.html#networkx.algorithms.flow.gomory_hu_tree
    nx.set_edge_attributes(G, 1, "capacity")
    ght = nx.gomory_hu_tree(G)
    min_weight, edge = min( (ght[a][b]["weight"], (a, b)) for a, b in ght.edges)
    ght.remove_edge(*edge)
    U, V = nx.connected_components(ght)
    print(len(U) * len(V))



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
