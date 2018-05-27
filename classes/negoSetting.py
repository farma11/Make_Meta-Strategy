# coding: UTF-8

import domain, preference

class NegoSetting(object):

    def __init__(self, domain_path, pref_pathes):
        self.domain = domain.Domain(domain_path)
        self.prefs = []
        for pref_path in pref_pathes:
            self.prefs.append(preference.Preference(domain_path, pref_path))

    def getUtilityValue(self, prefID, bid):
        return self.prefs[prefID-1].getUtilityValue(bid)
    
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

