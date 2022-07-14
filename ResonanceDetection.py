import numpy as np
from scipy.optimize import curve_fit
from ProcessComtradeObj import ProcessComtradeObj
import datetime
pi = np.pi
arrs=[20/3, 60]      

class ResonanceDetection:
    def __init__(self, comtradeObj, path):
        self.log = ""
        self.comtradeObj = comtradeObj
        self.ProcessComtradeObj=ProcessComtradeObj(self.comtradeObj,0)
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
                self.checkwave(tep_phase_data, window_size, tep_phase_data.index[0],comtradeObj,path)
    def func(self, x, a0, a1):
        return a0 * np.sin( x + a1) 


    def corr(self, v, v_):
        return np.corrcoef([v,v_])[0,1]


    #统计数组0点个数
    def zeroNum(self,array):
        #记录零点个数
        sum=0
        i=array.index[0]
        maxindex=array.index[len(array)-1]
        while i<maxindex:
        #前后两值异号有零点
            if array[i]*array[i+1]<=0:
                sum+=1
        #+2防止有一点刚好为0
                i+=2
                if i>=maxindex:
                    return sum
            i=i+1
        return sum



    #谐振波检测
    def check(self,i, a0, value, window_size, comtradeObj, path):
        tep_phase_data=value
        value=value.iloc[:,1]
        for arr in arrs:
            maxindex=value.index[len(value)-1]
            minindex=value.index[0]
            k=0
            xi=arr/20
            #num为对应周期取点个数
            num=int(window_size*xi)
            xzhou=2*pi
            #print (num)
            x3 = np.linspace(0, xzhou, num)
            if i+num > maxindex:
                return k,maxindex
            y3=value[i-minindex:i+num-minindex]
            print(x3)
            print(y3)
            print(value)
            pa, pcov=curve_fit(self.func, x3, y3)  
            max=y3[y3.index[0]]
            for yvalue in y3:
                if yvalue>max:
                    max=yvalue
            if (self.zeroNum(y3)==2 and max>1.2*a0):
                #j记录检测周期数
                j=1
                while j<10:
                    if i+(j+1)*num>maxindex:
                        break
                    y=value[i+j*num-minindex:i+(j+1)*num-minindex]
                    max=y[y.index[0]]
                    for yvalue in y:
                        if yvalue>max:
                            max=yvalue


                    zeronum=self.zeroNum(y)
                    para,_=curve_fit(self.func, x3, y)
                    if zeronum==2 and max>=1.2*a0:
                        k+=1
                    j+=1
                if k>=8:
                    y=value[i-minindex-num:i+j*num-minindex]
                    ycsv=tep_phase_data[i-minindex-num:i+j*num-minindex]
                    print(str(ycsv.columns[1])+"-谐振-"+str(ycsv.iloc[0,0])+"-"+str(ycsv.iloc[-1,0]))
                    self.log+=str(ycsv.columns[1])+"-谐振-"+str(ycsv.iloc[0,0])+"-"+str(ycsv.iloc[-1,0])+"\n"
                    path=path+"\\"+"自动检测-"+str(comtradeObj.cfg_data["station_name"])+str(comtradeObj.cfg_data["rec_dev_id"])+"-谐振-"+str(datetime.datetime.now()).replace(":", "-")
                    self.log+=path+".csv\n"
                    ycsv.to_csv(path+".csv", index=False, encoding="ansi")  
                    return k,i+j*num
                else:
                    return k,i+window_size
            else:
                continue
        return k, i+window_size
    def checkwave(self,value,window_size,i,comtradeObj,path):
        tep_phase_data=value

        value=value.iloc[:,1]
        xdata = np.linspace(0, 2*pi, window_size)
        maxindex=value.index[len(value)-1]
        minindex=value.index[0]
        while value[i]<0.5:
            i += 1
            if i >= maxindex:
                return  
        if (i+window_size)>=maxindex:
            return
        while i<maxindex:
            ydata = value[i-minindex:i+window_size-minindex]    
            popt, pcov = curve_fit(self.func, xdata, ydata)
            a0=abs(popt[0])
            ydata1 = [self.func(a, popt[0], popt[1]) for a in xdata]
            
            corrdata = self.corr(ydata, ydata1)

            if corrdata>0.9:
                while i<maxindex:
                    if  value[i]>1.2*abs(a0):
                        k=self.check(i, a0, tep_phase_data, window_size, comtradeObj, path)
                        if k[0]>=8:
                            i=k[1]
                        else:
                            i=k[1]
                    else:
                        i = i+1
            else:
                i=i+window_size
                