# -*- coding: utf-8 -*-

from typing import Callable, Dict
from binance import Client
from binance.enums import *
from bot_binance.utils import OHLC_COLUMNS, right_rounding, read_api_keys
from strategies.Strategy import Strategy, Sma200Rsi10Strategy

import pandas as pd
import logging

logger_info_order = logging.getLogger('logger_order')
logger_info = logging.getLogger('logger_info')


class Bot:

    def __init__(self, api_key: str, api_secret: str, position_file: str, testnet: bool):
        self.client: Client = Client(api_key=api_key, api_secret=api_secret, testnet=testnet)
        self.path_positions = position_file
        self.positions: pd.DataFrame = self.__initialisation()
        self._strat: Strategy = None

    def __initialisation(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.path_positions)
        except FileNotFoundError:
            df_symbol_info = pd.DataFrame(self.client.get_exchange_info()['symbols'])
            df_pos = df_symbol_info[df_symbol_info.symbol.str.contains('USDT')][['symbol']]
            df_pos['position'] = 0
            df_pos['qty'] = 0.0
            df_pos['orderId'] = 'NA'
            df_pos.to_csv(self.path_positions, index=False)
            return df_pos

    def choose_strategy(self, strategy: Callable[[], Strategy]):
        self._strat = strategy()

    def get_historical_data(self, coin: str) -> pd.DataFrame:
        data = self.client.get_historical_klines(coin, self._strat.INTERVAL, self._strat.PERIOD)
        frame = pd.DataFrame(data)
        frame = frame[[0, 1, 2, 3, 4, 5]]
        frame.columns = OHLC_COLUMNS
        frame.drop(['Open', 'High', 'Low'], axis=1, inplace=True)
        frame.set_index('Time', inplace=True)
        frame.index = pd.to_datetime(frame.index, unit='ms')
        frame = frame.astype('float')
        return frame

    def apply_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._strat.apply_strategy(df)

    def buy(self, symbol: str, investment: float) -> Dict:
        order = self.client.order_limit_buy(symbol=symbol,
                                            price=self.price_calc(symbol, 0.98),
                                            quantity=self.quantity_calc(symbol, investment))

        logger_info_order.info(f'BUY orderId {order["orderId"]}: '
                               f'{order["origQty"]} {order["symbol"]} for {order["price"]} ')
        self.change_positions(symbol, is_open=True, qty=float(order['origQty']), order_id=order['orderId'])
        return order

    def sell(self, symbol: str, qty: float) -> Dict:
        order = self.client.create_order(symbol=symbol,
                                         side=SIDE_SELL,
                                         type=ORDER_TYPE_MARKET,
                                         quantity=qty)

        logger_info_order.info(f'SELL orderId {order["orderId"]}: '
                               f'{order["origQty"]} {order["symbol"]} for {order["fills"][0]["price"]} >'
                               f' {float(order["origQty"]) * float(order["fills"][0]["price"])}')
        self.change_positions(symbol, is_open=False, qty=0, order_id=order['orderId'])
        return order

    def check_buy(self, symbol: str, df: pd.DataFrame) -> bool:
        open_position = self.is_open_position(symbol)
        if not open_position:
            if df.Buy.values:
                return True
        else:
            logger_info.info('Already un position')
            return False

    def check_sell(self, symbol: str, df: pd.DataFrame):
        order_status = self.client.get_order(symbol=symbol, order_id=self.get_order_id(symbol))
        if self.is_open_position(symbol):
            if order_status['status'] == 'NEW':
                logger_info.info('Buy limit order is still pending')
            elif order_status['status'] == 'FILLED':

                if self._strat.is_take_profit_condition(df, order_status):
                    self.sell(symbol, order_status['origQty'])
            else:
                logger_info.info('Currently not in position, no checks for selling')

    def price_calc(self, symbol: str, limit: float) -> float:
        raw_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
        dec_len = len(str(raw_price).split('.')[1])
        price = raw_price * limit
        return round(price, dec_len)

    def quantity_calc(self, symbol: str, investment: float) -> float:
        info = self.client.get_symbol_info(symbol=symbol)
        lot_size = float([i for i in info['filters'] if i['filterType'] == 'LOT_SIZE'][0]['minQty'])
        price = self.price_calc(symbol, 0.98)
        qty = round(investment / price, right_rounding(lot_size))
        return qty

    def is_open_position(self, symbol: str) -> bool:
        if self.positions.loc[self.positions['symbol'] == symbol, 'position'].values[0] == 1:
            return True
        else:
            return False

    def get_order_id(self, symbol: str) -> str:
        return self.positions.loc[self.positions.symbol == symbol, 'orderId'][0]

    def change_positions(self, symbol: str, is_open: bool, qty: float, order_id: str) -> None:
        if is_open:
            self.positions.loc[self.positions.symbol == symbol, 'position'] = 1
            self.positions.loc[self.positions.symbol == symbol, 'orderId'] = order_id
        else:
            self.positions.loc[self.positions.symbol == symbol, 'position'] = 0
            self.positions.loc[self.positions.symbol == symbol, 'orderId'] = 'NA'

        self.positions.loc[self.positions.symbol == symbol, 'qty'] = qty
        self.write_positions()

    def write_positions(self) -> None:
        self.positions.to_csv(self.path_positions, index=False)

    def run(self):
        for coin in self.positions.symbol:
            hist_frame = self.get_historical_data(coin)
            df = self.apply_indicators(hist_frame)
            if self.check_buy(coin, df):
                self.buy(coin, 100)

            try:
                self.check_sell(coin, df)
                logger_info_order.info(f'Current assets UDST = {self.client.get_asset_balance(asset="USDT")["free"]}')
            except:
                logger_info.info(f'{coin} : Not an order yet')
