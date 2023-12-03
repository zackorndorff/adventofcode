#!/usr/bin/env python3

from collections import defaultdict
import re

ugh = {
                    'one': '1',
                    'two': '2',
                    'three': '3',
                    'four': '4',
                    'five': '5',
                    'six': '6',
                    'seven': '7',
                    'eight': '8',
                    'nine': '9',
                    }

alternation = "|".join(ugh.keys())

#ugh2 = r'^[a-z]*?(' + alternation + '|\d)[a-z0-9]*?(' + alternation + '|\d)?[a-z]*$'
#ugh2 = r'^[a-z]*?(' + alternation + '|\d)[a-z0-9]*?(' + alternation + '|\d)?$'
#print("RE", ugh2)
ugh3 = r'(?=(\d|' + alternation + '))'
print("RE", ugh3)

LINE_RE = re.compile(ugh3)
def main():
    accum = 0
    with open("01.txt", "r") as fp:
        for line in fp:
            line = line.strip()

            m = LINE_RE.findall(line.strip())
            one = m[0]
            two = m[-1]
            #one, two = m.groups()
            print(one, two, end=" ")
            #if two is None:
            #    two = one
            if one in ugh:
                one = ugh[one]
            if two in ugh:
                two = ugh[two]
            sum = int(one + two)
            print(line, one, two, sum)
            accum += sum
    print(accum)
        # elves = defaultdict(list)
        # elf = 1
        # for line in fp:
        #     if not line.strip():
        #         elf += 1
        #         continue
        #     elves[elf].append(int(line.strip()))
        # data = sorted(elves.items(), key=lambda x: (print(x),sum(x[1])), reverse=True)
        # print(sum(data[0][1]))
        # print(sum(data[0][1]) + sum(data[1][1]) + sum(data[2][1]))


main()
