from abc import ABC, abstractmethod

import pandas as pd
from typing import Dict
from binance import Client
from datetime import timedelta

import ta


class Strategy(ABC):

    NAME: str
    INTERVAL: str
    PERIOD: str

    def get_data_parameters(self) -> Dict:
        return {'interval': self.__class__.INTERVAL,
                'period': self.__class__.PERIOD}

    @abstractmethod
    def apply_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        ...

    @abstractmethod
    def is_take_profit_condition(self, df: pd.DataFrame, order_status: Dict) -> bool:
        ...


class Sma200Rsi10Strategy(Strategy):

    NAME: str = 'SMA200_&_RSI10'
    INTERVAL: str = Client.KLINE_INTERVAL_15MINUTE
    PERIOD: str = '3000 minutes ago UTC'

    def apply_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        df['SMA_200'] = ta.trend.sma_indicator(df.Close, window=200)
        df['stochrsi_10'] = ta.momentum.stochrsi_k(df.Close, window=10)
        df.dropna(inplace=True)
        df['Buy'] = (df.Close > df.SMA_200) & (df.stochrsi_10 < 0.05)
        return df

    def is_take_profit_condition(self, df: pd.DataFrame, order_status: Dict) -> bool:
        cond1_is_benef_tp = df.Close.values > float(order_status['price'])
        cond2_is_benef_grows = pd.to_datetime('now') >= (pd.to_datetime(order_status['updateTime'], unit='ms') +
                                                         timedelta(minutes=150))
        return cond1_is_benef_tp or cond2_is_benef_grows
