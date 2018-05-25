# coding: UTF-8

import sys
from lxml import etree # XMLのパース

class UtilitySpace(object):
    """
        効用空間のクラス
    """

    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.tree = etree.parse(xml_path)
        self.root = self.tree.getroot()

        self.issues = self.root.find('objective').findall('issue')
        self.weights = self.__getIssueWeights()
        self.values = self.__getValues()
        self.discoutFactor = float(self.root.find('discount_factor').get('value'))
        self.reservationValue = float(self.root.find('reservation').get('value'))


    def getXML_Text(self):
        return etree.tostring(self.root)

    def getRoot(self):
        return self.root


    ### UtilitySpace概要
    def getUtilitySpaceName(self):
        return self.root.find('objective').get('name')


    ### Issue関連
    def getIssues(self):
        return self.issues

    def getIssue(self, issuesID):
        return self.issues[issuesID-1]

    def getIssueSize(self):
        return len(self.issues)

    def __getIssueWeights(self):
        weights = []
        weight_tags = self.root.find('objective').findall('weight')
        for weight_tag in weight_tags:
            weights.append(float(weight_tag.get('value')))
        return weights

    ### Value関連
    def __getValues(self):
        values = []
        for issue in self.issues:
            values.append(issue.findall('item'))
        return values

    def getValues(self, issueID):
        return self.values[issueID-1]

    def getValue(self, issueID, valueID):
        return self.values[issueID-1][valueID-1]

    def getValueSize(self, issueID):
        return len(self.values[issueID-1])

    ### 割引効用関係
    def getDiscountFactor(self):
        return self.discoutFactor

    ### 留保価格関係
    def getReservationValue(self):
        return self.reservationValue

    ### デバック関連
    def printUtilitySpaceInfo(self):
        print("Name: " + self.getUtilitySpaceName())

        issues = self.getIssues()
        for i, issue in enumerate(issues):
            print("Issue " + str(i) + ": " + issue.get('name') + " | ", end='')

            values = self.getValues(i+1)
            for value in values:
                print(value.get('value'), end=' ')
            print()
        print("Discount Factor: " + str(self.getDiscountFactor()))
        print("Reservation Value: " + str(self.getReservationValue()))




# テスト

xml_path = './testXML.xml'
us = UtilitySpace(xml_path)
us.printUtilitySpaceInfo()
