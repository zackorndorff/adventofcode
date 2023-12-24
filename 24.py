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
import numpy as np
import sympy

from tqdm import tqdm

def print_depth(*args, **kwargs):
    print("    " * (len(inspect.stack(0))-5), end="")
    return print(*args, **kwargs)

@dataclass
class Hail:
    position: np.array
    velocity: np.array

    def intersects_xy(self, other):
        # So set the two positions equal to each other and solve for time they
        # intersect for both x-component and y-component
        # v_1 * t_1 + s_1 = v_2 * t_2 + s_2
        # vx_1 * t_1 + sx_1 = vx_2 * tx_2 + sx_2
        # ALSO: vy_1 * t_1 + sy_1 = vy_2 * t_2 + sy_2

        # How to solve it
        #vx_1, t_1, sx_1, vx_2, t_2, sx_2, vy_1, sy_1, vy_2, sy_2  = map(lambda s: sympy.Symbol(s), ["vx_1", "t_1", "sx_1", "vx_2", "t_2", "sx_2", "vy_1", "sy_1", "vy_2", "sy_2"])
        #eq1 = sympy.Eq(vx_1 * t_1 + sx_1,  vx_2 * t_2 + sx_2)
        #eq2 = sympy.Eq(vy_1 * t_1 + sy_1,  vy_2 * t_2 + sy_2)
        #print("solution", sympy.solvers.solvers.solve([eq1, eq2], [t_1, t_2], dict=True))
        ## [{t_1: (-sx_1*vy_2 + sx_2*vy_2 + sy_1*vx_2 - sy_2*vx_2)/(vx_1*vy_2 - vx_2*vy_1), t_2: (-sx_1*vy_1 + sx_2*vy_1 + sy_1*vx_1 - sy_2*vx_1)/(vx_1*vy_2 - vx_2*vy_1)}]

        s_1 = self.position[0:2]
        s_2 = other.position[0:2]
        sx_1, sy_1 = s_1
        sx_2, sy_2 = s_2

        v_1 = self.velocity[0:2]
        v_2 = other.velocity[0:2]
        vx_1, vy_1 = v_1
        vx_2, vy_2 = v_2

        if (vx_1*vy_2 - vx_2*vy_1) == 0:
            return (None, None), (None, None)
        t_1 = (-sx_1*vy_2 + sx_2*vy_2 + sy_1*vx_2 - sy_2*vx_2)/(vx_1*vy_2 - vx_2*vy_1)
        t_2 = (-sx_1*vy_1 + sx_2*vy_1 + sy_1*vx_1 - sy_2*vx_1)/(vx_1*vy_2 - vx_2*vy_1)

        p_1 = v_1 * t_1 + s_1
        p_2 = v_2 * t_2 + s_2
        return (p_1, t_1), (p_2, t_2)


def main(realdata=False, part2=False, verbose=False, num=None):
    if realdata:
        data = open("24.txt", "r")
        search_min = 200000000000000
        search_max = 400000000000000
    else:
        data = """19, 13, 30 @ -2,  1, -2
18, 19, 22 @ -1, -1, -2
20, 25, 34 @ -2, -2, -4
12, 31, 28 @ -1, -2, -1
20, 19, 15 @  1, -5, -3""".splitlines()
        search_min = 7
        search_max = 27

    hailstones = []
    for linenum, line in enumerate(data):
        line = line.strip()
        p, v = line.split(" @ ")
        position = np.array([int(i) for i in p.split(", ")])
        velocity = np.array([int(i) for i in v.split(", ")])
        hailstones.append(Hail(position, velocity))

    within = 0
    for a, b in itertools.combinations(hailstones, 2):
        if a is b:
            continue
        print("Hailstone A:", a.position, a.velocity)
        print("Hailstone B:", b.position, b.velocity)
        (p_1, t_1), (p_2, t_2) = a.intersects_xy(b)
        if t_1 is None:
            assert t_2 is None
            print("Hailstones' paths are parallel; they never intersect.")
        elif t_1 < 0:
            print("Hailstones' paths crossed in the past for hailstone A.")
        elif t_2 < 0:
            print("Hailstones' paths crossed in the past for hailstone B.")
        else:
            #assert (p_1 - p_2 < np.full(2, 0.1)).all()
            x, y = p_1
            if x < search_min or x > search_max or y < search_min or y > search_max:
                print(f"Hailstones' paths will cross outside the test area (at {x=}, {y=}).")
            else:
                print(f"Hailstones' paths will cross inside the test area (at {x=}, {y=}).")
                within += 1
        print()
    print(f"{within=}")


        



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
