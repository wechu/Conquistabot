import BoardState
from MonteCarloTreeSearch import UCT
import time

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

y = BoardState.BoardState()
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