from abc import abstractmethod
import pandas as pd


class SL(object):
    def __init__(self, is_dinamic: bool=False, coef: float=0.25):
        self.is_dinamic=is_dinamic
        self.coef=coef

    @abstractmethod
    def get_dinamic_sl(self, df: pd.DataFrame, position_type:int, is_start:bool=False) -> float:        
        pass

    def get_sl(self, df: pd.DataFrame, position_type:int, is_start:bool=False) -> float:
        price=df['close'].values
        if not self.is_dinamic:
            if position_type==-1 or position_type==2:
                return price[-1]+price[-1]*self.coef
            else:
                return price[-1]-price[-1]*self.coef
        else: return self.get_dinamic_sl(df, position_type, is_start)




