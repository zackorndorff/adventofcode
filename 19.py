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

import ast

def print_depth(*args, **kwargs):
    print("    " * (len(inspect.stack(0))-5), end="")
    return print(*args, **kwargs)

op_map = {
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        }
@dataclass
class Rule:
    condition: str
    outcome: str

    def evaluate(self, part):
        if self.condition is None:
            return True
        else:
            attr, op = self.condition[:2]
            num = int(self.condition[2:])
            return op_map[op](part.attributes[attr], num)
            

def parse_rule(s):
    if ":" in s:
        condition, outcome = s.split(":")
    else:
        condition = None
        outcome = s
    return Rule(condition, outcome)


def parse_workflow(s) -> Tuple[str, List[Rule]]:
    assert s.endswith("}")
    rule_name, rest = s.split("{")
    rest = rest[:-1] # remove "}"
    return rule_name, [parse_rule(i) for i in rest.split(",")]


class InterpreterState:
    def __init__(self, workflows):
        self.workflows = workflows
        self.current_workflow = "in"
        self.rule_index = 0

    def evaluate(self, part):
        while True:
            wf = self.workflows[self.current_workflow]
            rule = wf[self.rule_index]
            print(" ", self.current_workflow, rule)
            if rule.evaluate(part):
                if rule.outcome == "A":
                    return True
                elif rule.outcome == "R":
                    return False
                else:
                    self.current_workflow = rule.outcome
                    self.rule_index = 0
            else:
                self.rule_index += 1

class Part:
    def __init__(self, s):
        assert s.startswith("{")
        assert s.endswith("}")
        attrs = s[1:-1].split(",")
        tuples = [tuple(i.split("=")) for i in attrs]
        tuples = [(a, int(b)) for a, b in tuples]
        self.attributes = dict(tuples)

    def __repr__(self):
        return f"Part({self.attributes=})"

    def score(self):
        attrs = list("xmas")
        return sum(self.attributes[i] for i in attrs)

class SymVar:
    def __init__(self):
            self.lower_bound = 1
            self.upper_bound_exclusive = 4001

    def copy(self):
        other = SymVar()
        other.lower_bound = self.lower_bound
        other.upper_bound_exclusive = self.upper_bound_exclusive
        return other

    def valid(self):
        return self.lower_bound < self.upper_bound_exclusive

    def __repr__(self):
        return f"({self.lower_bound}, {self.upper_bound_exclusive})"

    def total_states(self):
        assert self.valid()
        return self.upper_bound_exclusive - self.lower_bound



# Tree walk through all states tracking what states got me there
class SymbolicState:
    def __init__(self):
        self.attributes = {k: SymVar() for k in list("xmas")}
        self.current_workflow = "in"
        self.rule_index = 0

    def finish_rule(self, rule):
        assert rule.condition is None
        self.current_workflow = rule.outcome
        self.rule_index = 0

    def constrain(self, condition, invert):
        attr, op = condition[:2]
        attr = self.attributes[attr]
        assert op in "><"
        inverse = {">": "<=", "<": ">="}
        if invert:
            op = inverse[op]
        num = int(condition[2:])
        if op == ">":
            attr.lower_bound = max(attr.lower_bound-1, num) + 1
        elif op == "<":
            attr.upper_bound_exclusive = min(attr.upper_bound_exclusive, num)
        elif op == ">=":
            attr.lower_bound = max(attr.lower_bound, num)
        elif op == "<=":
            attr.upper_bound_exclusive = min(attr.upper_bound_exclusive, num+1)
        else:
            raise Exception("unreachable")

    def valid(self):
        return all(i.valid() for i in self.attributes.values())

    def copy(self):
        other = SymbolicState()
        other.attributes = {k: v.copy() for k, v in self.attributes.items()}
        other.current_workflow = self.current_workflow
        other.rule_index = self.rule_index
        return other

    def __repr__(self):
        attrs = ', '.join(f"{name}={value}" for name, value in self.attributes.items())
        return f"SymbolicState({attrs}, wf={self.current_workflow}, idx={self.rule_index})"

    def total_states(self):
        assert self.valid()
        accum = 1
        for sv in self.attributes.values():
            accum *= sv.total_states()
        return accum

    #def possible(self, condition):
    #    attr, op = condition[:2]
    #    assert op in "><"
    #    num = int(condition[2:])

# Inspired by what little I know of angr's API -- y'all are awesome
class SimulationManager:
    def __init__(self, workflows: dict):
        self.workflows = workflows
        self.states = [SymbolicState()]
        self.succeeded = []
        self.failed = []

    def execute_condition(self, state, rule, not_taken):
        state = state.copy()
        print("Constraining", state, "with", rule.condition, not not_taken)
        state.constrain(rule.condition, not_taken)
        print("output state", state)
        if not_taken:
            state.rule_index += 1
        else:
            state.current_workflow = rule.outcome
            state.rule_index = 0
        return state

    def explore(self):
        while self.states:
            print(self)
            state = self.states.pop()
            if state.current_workflow in list("AR"):
                if state.current_workflow == "A":
                    self.succeeded.append(state)
                else:
                    assert state.current_workflow == "R"
                    self.failed.append(state)
                continue
            wf = self.workflows[state.current_workflow]
            rule = wf[state.rule_index]
            if rule.condition is None:
                state.finish_rule(rule)
                self.states.append(state)
            else:
                branch_taken = self.execute_condition(state, rule, False)
                branch_not_taken = self.execute_condition(state, rule, True)
                new_states = list(filter(lambda i: i.valid(), [branch_taken, branch_not_taken]))
                self.states.extend(new_states)

    def __str__(self):
        return f"Simgr(states={len(self.states)}, succeeded={len(self.succeeded)}, failed={len(self.failed)})"


def main(realdata=False, part2=False, verbose=False, num=None):
    if realdata:
        data = open("19.txt", "r")
    else:
        data = """px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}

{x=787,m=2655,a=1222,s=2876}
{x=1679,m=44,a=2067,s=496}
{x=2036,m=264,a=79,s=2244}
{x=2461,m=1339,a=466,s=291}
{x=2127,m=1623,a=2188,s=1013}""".splitlines()

    parts = []
    workflows = {}
    state = 0
    for linenum, line in enumerate(data):
        line = line.strip()
        if state == 0:
            if not line:
                state = 1
                continue
            name, workflow = parse_workflow(line)
            print(name, workflow)
            workflows[name] = workflow
        elif state == 1:
            part = Part(line)
            parts.append(part)

    if not part2:
        total = 0
        for part in parts:
            print("evaluating", part)
            istate = InterpreterState(workflows)
            if istate.evaluate(part):
                print("part was good")
                total += part.score()
            else:
                print("part was bad")
        print("total", total)
    else:
        simgr = SimulationManager(workflows)
        simgr.explore()
        print("result", sum(i.total_states() for i in simgr.succeeded))


if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    #@num = next((i for i in lower_args if str(int(i)) == i), None)
    num = None
    main(real, part2, verbose, num)
