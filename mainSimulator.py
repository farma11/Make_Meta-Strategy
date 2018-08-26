# coding: UTF-8

import json
import datetime
import sys
import os
import site
import importlib

from classes import absNegoRule
from classes import agentAction
from classes import negoSetting

ABSPATH = os.path.dirname(os.path.abspath(__file__)) + "/../"
sys.path.append(os.path.join(ABSPATH, "agents"))


class MainSimulator:
    def __init__(self, deadline_type, deadline: int, domain_path, pref_pathes: list):
        """
        :param DeadlineType deadline_type: 交渉における終了形式
        :param int deadline: 交渉の最大時間（/ラウンド）
        :param str domain_path: 交渉ドメインの設定ファイル
        :param List[str] pref_pathes: 交渉ドメインファイルのリスト
        """
        if deadline_type == absNegoRule.DeadlineType.Round:
            self.__rule = absNegoRule.NegotiationRuleRound(deadline)
        elif deadline_type == absNegoRule.DeadlineType.Time:
            self.__rule = absNegoRule.NegotiationRuleTime(deadline)
        else:
            raise ValueError('deadline type error in mainSimulator init')
        
        self.__negoSetting = negoSetting.NegoSetting(domain_path, pref_pathes)

        self.__domain_path = domain_path
        self.__pref_pathes = pref_pathes
        self.__agent_list = []

        self.__action_list_list = []
        self.__get_agreement_list = []

    def set_agent(self, module, class_name, agent_name):
        """
        エージェントを登録する

        :param module module: 自動交渉エージェントのモジュール
        :param str class_name: 自動交渉エージェントのクラス名
        """
        instance = getattr(module, class_name)
        self.__agent_list.append(instance(
                    agent_name,
                    self.__domain_path,
                    self.__pref_pathes[len(self.__agent_list)],
                    self.__rule,
                    len(self.__agent_list)
                    ))
        # self.display.set_agent_name(self.__agent_list[-1].get_name())

    def get_action_list_list(self):
        '''
        過去の交渉履歴を取得する．
        :rtype: [[AbstractAction]]
        :return: 繰り返し提案応答ゲームにおける，過去の交渉履歴
        '''
        return self.__action_list_list

    def get_agreement_list(self):
        '''
        過去の合意履歴を取得する．
        :rtype: [[bool, AbstractAction]]
        :return: 繰り返し提案応答ゲームにおける，過去の合意履歴
        '''
        return self.__get_agreement_list

    def get_end_utility_list(self):
        '''
        過去の合意結果の効用値に関する情報のリストを取得する．
        :rtype: [[bool, AbstractAction]]
        :return: 過去の合意結果の効用値に関する情報を取得する．
        '''
        end_utility_list = []
        for get_agreement_list in self.__get_agreement_list:
            end_utility = {}
            if get_agreement_list[0]:
                action = get_agreement_list[1]
                for j, agent in enumerate(self.__agent_list):
                    if not isinstance(action, agentAction.EndNegotiation):
                        end_utility[agent.get_name()] = self.__negoSetting.getDiscountedUtilityValue(j+1, action.get_bid(), action.get_time_offered())
                    else:
                        end_utility[agent.get_name()] = self.__negoSetting.getDiscountedReservationValue(j+1, action.get_time_offered())
                # print("last turn:", self.__rule.get_time_now())
                if not isinstance(action, agentAction.EndNegotiation):
                    acceptedBid = action.get_bid()
                    end_utility["agreement_bid"] = acceptedBid
                    end_utility["time"] = self.__rule.get_time_now()
                    end_utility["Dist.Pareto"] = self.__negoSetting.getParetoFrontierDistance(acceptedBid)
                    end_utility["Dist.Nash"] = self.__negoSetting.getNashDistance(acceptedBid)
                else:
                    end_utility["agreement_bid"] = 0
                    end_utility["time"] = self.__rule.get_time_now()
                    # end_utility["parato_distance"] = self.display.get_parato_distance(
                    #     self.__utilities.get_discount_reservation_value_list(action.get_time_offered())
                    # )
            else:
                for j, agent in enumerate(self.__agent_list):
                    end_utility[agent.get_name()] = 0
                end_utility["agreement_bid"] = 0
                end_utility["parato_distance"] = 0
            end_utility_list.append(end_utility)
        return end_utility_list


    def do_negotiation(self, is_printing: bool, print_times=10) -> bool:
        """
        提案応答ゲームを行う

        :param bool is_printing: 描画するかどうかのフラグ
        :param int print_times: 何巡毎に描画を行うか
        :rtype: bool
        :return: 正常に自動交渉が終了したかどうかのbool
        """
        if self.__rule.get_type() == absNegoRule.DeadlineType.Round:
            self.__rule.start_negotiation()
        elif self.__rule.get_type() == absNegoRule.DeadlineType.Time:
            self.__rule.start_negotiation()
        else:
            print('unexpected invalid NegotiationRuleType')
            return False

        print("-" * 30)
        print("start negotiation:", len(self.__get_agreement_list)+1)
        for agent in self.__agent_list:
            agent.receive_start_negotiation()

        action_list = []
        self.__accept_num = 1
        can_proceed = True

        while can_proceed:
            for i in range(len(self.__agent_list)):
                #agentにアクションを起こさせて、時間内かつアクションが有効か検証する
                action = self.__agent_list[i].send_action()
                if self.__rule.get_time_now() > 1.0:
                    return self.__end_negotiation(action_list, [False])
                elif not self.__is_valid_action(action, len(action_list)):
                    print('unexpected invalid action caused')
                    for agent in self.__agent_list:
                        agent.receive_end_negotiation()
                    return False
                elif isinstance(action, agentAction.Accept):
                    action.set_bid(action_list[-1].get_bid())
                action.set_time_offered(self.__rule.get_time_now())
                action_list.append(action)

                #各agentにアクションを知らせる
                for j in range(len(self.__agent_list)):
                    if i == j:
                        continue
                    self.__agent_list[j].receive_action(action_list[-1])
                #ネゴシエーションの終了判定
                if self.__is_finished_negotiation(action):
                    # if is_printing:
                    #     self.display.update_end(action_list, [True, action])
                    # EndNegotiationもprato_distanceをだせるように
                    if not isinstance(action, agentAction.EndNegotiation):
                        acceptedBid = action.get_bid()
                        print("last turn:", self.__rule.get_time_now())
                        print("agreement bid:", acceptedBid)
                        print("Dist. Pareto:", self.__negoSetting.getParetoFrontierDistance(acceptedBid))
                        print("Dist. Nash:", self.__negoSetting.getNashDistance(acceptedBid))
                        for j, agent in enumerate(self.__agent_list):
                            print(agent.get_name(), ":", self.__negoSetting.getDiscountedUtilityValue(j+1, acceptedBid, action.get_time_offered()))
                    else:
                        print("last turn:", self.__rule.get_time_now())
                        print("agreement bid: Nothing (EndNegotiation)")
                    # EndNegotiationもprato_distanceをだせるように
                    return self.__end_negotiation(action_list, [True, action])
                elif self.__rule.get_type() == absNegoRule.DeadlineType.Time and \
                    not self.__rule.__proceed_negotiation():
                    return self.__end_negotiation(action_list, [False])
            # if is_printing and len(action_list) % print_times == 0:
            #     self.display.update(action_list)
            if self.__rule.get_type() == absNegoRule.DeadlineType.Round:
                can_proceed = self.__rule.proceed_negotiation()
        print("fail to get agreement")
        return self.__end_negotiation(action_list, [False])


    def __is_valid_action(self, action: agentAction.AbstractAction, action_len: int) -> bool:
        if isinstance(action, agentAction.Accept) and action_len == 0:
            raise ValueError('first accept error in agent_id:', action.get_agent_id())
        # elif isinstance(action, agentAction.Offer) and not self.__utilities.is_valid_bid(action.get_bid()):
        #     raise ValueError('bid index error in agent_id:', action.get_agent_id())
        return True

    def __is_finished_negotiation(self, action: agentAction.AbstractAction) -> bool:
        if isinstance(action, agentAction.EndNegotiation):
            return True
        elif isinstance(action, agentAction.Accept):
            self.__accept_num += 1
            if self.__accept_num == len(self.__agent_list):
                return True
        else:
            self.__accept_num = 1
        return False
    
    def __end_negotiation(self, actions, agreement) -> bool:
        for agent in self.__agent_list:
            agent.receive_end_negotiation()
        self.__action_list_list.append(actions)
        self.__get_agreement_list.append(agreement)
        return True

    def get_agent_num(self):
        """
        自動交渉に参加するエージェントの数を返す
        :rtype: int
        :return: 自動交渉に参加するエージェントの数
        """
        return len(self.__agent_list)


def test(is_printed=True, is_notebook=False):
    """
    Jupiterをテスト実行する
    :param bool is_printed: 描画するかどうかのフラグ
    :param bool is_notebook: notebook上での描画かどうか
    """
    here = os.path.dirname(os.path.abspath(__file__))
    simulator = MainSimulator(absNegoRule.DeadlineType.Round, 180,
                      here + '/Scenarios/Domain2/Domain2.xml',
                      [
                          here + '/Scenarios/Domain2/Domain2_util1.xml',
                          here + '/Scenarios/Domain2/Domain2_util2.xml'
                      ])
                
    module = importlib.import_module('agents.linearAgent')
    simulator.set_agent(module, 'LinearAgent', "LinearAgent1")
    module = importlib.import_module('agents.concederAgent')
    simulator.set_agent(module, 'ConcederAgent', "ConcederAgent1")

    simulator.do_negotiation(is_printing=True, print_times=1)

    # if is_notebook:
    #     simulator.set_notebook_flag()
    #     simulator.do_negotiation(is_printing=False, print_times=1)
    #     simulator.display.plot_initialize()
    #     simulator.display.plot2_notebook(simulator.get_action_list_list()[-1],
    #                                    simulator.get_agreement_list()[-1])
    #     # jupiter.display.show()
    # else:
    #     simulator.do_negotiation(is_printing=True, print_times=1)
    # # jupiter.display.delete_plot()
    # simulator.display.show()
    return 0

# test()