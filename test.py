import serial
ser = serial.Serial('/dev/tty.usbmodem21301', 115200, timeout=10)

def loopRun(fn=lambda freqs,pds:(freqs,pds)):

    global dataList
    for _ in range(250):
        data = ser.readline().decode('utf-8').strip()
        # print(data,time.strftime("%H:%M:%S", time.localtime()))
        # Debounce
        print(data)
        
        
        ser.flushInput()
while True:
    try:
        # Process serial data
        loopRun()
    except Exception as e:
        print(e, "\nBlink now...")
        continue