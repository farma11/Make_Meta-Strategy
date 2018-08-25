# coding: UTF-8

from enum import IntEnum, unique
from abc import ABCMeta, abstractmethod
import time

@unique
class DeadlineType(IntEnum):
    '''
    列挙型
    自動交渉のtypeを表す
    '''
    Round = 1
    Time = 2

class AbsNegoRule(metaclass=ABCMeta):
    """
    自動交渉を行う際のルール
    各ルールはこのクラスを継承すること
    """
    @abstractmethod
    def __init__(self, time_max_ms: int):
        self.__type = None
        self.__time_now = 0
        self.__max_time = time_max_ms
        pass

    def __start_negotiation(self):
        pass

    def __proceed_negotiation(self):
        pass

    @abstractmethod
    def get_type(self):
        """
        自動交渉のタイプを返す

        :rtype: TypeOfNegotiation
        :return: 自動交渉のタイプ
        """
        return self.__type

    @abstractmethod
    def get_time_now(self):
        """
        交渉中における，正規化された現在の時刻を返す

        :rtype: float
        :return: 正規化された現在の時刻
        """
        return float(self.__time_now) / self.__max_time


class NegotiationRuleRound(AbsNegoRule):
    """
    自動交渉を行う際のルールの1つ
    Round制
    """
    def __init__(self, time_max_round: int):
        '''
        Round制のとき用いる自動交渉のルール

        :param int time_max_turn: 最大ターン数
        '''
        self.__type = DeadlineType.Round
        self.__max_time = time_max_round
        self.__time_now = 0
        pass

    def start_negotiation(self):
        self.__time_now = 1

    def proceed_negotiation(self):
        self.__time_now += 1
        if self.__time_now <= self.__max_time:
            return True
        else:
             return False

    def get_time_max(self):
        """
        その交渉における最大ターン数を返す

        :rtype: int
        :return: その交渉における最大ターン数
        """
        return self.__max_time

    def get_time_now(self):
        """
        交渉中における，正規化された現在の時刻を返す

        :rtype: float
        :return: 正規化された現在の時刻
        """
        return float(self.__time_now - 1) / self.__max_time

    def get_type(self):
        """
        自動交渉のタイプを返す．

        :rtype: TypeOfNegotiation.Round
        :return: 自動交渉のタイプ
        """
        return self.__type

class NegotiationRuleTime(AbsNegoRule):
    """
    自動交渉を行う際のルールの1つ
    時間制
    """
    def __init__(self, time_max_s: float):
        '''
        time制のとき用いる自動交渉のルール

        :param float time_max_s: 最大の交渉時間．単位は秒．
        '''
        self.__type = DeadlineType.Time
        self.__max_time = time_max_s
        self.__time_now = 0
        pass

    def start_negotiation(self):
        self.__time_begining = time.time()

    def proceed_negotiation(self):
        self.__time_now = time.time() - self.__time_begining
        if self.__time_now <= self.__max_time:
            return True
        else:
             return False

    def get_time_max(self):
        """
        その交渉における最大の時間を返す

        :rtype: float
        :return: その交渉における最大の交渉時間．単位は秒
        """
        return self.__max_time

    def get_time_now(self):
        """
        交渉中における，正規化された現在の時刻を返す

        :rtype: float
        :return: 正規化された現在の時刻
        """
        self.__time_now = time.time() - self.__time_begining
        return float(self.__time_now) / self.__max_time
        #return self.__time_now

    def get_type(self):
        """
        自動交渉のタイプを返す．

        :rtype: TypeOfNegotiation.Time
        :return: 自動交渉のタイプ
        """
        return self.__type