# coding: UTF-8

import random
from classes import absAgent
from classes import agentAction
from classes import preference
from classes import absNegoRule


class BoulwareAgent(absAgent.AbsAgent):
    def __init__(self, pref: preference.Preference,
                 negotiation_rule: absNegoRule.AbsNegoRule,
                 agent_id: int, agent_name: str, agent_num: int):
        self.__pref = pref
        self.__rule = negotiation_rule
        self.__agent_id = agent_id
        self.__agent_name = agent_name
        self.__opponent_bid = None

    def get_conssetion_value(self):
        return (1.0 - pow(self.__rule.get_time_now(), 10))

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
        return allBids[random.randrange(self.__pref.getDomainSize())]
    
    def receive_start_negotiation(self):
        self.__opponent_bid = None

    def receive_end_negotiation(self):
        pass

    def get_name(self):
        return self.__agent_name
