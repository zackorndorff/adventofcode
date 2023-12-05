from collections import defaultdict
from dataclasses import dataclass, field
import functools
import itertools
import json
import re
import sys

from tqdm import tqdm

@dataclass
class Map:
    dest: int
    src: int
    rnge: int
    src_range: range = field(init=False, repr=False)
    dest_range: range = field(init=False, repr=False)
    def __post_init__(self):
        self.src_range = self.__src_range()
        self.dest_range = self.__dest_range()
    def __src_range(self):
        return range(self.src, self.src + self.rnge)
    def __dest_range(self):
        return range(self.dest, self.dest + self.rnge)
    def mapit(self, src):
        #assert src in self.src_range()
        #out = src - self.src + self.dest
        #assert out in self.dest_range
        #return out
        return src - self.src + self.dest

class Mapper:
    def __init__(self):
        self.maps = []
    def mapit(self, num):
        for m in self.maps:
            if num in m.src_range:
                return num - m.src + m.dest
                # Optimized out
                #return m.mapit(num)
        return num
    def append(self, m):
        self.maps.append(m)
    def __repr__(self):
        return repr(self.maps)
    def range_len(self):
        return sum(i.rnge for i in self.maps)
            

def main(realdata=False, part2=False):
    if realdata:
        data = open("05.txt", "r")
    else:
        data = """seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4""".splitlines()

    seeds = []
    maps = defaultdict(Mapper)
    for linenum, line in enumerate(data):
        line = line.strip()
        if ":" in line:
            title, rest = line.split(":")
            if rest.strip():
                assert title == "seeds"
                seeds = [int(i) for i in rest.split()]
            continue
        elif not line:
            continue
        dest, src, rnge = [int(i) for i in line.split()]
        my_map = Map(dest, src, rnge)
        maps[title].append(my_map)

    #print(maps)
    if not part2:
        lowest_loc = None
        lowest_seed = None
        for seed in seeds:
            val = seed
            for m in maps.values():
                val = m.mapit(val)
            if lowest_loc is None or val < lowest_loc:
                lowest_seed = seed
                lowest_loc = val
        print("part1", lowest_seed, lowest_loc)
    else:
        assert (len(seeds) % 2) == 0
        seedranges = []
        lengths = []
        for idx1, idx2 in zip(range(0, len(seeds), 2), range(1, len(seeds), 2)):
            seedranges.append(range(seeds[idx1], seeds[idx1] + seeds[idx2]))
            lengths.append(seeds[idx2])
        assert len(lengths) == len(seeds)/2
        assert sum(len(i) for i in (seedranges)) == sum(lengths)
        print(sum(lengths))
        print("sum of ranges", next(iter(maps.values())).range_len())

        lowest_loc = int(2**32-1) # Verified by testing that this gets overwritten at least once.
        lowest_seed = None
        my_maps = list(maps.values())
        for i, seed in tqdm(enumerate(itertools.chain(*seedranges)), total=sum(lengths)):
            #if i > 1000000:
            #    raise SystemExit
            val = seed
            for m in my_maps:
                val = m.mapit(val)
            if val < lowest_loc:
                lowest_seed = seed
                lowest_loc = val
        print("part2", lowest_seed, lowest_loc)




if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    main(real, part2)
