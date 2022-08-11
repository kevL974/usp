# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 16:36:20 2021

@author: kevL974
"""
from sys import exit


class Strategy:
    def __init__(self, name: str):
        self._name = name
        self._trigger = {}

    def get_action(self, trigger_type: str) -> str:
        return self._trigger[trigger_type]['action']

    def get_rate(self, trigger_type: str) -> str:
        return self._trigger[trigger_type]['rate']

    def def_rule(self, trigger_type: str, trigger_action: str, rate: float) -> None:
        if trigger_type == 'buy':
            self._trigger['buy'] = {
                'action': trigger_action,
                'rate': rate
            }

        elif trigger_type == 'sell':
            self._trigger['sell'] = {
                'action': trigger_action,
                'rate': rate
            }

        else:
            print('Unknown action')
            exit(3)
