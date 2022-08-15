import time

import ta
from datetime import timedelta
from binance import Client
from binance.enums import *
from typing import Dict
from bot_binance.utils import read_api_keys, OHLC_COLUMNS

import pandas as pd

pos_dict={'in_position': False}
def read_pos() -> pd.DataFrame:
    return pd.read_csv('./ressources/position.csv')


def init_wokspace(client: Client) -> pd.DataFrame:
    df_symbol_info = pd.DataFrame(client.get_exchange_info()['symbols'])
    df_pos = df_symbol_info[df_symbol_info.symbol.str.contains('USDT')][['symbol']]
    df_pos['position'] = 0
    df_pos['price'] = 0.0
    df_pos['time'] = 'NA'
    df_pos.to_csv('./ressources/position.csv')
    return df_pos


def get_historical_data(client: Client, coin: str, interval: str, ago: str):
    data = client.get_historical_klines(coin, interval, ago)
    frame = pd.DataFrame(data)
    frame = frame[[0, 1, 2, 3, 4, 5]]
    frame.columns = OHLC_COLUMNS
    frame.drop(['Open', 'High', 'Low'], axis=1, inplace=True)
    frame.set_index('Time', inplace=True)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype('float')
    return frame


def get_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['SMA_200'] = ta.trend.sma_indicator(df.Close, window=200)
    df['stochrsi_10'] = ta.momentum.stochrsi_k(df.Close, window=10)
    df.dropna(inplace=True)
    df['Buy'] = (df.Close > df.SMA_200) & (df.stochrsi_10 < 0.05)
    return df


def price_calc(client: Client, symbol: str, limit: float) -> float:
    raw_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
    dec_len = len(str(raw_price).split('.')[1])
    price = raw_price * limit
    return round(price, dec_len)


def right_rounding(lot_size: float) -> int:
    splitted = str(lot_size).split('.')

    if float(splitted[0]) == 1:
        return 0
    else:
        return len(splitted[1])


def quantity_calc(client: Client, symbol: str,  investment: float) -> float:
    info = client.get_symbol_info(symbol=symbol)
    lot_size = float([i for i in info['filters'] if i['filterType'] == 'LOT_SIZE'][0]['QtyMin'])
    price = price_calc(symbol)
    qty = round(investment/price, right_rounding(lot_size))
    return qty


def buy(client: Client, symbol: str, investment: float) -> Dict:
    order = client.order_limit_buy(symbol=symbol,
                                   price=price_calc(client, symbol, 0.98),
                                   quantity=quantity_calc(client, symbol, investment))
    print(order)
    pos_dict['in_position'] = True
    return order


def sell(client: Client, symbol: str,  qty: float) -> Dict:
    order = client.create_order(symbol=symbol,
                                 side=SIDE_SELL,
                                 type=ORDER_TYPE_MARKET,
                                 quantity=qty)
    print(order)
    pos_dict['in_position'] = False
    return order


def check_buy(df: pd.DataFrame) -> bool:
    if not pos_dict['in_position']:
        if df.Buy.values:
            return True
    else:
        print('Already un position')
        return False


def check_sell(client: Client, symbol: str, order: Dict, df: pd.DataFrame):
    order_status = client.get_order(symbol=symbol, orderId=order['orderId'])
    if pos_dict['in_position']:
        if order_status['status'] == 'NEW':
            print('Buy limit order is still pending')
        elif order_status['status'] == 'FILLED':
            cond1_is_benef_tp = df.Close.values > float(order_status['price'])
            cond2_is_benef_grows = pd.to_datetime('now') >= (pd.to_datetime(order_status['updateTime'], unit='ms') +
                                                             timedelta(minutes=150))
            #cond3 -> stop-loss
            if cond1_is_benef_tp or cond2_is_benef_grows:
                sell(client,symbol,order_status['origQty'])
        else:
            print('Currently not in position, no checks for selling')

def bot(api_key: str, api_secret: str, testnet: bool = True):
    client = Client(api_key, api_secret, testnet=testnet)
    pos = None
    try:
        pos = read_pos()
    except FileNotFoundError:
        pos = init_wokspace(client)

    while True:
        for coin in pos.symbol:
            hist_frame = get_historical_data(client, coin, Client.KLINE_INTERVAL_15MINUTE, "3000 minutes ago UTC")
            df = get_indicators(hist_frame)
            if check_buy(df):
                current_order = buy(client, coin, 100)
            try:
                check_sell(client, coin, current_order, df)
            except:
                print(f'{coin} : Not an order yet')
        time.sleep(60)

if __name__ == '__main__':
        api_key, api_secret = read_api_keys('../ressources/api.json')
        bot(api_key, api_secret, testnet=True)
