from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, List, Set, Tuple, Optional
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

class LogicCell:
    graph_name = ""
    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs
    def append_input(self, input_name: str):
        pass
    def in_pulse(self, pulse: bool, whence: str) -> Optional[bool]:
        # Returns True/False to send a pulse or None to do nothing
        raise NotImplementedError

class FlipFlop(LogicCell):
    graph_name = "FF"
    def __init__(self, name, outputs):
        super().__init__(name, outputs)
        self.state = False
    def in_pulse(self, pulse, whence):
        if pulse is True:
            return None
        assert pulse is False
        self.state = not self.state
        return self.state
    def __hash__(self):
        return hash((
            self.name,
            tuple(self.outputs),
            self.state,
        ))
    def __eq__(self, other):
        return self.name == other.name and self.outputs == other.outputs and self.state == other.state

class Conjunction(LogicCell):
    graph_name = "AND"
    def __init__(self, name, outputs):
        super().__init__(name, outputs)
        self.state = {}

    def in_pulse(self, pulse, whence: str):
        if len(self.state.keys()) == 0:
            raise Exception("Need to init state")
        self.state[whence] = pulse
        if all(i is True for i in self.state.values()):
            return False
        else:
            return True

    def append_input(self, input_name: str):
        self.state[input_name] = False

    def __as_tuple(self):
        return (
            self.name,
            tuple(self.outputs),
            tuple((k,v) for k, v in self.state.items()),
        )

    def __hash__(self):
        return hash(self.__as_tuple())
    def __eq__(self, other):
        return self.__as_tuple() == other.__as_tuple()

class Broadcaster(LogicCell):
    def __init__(self, name, outputs):
        super().__init__(name, outputs)

    def in_pulse(self, pulse, whence):
        return pulse

def make_logiccell(tyype: str, name: str, outputs: List[str]):
    match tyype:
        case "%":
            return FlipFlop(name, outputs)
        case "&":
            return Conjunction(name, outputs)
        case "broadcaster":
            return Broadcaster(name, outputs)
    raise Exception(f"shouldn't be here: {tyype}")

# Cell types:
# % - flip-flop: on/off default off
#   high pulse ignored
#   low pulse flips state + sends pulse with that state
# & - conjunction: remember state of all inputs: default all low.
#   when pulse received, update state
#   If all high, send low
#   If any low, send high
#   NB: this means it needs to know its inputs: getting a single high can't pull
#   it low unless it only has one input
# broadcaster: just parrots pulses. Provides the button.

# We want our state to be hashable, because part2 is presumably going to ask us
# to optimize it.
class LogicSim:
    def get_cell(self, name):
        return self._cells[self._cell_index[name]]

    def to_dot(self):
        name_map = {}
        for cell in self._cells:
            name_map[cell.name] = f"{cell.graph_name}_{cell.name}"
        fragments = []
        fragments.append("digraph G {")
        for cell in self._cells:
            for output in cell.outputs:
                lhs = name_map.get(cell.name, cell.name)
                rhs = name_map.get(output, output)
                fragments.append(f"{lhs} -> {rhs}")
        fragments.append("}")
        return "\n".join(fragments)

    def __init__(self, cells):
        self._low_pulses = 0
        self._high_pulses = 0
        self._cells = cells
        self._cell_index = {i.name: idx for idx, i in enumerate(self._cells)}
        self._first_lows = {}
        visited = set()
        # tree walk to populate inputs and check for cycles
        queue = [self.get_cell("broadcaster")]
        while queue:
            i = queue.pop()
            addr = id(i)
            if addr in visited:
                continue
            visited.add(addr)
            for output in i.outputs:
                if output == "output":
                    continue
                try:
                    output = self.get_cell(output)
                except KeyError:
                    continue
                output.append_input(i.name)
                queue.append(output)

    def count(self, pulse):
        assert pulse in (True, False)
        if pulse:
            self._high_pulses += 1
        else:
            self._low_pulses += 1

    def score(self):
        return self._high_pulses * self._low_pulses

    def simulate_input(self, pulse, i=0):
        pulses = deque([("broadcaster", pulse, None)])
        while pulses:
            name, pulse, whence = pulses.popleft()
            # Count it
            self.count(pulse)
            if name == "output":
                print("Output:", pulse)
                continue
            try:
                cell = self.get_cell(name)
            except KeyError:
                continue
            result = cell.in_pulse(pulse, whence)
            if result is not None:
                if result is True and cell.name not in self._first_lows:
                    self._first_lows[cell.name] = i
                for output in cell.outputs:
                    pulses.append((output, result, name))

def main(realdata=False, part2=False, verbose=False, num=None):
    if realdata:
        data = open("20.txt", "r")
    else:
        data = """broadcaster -> a, b, c
%a -> b
%b -> c
%c -> inv
&inv -> a""".splitlines()
        data2 = """broadcaster -> a
%a -> inv, con
&inv -> b
%b -> con
&con -> output""".splitlines()
        data = data2

    cells = []
    for linenum, line in enumerate(data):
        line = line.strip()
        lhs, rhs = line.split(" -> ")
        if lhs == "broadcaster":
            tyype = lhs
            name = lhs
        else:
            tyype = lhs[:1]
            name = lhs[1:]
        outputs = rhs.split(", ")
        cell = make_logiccell(tyype, name, outputs)
        cells.append(cell)
    sim = LogicSim(cells)
    if not part2:
        for i in range(1000):
            sim.simulate_input(False)
        print("score", sim.score())
    else:
        print(sim.to_dot())
        interesting = ["sp", "sv", "qs", "pg"]
        for i in tqdm(range(10000000000000)):
            sim.simulate_input(False, i+1)
            if all(j in sim._first_lows for j in interesting):
                fun = [(cell, sim._first_lows[cell]) for cell in interesting]
                print(math.lcm(*(a for _, a in fun)))
                break





if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    #@num = next((i for i in lower_args if str(int(i)) == i), None)
    num = None
    main(real, part2, verbose, num)
