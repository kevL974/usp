import asyncio
import json
from pandas import DataFrame, to_datetime
from binance import AsyncClient, BinanceSocketManager
from binance.enums import *
from typing import Dict, Tuple
from strategies.Strategy import Strategy
from strategies.ROCStrategy import ROCStrategy

COLUMNS_NAME_MAP = {'T': 'Time',
                    'o': 'Open',
                    'h': 'High',
                    'l': 'Low',
                    'c': 'Close',
                    'v': 'Volume'
                    }


def read_api_keys() -> Tuple:
    with open('./ressources/api.json', 'r') as f:
        doc = json.load(f)
        api_key = doc['API_DEMO_KEY']
        api_secret = doc['API_DEMO_SECRET']
        return api_key, api_secret


def create_frame_from_socket(klines: Dict) -> DataFrame:
    frame = DataFrame([klines])
    frame = frame.loc[:, ['T', 'o', 'h', 'l', 'c', 'v']]
    frame.rename(columns=COLUMNS_NAME_MAP, inplace=True)
    frame.set_index('Time', inplace=True)
    frame.index = to_datetime(frame.index, unit='ms')
    frame = frame.astype('float')
    return frame


async def run_bot(client: AsyncClient, strat: Strategy, quoteOrderQty: float, symbol: str = 'ETHUSDT',
                  interval: str = '1m') -> None:
    bm = BinanceSocketManager(client)

    open_position = False

    async with bm.kline_socket(symbol=symbol, interval=interval) as stream:

        df = DataFrame()
        num_order = 0
        MAX_ORDER = 3
        while num_order < MAX_ORDER:
            res = await stream.recv()
            frame = create_frame_from_socket(res['k'])
            df = df.append(frame)
            if not open_position:
                if strat.out_position_with_historical(frame, df):
                    # create_order -> buy
                    client.get
                    order = client.create_order(symbol=symbol,
                                                      side=SIDE_BUY,
                                                      type=ORDER_TYPE_MARKET,
                                                      quoteOrderQty=quoteOrderQty)
                    print(order)
                    open_position = True
                else:
                    print(df)

            if open_position:
                if strat.in_position_with_historical(frame, df, order):
                    # create_order -> sell
                    order = client.create_order(symbol=symbol,
                                                side=SIDE_SELL,
                                                type=ORDER_TYPE_MARKET,
                                                quantity=float(order['fills'][0]['qty']))
                    print(order)
                    sellprice = float(order['fills'][0]['price'])
                    print(f'You made {(sellprice-quoteOrderQty)}$')
                    open_position = False
                    num_order += 1


async def bot(api_key: str, api_secret: str, testnet: bool = True):
    client = await AsyncClient.create(api_key, api_secret, testnet=testnet)

    await run_bot(client, quoteOrderQty=150, strat=ROCStrategy())


if __name__ == '__main__':
    api_key, api_secret = read_api_keys()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot(api_key, api_secret, testnet=True))
