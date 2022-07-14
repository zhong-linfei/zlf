import math
from TimeTransformer import TimeTransformer
from ComtradeRecord import ComtradeRecord
import pandas as pd

class ProcessComtradeObj:
    def __init__(self, comtradeObj, filter_flag):
        self.comtradeObj = comtradeObj
        self.filter_flag = filter_flag
    
    def preprocess_comtradeObj(self):
        N = self.comtradeObj.cfg_data['endsamp']
        samp = self.comtradeObj.cfg_data['samp']
        if sum(N) != len(self.comtradeObj.cfg_data["A"][0]["values"]):
            pass
        else:
            # 连续化
            for i in range(len(N)):
                if i >= 1:
                    N[i] = N[i] + N[i - 1]
        time_dataframe = TimeTransformer(self.comtradeObj).excute()
        filtered_data = self.filter_data(time_dataframe, self.comtradeObj, self.filter_flag)
        if filtered_data is not None:     
            return pd.concat([filtered_data, pd.DataFrame(samp,columns = ['samp']), pd.DataFrame(N, columns=['endsamp'])],axis = 1)
        
    # 过滤单个文件的电压或电流数据
    # 0：电压
    # 1：电流
    def filter_data(self, time_dataframe, comtradeObj, flag):
        result_filter_dataframe = pd.concat([time_dataframe])
        if flag == 0:
            name_list1 = ['Ua', 'Ub', 'Uc']
            name_list2 = ['UA', 'UB', 'UC']
        else:
            name_list1 = ['Ia', 'Ib', 'Ic']
            name_list2 = ['IA', 'IB', 'IC']
        for i in range(comtradeObj.cfg_data['#A']):
            if any(name in comtradeObj['A'][i]['ch_id'] for name in name_list1) or any(name in comtradeObj['A'][i]['ch_id'] for name in name_list2):
                AnalogChannelData = comtradeObj['A'][i]['values']
                AnalogChannelData_DataFrame = pd.DataFrame(AnalogChannelData)
                AnalogChannelData_DataFrame.columns = [comtradeObj['A'][i]['ch_id']]
                result_filter_dataframe = pd.concat([result_filter_dataframe, AnalogChannelData_DataFrame], axis=1)
        if len(result_filter_dataframe.shape)==2 and result_filter_dataframe.shape[1]>1:
            return result_filter_dataframe
    
    def cutting_data(self, raw_filter_dataframe):
        samp = raw_filter_dataframe['samp']
        endsamp = raw_filter_dataframe['endsamp']
        samp_arr = []
        filter_dataframe = raw_filter_dataframe.iloc[:, :-2]
        cutting_data_arr = []
        for i in range(len(endsamp)):
            if(math.isnan(endsamp[i])):
                break
            if samp[i]<=1000:
                continue
            samp_arr.append(int(samp[i]))
            if(i==0):
                cutting_data_arr.append(filter_dataframe.iloc[:int(endsamp[i]),:])
            else:
                cutting_data_arr.append(filter_dataframe.iloc[int(endsamp[i-1]):int(endsamp[i]),:])   
        if len(cutting_data_arr)>0:
            return cutting_data_arr, samp_arr
        
    def excute(self):
        filtered_data = self.preprocess_comtradeObj()
        return filtered_data
'''
        if filtered_data is None:
            return
        cutting_result = self.cutting_data(filtered_data)
        if cutting_result is None:
            return
        
        return cutting_result[0], cutting_result[1]
'''
        
        
        
        
        
        