# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 19:25:28 2021

@author: kevla
"""

from usp.TimeMachine import TimeMachine
from usp.CoinBaseProBank import CoinbaseProBank
from usp.Strategy import Strategy
from usp.VirtualWallet import VirtualWallet

if __name__ == '__main__':
    wallet = VirtualWallet(1000)

    strat = Strategy('5 percent')
    strat.def_rule('buy', 'down', 5)
    strat.def_rule('sell', 'up', 5)

    timeMachine = TimeMachine(start='2021-01-04', end='2021-08-04')
    timeMachine.choose_bank(CoinbaseProBank)
    timeMachine.attach_wallet(wallet)
    timeMachine.init_db()
    timeMachine.get_data('ETH')
    transactions = timeMachine.test_strategy(strat)
    timeMachine.show_data(type='graph', extra=transactions)

    #timeMachine.__del__()
