# -*- coding: utf-8 -*-

from typing import Tuple, Dict
from pandas import DataFrame, to_datetime

import json


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


COLUMNS_NAME_MAP = {'T': 'Time',
                    'o': 'Open',
                    'h': 'High',
                    'l': 'Low',
                    'c': 'Close',
                    'v': 'Volume'
                    }

OHLC_COLUMNS = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume' ]