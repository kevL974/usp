# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 16:10:46 2021

@author: kevL974
"""

from typing import List


class VirtualWallet:
    def __init__(self, value: float):
        self._value = value
        self._coins = 0
        self._transactions = []

    def get_total_funds(self) -> float:
        return self._value

    def get_total_coins(self) -> float:
        return self._coins

    def get_transactions(self) -> List:
        return self._transactions

    def show_transactions(self) -> None:
        for transaction in self._transactions:
            if transaction[0] == 'buy':
                print(
                    f'{transaction[3]} - {transaction[4]} : achat de {transaction[2]} coins '
                    f'pour {transaction[1]} € (taux : {transaction[5]})')
            else:
                print(
                    f'{transaction[3]} - {transaction[4]} : vente de {transaction[2]} coins '
                    f'pour {transaction[1]} € (taux : {transaction[5]})')

    def buy(self, value: float, coin_rate: float, date: str, time: str, num_op: int) -> None:
        if value > self._value:
            print('Not enough funds in wallet')
        self._value -= value
        self._coins = value / coin_rate
        self._transactions.append(('buy', value, self._coins, date, time, coin_rate, num_op))

    def sell(self, coins: float, coin_rate: float, date: str, time: str, num_op: int) -> None:
        if coins > self._coins:
            print('Not enough coins in wallet')
        self._coins -= coins
        self._value = coins * coin_rate
        self._transactions.append(('sell', self._value, coins, date, time, coin_rate, num_op))