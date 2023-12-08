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

@dataclass
class Node:
    id: str
    adj: List[str] = field(default_factory=list)

@dataclass
class Graph:
    nodes: Dict[str, Node] = field(default_factory=dict)

    def append(self, node: Node):
        assert node.id not in self.nodes
        self.nodes[node.id] = node

    def __getitem__(self, key: str):
        return self.nodes[key]

LINE_RE = re.compile(r'([0-9A-Z]+) = \(([0-9A-Z]+), ([0-9A-Z]+)\)')
def main(realdata=False, part2=False):
    if realdata:
        data = open("08.txt", "r")
    else:
        data = """RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)""".splitlines()
        if part2:
            data = """LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)""".splitlines()

    instructions = ""
    graph = Graph()
    for linenum, line in enumerate(data):
        line = line.strip()
        print(line)
        if linenum == 0:
            instructions = line
            continue
        if not line:
            continue
        m = LINE_RE.match(line)
        if not m:
            raise Exception("bad")
        nid, el1, el2 = m.groups()
        node = Node(nid, [el1, el2])
        graph.append(node)

    #print(graph)

    if not part2:
        count = 0
        cur = graph["AAA"]
        for insn in itertools.cycle(instructions):
            insnmap = {
                    "L": 0,
                    "R": 1,
            }
            cur = graph[cur.adj[insnmap[insn]]]
            count += 1
            if cur.id == "ZZZ":
                break

        print(count)
    else:
        print("instruction len is", len(instructions))
        assert len(instructions) == 271
        count = 0
        cur = [node for node in graph.nodes.values() if node.id.endswith("A")]
        print("starting", cur)
        reported = defaultdict(lambda: False)
        counts = []
        for insn in itertools.cycle(instructions):
            insnmap = {
                    "L": 0,
                    "R": 1,
            }
            for i in range(len(cur)):
                c = cur[i]
                new_c = graph[c.adj[insnmap[insn]]]
                cur[i] = new_c
            count += 1
            for i, c in enumerate(cur):
                if c.id.endswith("Z") and not reported[i]:
                    print(f"After {count} steps [{count%271} %271], state is {c} for index {i}")
                    reported[i] = True
                    counts.append(count)
                    assert count%271 == 0
            if all(i.id.endswith("Z") for i in cur):
                print("lol this will never happen")
                print(count)
                break
            if all(reported[i] for i in range(len(cur))):
                break

        # This relies on the only time each chain lands on Z being the end of
        # the instruction set.
        # That's an ... odd structure to this problem and I'm not sure how to
        # validate it other than experimentally
        # But that seems to have been the intended solution.
        # The instruction length was prime, but I'm not sure if that matters
        # here.
        # So now we have the interval at which each chain will hit Z, so the
        # answer for all of them to hit Z is the LCM of them.
        print(math.lcm(*counts))

        # During my actual solve I called math.lcm by hand after dumping out all
        # the chain lengths.


if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    main(real, part2)
