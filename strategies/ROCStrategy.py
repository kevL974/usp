from strategies.Strategy import Strategy, Action
from pandas import DataFrame, to_datetime
from ta.momentum import roc
from typing import Dict


class ROCStrategy(Strategy):
    NAME: str = "ROC"

    def __init__(self):
        super().__init__()

    def out_position(self, new_frame: DataFrame) -> bool:
        return False

    def out_position_with_historical(self, new_frame: DataFrame, hist_frame: DataFrame) -> bool:
        return (roc(hist_frame.Close, 30).iloc[-1] > 0) and \
               (roc(hist_frame.Close, 30).iloc[-1] > roc(hist_frame.Close, 30).iloc[-2])

    def in_position(self, new_frame: DataFrame) -> bool:
        return False

    def in_position_with_historical(self, new_frame: DataFrame, hist_frame: DataFrame, option: Dict) -> bool:
        subdf = hist_frame[hist_frame.Time >= to_datetime(option['transactTime'], unit='ms')]
        sell = False
        if len(subdf) > 1:
            subdf['highest'] = subdf.Close.cumMax()
            subdf['trailingStop'] = subdf['highest'] * 0.995

            if (subdf.iloc[-1].Close < subdf.iloc[-1].trailingStop) or \
                    (subdf.iloc[-1].Close / float(option['fills'][0]['price']) > 1.002):
                sell = True

        return sell

    def _init(self) -> None:
        return None