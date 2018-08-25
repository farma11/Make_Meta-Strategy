# coding: UTF-8

import sys
import math
from lxml import etree # XMLのパース
from . import domain


class Preference(domain.Domain):
    
    def __init__(self, domainXML_path, preferenceXML_path):
        self.domainXML_path = domainXML_path
        self.domain = domain.Domain(domainXML_path)

        self.preferenceXML_path = preferenceXML_path
        self.tree = etree.parse(preferenceXML_path)
        self.root = self.tree.getroot()

        self.issueWeights = []
        self.valueWeights = []
        self.issueMaxEvaluations = []
        self.discoutFactor = -1.0
        self.reservationValue = -1.0
        if self.__isCurrectFormat():
            self.__getPreferenceInfo()
        else:
            print(preferenceXML_path)
            print("Error (" + self.domainXML_path + "): 交渉ドメインとフォーマットが一致しません．プログラムを終了します．", file=sys.stderr)
            sys.exit(1) # 異常終了


    def __getPreferenceInfo(self):
        self.issueWeights = self.__getIssueWeights()
        for issue in self.root.find('objective').findall('issue'):
            self.valueWeights.append(self.__getValueWeights(issue))
        self.issueMaxEvaluations = self.__getIssueMaxEvaluation()
        self.discoutFactor = float(self.root.find('discount_factor').get('value'))        
        self.reservationValue = float(self.root.find('reservation').get('value'))

    def __getIssueWeights(self):
        weights = []
        weight_tags = self.root.find('objective').findall('weight')
        for weight_tag in weight_tags:
            weights.append(float(weight_tag.get('value')))
        return weights

    def __getValueWeights(self, issue):
        weights = []
        values = issue.findall('item')
        for value in values:
            weights.append(int(value.get('evaluation')))
        return weights

    def __getIssueMaxEvaluation(self):
        evaluations = [0] * self.domain.getIssueSize()
        issues = self.root.find('objective').findall('issue')
        for i, issue in enumerate(issues):
            values = issue.findall('item')
            for value in values:
                evaluations[i] = max(evaluations[i], int(value.get('evaluation')))
        return evaluations


    def __isCurrectFormat(self):
        issues = self.root.find('objective').findall('issue')
        if len(issues) != self.domain.getIssueSize():
            print("Error: Issue数が不一致です", file=sys.stderr)
            return False
        for i, issue in enumerate(issues):
            values = issue.findall('item')
            if len(values) != self.domain.getValueSize(i+1):
                print("Error: Value数が不一致です. (" + str(i) + ") " + str(len(values)) + "!=" + str(self.domain.getValueSize(i)), file=sys.stderr)
                return False
        return True

    ### Preference概要
    def getPreferenceName(self):
        return self.root.find('objective').get('name')

    def getDomain(self):
        return self.domain

    def getIssueWeight(self, issueID):
        return self.issueWeights[issueID-1]

    def getValueWeight(self, issueID, valueID):
        return self.valueWeights[issueID-1][valueID-1]

    def getUtilityValue(self, bid):
        utility = 0.0
        issues = self.root.find('objective').findall('issue')
        for i, issue in enumerate(issues):
            value = issue.findall('item')[bid[i]-1]

            utility += self.issueWeights[i] * float(value.get('evaluation')) / self.issueMaxEvaluations[i]
        return utility

    def getDiscountedValue(self, time, value):
        return value * (self.discoutFactor ** time)


    ### 割引効用関係
    def getDiscountFactor(self):
        return self.discoutFactor

    def putDiscountFactor(self, df):
        if 0.0 < df <= 1.0:
            self.discoutFactor = df
        else:
            print("Error: 割引係数の値が不正です．プログラムを終了します．", file=sys.stderr)
            sys.exit(1) # 異常終了
    
    def getDiscountedUtilityValue(self, bid, time: float):
        return self.getUtilityValue(bid) * (self.discoutFactor ** time)

    ### 留保価格関係
    def getReservationValue(self):
        return self.reservationValue

    def putReservationValue(self, rv):
        if 0.0 <= rv <= 1.0:
            self.reservationValue = rv
        else:
            print("Error: 留保価格の値が不正です．プログラムを終了します．", file=sys.stderr)
            sys.exit(1) # 異常終了

    def getDiscountedReservationValue(self, time: float):
        return self.reservationValue * (self.discoutFactor ** time)

    ### 合意案候補関係
    def getAllBids(self):
        return self.domain.getAllBids()

    def getOverRV_Bids(self, allBids):
        allBids = self.domain.getAllBids()

        overRV_bids = []
        for bid in allBids:
            if self.getUtilityValue(bid) >= self.reservationValue:
                overRV_bids.append(bid)
        return overRV_bids

    ### デバック関連
    def printUtilitySpaceInfo(self):
        print("Name: " + self.getPreferenceName())

        domainInfo = self.getDomain()
        issues = domainInfo.getIssues()
        for issue in issues:
            issueID = domainInfo.getIssueID(issue)
            print("Issue " + str(issueID) + ": " \
                + str(domainInfo.getIssueName(issueID)) + " (" + str(self.getIssueWeight(issueID)) + " x)" \
                + " | ", end='')
            values = domainInfo.getValues(issueID)
            for value in values:
                valueID = domainInfo.getValueID(issueID, value)
                print(str(domainInfo.getValueName(issueID, valueID)) + "(" + str(self.getValueWeight(issueID, valueID)) + ")", end=' ')
            print()
        print("Discount Factor: " + str(self.getDiscountFactor()))
        print("Reservation Value: " + str(self.getReservationValue()))

        bids = domainInfo.getAllBids()
        for bid in bids:
            print(bid, end=' ')
            print('{0:.4f}'.format(self.getUtilityValue(bid)))

# テスト
# us = Preference('../Scenarios/testScenario/testDomain.xml', '../Scenarios/testScenario/testPreference1.xml')
# us.printUtilitySpaceInfo()
# print(us.getAllBids())
# print(us.getOverRV_Bids())
# us.putDiscountFactor(0.39)
# us.putReservationValue(0.9)
# us.printUtilitySpaceInfo()
# print(us.getAllBids())
# print(us.getOverRV_Bids())

        