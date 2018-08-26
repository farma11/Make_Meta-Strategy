import importlib
import mainSimulator
from classes import absNegoRule

class SelectStrategyGame:
    def __init__(self, agent_pathes, agent_module_names, agent_names, domain_path, pref_pathes):
        self.__agent_pathes = agent_pathes
        self.__agent_module_names = agent_module_names
        self.__agent_names = agent_names
        self.__domain_path = domain_path
        self.__pref_pathes = pref_pathes
        self.__games = self.__makeBilateralNegoGame()

    def __makeBilateralNegoGame(self):
        games = []
        for i in range(len(self.__agent_pathes)):
            temp_game = []
            for j in range(len(self.__agent_pathes)):
                simulator = mainSimulator.MainSimulator(
                        absNegoRule.DeadlineType.Round, 180, self.__domain_path, self.__pref_pathes
                    )
                module = importlib.import_module(self.__agent_pathes[i])
                simulator.set_agent(module, self.__agent_module_names[i], self.__agent_names[i] + "1")
                module = importlib.import_module(self.__agent_pathes[j])
                simulator.set_agent(module, self.__agent_module_names[j], self.__agent_names[j] + "2")
                temp_game.append(simulator)
            games.append(temp_game)
        return games

    def playGames(self):
        for i in range(len(self.__agent_pathes)):
            for j in range(len(self.__agent_pathes)):
                self.__games[i][j].do_negotiation(is_printing=False)
        return

    def getPayoffMatrix(self, game_index):
        payoffMatrix = []
        for i in range(len(self.__agent_pathes)):
            temp_payoffMatric = []
            for j in range(len(self.__agent_pathes)):
                temp_payoffMatric.append([
                    self.__games[i][j].get_end_utility_list()[game_index][self.__agent_names[i] + "1"],
                    self.__games[i][j].get_end_utility_list()[game_index][self.__agent_names[j] + "2"]
                ])
            payoffMatrix.append(temp_payoffMatric)
        return payoffMatrix

    def getNashEquilibrium(self, matrix):
        isNashEquilibrium = []
        for i in range(len(matrix)):
            isNashEquilibrium.append([])
            max_indexes = []
            max_value = 0
            for j in range(len(matrix[i])):
                isNashEquilibrium[i].append(False)
                if (abs(matrix[i][j][1] - max_value) < 1e-7):
                    max_indexes.append(j)
                    # print("1", max_indexes, max_value)
                elif (matrix[i][j][1] - max_value > 0):
                    max_indexes = [j]
                    max_value = matrix[i][j][1]
                    # print("2", max_indexes, max_value)
                # else: print("3")
            for max_index in max_indexes:
                isNashEquilibrium[i][max_index] = True
        # print(isNashEquilibrium)
        for i in range(len(matrix[0])):
            max_indexes = []
            max_value = 0
            for j in range(len(matrix)):
                if (abs(matrix[j][i][0] - max_value) < 1e-7):
                    max_indexes.append(j)
                    # print("1", max_indexes, max_value)
                elif (matrix[j][i][0] - max_value > 0):
                    max_indexes = [j]
                    max_value = matrix[j][i][0]
                    # print("2", max_indexes, max_value)
                # else: print("3")
            for j in range(len(matrix)):
                if j in max_indexes:
                    isNashEquilibrium[j][i] &= True
                else:
                    isNashEquilibrium[j][i] = False
        # print(isNashEquilibrium)
        return isNashEquilibrium

        


    def getPayoffMatric_csv(self, matrix):
        matric_csv = "\t "
        for agent_name in self.__agent_names:
            matric_csv += agent_name + "\t "
        matric_csv += "\n"

        for i in range(len(self.__agent_pathes)):
            matric_csv += self.__agent_names[i] + "\t "
            for j in range(len(self.__agent_pathes)):
                matric_csv += str(matrix[i][j]) + "\t "
            matric_csv += "\n"
        return matric_csv

    def getGames(self):
        return self.__games



