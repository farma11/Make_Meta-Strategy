# coding: UTF-8

import sys
from lxml import etree # XMLのパース
import domain


class Preference(domain.Domain):
    
    def __init__(self, domainXML_path, preferenceXML_path):
        self.domainXML_path = domainXML_path
        self.domain = domain.Domain(domainXML_path)

        self.preferenceXML_path = preferenceXML_path
        self.tree = etree.parse(preferenceXML_path)
        self.root = self.tree.getroot()

        self.discoutFactor = -1.0
        self.reservationValue = -1.0
        self.__getPreferenceInfo()

    def __getPreferenceInfo(self):
        self.weights = self.__getIssueWeights()
        self.discoutFactor = float(self.root.find('discount_factor').get('value'))        
        self.reservationValue = float(self.root.find('reservation').get('value'))

    def __getIssueWeights(self):
        weights = []
        weight_tags = self.root.find('objective').findall('weight')
        for weight_tag in weight_tags:
            weights.append(float(weight_tag.get('value')))
        return weights

    ### Preference概要
    def getUtilitySpaceName(self):
        return self.root.find('objective').get('name')

    def getDomain(self):
        return self.domain

    ### 割引効用関係
    def getDiscountFactor(self):
        return self.discoutFactor

    ### 留保価格関係
    def getReservationValue(self):
        return self.reservationValue

    ### デバック関連
    def printUtilitySpaceInfo(self):
        print("Name: " + self.getUtilitySpaceName())

        domain = self.getDomain()
        issues = domain.getIssues()
        for i, issue in enumerate(issues):
            print("Issue " + str(i) + ": " + issue.get('name') + " | ", end='')

            values = domain.getValues(i+1)
            for value in values:
                print(value.get('value'), end=' ')
            print()
        print("Discount Factor: " + str(self.getDiscountFactor()))
        print("Reservation Value: " + str(self.getReservationValue()))

# テスト
us = Preference('./testDomain.xml', './testXML.xml')
us.printUtilitySpaceInfo()

        