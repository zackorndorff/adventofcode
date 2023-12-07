from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List
import functools
import itertools
import json
import re
import sys

ranking = list(reversed("AKQT98765432J"))

class HandType(IntEnum):
    FIVE      = 7
    FOUR      = 6
    FULLHOUSE = 5
    THREE     = 4
    TWOPAIR   = 3
    ONEPAIR   = 2
    HIGHCARD  = 1


@dataclass(order=True)
class Hand:
    sort_index: Any = field(init=False, repr=False)
    cards: str
    bid: int

    _buckets: Dict = field(init=False, repr=False)

    def __post_init__(self):
        self._buckets = self.__buckets()
        self.sort_index = (self.rank, tuple([ranking.index(card) for card in self.cards]))

    def __buckets(self):
        buckets = defaultdict(list)
        for i, card in enumerate(self.cards):
            card = ranking.index(card)
            buckets[card].append(i)
        return buckets

    @property
    def rank(self):
        if self.is_kind(5):
            return HandType.FIVE
        elif self.is_kind(4):
            return HandType.FOUR
        elif self.is_fullhouse():
            return HandType.FULLHOUSE
        elif self.is_kind(3):
            return HandType.THREE
        else:
            pairs = self.pairs()
            if len(pairs) == 2:
                return HandType.TWOPAIR
            elif len(pairs) == 1:
                return HandType.ONEPAIR
            else:
                return HandType.HIGHCARD

    @property
    def buckets(self):
        return self._buckets

    def is_kind(self, count):
        jokers = len(self.buckets[0])
        highest = []
        for i, bucket in self.buckets.items():
            if i == 0:
                continue
            if len(bucket) == count:
                return bucket
            elif len(bucket) > len(highest):
                highest = bucket
        if len(highest) + jokers >= count:
            if len(highest) == 0:
                return self.buckets[0]
            return highest
        return None

    def is_fullhouse(self):
        jokers = len(self.buckets[0])
        counts = list(sorted([len(v) for i, v in self.buckets.items() if i != 0], reverse=True))
        if counts[0] < 3:
            if jokers >= (3 - counts[0]):
                jokers -= 3 - counts[0]
            else:
                return False
        # We have a 3 of a kind and some number of jokers remaining
        if counts[1] < 2:
            assert counts[1] == 1
            if jokers >= (2 - counts[1]):
                jokers -= 2 - counts[1]
            else:
                return False
        return True

    def pairs(self):
        jokers = len(self.buckets[0])
        # If we have 2 jokers we're guaranteed 3 of a kind
        # So we only need to handle the single joker case
        pairs = []
        for i, bucket in self.buckets.items():
            if i == 0:
                continue
            if len(bucket) >= 2:
                pairs.append(bucket)
            elif jokers:
                jokers -= 1
                pairs.append(bucket)
        return pairs


def main(realdata=False, part2=False):
    if realdata:
        data = open("07.txt", "r")
    else:
        data = """32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483""".splitlines()

    hands = []
    for linenum, line in enumerate(data):
        line = line.strip()
        cards, bid = line.split()
        hand = Hand(cards, int(bid))
        hands.append(hand)

    total = 0
    for i, hand in enumerate(sorted(hands)):
        print(hand, hand.buckets, hand.rank.name, hand.bid, i+1)
        total += (i+1) * hand.bid

    print(total)




if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    main(real, part2)
