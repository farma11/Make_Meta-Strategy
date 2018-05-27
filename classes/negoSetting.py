# coding: UTF-8

import domain, preference

class NegoSetting(object):

    def __init__(self, domain_path, pref_pathes):
        self.domain = domain.Domain(domain_path)
        self.prefs = []
        for pref_path in pref_pathes:
            self.prefs.append(preference.Preference(domain_path, pref_path))
    
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