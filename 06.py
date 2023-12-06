from collections import defaultdict
from dataclasses import dataclass, field
import functools
import itertools
import json
import re
import sys

def main(realdata=False, part2=False):
    if realdata:
        data = open("06.txt", "r")
    else:
        data = """Time:      7  15   30
Distance:  9  40  200""".splitlines()

    parsed = {}
    for linenum, line in enumerate(data):
        line = line.strip()
        title, rest = line.split(":")
        rest = [int(i) for i in rest.strip().split()]
        parsed[title] = rest
    time = parsed["Time"]
    distance = parsed["Distance"]

    print(parsed)
    assert len(time) == len(distance)

    if not part2:
        all_ways = []
        for race in range(len(time)):
            t, d = time[race], distance[race]
            ways = 0
            for i in range(t):
                held = i
                went = (t-held)*held
                if went > d:
                    ways += 1

            all_ways.append(ways)

        total = all_ways[0]
        for way in all_ways[1:]:
            total *= way
        print(total)
    else:
        time = int(''.join(str(i) for i in time))
        distance = int(''.join(str(i) for i in distance))
        t, d = time, distance
        ways = 0
        for i in range(t):
            held = i
            went = (t-held)*held
            if went > d:
                ways += 1
        print("part2", ways)






if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    main(real, part2)
