from abc import abstractmethod
import pandas as pd


class TP(object):
    def __init__(self, is_dinamic: bool=False, coef: float=0.5):
        self.is_dinamic=is_dinamic
        self.coef=coef

    @abstractmethod
    def get_dinamic_tp(self, df: pd.DataFrame, position_type:int) -> float:
        pass    

    def get_tp(self, df: pd.DataFrame, position_type:int) -> float:
        price=df['close'].values
        if not self.is_dinamic:
            if position_type==-1 or position_type==2:
                return price[-1]-price[-1]*self.coef
            else:
                return price[-1]+price[-1]*self.coef
        else: return self.get_dinamic_tp(df, position_type)




