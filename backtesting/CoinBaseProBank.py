# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 13:21:26 2021

@author: kevL974
"""
from abc import ABC
from backtesting.Bank import Bank
from typing import Dict, List, Tuple


class CoinbaseProBank(Bank, ABC):
    NAME: str = 'CoinBase pro'
    URL: str = 'https://pro.coinbase.com/'
    API: str = 'https://api.exchange.coinbase.com/'  # 'https://api.pro.coinbase.com/'
    TIME: str = ''
    # 'GMT12:00:00'

    def __init__(self):
        super().__init__()

    def get_currencies(self) -> List:
        return self._request(self._make_request('products'))

    def get_historical_data(self, currency: str, start: str, end: str, granularity: int) -> List:
        granularity = 86400
        print(f'Request : {CoinbaseProBank.API}products/{currency}/candles?start={start}{CoinbaseProBank.TIME}'
              f'&end={end}{CoinbaseProBank.TIME}&granularity={granularity}')
        return self._request(self._make_request(
            f'products/{currency}/candles?start={start}{CoinbaseProBank.TIME}&end={end}{CoinbaseProBank.TIME}'
            f'&granularity={granularity}'))
