# -*- coding: utf-8 -*-

from typing import Tuple, Dict
import pandas as pd

import json


def read_api_keys(path: str) -> Tuple:
    with open(path, 'r') as f:
        doc = json.load(f)
        api_key = doc['API_DEMO_KEY']
        api_secret = doc['API_DEMO_SECRET']
        return api_key, api_secret


def create_frame_from_socket(klines: Dict) -> pd.DataFrame:
    frame = pd.DataFrame([klines])
    frame = frame.loc[:, ['T', 'o', 'h', 'l', 'c', 'v']]
    frame.rename(columns=COLUMNS_NAME_MAP, inplace=True)
    frame.set_index('Time', inplace=True)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype('float')
    return frame


def right_rounding(lot_size: float) -> int:
    splitted = format(lot_size, 'f').split('.')

    if float(splitted[0]) == 1:
        return 0
    else:
        return len(splitted[1])


COLUMNS_NAME_MAP = {'T': 'Time',
                    'o': 'Open',
                    'h': 'High',
                    'l': 'Low',
                    'c': 'Close',
                    'v': 'Volume'
                    }

OHLC_COLUMNS = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume' ]