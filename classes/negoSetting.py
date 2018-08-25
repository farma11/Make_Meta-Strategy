# coding: UTF-8

import matplotlib.pyplot as plt
import itertools
import numpy as np
from scipy.spatial.distance import euclidean
from collections import Counter
from mpl_toolkits.mplot3d import Axes3D

from . import domain, preference


class NegoSetting(object):

    def __init__(self, domain_path, pref_pathes):
        self.domain = domain.Domain(domain_path)
        self.prefs = []
        for pref_path in pref_pathes:
            self.prefs.append(preference.Preference(domain_path, pref_path))

    def getDomain(self):
        return self.domain
    
    def getUtilityValue(self, prefID, bid):
        return self.prefs[prefID-1].getUtilityValue(bid)

    def getDiscountedUtilityValue(self, prefID, bid, time: float):
        return self.prefs[prefID-1].getDiscountedUtilityValue(bid, time)

    def getOverRV_Bids_forAllPlayers(self, allBids):
        overRV_Bids_set = set(set(map(tuple, allBids)))
        for pref in self.prefs:
            temp_overRV_Bids_set = set(set(map(tuple, pref.getOverRV_Bids(allBids))))
            overRV_Bids_set = overRV_Bids_set.intersection(temp_overRV_Bids_set)
            # print(overRV_Bids_set)
        return list(overRV_Bids_set) 

    ### Pareto最適に関連する関数群
    def getParetoBids_for2Players(self, prefID1, prefID2):
        paretoBids = []

        allBids = self.domain.getAllBids()
        bidInfoes = []
        for bid in allBids:
            bidInfoes.append((bid, self.getUtilityValue(prefID1, bid), self.getUtilityValue(prefID2, bid)))

        bidInfoes = sorted(bidInfoes, key=lambda x: float(-x[1]))

        maxIdx = -1
        maxUtil = -1.0
        for i, bidInfo in enumerate(bidInfoes):
            if 1.0 - bidInfo[1] < 1e-10 and 1.0 - bidInfo[2] < 1e-10:
                return [bidInfo[0]]

            if maxUtil < bidInfo[2]:
                if maxIdx != -1 and bidInfoes[maxIdx][1] > bidInfo[1]:
                    paretoBids.append(bidInfoes[maxIdx][0])
                maxUtil = bidInfo[2]
                maxIdx = i

        bidInfoes = sorted(bidInfoes, key=lambda x: float(-x[2]))

        maxIdx = -1
        maxUtil = -1.0
        for i, bidInfo in enumerate(bidInfoes):

            if maxUtil < bidInfo[1]:
                if i != 0 and bidInfoes[i-1][2] > bidInfo[2]:
                    if bidInfoes[maxIdx][0] not in paretoBids:
                        paretoBids.append(bidInfoes[maxIdx][0])
                maxUtil = bidInfo[1]
                maxIdx = i

        return paretoBids

    def getParetoBids_forMultiPlayers(self):
        players_comb = itertools.combinations([i+1 for i in range(len(self.prefs))],2)
        paretoBids_set = set()

        for comb in players_comb:
            addBids_set = set(map(tuple, self.getParetoBids_for2Players(comb[0], comb[1])))
            # print(str(comb[0]) + " " + str(comb[1]) + ": " + str(addBids_set))
            paretoBids_set = paretoBids_set.union(addBids_set)

        return list(paretoBids_set)

    ### Nash交渉解に関連する関数群
    def getNashProduct(self, bid):
        isOver_RV = True

        nashProduct = 1.0
        for pref in self.prefs:
            if pref.getUtilityValue(bid) > pref.getReservationValue():
                nashProduct *= (pref.getUtilityValue(bid) - pref.getReservationValue())
            else: 
                isOver_RV = False
        if isOver_RV: return nashProduct
        else: return 1e-6 - 10
    
    def getNashSolution(self):
        allOverRV_Bids = self.getOverRV_Bids_forAllPlayers(self.getDomain().getAllBids())

        nashSolutions = []
        nashProduct_max = 0.0
        for bid in allOverRV_Bids:
            nashProduct_temp = 1.0
            for pref in self.prefs:
                nashProduct_temp *= (pref.getUtilityValue(bid) - pref.getReservationValue())
            if nashProduct_max < nashProduct_temp:
                nashProduct_max = nashProduct_temp
                nashSolutions = [bid]
            elif abs(nashProduct_max - nashProduct_temp) <= 1e-10:
                nashSolutions.append(bid)
        return nashSolutions


    ### 2点間の距離
    def getPoint2PointDistance(self, p1, p2):
        p1_npArray = np.array(p1)
        p2_npArray = np.array(p2)
        return euclidean(p1_npArray, p2_npArray)

    def getNashDistance(self, p):
        nash_ps = self.getNashSolution()

        dist = int(1e7)
        for nash_p in nash_ps:
            dist = min(dist, self.getPoint2PointDistance(nash_p, p))
        return dist

    def getParetoFrontierDistance(self, p):
        pareto_ps = self.getParetoBids_forMultiPlayers()

        dist = int(1e7)
        for pareto_p in pareto_ps:
            dist = min(dist, self.getPoint2PointDistance(pareto_p, p))
        return dist


    ### MOL: Metric of Opposition Level に関する関数群
    def getMultiMOL(self, bids):
        if len(bids) == 0: return 0.0 # 対象bidが空集合の場合は0を返す

        # 各bidに対してそれぞれ距離を計算し、和をとる
        dist = 0.0
        for bid in bids:
            # bidにおける各エージェントの効用の総和を計算
            sumUtil = 0.0
            for pref in self.prefs:
                sumUtil += pref.getUtilityValue(bid)

            # bidにおける距離を加算
            for pref in self.prefs:
                dist += (pref.getUtilityValue(bid) - sumUtil / len(self.prefs))**2
        return (dist * len(self.prefs)) / ((len(self.prefs)-1) * len(bids))


    ### グラフの描画に関する関数群
    def show3Dgraph(self, bids):

        bidUtils = [[], [], []]
        for bid in bids:
            bidUtils[0].append(self.prefs[0].getUtilityValue(bid))
            bidUtils[1].append(self.prefs[1].getUtilityValue(bid))
            bidUtils[2].append(self.prefs[2].getUtilityValue(bid))

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(bidUtils[0], bidUtils[1], bidUtils[2], label='bid')
        ax.legend()
        ax.set_xlabel('Agent 0\'s utility')
        ax.set_ylabel('Agent 1\'s utility')
        ax.set_zlabel('Agent 2\'s utility')
        plt.show()

            
    
    def printNegoSetting(self):
        print("Name: " + self.domain.getDomainName())

        domain = self.domain
        issues = domain.getIssues()
        for i, issue in enumerate(issues):
            print("Issue " + str(i) + ": " + issue.get('name') + " | ", end='')

            values = domain.getValues(i+1)
            for value in values:
                print(value.get('value'), end=' ')
            print()

        print("Discount Factor  : ", end="")
        for pref in self.prefs:
            print(pref.getDiscountFactor(), end=" ")
        
        print("\nReservation Value: ", end="")
        for pref in self.prefs:
            print(pref.getReservationValue(), end=" ")
       
        allBids = self.domain.getAllBids()
        print("\nMOL (ALL bids)              : " + '{0:.6f}'.format(self.getMultiMOL(allBids)))
        
        overRV_Bids = self.getOverRV_Bids_forAllPlayers(allBids)
        print("MOL (ALL OverRV bids)       : " + '{0:.6f}'.format(self.getMultiMOL(overRV_Bids)))

        paretoBids = self.getParetoBids_forMultiPlayers()
        print("MOL (ALL Pareto bids)       : " + '{0:.6f}'.format(self.getMultiMOL(paretoBids)))

        overRV_paretoBids = self.getOverRV_Bids_forAllPlayers(paretoBids)
        print("MOL (ALL OverRV-Pareto bids): " + '{0:.6f}'.format(self.getMultiMOL(overRV_paretoBids)))

        nashSolution_Bids = self.getNashSolution()
        print("MOL (ALL Nash-Solution bids): " + '{0:.6f}'.format(self.getMultiMOL(nashSolution_Bids)))

        
        print("\nbid, util1, util2, util3, pareto_dist, nash_dist")
        for bid in allBids:
            print(bid, end=' ')
            for i in range(len(self.prefs)):
                print('{0:.4f}'.format(self.getUtilityValue(i, bid)), end=' ')
            print('{0:.4f}'.format(self.getParetoFrontierDistance(bid)), end=' ')
            print('{0:.4f}'.format(self.getNashDistance(bid)), end='\n')
            # print('{0:.6f}'.format(ns.getNashProduct(bid)))
        
        print("Pareto Frontier: " + str(self.getParetoBids_forMultiPlayers()))
        print("Nash Solutions : " + str(self.getNashSolution()))

        # self.show3Dgraph(allBids)
        


# テスト
# root_path = '../Scenarios/Domain2/'
# ns = NegoSetting(
#     root_path + 'Domain2.xml',
#     [
#         root_path + 'Domain2_util1.xml',
#         root_path + 'Domain2_util2.xml',
#         root_path + 'Domain2_util3.xml',
#     ]
# )
# ns.printNegoSetting()
# allBids = ns.getDomain().getAllBids()

# if False:
#     print("OverRV Bids   : ", end="")
#     print(ns.getOverRV_Bids_forAllPlayers(allBids))

#     print("Pareto Bids   : ", end="")
#     print(ns.getParetoBids_forMultiPlayers())

# print("Nash Solutions: ", end="")
# print(ns.getNashSolution())
    # ns.show3Dgraph(ns.getOverRV_Bids_forAllPlayers(allBids))

