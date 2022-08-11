from pandas import DataFrame, to_datetime
from binance.client import Client
from matplotlib import pyplot as plt
import json
import pandas as pd

if __name__ == "__main__":
    api_key = ''
    api_secret = ''
    with open('api.json', 'r') as f:
        doc = json.load(f)
        api_key = doc['API_DEMO_KEY']
        api_secret = doc['API_DEMO_SECRET']

    client = Client(api_key, api_secret, testnet=True)

    klines = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_1DAY, "60 days ago UTC")

    df_klines = DataFrame(klines)
    df_close = df_klines.iloc[:, :6]

    df_close.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
    df_close = df_close.set_index("Time")
    df_close.index = to_datetime(df_close.index, unit="ms")
    df_close = df_close.astype("float")
    print(df_close)
    df_close["Close"].plot()
    plt.show()