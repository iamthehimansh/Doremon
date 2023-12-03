# Human Computer Interface (HCI) 
# game controller for games like dino and flappy bird

import json
import serial
import time,numpy
import pyautogui
from scipy.signal import welch
from typing import Optional
import numpy as np
import numpy as np
# return time in ms
def milis():
    return int(round(time.time() * 1000))

# Arduino serial port interface
ser = serial.Serial('/dev/tty.usbmodem2101', 115200, timeout=10)

# Timing variable
timer = milis()

latency =  24
dataList=[]
baseline_frequencies=[]
baseline_data=[]

def getPSD(freqs,pds,val,threshold=0.5):
    """Compair the freq with with the error of the threshold"""
    for i in range(len(freqs)):
        if  val-threshold<=freqs[i] and freqs[i]<=val+threshold:
            return pds[i]
    return None
def getMeanAndStandardDeviation(psd):
    """Return the mean and standard deviation of the pds"""
    mean=0
    for i in range(len(psd)):
        mean+=psd[i]
    mean/=len(psd)
    std=0
    for i in range(len(psd)):
        std+=(psd[i]-mean)**2
    std/=len(psd)
    std=std**0.5
    return mean,std

def calculate_standard_deviation_with_baseline(baseline_frequencies, baseline_data, live_frequencies, live_data):
    # Ensure that the baseline and live data have the same frequencies
    # print("#",baseline_frequencies,"#",live_frequencies,"#")
    # assert baseline_frequencies == live_frequencies, "Frequency mismatch between baseline and live data"

    n = len(baseline_frequencies)

    # Calculate the differences between live and baseline data
    differences = [live_data[i] - baseline_data[i] for i in range(n)]

    # Calculate the mean difference
    mean_difference = sum(differences) / n

    # Calculate the squared differences from the mean
    squared_diff = [(x - mean_difference) ** 2 for x in differences]

    # Calculate the variance
    variance = sum(squared_diff) / n

    # Calculate the standard deviation
    std_deviation = variance ** 0.5

    return std_deviation

def loopRun(fn=lambda freqs,pds:(freqs,pds),multiplyer=1):

    global dataList
    for _ in range(250*multiplyer):
        data = ser.readline().decode('utf-8').strip()
        # print(data,time.strftime("%H:%M:%S", time.localtime()))
        # Debounce
        # print(len(dataList))
        if data.strip()!="":
            dataList.append(float(data))
        else:
            dataList.append(0)

        if len(dataList) ==250*multiplyer:
            # print(dataList)
            freqs,pds=welch(dataList, fs=256, nperseg=250)
            dataList=[]
            # print(freqs)
            # print(pds)
            return fn(freqs,pds)
        
        ser.flushInput()


def calibrate(n=60):
    # """Calibrate the device"""
    # print("Calibrating...")
    # pds=[]
    # for _ in range(n):
    #     pds.append(loopRun(lambda freqs,pds:getPSD(freqs,pds,val)))
    # mean,std=getMeanAndStandardDeviation(pds)
    # return mean,std
    global baseline_frequencies, baseline_data
    print("Calibrating...")
    bf = []
    bd = []
    freq = None
    for _ in range(n):
        
        f1, d1 = loopRun(lambda freqs, pds: (freqs, pds), multiplyer=1)
        bf.append(f1)
        bd.append(d1)
        freq = f1
        print(((_+1)/60)*100,"%")

    # input("Press enter to continue...")
    average_bd = np.mean(bd, axis=0)  # Take the mean along the first axis (rows)
    print(average_bd)

    baseline_frequencies, baseline_data = freq, average_bd
    # print("Calibration complete")
    print("Baseline frequencies: ", baseline_frequencies)
    # input("Press enter to continue...")
    print("Baseline data: ", baseline_data)
    # input("Press enter to continue...")

    



        
freqList=[8,13,23,33]#
def Do(freq):
    mydata=json.load(open("./SSVEP/data.json","r"))
    print(ferq,mydata)
    mydata[str(freqList.index(freq)+1)]=1 if mydata[str(freqList.index(freq)+1)]==0 else 0
    json.dump(mydata,open("./SSVEP/data.json","w"))
# Infinite loop
calibrate()
while True:
    # try:
    # Process serial data
    livedata=loopRun()
    avgStd=calculate_standard_deviation_with_baseline(baseline_frequencies, baseline_data, *livedata)
    freqs,pds=livedata
    for ferq in freqList:
        if(ferq in freqs):
            index=freqs.tolist().index(i)
            diff=pds[index]-avgStd
            print(ferq,diff)
            if(diff<=0):
                diff*=-1
            if(diff<=1):
                Do(ferq)
        else:
            for i in freqs:
                if (i+4>=ferq and i-4<=ferq):
                    
                    index=freqs.tolist().index(i)
                    diff=pds[index]-avgStd
                    print(ferq,diff)
                    if(diff<=0):
                        diff*=-1
                    if(diff<=1):
                        Do(ferq)
                    

    # except Exception as e:
    #     print(e, "\n......")
    #     continue