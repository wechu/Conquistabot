# As of 2015/07/11

board = {0: (1, 12, 39, 46),
         1: (0, 2, 7, 12, 13),
         2: (1, 3, 8),
         3: (2, 4, 8, 9),
         4: (3, 5, 9, 10),
         5: (4, 6, 10, 11),
         6: (5, 24, 25),
         7: (1, 8, 14),
         8: (7, 2, 3, 14),
         9: (3, 4, 10, 19, 27),
         10: (4, 5, 9, 11, 27),
         11: (5, 10, 25),
         12: (0, 1, 47),
         13: (12, 14, 1, 18),
         14: (13, 15, 7, 8),
         15: (13, 14, 18, 19, 22),
         16: (17, 19, 20),
         17: (16, 20, 23, 28),
         18: (13, 15, 21),
         19: (15, 9, 16, 22),
         20: (16, 17, 23),
         21: (18,),
         22: (19, 15),
         23: (17, 20),
         24: (6, 25, 26),
         25: (6, 11, 24, 27, 28, 29),
         26: (24, 29, 30, 31),
         27: (9, 10, 25, 28),
         28: (27, 25, 29, 33, 17),
         29: (25, 26, 28, 33, 30),
         30: (26, 29, 31, 33, 34),
         31: (26, 30, 32, 34, 35),
         32: (31, 35, 40, 41),
         33: (28, 29, 30),
         34: (30, 31, 35),
         35: (34, 31, 32, 40, 44),
         36: (37, 38),
         37: (36, 38, 39),
         38: (36, 37, 39, 41, 42),
         39: (0, 37, 43),
         40: (32, 35, 41, 44, 45),
         41: (32, 38, 40, 42, 45, 46),
         42: (38, 43, 41, 46),
         43: (39, 42),
         44: (35, 45, 47),
         45: (40, 41, 44, 46),
         46: (41, 42, 45, 0, 47),
         47: (46, 44, 12)}

city_color = {}
for i in range(0, 12):
    city_color[i] = "BLUE"
for i in range(12, 24):
    city_color[i] = "YELLOW"
for i in range(24, 36):
    city_color[i] = "BLACK"
for i in range(36, 48):
    city_color[i] = "RED"

color_order = ["BLUE", "YELLOW", "BLACK", "RED"]

class MCBoard:
    # Contains houses, cubes and adding cubes
    def __init__(self):
        self.nodes = [[False, 0] for i in range(48)]  # [house, cubes]
        self.outbreaks = 0
        # self.graph = ((1, 12, 39, 46),  # graph for possible movement locations
        #               (0, 2, 7, 12, 13),  # Note this doesn't include house travel
        #               (1, 3, 8),
        #               (2, 4, 8, 9),
        #               (3, 5, 9, 10),
        #               (4, 6, 10, 11),
        #               (5, 24, 25),
        #               (1, 8, 14),
        #               (7, 2, 3, 14),
        #               (3, 4, 10, 19, 27),
        #               (4, 5, 9, 11, 27),
        #               (5, 10, 25),
        #               (0, 1, 13, 47),
        #               (12, 14, 1, 18),
        #               (13, 15, 7, 8),
        #               (13, 14, 18, 19, 22),
        #               (17, 19, 20),
        #               (16, 20, 23, 28),
        #               (13, 15, 21),
        #               (15, 9, 16, 22),
        #               (16, 17, 23),
        #               (18,),
        #               (19, 15),
        #               (17, 20),
        #               (6, 25, 26),
        #               (6, 11, 24, 27, 28, 29),
        #               (24, 29, 30, 31),
        #               (9, 10, 25, 28),
        #               (27, 25, 29, 33, 17),
        #               (25, 26, 28, 33, 30),
        #               (26, 29, 31, 33, 34),
        #               (26, 30, 32, 34, 35),
        #               (31, 35, 40, 41),
        #               (28, 29, 30),
        #               (30, 31, 35),
        #               (34, 31, 32, 40, 44),
        #               (37, 38),
        #               (36, 38, 39),
        #               (36, 37, 39, 41, 42),
        #               (0, 37, 43),
        #               (32, 35, 41, 44, 45),
        #               (32, 38, 40, 42, 45, 46),
        #               (38, 43, 41, 46),
        #               (39, 42),
        #               (35, 45, 47),
        #               (40, 41, 44, 46),
        #               (41, 42, 45, 0, 47),
        #               (46, 44, 12))

    def adding_cubes(self, node, num):
        boom = []
        def check_cube(node):
                if self.outbreaks == 8:
                    return
                elif self.nodes[node][1] == 3:  # [1] is cubes
                    #print("Outbreak! at " + str(node))
                    self.outbreaks += 1
                    boom.append(node)

                    for b in board[node]:
                        if b not in boom:
                            # Outbreaks only spreading to cities of the same color
                            if node in range(0, 12):
                                if b in range(0, 12):
                                    check_cube(b)
                            elif node in range(12, 24):
                                if b in range(12, 24):
                                    check_cube(b)
                            elif node in range(24, 36):
                                if b in range(24, 36):
                                    check_cube(b)
                            elif node in range(36, 48):
                                if b in range(36, 48):
                                    check_cube(b)
                    boom.pop()
                else:
                    self.nodes[node][1] += 1

        for a in range(num):
            check_cube(node)

    def clone(self):
        board_clone = MCBoard()
        board_clone.nodes = [i[:] for i in self.nodes]
        board_clone.outbreaks = self.outbreaks
        #board_clone.graph = [i[:] for i in self.graph]

        return board_clone

    def startCode(self):
        """ Generates code string: outbreaks (0), houses (1-48), cubes (49-96)"""
        code_house = "".join("1" if x[0] else "0" for x in self.nodes)
        code_cubes = "".join(str(x[1]) for x in self.nodes)
        return str(self.outbreaks) + code_house + code_cubes

    def __repr__(self):
        info = "Cubes: " + str([x[1] for x in self.nodes]) + "\nHouses: " + str([x[0] for x in self.nodes])
        return info

