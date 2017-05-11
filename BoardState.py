# As of 2015/07/11

import Graph
import Player
import Deck

import numpy as np
import random
from math import *

import time

class BoardState():
    def __init__(self, board=None, players=None, player_deck=None, infect_deck=None):
        self.playerTurn = 1  # current player's turn
        self.actionsDone = 0  # number of action in current player's turn
        self.drawStep = False  # False if player is doing actions, True if player is drawing cards
        self.board = board  # nodes is for houses and cubes
        self.all_players = players  # [player1, player2] | cards in hand, locations
        self.p_deck = player_deck  # cards and epidemics
        self.i_deck = infect_deck  # memory lists
        self.ending = 2  # =1 when win, =0 when lose , =2 when game is ongoing
        # Note outbreaks are in MCBoard and cures are in MCPlayer (in the first player)

        # Improvements
        self.last_action = None  # keep track of last action/location to pick better actions next
        self.last_location = None

        # Stats
        self.playerMoves = [0, 0, 0, 0, 0, 0, 0, 0]  # In this order M1 | M2 | F1 | F2 | H | T | C | R
        # Note only the moves played onwards from the state are counted

    def setup(self, start_code=None):
        """ Initializes all the parameters. Also, places initial cubes and draws initial cards. """
        self.board = Graph.MCBoard()
        self.all_players = [Player.MCPlayer(), Player.MCPlayer()]
        self.p_deck = Deck.MCPlayerDeck(4)  # 4 epidemics
        self.i_deck = Deck.MCInfectionDeck()

        # Reset to beginning
        self.ending = 2
        self.playerTurn = 1
        self.actionsDone = 0
        self.drawStep = False
        self.all_players[0].cures = [False, False, False, False]
        self.last_action = None
        self.last_location = None
        self.playerMoves = [0, 0, 0, 0, 0, 0, 0, 0]

        # Random start
        if start_code is None:
            # Put a house on your starting location
            self.board.nodes[7][0] = True

            # Add event cards (none for now)
            # Draw starting hand
            for player in self.all_players:
                self.p_deck.setupDraw(player, 4)

            # Infect initial cities
            for num_cubes in range(1, 4):
                self.i_deck.setupInfect(3, num_cubes, self.board)

        # Start code is a string
        # Where to find each piece of info about the board state:
        # Board: outbreaks (0), houses (1-48), cubes (49-96)
        # Player 1: cures (97-100), location (101), cards (102-115)
        # Player 2: cures (116-119), location (120), cards (121-134)
        # Player deck: length (135-136), epis in deck (138), counter (139-140), deck (141-220)
        # Infection deck: epis occurred (221), deck (222-299), discards (300-316)

        # Use the start code to initialize the board in a certain configuration
        else:
            # Board
            self.board.outbreaks = int(start_code[0])
            for i in range(48):
                self.board.nodes[i][0] = bool(int(start_code[i+1]))
                self.board.nodes[i][1] = int(start_code[i+49])

            # Player 1
            for i in range(4):  # only need to initialize cures once
                self.all_players[0].cures[i] = bool(int(start_code[i+97]))
            self.all_players[0].location = int(start_code[101])
            self.all_players[0].cards = [int(start_code[j:j+2]) for j in range(102, 116, 2) if start_code[j:j+2]!="-1"]
            # Player 2
            self.all_players[1].location = int(start_code[120])
            self.all_players[1].cards = [int(start_code[j:j+2]) for j in range(121, 135, 2) if start_code[j:j+2]!="-1"]

            # Player deck
            self.p_deck.initial_length = int(start_code[135:137])
            self.p_deck.num_epidemics = int(start_code[137])
            self.p_deck.epidemic_counter = int(start_code[138:140])  # should be 0, doesn't work for neg values
            self.p_deck.deck = [int(start_code[j:j+2]) for j in range(140, 219, 2)]

            # Infection deck
            self.i_deck.epidemics = int(start_code[220])
            self.i_deck.deck = [int(start_code[j:j+2]) for j in range(221, 298, 2)]
            self.i_deck.discard_pile = [int(start_code[j:j+2]) for j in range(299, 317, 2)]

            #print("Does the code match?" + str(start_code == self.startCode()))

        if start_code is None:
            print("Random start with: " + self.startCode())
        else:
            print("Initialized with:\n" + start_code)

        return

    def clone(self):
        # Make a deep copy of the state
        clone_players = [self.all_players[0].clone(), self.all_players[1].clone()]
        clone_state = BoardState(self.board.clone(), clone_players, self.p_deck.clone(), self.i_deck.clone())
        clone_state.playerTurn = self.playerTurn
        clone_state.actionsDone = self.actionsDone
        clone_state.drawStep = self.drawStep
        clone_state.ending = self.ending
        clone_state.last_action = self.last_action
        clone_state.last_location = self.last_location

        return clone_state

    def getActions(self):
        """ Gets all actions possible from the current state"""
        action_list = []
        player = self.all_players[self.playerTurn - 1]

        if not self.drawStep:
            # Generates a list of all possible actions for a player
            # M is move, F is fly, H is house, C is cure and R is research
            # Trade to be done later

            # Movement actions
            # Walk
            for node in Graph.board[player.location]:
                action_list.append("M1 {0}".format(node))

            moves = list(Graph.board[player.location])  # contains locations you don't want to fly/house travel to
            moves.append(player.location)  # can't move to current location

            # House Travel
            if self.board.nodes[player.location][0]:
                for i in range(0, 48):
                    if self.board.nodes[i][0] and i not in moves:
                        action_list.append("M2 {0}".format(i))
                        moves.append(i)  # don't want to fly to places you can house travel to

            #Fly from (F1)
            if player.location in player.cards:
                for i in range(0, 48):
                    if i not in moves:
                        if self.board.nodes[i][1] > 1:  # can you C? scotch-tape fix (edit: not sure what was wrong)
                            action_list.append("F1 {0}".format(i))
                        elif i in player.cards and not self.board.nodes[i][0]:  # can you H?
                                # or \
                                # self.all_players[2 - self.playerTurn].location == i:
                            # check if you can C, H or T (TBD)
                            # check for R (TBD?)
                            action_list.append("F1 {0}".format(i))

            #Fly to (F2)
            for fly_location in player.cards:
                if fly_location not in moves:
                    action_list.append("F2 {0}".format(fly_location))

            # Immobile actions
            # Build house
            if player.location in player.cards and not self.board.nodes[player.location][0]:
                action_list.append("H {0}".format(player.location))

            # Trade
            if self.all_players[2 - self.playerTurn].location == player.location:
                if player.location in player.cards:
                    action_list.append("T {0}".format(player.location))

            # Cure cube
            if self.board.nodes[player.location][1] >= 1:
                action_list.append("C")

            # Find cure
            if self.board.nodes[player.location][0]:
                hand_colors = [Graph.city_color[i] for i in player.cards]
                colors = ["BLUE", "YELLOW", "BLACK", "RED"]
                for color in colors:
                    if hand_colors.count(color) >= 5:
                        if ((color == "BLUE" and not self.all_players[0].cures[0])
                           or (color == "YELLOW" and not self.all_players[0].cures[1])
                           or (color == "BLACK" and not self.all_players[0].cures[2])
                           or (color == "RED" and not self.all_players[0].cures[3])):
                            action_list.append("R {0}".format(color))

            # Action filtering
            if self.last_action is None:
                return action_list

            bad_list = []

            # Can't house travel after house traveling
            if self.last_action[0:2] == "M2":
                for act in action_list:
                    if act[0:2] == "M2":
                        bad_list.append(act)

            # Can't do a movement action after F1
            elif self.last_action[0:2] == "F1":
                for act in action_list:
                    if act[0] == "M" or act[0] == "F":
                        bad_list.append(act)

            # Can't do F2 after a movement action
            if self.last_action[0] == "M" or self.last_action[0] == "F":
                for act in action_list:
                    if act[0:2] == "F2":
                        bad_list.append(act)

            # Filter out moves in bad_list
            action_list = [x for x in action_list if x not in bad_list]

            # Remove movements to previous location
            if self.last_action[0] == "M" or self.last_action[0] == "F":
                moving_back = ["M1 {0}".format(self.last_location), "M2 {0}".format(self.last_location),
                               "F1 {0}".format(self.last_location), "F2 {0}".format(self.last_location)]
                action_list = [x for x in action_list if x not in moving_back]

                if self.last_location == 18 and player.location == 21:  # don't get stuck at santiago
                    action_list.append("M1 18")

        # Possible draws for draw step
        elif self.drawStep:
            # Drawing from the player deck
            for i in range(5):  # Number of sample draws can be changed

                p_temp_draws = self.p_deck.getDraw(2)
                discards = {}
                if len(player.cards) > 5:  # checks for discards
                    discards = player.getDiscards(p_temp_draws)

                p_draws = (p_temp_draws, discards)

            # Drawing an epidemic card
                if "Epidemic" in p_draws[0]:
                    epi_draw = self.i_deck.getEpidemic()
                else:
                    epi_draw = -1

            # Drawing from the infection deck
                if epi_draw != -1:
                    self.i_deck.epidemics += 1  # Adjust the epidemic counter before infecting

                i_draws = self.i_deck.getInfect()

                if epi_draw != -1:
                    self.i_deck.epidemics -= 1

            # Put all the draws together
                all_draws = (p_draws, epi_draw, i_draws)
                if all_draws not in action_list:
                    action_list.append(all_draws)

        return action_list

    def doAction(self, action):
        """ Do an action """
        player = self.all_players[self.playerTurn - 1]

        if self.drawStep == 0:
            # Save current location and action done
            if self.actionsDone < 3:
                self.last_action = action
                self.last_location = player.location
            else:
                self.last_action = None
                self.last_location = None

            # Walk
            if action[0:2] == "M1":
                node = int(action[3:])
                player.location = node
                # Stats
                self.playerMoves[0] += 1
            # House travel
            elif action[0:2] == "M2":
                node = int(action[3:])
                player.location = node
                # Stats
                self.playerMoves[1] += 1

            # Fly
            elif action[0:2] == "F1":  # using current city card
                node = int(action[3:])

                self.p_deck.discard_pile.append((player.location, player.cards.index(player.location)))
                player.cards.remove(player.location)

                player.location = node

                # Stats
                self.playerMoves[2] += 1

            elif action[0:2] == "F2":  # using destination city card
                node = int(action[3:])
                try:
                    self.p_deck.discard_pile.append((node, player.cards.index(node)))
                except ValueError:
                    print(self.p_deck.discard_pile)
                    print(player.cards)
                player.cards.remove(node)

                player.location = node

                # Stats
                self.playerMoves[3] += 1

            # Build house
            elif action[0] == "H":
                self.board.nodes[player.location][0] = True

                self.p_deck.discard_pile.append((player.location, player.cards.index(player.location)))
                player.cards.remove(player.location)

                # Stats
                self.playerMoves[4] += 1

            # Trade
            elif action[0] == "T":
                player.cards.remove(player.location)
                self.all_players[2 - self.playerTurn].cards.append(player.location)

                # Stats
                self.playerMoves[5] += 1

            # Cure
            elif action[0] == "C":
                if Graph.city_color[player.location] == "BLUE" and self.all_players[0].cures[0]:
                    self.board.nodes[player.location][1] = 0
                elif Graph.city_color[player.location] == "YELLOW" and self.all_players[0].cures[1]:
                    self.board.nodes[player.location][1] = 0
                elif Graph.city_color[player.location] == "BLACK" and self.all_players[0].cures[2]:
                    self.board.nodes[player.location][1] = 0
                elif Graph.city_color[player.location] == "RED" and self.all_players[0].cures[3]:
                    self.board.nodes[player.location][1] = 0
                else:
                    self.board.nodes[player.location][1] -= 1
                # Stats
                self.playerMoves[6] += 1

            # Research
            elif action[0] == "R":
                color = action[2:]

                color_hand = []

                if color == "BLUE":
                    self.all_players[0].cures[0] = True
                    for card in player.cards:
                        if card in range(0, 12):
                            color_hand.append(card)

                elif color == "YELLOW":
                    self.all_players[0].cures[1] = True
                    for card in player.cards:
                        if card in range(12, 24):
                            color_hand.append(card)

                elif color == "BLACK":
                    self.all_players[0].cures[2] = True
                    for card in player.cards:
                        if card in range(24, 36):
                            color_hand.append(card)

                elif color == "RED":
                    self.all_players[0].cures[3] = True
                    for card in player.cards:
                        if card in range(36, 48):
                            color_hand.append(card)

                for i in range(5):
                        random_card = color_hand[0]
                        self.p_deck.discard_pile.append((random_card, player.cards.index(random_card)))
                        player.cards.remove(random_card)
                        color_hand.remove(random_card)

                # Stats
                self.playerMoves[7] += 1

            # Update the number of actions done
            self.actionsDone += 1
            if self.actionsDone == 4:
                self.drawStep = True

        # Draw/infect phase
        elif self.drawStep:
            # Draw from player deck
            self.p_deck.doDraw(action[0], player)

            # Epidemic! (if applicable)
            if action[1] != -1:  # checks if epidemic occurred
                self.i_deck.doEpidemic(action[1], self.board)

            # Win if there are not enough cards in i_deck
            if len(self.i_deck.deck) < self.i_deck.infect_rates[self.i_deck.epidemics]:
                self.ending = 1
                return

            # Draw infections
            self.i_deck.doInfect(action[2], self.board)

            # Checking for terminal position
            if self.all_players[0].cures == [True, True, True, True]:
                self.ending = 1
                return

            # Easy mode (need one cure)
            # if (self.all_players[0].cures[0] or self.all_players[0].cures[1] or
            #     self.all_players[0].cures[2] or self.all_players[0].cures[3]):
            #     self.ending = 1
            #     return

            elif self.board.outbreaks >= 8:
                self.ending = 0
                return

            elif not self.p_deck.deck:
                self.ending = 0
                return

            # Next player's turn
            self.playerTurn = 3 - self.playerTurn
            self.actionsDone = 0
            self.drawStep = False

        return action

    def undoAction(self, action):
        """ Used for getTurns. Note, to undo an action, you also have to change last location/action separately """
        player = self.all_players[self.playerTurn - 1]

        if action[0] == "F":
            card = self.p_deck.discard_pile.pop()  # card is a tuple (node, index)
            player.cards.insert(card[1], card[0])  # preserves the previous order of the cards

        elif action[0] == "H":
            self.board.nodes[player.location][0] = False
            card = self.p_deck.discard_pile.pop()
            player.cards.insert(card[1], card[0])

        elif action[0] == "T":
            player.cards.append(player.location)
            self.all_players[2 - self.playerTurn].cards.remove(player.location)

        elif action[0] == "C":
            self.board.nodes[player.location][1] += 1
            # This isn't an accurate 'undo' if you have the cure
            # but it doesn't matter since we are just checking possible moves

        elif action[0] == "R":
            if action[2:] == "BLUE":
                self.all_players[0].cures[0] = False
            elif action[2:] == "YELLOW":
                self.all_players[0].cures[1] = False
            elif action[2:] == "BLACK":
                self.all_players[0].cures[2] = False
            elif action[2:] == "RED":
                self.all_players[0].cures[3] = False

            for i in range(5):
                card = self.p_deck.discard_pile.pop()
                player.cards.insert(card[1], card[0])

        self.actionsDone -= 1

        return action

    def getTurns(self):
        """ Generates all possible sequences of four actions for a turn """

        #First check if it is draw phase
        if self.drawStep:
            return self.getActions()

        turn_list = []  # list of all possible turns

        past_locations = []  # stores locations temporarily
        turn = []  # stores actions temporarily

        clone = self.clone()
        player = clone.all_players[clone.playerTurn - 1]

        past_locations.append(player.location)
        for act1 in clone.getActions():
            clone.doAction(act1)
            turn.append(act1)

            past_locations.append(player.location)
            for act2 in clone.getActions():
                clone.doAction(act2)
                turn.append(act2)

                past_locations.append(player.location)
                for act3 in clone.getActions():
                    clone.doAction(act3)
                    turn.append(act3)

                    for act4 in clone.getActions():
                        turn.append(act4)
                        turn_list.append(turn[:])  # Add one possible turn

                        turn.pop()

                    clone.undoAction(turn.pop())  # Goes back to choose a different 3rd action
                    player.location = past_locations[2]
                    clone.last_action = turn[1]

                clone.undoAction(turn.pop())
                player.location = past_locations[1]
                past_locations.pop()
                clone.last_action = turn[0]

            clone.undoAction(turn.pop())
            player.location = past_locations[0]
            past_locations.pop()
            clone.last_action = None

        # Filter out turns that consist of just movement actions
        turn_list = [x for x in turn_list if not ((x[0][0] == 'M' or x[0][0] == 'F')
                                                and (x[1][0] == 'M' or x[1][0] == 'F')
                                                and (x[2][0] == 'M' or x[2][0] == 'F')
                                                and (x[3][0] == 'M' or x[3][0] == 'F'))]

        return turn_list

    def doTurn(self, actions):
        """ Does 4 consecutive actions """
        if self.drawStep:
            self.doAction(actions)  # drawing cards
        else:
            for i in range(4):
                self.doAction(actions[i])

        return actions

    def getRandomAction(self):
        """ Generates next action to take in simulation phase """
        action_list = self.getActions()

        player = self.all_players[self.playerTurn - 1]

        # Bonuses to some actions
        if not self.drawStep:
        # Finding cure bonus (it's always picked if available)
            for act in action_list:
                if act[0] == "R":
                    return act

        random_act = random.choice(action_list)

        return random_act

    def showTurn(self):
        print("Player:", self.playerTurn, "Acts:", self.actionsDone, "Draw:", self.drawStep)

    def showStats(self):
        print("M1:", self.playerMoves[0])
        print("M2:", self.playerMoves[1])
        print("F1:", self.playerMoves[2])
        print("F2:", self.playerMoves[3])
        print("H:", self.playerMoves[4])
        print("T:", self.playerMoves[5])
        print("C:", self.playerMoves[6])
        print("R:", self.playerMoves[7])

    def startCode(self):
        """ Generates a string encoding all information about the current board state """
        # Board: outbreaks (0), houses (1-48), cubes (49-96)
        code_board = self.board.startCode()
        # Player 1: cures (97-100), location (101), cards (102-115)
        code_p1 = self.all_players[0].startCode()
        # Player 2: cures (116-119), location (120), cards (121-134)
        code_p2 = self.all_players[1].startCode()
        # Player deck: length (135-136), epis in deck (138), counter (139-140), deck (141-220)
        code_p_deck = self.p_deck.startCode()
        # Infection deck: epis occurred (221), deck (222-299), discards (300-317)
        code_i_deck = self.i_deck.startCode()

        return code_board + code_p1 + code_p2 + code_p_deck + code_i_deck

class TreeNode:
    def __init__(self, state, action=None, parent=None, chance_node=False):
        self.rewards = 0
        self.visits = 0
        self.action = action  # action that led to the state
        self.parent = parent
        self.children = []
        self.untriedActions = state.getTurns()
        self.chance = chance_node

    def selectChild(self):
        """Use UCB1 formula to select best child. Note there is a constant to be tuned."""
        if self.chance:
            picked_node = random.choice(self.children)
        else:
            picked_node = sorted(self.children, key=lambda child: child.rewards/child.visits
                                 + sqrt(0.01*log(self.visits/child.visits)))[-1]
        return picked_node

    def addChild(self, action, state):
        """Creates a new child node and updates the untried moves list"""
        if not state.drawStep:
            new_node = TreeNode(state, action, self, False)
        else:
            new_node = TreeNode(state, action, self, True)

        self.untriedActions.remove(action)
        self.children.append(new_node)
        return new_node

    def update(self, result):
        self.visits += 1
        self.rewards += result

    def __repr__(self):
        return "[M:" + str(self.action) + " R/V:" + str(round(self.rewards, 3)) + "/" + str(round(self.visits, 3)) + \
               " C:" + str(self.chance) + "]"
               #+ " U:" + str(self.untriedActions)+ "]"

    def treeToString(self, indent):
        s = self.indentString(indent) + str(self)
        for child in self.children:
            s += child.treeToString(indent+1)
        return s

    def indentString(self, indent):
        s = "\n"
        for i in range(1, indent+1):
            s += "| "
        return s

    def childrenToString(self):
        s = ""
        for child in self.children:
            s += str(child) + "\n"
        return s

def UCT(root_state, itermax):
    """ Returns best move from root_state """
    root_node = TreeNode(root_state)

    for i in range(itermax):
        # Skip UCT for chance nodes
        if root_state.drawStep:
            break

        # Run UCT
        node = root_node
        state = root_state.clone()

        # Selection
        while node.untriedActions == [] and node.children != []:  # node is fully expanded
            node = node.selectChild()
            state.doTurn(node.action)

        # Expansion
        if state.ending == 2:  # check if state is non-terminal
            act = random.choice(node.untriedActions)
            state.doTurn(act)
            node = node.addChild(act, state)

        # Simulation
        while state.ending == 2:  # check if state is non-terminal
            state.doAction(state.getRandomAction())

        # Backpropagation
        while node is not None:  # backpropagate to root node
            if state.ending == 1:
                node.update(state.ending)  # state is terminal so update each result (could use state.getResult())
            else:
                score = 0
                # for move in state.playerMoves:
                #     score -= move * 0.0005

                score += state.playerMoves[7] * 0.25
                if score >= 1:
                    score = 1

                node.update(score)
            node = node.parent

    #print(root_node.treeToString(0))
    print("Overall: ", repr(root_node))
    if root_state.drawStep:
        print(root_node.untriedActions)
    else:
        print(sorted(root_node.children,
                                key=lambda child: child.visits)[-1])
        #print(sorted(root_node.children,
        #                        key=lambda child: child.visits))

    print("-------- TURN END --------")


    if root_state.drawStep:
        result = random.choice(root_node.untriedActions)
    else:
        result = sorted(root_node.children, key=lambda child: child.visits)[-1].action

    print("Action taken: " + str(result))
    return result

def playGames(board_state, num_games, num_iterations, start_code=None):

    start_time = time.clock()
    total_actions = 0
    stats = board_state.playerMoves[:]
    gametimes = []


    for i in range(num_games):
        board_state.setup(start_code)
        print("--- Game {0} ---".format(i+1))

        time1 = time.clock()

        while y.ending == 2:
            y.doTurn(UCT(board_state, num_iterations))

        num_actions = 0
        for act in y.playerMoves:
            num_actions += act
        print("Acts:", num_actions)
        y.showStats()


        time2 = time.clock()
        print("Time: {0}".format(time2 - time1))
        gametimes.append(time2 - time1)

        for j in range(len(y.playerMoves)):
            stats[j] += y.playerMoves[j]
        total_actions += num_actions
        print("GAME OVER", y.ending)

    print("-----------------------")
    print("Avg Times:", sum(gametimes) / len(gametimes))
    print("All Times:", str(gametimes))

    print("Total Acts:", total_actions)
    board_state.playerMoves = stats[:]
    board_state.showStats()

    print("Avg Acts:", total_actions / num_games)
    stats = [x / num_games for x in stats]
    board_state.playerMoves = stats[:]
    board_state.showStats()


    print("--- {0} seconds ---".format(time.clock() - start_time))

#Testing

import cProfile

y = BoardState()
#y.setup()



# print(y.startCode())
# print(y.all_players[0])
# print(y.all_players[1])
# print(y.board)
# print(y.p_deck)
# print(y.i_deck)

playGames(y, 3, 5000,"00000000100000000000000000000000000000000000000002003000200001210000000033000000000"
                    "010000000000000000737021334-1-1-10000728302716-1-1-14040000010304050607080910111214"
                    "15171819202122232425262931323335363839404142434445464700102040506080910111516171819"
                    "20212225262728293031323334363738394041424344454647141235000713032423")

# x1 = y.all_players[0]
# x2 = y.all_players[1]

# start_time = time.clock()
# print(UCT(y, 1000))
#
# print("--- {0} seconds ---".format(time.clock() - start_time))

#cProfile.run('UCT(y, 1)')

#print(y.summary_dict)