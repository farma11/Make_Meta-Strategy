# coding: UTF-8

import matplotlib.pyplot as plt
import itertools
from collections import Counter
from mpl_toolkits.mplot3d import Axes3D

import domain, preference


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

    def getOverRV_Bids_forAllPlayers(self):
        overRV_Bids_set = set(set(map(tuple, self.domain.getAllBids())))
        for pref in self.prefs:
            temp_overRV_Bids_set = set(set(map(tuple, pref.getOverRV_Bids())))
            overRV_Bids_set = overRV_Bids_set.intersection(temp_overRV_Bids_set)
            # print(overRV_Bids_set)
        return list(overRV_Bids_set) 

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
       
        bids = ns.domain.getAllBids()
        print("MOL (All bids)       : " + '{0:.6f}'.format(self.getMultiMOL(bids)))
        
        overRV_Bids = ns.getOverRV_Bids_forAllPlayers()
        print("MOL (ALL OverRV bids): " + '{0:.6f}'.format(self.getMultiMOL(overRV_Bids)))

        paretoBids = ns.getParetoBids_forMultiPlayers()
        print("MOL (ALL Pareto bids): " + '{0:.6f}'.format(self.getMultiMOL(paretoBids)))

        for bid in bids:
            print(bid, end=' ')
            print('{0:.4f}'.format(ns.getUtilityValue(1, bid)), end=' ')
            print('{0:.4f}'.format(ns.getUtilityValue(2, bid)), end=' ')
            print('{0:.4f}'.format(ns.getUtilityValue(3, bid)))
        

# テスト
root_path = '../Scenarios/testScenario/'
ns = NegoSetting(
    root_path + 'testDomain.xml',
    [
        root_path + 'testPreference1.xml',
        root_path + 'testPreference2.xml',
        root_path + 'testPreference3.xml',
    ]
)
ns.printNegoSetting()
# print("Pareto: ", end="")
# print(ns.getParetoBids_forMultiPlayers())
ns.show3Dgraph(ns.getOverRV_Bids_forAllPlayers())

