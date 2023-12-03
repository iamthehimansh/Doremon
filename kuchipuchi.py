# Human Computer Interface (HCI) 
# game controller for games like dino and flappy bird

import serial
import time
import pyautogui
from scipy.signal import welch
from typing import Optional
# return time in ms
def milis():
    return int(round(time.time() * 1000))

# Arduino serial port interface
ser = serial.Serial('/dev/tty.usbmodem21301', 115200, timeout=10)

# Timing variable
timer = milis()

latency =  24
dataList=[]

def getPSD(freqs,pds,val,threshold=0.5)->Optional(float):
    """Compair the freq with with the error of the threshold"""
    for i in range(len(freqs)):
        if  val-threshold<=freqs[i] and freqs[i]<=val+threshold:
            return pds[i]
    return None
def getMeanAndStandardDeviation(psd)->tuple(float,float):
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



def loopRun(fn=lambda freqs,pds:(freqs,pds)):

    global dataList
    for _ in range(250):
        data = ser.readline().decode('utf-8').strip()
        # print(data,time.strftime("%H:%M:%S", time.localtime()))
        # Debounce
        print(len(dataList))
        dataList.append(data)
        if len(dataList) ==250:
            freqs,pds=welch(dataList, fs=256, nperseg=250)
            dataList=[]
            print(freqs)
            print(pds)
            return fn(freqs,pds)
        
        ser.flushInput()


def calibrate(n=10,val=7)->tuple(float,float):
    """Calibrate the device"""
    print("Calibrating...")
    pds=[]
    for _ in range(n):
        pds.append(loopRun(lambda freqs,pds:getPSD(freqs,pds,val)))
    mean,std=getMeanAndStandardDeviation(pds)
    return mean,std
        

# Infinite loop
calibrate()
while True:
    try:
        # Process serial data
        loopRun()
    except Exception as e:
        print(e, "\nBlink now...")
        continue