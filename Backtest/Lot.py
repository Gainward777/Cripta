from abc import abstractmethod
import pandas as pd

class Lot(object):
    def __init__(self, start_deposit:float=None, lot_coef: float=0.1, risk_coef:float=0.01, 
                 leverage:float=1, is_dinamic: bool=True):
        self.lot_coef=lot_coef
        self.is_dinamic=is_dinamic
        self.risk_coef=risk_coef
        self.leverage=leverage
        self.start_deposit=start_deposit

    @abstractmethod
    def get_dinamic_lot(self, deposit:float, sl:float, price:float) -> tuple:
        pos_volume=self.lot_coef*(deposit*self.risk_coef/abs(sl/price/100))*self.leverage
        lot=pos_volume/price
        return (pos_volume, lot)
    
    @abstractmethod
    def get_static_lot(self, deposit:float, price:float) -> tuple:
            if self.start_deposit==None:
                dep=deposit
            else: dep=self.start_deposit
            pos_volume=(dep*self.risk_coef)*self.leverage
            lot=pos_volume/price
            return (pos_volume, lot)

    def get_volume_and_lot(self, deposit:float, sl:float, price:float) -> tuple:
        #price=df['close']
        if not self.is_dinamic:
            return self.get_static_lot(deposit, price)
        else: return self.get_dinamic_lot(deposit, sl, price)