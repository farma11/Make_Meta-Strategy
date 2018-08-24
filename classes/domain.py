# coding: UTF-8

import sys, copy, math
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

    def getIssueID(self, issue):
        return self.issues.index(issue) + 1

    def getIssueSize(self):
        return len(self.issues)

    def getValues(self, issueID):
        return self.values[issueID-1]

    def getValue(self, issueID, valueID):
        return self.values[issueID-1][valueID-1]

    def getValueID(self, issueID, value) -> int:
        return self.values[issueID-1].index(value) + 1

    def getValueSize(self, issueID) -> int:
        return len(self.values[issueID-1])

    def getDomainSize(self):
        return self.domainSize

    def getAllBids(self):
        bids = [[]]
        for i in range(len(self.issues)):
            tbids = copy.deepcopy(bids)
            for j in range(len(self.values[i])-1):
                bids = bids + copy.deepcopy(tbids)
            for j in range(len(self.values[i])):
                for k in range(len(tbids)):
                    bids[k + j*len(tbids)].append(j+1)

        if self.domainSize == len(bids):
            return bids
        else:
            print("Error (" + __file__ + "): 全ての合意案候補を取得失敗しました．プログラムを終了します．", file=sys.stderr)
            sys.exit(1) # 異常終了


    def printDomainInfo(self):
        print("Name: " + self.getDomainName())

        issues = self.getIssues()
        for issue in issues:
            # print("Issue " + str(i) + ": " + issue.get('name') + " | ", end='')
            issueID = self.getIssueID(issue)
            print("Issue " + str(issueID) + ": " + issue.get('name') + " | ", end='')

            values = self.getValues(issueID)
            for value in values:
                print("v" + str(self.getValueID(issueID, value)) + ":" + value.get('value'), end=' ')
            print()

        print("Domain Size: " + str(self.getDomainSize()))
        print(self.getAllBids())


# domain = Domain('../Scenarios/testScenario/testDomain.xml')
# domain.printDomainInfo()

    