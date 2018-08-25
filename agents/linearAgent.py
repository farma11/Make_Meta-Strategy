# coding: UTF-8

import random
from classes import absAgent
from classes import agentAction
from classes import preference
from classes import absNegoRule


class LinearAgent(absAgent.AbsAgent):
    def __init__(self, agent_name: str, domain_path: str, pref_path: str,
                 negotiation_rule: absNegoRule.AbsNegoRule, agent_id: int):
        self.__pref = preference.Preference(domain_path, pref_path)
        self.__rule = negotiation_rule
        self.__agent_id = agent_id
        self.__agent_name = agent_name
        self.__opponent_bid = None

    def get_conssetion_value(self):
        return (1.0 - self.__rule.get_time_now())

    def receive_action(self, agentAction_: agentAction.AbstractAction):
        if isinstance(agentAction_, agentAction.Offer):
            self.__opponent_bid = agentAction_.get_bid()

    def send_action(self):
        if self.__opponent_bid is not None and \
           self.get_conssetion_value() < self.__pref.getUtilityValue(self.__opponent_bid):
            return agentAction.Accept(self.__agent_id)

        bid_offer = self.getRandomBid()
        return agentAction.Offer(self.__agent_id, bid_offer)

    def getRandomBid(self):
        allBids = self.__pref.getAllBids()
        return allBids[random.randrange(self.__pref.getDomain().getDomainSize())]
    
    def receive_start_negotiation(self):
        self.__opponent_bid = None

    def receive_end_negotiation(self):
        pass

    def get_name(self):
        return self.__agent_name



