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

def HASH(s):
    accum = 0
    for ch in s:
        accum += ord(ch)
        accum *= 17
        accum %= 256
    return accum

@dataclass
class Instruction:
    label: str
    op: str
    immediate: int
def parse_insn(insn):
    label = []
    for i, ch in enumerate(insn):
        if ch not in "-=":
            label.append(ch)
            continue
        if ch == "-":
            return Instruction(''.join(label), ch, 0)
        else:
            break
    if ch != "=":
        raise Exception(f"bad insn {insn=} {label=} {ch=}")
    imm = insn[i+1:]
    return Instruction(''.join(label), ch, int(imm))



def main(realdata=False, part2=False, verbose=False, num=None):
    if realdata:
        data = open("15.txt", "r")
    else:
        data = """rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7""".splitlines()

    boxes = defaultdict(dict)
    total = 0
    for linenum, line in enumerate(data):
        line = line.strip()
        #print(line)
        steps = line.split(",")
        for i, step in enumerate(steps):
            print("evaluating", step)
            total += HASH(step)
            insn = parse_insn(step)
            box = boxes[HASH(insn.label)]
            if insn.op == "-":
                try:
                    del box[insn.label]
                except KeyError:
                    pass
            elif insn.op == "=":
                box[insn.label] = insn.immediate
            print(f"after step {i}, state is {boxes}")

    print("part1:", total)

    part2_total = 0
    for i in range(256):
        box = boxes[i]
        for j, (label, power) in enumerate(box.items()):
            part2_total += (i+1) * (j+1) * power
    print("part2:", part2_total)





if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    #num = next((i for i in lower_args if str(int(i)) == i), None)
    num = None
    main(real, part2, verbose, num)
