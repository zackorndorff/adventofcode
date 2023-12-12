from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, List, Set, Tuple
import functools
import itertools
import json
import math
import re
import sys

from tqdm import tqdm

import inspect

def matches_summary(records, summary):
    in_run = False
    run_length = 0
    run_lengths = []
    for ch in records:
        if ch == "#" and in_run:
            run_length += 1
        elif ch == "#" and not in_run:
            run_length = 1
            in_run = True
        elif ch == "." and in_run:
            run_lengths.append(run_length)
            in_run = False
            run_length = 0
    if run_length:
        run_lengths.append(run_length)
    return tuple(run_lengths) == summary, run_lengths

def print_depth(*args, **kwargs):
    print("    " * (len(inspect.stack(0))-5), end="")
    return print(*args, **kwargs)

@functools.cache
def partial(records, summary, verbose=False):
    mprint = print_depth if verbose else (lambda *args: None)
    mprint(f"partial({records}, {summary})")
    if records == "" and len(summary) == 0:
        return 1
    if records == "" and len(summary) >  0:
        return 0
    # No decision to make in case of first char ".", just move along
    if records[0] == ".":
        mprint("    recursing 1 (ignoring '.')")
        result = partial(records[1:], summary, verbose)
        mprint(f"    {result=}")
        return result
    if records != "" and len(summary) == 0:
        if "#" in records:
            return 0
        else:
            return 1
    try:
        first_dot = records.index(".")
    except ValueError:
        first_dot = len(records)
    mprint(f"  {first_dot=} {summary[0]=}")
    try:
        next_pound = records.index("#")
    except ValueError:
        next_pound = len(records)
    # If we don't have enough room to equal summary[0] then all wildcards must
    # be dots and we'll make it up with the next group of #'s
    if first_dot < summary[0]:
        # If we have a # before then, then we fail.
        if next_pound < first_dot:
            return 0
        mprint("    recursing 2 (setting all '?' to '.')")
        result = partial(records[first_dot:], summary, verbose)
        mprint(f"    {result=}")
        return result

    # After this point, we have at least one way to remove summary[0]

    # So our overlapping substructure is looking for places to add dots and
    # still remove summary[0]

    # Note: we must include the case of setting all to dots

    if records[0] == "#":
        # If we started with a #, we have no room to add dots. Just recurse.
        # We know we have enough #'s or ?'s due to the first_dot check. We must
        # remove summary[0], so we assume we'll set all ? to # and keep going.
        try:
            if records[summary[0]] == "#": # there has to be a dot after us!
                mprint("    failing to recursing 3 (nowhere to add dots) due to missing dot after us")
                return 0
        except IndexError:
            pass
        mprint("    recursing 3 (nowhere to add dots)")
        result = partial(records[summary[0]+1:], summary[1:], verbose)
        mprint(f"    {result=}")
        return result

    # We must have a "?". How many?
    wildcards = min(next_pound, first_dot)
    mprint(f"  {wildcards=}")

    wiggle_room = first_dot - summary[0]
    mprint(f"  {wiggle_room=}")
    assert wiggle_room >= 0, f"not enough wiggle_room: {wiggle_room}"

    total = 0
    # We want to use all our wildcards subject to how much spare room we have
    # And how much stuff we need to pull
    dots_to_add = min(wildcards, wiggle_room)
    mprint(f"  {dots_to_add=}")
    for i in range(dots_to_add+1):
        # Insert i dots at the beginning, then summary[0] #'s
        fudge = 0
        #if dots_to_add <= wiggle_room:
        if i + summary[0] != first_dot:
            # If we don't go all the way to the next dot, we need some way of forcing a dot after us
            # but we have no guarantee of there being a dot there, so check this.
            if records[i+summary[0]] != "?":
                continue
            fudge = 1
        mprint(f"  {i=} {fudge=}")
        mprint(f"    recursing 4 (adding {i} dots?)")
        result = partial(records[i+summary[0] + fudge:], summary[1:], verbose)
        mprint(f"    {result=}")
        total += result

    ## TODO debug false hits here
    ## Also try setting summary[0] wildcards to dot 
    #mprint("    recursing 5 (one bunch of wildcards dots)")
    #result = partial(records[wildcards:], summary, verbose)
    #mprint(f"    {result=} (case 5)")
    #total += result

    if wildcards > wiggle_room:
        # Now add one too many dots so as to force a failure
        mprint("    recursing 5 (one bunch of wildcards dots)")
        result = partial(records[wiggle_room+1:], summary, verbose)
        mprint(f"    {result=} (case 5)")
        total += result

    # # We want to use all our wildcards subject to how much spare room we have
    # # And how much stuff we need to pull
    # dots_to_add = min(wildcards, wiggle_room, summary[0])
    # mprint(f"  {dots_to_add=}")
    # for i in range(dots_to_add+1):
    #     # Insert i dots at the beginning, then summary[0] #'s
    #     #to_remove = dots_to_add + summary[0]
    #     mprint(f"  {i=}")
    #     mprint("    recursing 4 (adding {i} dots?)")
    #     result = partial(records[i+summary[0]:], summary[1:], verbose)
    #     mprint(f"    {result=}")
    #     total += result

    # # Also try setting one wildcard to dot 
    # mprint("    recursing 5 (all wildcards dots)")
    # result = partial(records[wildcards:], summary, verbose)
    # mprint(f"    {result=}")
    # total += result

    return total

    # Now we need to try all the ways to remove summary[0]
    # We must have that many "#"'s in a row. We can arbitrarily add dots at the
    # beginning, that's our only question.

    # So now we have an arbitrarily complex set of ##?#???##???????##, finished
    # by either the end of the string or a dot.
    # We need to figure out the groupings that are possible from that, then
    # recurse with those removed from summary
    # We could leave it all together, or each ? could become a dot.
    # We only care about it if we can remove stuff from summary: if it doesn't
    # match then we lose anyway and can ignore it.


def handle(line, part2, verbose):
    records, summary = line.split()
    if part2:
        records = "?".join([records]*5)
        summary = ",".join([summary]*5)
    summary = tuple([int(i) for i in summary.split(",")])
    #print(''.join(records), summary)
    new_result = partial(records, summary, verbose)
    return new_result

    # Test code via brute
    unknowns = [i for i, ch in enumerate(records) if ch == "?"]
    records = list(records)

    total = 0
    hits = set()
    for i in range(2**len(unknowns)):
        for uidx, unknown in enumerate(unknowns):
            records[unknown] = "#" if ((i & (1 << (uidx))) >> uidx) else "."
            if records[unknown] == "#":
                hits.add(unknown)
        if matches_summary(records, summary)[0]:
            total += 1
        #print('wut', i, summary,  ''.join(records), matches_summary(records, summary))
    for i in unknowns:
        assert i in hits, f"unknown {i} not hit out of {len(unknowns)}"
    assert new_result == total, f"Error on {line=} {new_result=} {total=}"
    return total




def main(realdata=False, part2=False, verbose=False):
    if realdata:
        data = open("12.txt", "r")
    else:
        data = """???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1""".splitlines()

    total = 0
    for linenum, line in enumerate(tqdm(list(data))):
        # if linenum != 8:
        #     continue
        #if linenum < 1:
        #    continue
        # if linenum > 0:
        #     break
        line = line.strip()
        result = handle(line, part2, verbose)
        print("line", linenum, line, "had", result)
        total += result
    print("answer:", total)



if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    verbose = "verbose" in lower_args
    main(real, part2, verbose)
