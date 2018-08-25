# coding: UTF-8

import sys, copy, math
from lxml import etree # XMLのパース

class Domain(object):

    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.tree = etree.parse(xml_path)
        self.root = self.tree.getroot()

        self.issues = []
        self.issueNames = []
        self.values = []
        self.valueNames = []
        self.domainSize = 1
        self.__getDomainInfo()


    def __getDomainInfo(self):
        self.issues = self.root.find('utility_space').find('objective').findall('issue')
        for issue in self.issues:
            self.issueNames.append(issue.get('name'))
            values = issue.findall('item')
            self.values.append(values)
            self.domainSize *= len(values)
            tempValueNames = []
            for value in values:
                tempValueNames.append(value.get('value'))
            self.valueNames.append(tempValueNames)

    ### Domain全体
    def getDomainName(self):
        return self.root.find('utility_space').find('objective').get('name')

    def getDomainSize(self):
        return self.domainSize

    
    ### Issue関係
    def getIssues(self):
        return self.issues

    def getIssue(self, issuesID):
        return self.issues[issuesID-1]

    def getIssueID(self, issue):
        return self.issues.index(issue) + 1

    def getIssueName(self, issueID):
        return self.issueNames[issueID-1]

    def getIssueSize(self):
        return len(self.issues)


    ### Value関係
    def getValues(self, issueID):
        return self.values[issueID-1]

    def getValue(self, issueID, valueID):
        return self.values[issueID-1][valueID-1]

    def getValueID(self, issueID, value) -> int:
        return self.values[issueID-1].index(value) + 1

    def getValueName(self, issueID, valueID):
        return self.valueNames[issueID-1][valueID-1]

    def getValueSize(self, issueID) -> int:
        return len(self.values[issueID-1])

    
    ### 合意案候補関係
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


    ### デバック関連
    def printDomainInfo(self):
        print("Name: " + self.getDomainName())

        issues = self.getIssues()
        for issue in issues:
            # print("Issue " + str(i) + ": " + issue.get('name') + " | ", end='')
            issueID = self.getIssueID(issue)
            print("Issue " + str(issueID) + ": " + self.getIssueName(issueID) + " | ", end='')

            values = self.getValues(issueID)
            for value in values:
                valueID = self.getValueID(issueID, value)
                print("v" + str(valueID) + ":" + self.getValueName(issueID, valueID), end=' ')
            print()

        print("Domain Size: " + str(self.getDomainSize()))
        print(self.getAllBids())


# domain = Domain('../Scenarios/testScenario/testDomain.xml')
# domain.printDomainInfo()

    