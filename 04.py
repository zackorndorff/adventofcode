from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Card:
    id: int
    winning: set
    yours: set
testdata = """Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11"""

cards = []
total = 0
#for line in testdata.splitlines():
for line in open("04.txt", "r"):
    card_id, rest = line.split(":", 1)
    card_id = card_id.split(" ")[-1]

    set1, set2 = rest.split("|")

    winning = set([int(i) for i in set1.strip().split()])
    yours = set([int(i) for i in set2.strip().split()])

    cards.append(Card(int(card_id), winning, yours))

old_cards = cards
cards = defaultdict(list)
for card in old_cards:
    cards[card.id].append(card)

for card_idx in range(1, 1+len(cards.keys())):
    for count, card in enumerate(cards[card_idx]):
        winning = card.winning
        yours = card.yours

        matches = len(winning & yours)

        for id2 in range(card_idx+1, 1+ card_idx + (matches)):
            if id2 not in cards:
                break
            #print(f"Adding new copy of {id2} due to win ({matches}) on card {card_idx}[{count}]")
            cards[id2].append(cards[id2][0])

for cardlist in cards.values():
    total += len(cardlist)

for id, cardlist in cards.items():
    print(id, len(cardlist))

#card_idx = 0
#while card_idx < len(cards):
#    winning = cards[card_idx].winning
#    yours = cards[card_idx].yours
#
#    matches = len(winning & yours)
#    score = 0
#    for i in range(matches):
#        if score == 0:
#            score = 1
#        else:
#            score *= 2
#    total += score
#    card_idx += 1
print(total)
