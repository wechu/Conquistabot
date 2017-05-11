# As of 2015/07/11

import Graph

import random

#All the player related things

class MCPlayer:
    cures = [False, False, False, False]  # [Blue, Yellow, Black, Red]
    def __init__(self, special=None):
        self.location = 7  # defaults at beginning of game
        self.cards = []
        self.special = special

    def checkHandSize(self):
        while len(self.cards) > 7:
            junk_card = self.cards[0]  # Discards first card every time (which should be random)
            self.cards.remove(junk_card)

    def getDiscards(self, drawn_cards=None):
        potential_cards = self.cards[:]
        if drawn_cards is not None:
            cards = [x for x in drawn_cards if x != "Epidemic"]
            potential_cards.extend(cards)

        discards = []
        while len(potential_cards) > 7:
            #one_card = random.choice(potential_cards)

            #Discards one card from the color that you have the least of in your hand
            hand = [(i, Graph.city_color[i]) for i in potential_cards]
            hand_colors = [x[1] for x in hand]
            colors = ["BLUE", "YELLOW", "BLACK", "RED"]

            if any(self.cures):  # picks from colors you have cures of
                cure_colors = []
                if self.cures[0]:
                    cure_colors.append("BLUE")
                if self.cures[1]:
                    cure_colors.append("YELLOW")
                if self.cures[2]:
                    cure_colors.append("BLACK")
                if self.cures[3]:
                    cure_colors.append("RED")

                cure_color_hand = []
                for color in cure_colors:
                    for card in hand:
                        if card[1] == color:
                            cure_color_hand.append(card[0])

                if cure_color_hand:
                    one_card = random.choice(cure_color_hand)
                else:
                    random.shuffle(colors)  # no priority in the case of a tie
                    color_counts = [hand_colors.count(x) for x in colors]

                    least_color_index = color_counts.index(min(count for count in color_counts if count > 0))
                    least_color_hand = [i[0] for i in hand if i[1] == colors[least_color_index]]

                    one_card = random.choice(least_color_hand)

            else:
                random.shuffle(colors)  # no priority in the case of a tie
                color_counts = [hand_colors.count(x) for x in colors]

                least_color_index = color_counts.index(min(count for count in color_counts if count > 0))
                least_color_hand = [i[0] for i in hand if i[1] == colors[least_color_index]]

                one_card = random.choice(least_color_hand)

            potential_cards.remove(one_card)
            discards.append(one_card)

        return set(discards)

    def clone(self):
        player_clone = MCPlayer()
        player_clone.location = self.location
        player_clone.cards = self.cards[:]
        player_clone.special = self.special
        player_clone.cures = self.cures[:]

        return player_clone

    def startCode(self):
        """ Generates code string: cures (0-3), location (4), cards (5-18) (note no discard pile)"""
        code_cures = "".join("1" if x else "0" for x in self.cures)

        cards = self.cards[:]
        while len(cards) < 7:
            cards.append(-1)
        code_cards = "".join(str(x).zfill(2) for x in cards)

        return code_cures + str(self.location) + code_cards

    def __repr__(self):
        info = "Location: " + str(self.location) + "\nCards: " + str(self.cards)  # +"\nCharacter: " + str(self.special)
        return info


