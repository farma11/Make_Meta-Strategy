# coding: UTF-8

import sys
from lxml import etree # XMLのパース

class Domain(object):

    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.tree = etree.parse(xml_path)
        self.root = self.tree.getroot()

        self.issues = []
        self.values = []
        self.domainSize = 1
        self.__getDomainInfo()


    def __getDomainInfo(self):
        self.issues = self.root.find('utility_space').find('objective').findall('issue')
        for issue in self.issues:
            values = issue.findall('item')
            self.values.append(values)
            self.domainSize *= len(values)

    def getDomainName(self):
        return self.root.find('utility_space').find('objective').get('name')

    def getIssues(self):
        return self.issues

    def getIssue(self, issuesID):
        return self.issues[issuesID-1]

    def getIssueSize(self):
        return len(self.issues)

    def getValues(self, issueID):
        return self.values[issueID-1]

    def getValue(self, issueID, valueID):
        return self.values[issueID-1][valueID-1]

    def getValueSize(self, issueID):
        return len(self.values[issueID-1])

    def getDomainSize(self):
        return self.domainSize

    def printDomainInfo(self):
        print("Name: " + self.getDomainName())

        issues = self.getIssues()
        for i, issue in enumerate(issues):
            print("Issue " + str(i) + ": " + issue.get('name') + " | ", end='')

            values = self.getValues(i+1)
            for value in values:
                print(value.get('value'), end=' ')
            print()

        print("Domain Size: " + str(self.getDomainSize()))


domain = Domain('./testDomain.xml')
domain.printDomainInfo()

    