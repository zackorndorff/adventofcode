from collections import defaultdict
import json

testdata = """Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green"""

def parse_entry(entry):
        entry = entry.strip()
        balls = entry.split(", ")
        parsed_balls = []
        for ball in balls:
            quantity, color = ball.split(" ")
            parsed_balls.append((int(quantity), color))
        return parsed_balls

games = {}
#for line in testdata.splitlines():
for line in open("02.txt", "r"):
    game_num_str, entries = line.split(":")
    game_num = int(game_num_str.split(" ")[1])
    entries_list = entries.split("; ")
    parsed_entries = []
    for entry in entries_list:
        parsed_entries.append(parse_entry(entry))
    games[game_num] = parsed_entries

truth = "12 red, 13 green, 14 blue"
parsed_truth = parse_entry(truth)
#print(json.dumps(games, indent=4))
print("truth", parsed_truth)

truth_dict = {color: count for count, color in parsed_truth}

total = 0
powers = 0

for game_num, game_data in games.items():
    possible = True
    maxes = defaultdict(int)
    for entry in game_data:
        for ball in entry:
            try:
                if maxes[ball[1]] < ball[0]:
                    maxes[ball[1]] = ball[0]
                if truth_dict[ball[1]] < ball[0]:
                    print(f"Game {game_num} is impossible: {ball}")
                    possible = False
                    #break
            except KeyError:
                print(f"Game {game_num} is impossible: {ball} (not found)")
                possible = False
                #break
        # if not possible:
        #     break
    if possible:
        print(f"Game {game_num} is good!")
        total += game_num
    power = maxes["red"] * maxes["green"] * maxes["blue"]
    print(f"Game {game_num}",  maxes, power)
    powers += power

print("total was", total)
print("total powers was", powers)
