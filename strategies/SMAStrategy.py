import Strategy


class MMAStrategy(Strategy):
    NAME: str = 'MMA'

    def __init__(self, st: int = 7, lt: int = 25):
        self.sl = st
        self.lt = lt

