
import Graph
import random

#Deck and cards

#Preset values
all_events = ["Airlift", "One Quiet Night", "Forecast", "Government Grant", "Resilient Population"]

# Monte Carlo
class MCPlayerDeck():
    """ New player deck for chance nodes """
    # At the beginning of a game, create PlayerDeck, addEvents then setupDraw
    # Note there are no real epidemic 'cards' in the deck
    def __init__(self, num_epidemics=0):
        self.deck = [i for i in range(48)]
        # Useful variables
        self.discard_pile = []  # note this doesn't include cards discarded due to exceeding max hand size
        self.initial_length = len(self.deck)
        self.num_epidemics = num_epidemics
        self.epidemic_counter = 0  # this is how many cards have passed since last epidemic (can be negative)

    def addEvents(self, num_events):
        temp_events = all_events[:]
        random.shuffle(temp_events)
        for i in range(num_events):
            self.deck.append(temp_events.pop())

        random.shuffle(self.deck)
        #update initial length
        self.initial_length = len(self.deck)

    def getDraw(self, num_cards):
        """ Generates cards drawn from the player deck (used in GetActions)"""
        drawn_cards = []
        current_counter = self.epidemic_counter # have to create a dummy var so the probs are calculated correctly

        for i in range(num_cards):
            # Check if an epidemic occurs
            if random.random() <= self.epidemicProb():
                drawn_cards.append("Epidemic")
                self.epidemic_counter -= ((self.initial_length // self.num_epidemics) + 1)
            else:
                one_card = random.choice(self.deck)
                drawn_cards.append(one_card)
            self.epidemic_counter += 1

        self.epidemic_counter = current_counter

        return set(drawn_cards)  # use a set since draws are unordered

    def doDraw(self, draws_action, player):
        """ Draws cards for a player (used in doAction) """
        for card in draws_action[0]:
            if card == "Epidemic":
                self.epidemic_counter -= ((self.initial_length // self.num_epidemics) + 1)
            else:
                player.cards.append(card)
                self.deck.remove(card)
            self.epidemic_counter += 1

        # Discards
        for discard in draws_action[1]:
            player.cards.remove(discard)

    def setupDraw(self, player, num_cards):
        """ Use this to draw the initial cards (can't draw epidemics) """
        drawn_cards = []
        for i in range(num_cards):
            card = random.choice(self.deck)
            self.deck.remove(card)
            drawn_cards.append(card)
            self.initial_length -= 1  # this is needed for correctly calculating epidemic probs

        player.cards.extend(drawn_cards)

        return drawn_cards

    def epidemicProb(self):
        if self.epidemic_counter < 0:
            return 0  # the last epidemic was recent enough
        else:
            return 1 / ((self.initial_length // self.num_epidemics) + 1 - self.epidemic_counter)

    def clone(self):

        p_deck_clone = MCPlayerDeck()
        p_deck_clone.deck = self.deck[:]
        p_deck_clone.discard_pile = self.discard_pile[:]
        p_deck_clone.initial_length = self.initial_length
        p_deck_clone.num_epidemics = self.num_epidemics
        p_deck_clone.epidemic_counter = self.epidemic_counter

        return p_deck_clone

    def startCode(self):
        """ Generates code string: length (0-1), epis in deck (3), counter (4-5), deck (6-85)"""
        code_deck = "".join(str(x).zfill(2) for x in self.deck)  # assumed to be 40 cards in the deck
        code = str(self.initial_length) + str(self.num_epidemics) + str(self.epidemic_counter).zfill(2)
        return code + code_deck

    def __repr__(self):
        info = "Deck: " + str(self.deck)
        return info

class MCInfectionDeck():
    """ New infection deck for chance nodes """
    def __init__(self):
        self.deck = list(range(48))  # mystery deck: only contains cards that are in the deck and not in memory lists
        # Useful variables
        self.infect_rates = (2, 2, 2, 3, 3, 4, 4)
        self.epidemics = 0
        self.discard_pile = []
        self.memory_lists = []  # Note the most recent memory list is the last one

    def setupInfect(self, num_infections, num_cubes, board):
        """ This is the general version used for setup """
        drawn_cards = []
        for i in range(num_infections):
            if self.memory_lists:
                one_card = random.choice(self.memory_lists[-1])
                self.memory_lists[-1].remove(one_card)
                self.cleanMemory()

                drawn_cards.append(one_card)
            else:
                one_card = random.choice(self.deck)
                self.deck.remove(one_card)

                drawn_cards.append(one_card)
            # add cubes on board
            board.adding_cubes(one_card, num_cubes)
            self.discard_pile.append(one_card)

        return drawn_cards

    def getInfect(self):
        """ Generates cards drawn from the infection deck (used in GetActions) """
        drawn_cards = []
        memory_clone = [i[:] for i in self.memory_lists]  # don't modify the original decks
        deck_clone = self.deck[:]
        for i in range(self.infect_rates[self.epidemics]):
            if memory_clone:
                one_card = random.choice(memory_clone[-1])
                memory_clone[-1].remove(one_card)
                # Clean memory
                memory_clone = [x for x in memory_clone if x != []]

                drawn_cards.append(one_card)
            else:
                one_card = random.choice(deck_clone)
                deck_clone.remove(one_card)

                drawn_cards.append(one_card)
        
        
        
        return set(drawn_cards)  # return a set since draws are unordered

    def doInfect(self, infects_action, board):
        """ Infects the board (used in doAction) """
        for card in infects_action:
            # draw from the deck
            if self.memory_lists:
                for lst in self.memory_lists:
                    if card in lst:
                        lst.remove(card)
                        break
                else:  # card is not in memory lists
                    self.deck.remove(card)
                # Clean memory
                self.memory_lists = [x for x in self.memory_lists if x != []]
            else:
                self.deck.remove(card)
            self.discard_pile.append(card)

            # Add cubes
            board.adding_cubes(card, 1)

    def getEpidemic(self):
        """ Used in getActions """
        epidemic_card = random.choice(self.deck)  # random card not in memory lists

        return epidemic_card

    def doEpidemic(self, epidemic_card, board):
        """ Used in doAction """
        try:
            self.deck.remove(epidemic_card)
        except ValueError:
            print(epidemic_card)
            print(self.deck)
            raise SystemExit
        self.discard_pile.append(epidemic_card)

        # add cubes on map
        board.adding_cubes(epidemic_card, 3)

        # increase epidemic counter
        self.epidemics += 1

        # memorize discard pile
        self.memory_lists.append(self.discard_pile)
        self.discard_pile = []

    def cleanMemory(self):
        """ Deletes a blank list from the memory_lists """
        if self.memory_lists:
            self.memory_lists = [x for x in self.memory_lists if x != []]

    def clone(self):
        i_deck_clone = MCInfectionDeck()
        i_deck_clone.deck = self.deck[:]
        i_deck_clone.epidemics = self.epidemics
        i_deck_clone.discard_pile = self.discard_pile[:]
        i_deck_clone.memory_lists = [i[:] for i in self.memory_lists]

        return i_deck_clone

    def startCode(self):
        """ Generates code string: epis occured (0), deck (1-78), discards (79-96)"""
        code_deck = "".join(str(x).zfill(2) for x in self.deck)
        code_discards = "".join(str(x).zfill(2) for x in self.discard_pile)
        # deck and discards lengths are assumed to be for the start
        # memory_lists aren't transformed

        return str(self.epidemics) + code_deck + code_discards

    def __repr__(self):
        info = "Discards: " + str(self.discard_pile) + "\nMemory: " + str(self.memory_lists) \
               + "\nDeck: " + str(self.deck)
        return info