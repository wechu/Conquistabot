import random
from math import *

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


