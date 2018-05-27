# coding: UTF-8

import sys
import math
from lxml import etree # XMLのパース
import domain


class Preference(domain.Domain):
    
    def __init__(self, domainXML_path, preferenceXML_path):
        self.domainXML_path = domainXML_path
        self.domain = domain.Domain(domainXML_path)

        self.preferenceXML_path = preferenceXML_path
        self.tree = etree.parse(preferenceXML_path)
        self.root = self.tree.getroot()

        self.issueWeights = []
        self.issueMaxEvaluations = []
        self.discoutFactor = -1.0
        self.reservationValue = -1.0
        if self.__isCurrectFormat():
            self.__getPreferenceInfo()
        else:
            print("Error (" + self.domainXML_path + "): 交渉ドメインとフォーマットが一致しません．プログラムを終了します．", file=sys.stderr)
            sys.exit(1) # 異常終了


    def __getPreferenceInfo(self):
        self.issueWeights = self.__getIssueWeights()
        self.issueMaxEvaluations = self.__getIssueMaxEvaluation()
        self.discoutFactor = float(self.root.find('discount_factor').get('value'))        
        self.reservationValue = float(self.root.find('reservation').get('value'))

    def __getIssueWeights(self):
        weights = []
        weight_tags = self.root.find('objective').findall('weight')
        for weight_tag in weight_tags:
            weights.append(float(weight_tag.get('value')))
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
            return False
        for i, issue in enumerate(issues):
            values = issue.findall('item')
            if len(values) != self.domain.getValueSize(i):
                return False
        return True

    ### Preference概要
    def getPreferenceName(self):
        return self.root.find('objective').get('name')

    def getDomain(self):
        return self.domain

    def getIssueWeight(self, issueID):
        return self.issueWeights[issueID-1]

    ### 割引効用関係
    def getDiscountFactor(self):
        return self.discoutFactor

    ### 留保価格関係
    def getReservationValue(self):
        return self.reservationValue

    ### デバック関連
    def printUtilitySpaceInfo(self):
        print("Name: " + self.getPreferenceName())

        domain = self.getDomain()
        issues = domain.getIssues()
        for i, issue in enumerate(issues):
            print("Issue " + str(i) + ": " \
                + issue.get('name') + " (" + str(self.getIssueWeight(i+1)) + ")" \
                + " | ", end='')
            values = domain.getValues(i+1)
            for value in values:
                print(value.get('value'), end=' ')
            print()
        print("Discount Factor: " + str(self.getDiscountFactor()))
        print("Reservation Value: " + str(self.getReservationValue()))

# テスト
us = Preference('../Scenarios/testScenario/testDomain.xml', '../Scenarios/testScenario/testPreference1.xml')
us.printUtilitySpaceInfo()

        