from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List
import functools
import itertools
import json
import re
import sys

ranking = list(reversed("AKQJT98765432"))

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
        for bucket in self.buckets.values():
            if len(bucket) == count:
                return bucket
        return None

    def is_fullhouse(self):
        three = None
        two = None
        for bucket in self.buckets.values():
            if len(bucket) == 3:
                three = bucket
            elif len(bucket) == 2:
                two = bucket
        if three and two:
            return three, two

    def pairs(self):
        pairs = []
        for bucket in self.buckets.values():
            if len(bucket) == 2:
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
        #print(hand, hand.buckets, hand.rank.name, hand.bid, i+1)
        total += (i+1) * hand.bid

    print(total)




if __name__ == '__main__':
    lower_args = [i.strip().lower() for i in sys.argv[1:]]
    real = "real" in lower_args
    part2 = "part2" in lower_args
    main(real, part2)
