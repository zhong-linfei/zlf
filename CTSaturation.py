import numpy as np
from ProcessComtradeObj import ProcessComtradeObj
import datetime
pi = np.pi
class CTSaturation:
    def __init__(self,comtradeObj,path):
        self.log = ""
        self.comtradeObj=comtradeObj
        self.ProcessComtradeObj=ProcessComtradeObj(self.comtradeObj,1)
        filtered_data= self.ProcessComtradeObj.excute()
        
        if filtered_data is None:
            return
        cutting_result = self.ProcessComtradeObj.cutting_data(filtered_data)
        if cutting_result is None:
            return
        filter_data=cutting_result[0]
        samp=cutting_result[1]
        for i in range(len(samp)):
            window_size =int(20/(1000/samp[i]))

            for j in range(filter_data[i].shape[1] - 1):
                tep_phase_data = filter_data[i].iloc[:, [0,j+1]]
                self.checkwave(tep_phase_data, tep_phase_data.index[0],window_size,comtradeObj,path)

    def checkwave(self, values, i, window_size, comtradeObj, path):
        tep_phase_data=values
        values=values.iloc[:,1]
        k = 0
        start = end= i
        maxindex = values.index[len(values)-1]
        minindex = values.index[0]
        while i < maxindex:
            if values[i] < -10:
                min = i
                i += 1
            else:
                i = i+1
                continue
            if i >= maxindex:
                break
            while values[i] <= values[min]:
                min = i
                i = i+1
                if i >= maxindex:
                    break
            if i >= maxindex:
                break

            zero=i
            while values[i] < 0:
                zero = i
                i += 1
                if i >= maxindex:
                    break
            max = zero
            if i == maxindex:
                break
            time1 = zero-min+1
            while values[i] >= values[max]:
                    max = i
                    i += 1
                    if i >= maxindex:
                        break
            time2 = max-zero
            if time1 != 0:
                bizhi = time2/time1
            ratio=self.gradientratio(values, max, zero, min)

            if ratio<2:
                i=zero
                continue

            num=max-min

            if 1.5 < bizhi < 3.4 and num >= 0.5*window_size and values[max] > 10:

                end=max+num-minindex
                if k==0:
                    start=min-minindex
                k=k+1

     #负方向饱和波检测
            while values[i]>0 :
                i+=1
                if (i>=maxindex):
                    break
            zero=i
            min=i
            i+=1
            if i>=maxindex:
                break

            while values[i]<values[min]:
                min=i
                i+=1
                if i>=maxindex:
                    break
            time2=zero-max
            time1=min-zero+1
            num=min-max
            bizhi=0
            if time2!=0:
                bizhi=time1/time2
            ratio=self.gradientratio(values, min, zero, max)

            if ratio<2:
                i=zero
                continue
            if 1.5 < bizhi < 3.4 and num >= 0.5*window_size and values[max] > 10:
                if (min+num)>maxindex:
                    break
                end=min+num-minindex
                if k==0:
                    start=max-minindex
                k=k+1

            i=zero



        if k!=0:
            path=path+"\\"+"自动检测-"+str(comtradeObj.cfg_data["station_name"])+str(comtradeObj.cfg_data["rec_dev_id"])+"-CT饱和-"+str(datetime.datetime.now()).replace(":", "-")
            num=end-start
            datacsv=tep_phase_data[start:end]
            self.a = datacsv
            print(str(datacsv.columns[1])+"-CT饱和故障-"+str(datacsv.iloc[0,0])+"-"+str(datacsv.iloc[-1,0]))
            self.log+=str(datacsv.columns[1])+"-CT饱和故障-"+str(datacsv.iloc[0,0])+"-"+str(datacsv.iloc[-1,0])+"\n"
            self.log+=path+".csv\n"
            datacsv.to_csv(path+".csv", index=False, encoding="ansi")
    def func(self, x, a0, a1, a2):
        return a0 * np.sin(x + a1) + a2


    def corr(self, v, v_):
        return np.corrcoef([v, v_])[0, 1]

    #斜率比值
    def gradientratio(self, values, max, zero, min):
        if zero==min or max==zero:
            return 0
        xielv1=abs(values[min])/abs(zero-min)
        xielv2=abs(values[max])/abs(max-zero)
        return xielv1/xielv2

