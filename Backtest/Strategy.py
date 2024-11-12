from abc import ABC, abstractmethod
import pandas as pd


class Strategy(ABC):

    @abstractmethod
    def get_signal(self, df: pd.DataFrame) -> tuple:
        # return format must be duble tuple: ((open/neutral/close, buy/sell, strategy_index)) 
        # or ((open/neutral/close, buy/sell, strategy_index), (open/neutral/close, buy/sell, strategy_index))
        # where:
        # open/neutral/close - 1 / None / 0
        # buy/sell - 1 / -1 or 2
        # strategy_index - index current main strategy part, if main strategy contains substrategies, 
        # if not, strategy_index must be just 1
        #
        # for example:
        # open buy position signal: (1, 1, 1)
        # open sell position signal: (1, -1, 1)
        # neutral position signal: (None, None, 1)
        # close position signal: (0, 1, 1)
        # 
        #return (.)(.)
        pass
                




