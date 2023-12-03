from collections import defaultdict
testdata = """467..114.1
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598.."""

from dataclasses import dataclass

SIZE=10

@dataclass
class Number:
    x: int
    y: int
    length: int
    data: int

    def adjacent_to_symbol_in(self, sym_map: 'Dict[Tuple[int, int], Symbol]'):
        return next((sym_map[point] for point in self.adjacent_points() if point in sym_map), None)

    def adjacent_points(self):
        # point to the left (if any)
        yield (self.x-1, self.y)
        # point to the right (if any)
        # skip conditional because I can
        yield (self.x+self.length, self.y)

        # point up-left
        yield (self.x-1, self.y-1)

        # point down-left
        yield (self.x-1, self.y+1)

        # point up-right
        yield (self.x+self.length, self.y-1)

        # point down-right
        yield (self.x+self.length, self.y+1)

        # point above/below all points on the number
        for i in range(self.length):
            yield (self.x+i, self.y-1)
            yield (self.x+i, self.y+1)
        

@dataclass
class Symbol:
    ch: str
    x: int
    y: int

def parse_line(line, y):
    numbers = []
    symbols = []

    current = None

    chidx = 0
    while chidx < len(line):
        if line[chidx] in "0123456789":
            if current is None:
                current = chidx
        else:
            if current is not None:
                numbers.append(Number(current, y, chidx - current, int(line[current:chidx])))
                current = None
            if line[chidx] != ".":
                # we're at a symbol
                symbols.append(Symbol(line[chidx], chidx, y))
        chidx += 1
    if current is not None:
        numbers.append(Number(current, y, chidx - current, int(line[current:chidx])))
        current = None
    return numbers, symbols
            


all_numbers, all_symbols = [], []
#for y, line in enumerate(testdata.splitlines()):
for y, line in enumerate(open("03.txt", "r")):
    numbers, symbols = parse_line(line.strip(), y)
    print(y, line.strip(), numbers, symbols)
    all_numbers.extend(numbers)
    all_symbols.extend(symbols)

sym_map = {}

for symbol in all_symbols:
    sym_map[(symbol.x, symbol.y)] = symbol

accum = 0
for number in all_numbers:
    if (adj := number.adjacent_to_symbol_in(sym_map)):
        print("number", number.data, "is adjacent to", adj)
        accum += number.data
print("part 1:", accum)


number_adjacency_points = defaultdict(list)
for number in all_numbers:
    for point in number.adjacent_points():
        number_adjacency_points[point].append(number)

accum2 = 0
for symbol in all_symbols:
    if symbol.ch != "*":
        continue
    adjacent = number_adjacency_points[(symbol.x, symbol.y)]
    if len(adjacent) != 2:
        continue
    gear_ratio = adjacent[0].data * adjacent[1].data
    accum2 += gear_ratio

print("part 2", accum2)



