import pandas as pd
from tqdm import tqdm
from . import SL
from . import TP
from . import Strategy
import copy
from . import Lot


class Backtest(object):

    def __init__(self, strategy: Strategy, sl: SL, tp: TP, lot:Lot, deposit: int=10000, 
                 spred_coef: float=0.1, look_back_window: int=999, is_check_sl:bool=True, 
                 is_check_tp:bool=True): #leverage:float=0.1

        self.strategy=strategy
        self.sl=sl
        self.tp=tp
        self.deposit=deposit
        self.spred_coef=spred_coef
        self.look_back_window=look_back_window
        self.is_check_sl=is_check_sl
        self.is_check_tp=is_check_tp
        self.lot=lot
        
    
    def run(self, df: pd.DataFrame)->tuple:

        positions={1: {}, -1: {}} # format {1: {2: {'stat_price': 122.1, 'sl': 99, 'tp': 333}}}
        past_positions=[]

        for i in tqdm(range(1, len(df))):            
            current_sentence=df.iloc[:i,:]
            if len(current_sentence)>(2*self.look_back_window): 
                current_sentence=current_sentence.iloc[i-self.look_back_window:i,:]

            currtent_candle=df.iloc[i,:]

            signals=self.strategy.get_signal(current_sentence) 
            
            if self.is_check_sl:
            #update SL in current positions
                if self.sl.is_dinamic:
                    self.updete_sl(positions, current_sentence, self.sl)
                #check if price triggered SL
                self.deposit=self.check_sl(currtent_candle, positions[1], positions[-1], past_positions, 
                                               self.deposit, self.spred_coef)
            if self.is_check_tp:
            #update SL in current positions
                if self.tp.is_dinamic:
                    self.updete_tp(positions, current_sentence, self.tp)
                #check if price triggered TP
                self.deposit=self.check_tp(currtent_candle, positions[1], positions[-1], past_positions, 
                                              self.deposit, self.spred_coef)

                #self.deposit=self.check_sl_tp(currtent_candle, positions[1], positions[-1], past_positions, self.deposit, self.spred_coef) 
            
            for signal in signals:
                if signal[0]==1:
                    if not self.is_exist(positions, signal):                        
                        sl=self.sl.get_sl(current_sentence,signal[1], True)
                        tp=self.tp.get_tp(current_sentence, signal[1])
                        pos_volume, lot = self.lot.get_volume_and_lot(self.deposit, sl, currtent_candle['close']) 
                        self.set_position(currtent_candle['close'], currtent_candle['date'], signal, positions, self.spred_coef, sl, tp, pos_volume, lot)
                elif signal[0]==0:
                    if self.is_exist(positions, signal):

                        self.deposit=self.close_by(positions[signal[1]], currtent_candle['close'], past_positions, signal[2], self.deposit,
                                                  self.spred_coef, currtent_candle['date'], 'signal', signal[1])                        
                    
        return (self.deposit, past_positions)


    def is_exist(self, positions:dict, signal:tuple) -> bool:
        try:
            positions[signal[1]][signal[-1]]
            return True
        except: return False


    def set_position(self, price:float, date: str, signal:tuple, positions:dict,spred_coef:float, sl:float, tp:float, volume:float, lot:float):
    
        if len(signal)>1:
            if signal[1]==1:
                positions[1][signal[-1]]=dict([('open_date', date), ('open_price',price+price*spred_coef), ('sl',sl), ('tp',tp), ('pos_volume', volume), ('lot', lot)])
            if signal[1]==-1 or signal[0]==2:
                positions[-1][signal[-1]]=dict([('open_date', date), ('open_price',price-price*spred_coef), ('sl',sl), ('tp',tp), ('pos_volume', volume), ('lot', lot)])


    def close_by(self, positions:dict, price:float, past_positions:list, key:int, 
                        deposit:float, spred_coef: float, date: str, key_name: str, position_type:int)->float:
        
        position=positions[key]
        position['position_type']=position_type

        if position_type==1:                             
            close_price=price-price*spred_coef
            deposit=deposit+(close_price-position['open_price'])*position['lot']
            
        elif position_type==-1 or position_type==2:                            
            close_price=price+price*spred_coef
            deposit=deposit+(position['open_price']-close_price)*position['lot']

        position['status']=f'closed_by_{key_name}'
        position['close_price']=close_price
        position['close_date']=date
        position['deposit_stat']=deposit
        past_positions.append(positions.pop(key))
        return deposit 
    


    def check_sl(self, currtent_candle:pd.DataFrame, buy_positions:dict, sell_positions:dict, 
                past_positions:list, deposit:float, spred_coef: float)->float:

        for key in tuple(copy.deepcopy(buy_positions).keys()):
            if currtent_candle['low']<=buy_positions[key]['sl'] and currtent_candle['high']>=buy_positions[key]['sl']: 
                deposit=self.close_by(buy_positions, buy_positions[key]['sl'], past_positions, key, deposit, spred_coef, 
                                      currtent_candle['date'], 'sl', 1)
                
        for key in tuple(copy.deepcopy(sell_positions).keys()):
            if currtent_candle['high']>=sell_positions[key]['sl'] and currtent_candle['low']<=sell_positions[key]['sl']:
                deposit=self.close_by(sell_positions, sell_positions[key]['sl'], past_positions, key, deposit, spred_coef, 
                                      currtent_candle['date'], 'sl', -1)                   
            
        return deposit



    def check_tp(self, currtent_candle:pd.DataFrame, buy_positions:dict, sell_positions:dict, 
                past_positions:list, deposit:float, spred_coef: float)->float:

        for key in tuple(copy.deepcopy(buy_positions).keys()):            
            if currtent_candle['high']>=buy_positions[key]['tp'] and currtent_candle['low']<=buy_positions[key]['tp']: 
                deposit=self.close_by(buy_positions, buy_positions[key]['tp'], past_positions, key, deposit, spred_coef, 
                                      currtent_candle['date'], 'tp', 1)

        for key in tuple(copy.deepcopy(sell_positions).keys()):            
            if currtent_candle['low']<=sell_positions[key]['tp'] and currtent_candle['high']>=sell_positions[key]['tp']:
                deposit=self.close_by(sell_positions, sell_positions[key]['tp'], past_positions, key, deposit, spred_coef, 
                                      currtent_candle['date'], 'tp', -1)

        return deposit


    #set sl into 
    def updete_sl(self, positions:dict, df: pd.DataFrame, sl:SL):
        for  pos_vector in positions:
            for key in positions[pos_vector]:
                sl_value=sl.get_sl(df,pos_vector)
                positions[pos_vector][key]['sl']=sl_value

    def updete_tp(self, positions:dict, df: pd.DataFrame, tp:TP):
        for  pos_vector in positions:
            for key in positions[pos_vector]:
                tp_value=tp.get_tp(df,pos_vector)
                positions[pos_vector][key]['tp']=tp_value


    


    def check_stat(self, backtes_results:tuple, started_deposit:int=10000):
        loses=[]
        wins=[]        
        for position in backtes_results[1]:
            if position['deposit_stat']<started_deposit:    
                loses.append(position)
            else:
                wins.append(position)
            started_deposit=position['deposit_stat']
        return len(loses), len(wins)