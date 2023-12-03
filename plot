import serial
import csv
import numpy as np
import mne
import time
import pylsl



ch_names=('Fp1','Fp1','Fp1','Fp1')
ch_types=('eeg','eeg','eeg','eeg')
myInt=[]
def Setup_EEG_LSL(name='Neuphony', stream_type='EEG', srate=250):
    global outlet
    info = pylsl.StreamInfo(name, stream_type, 1, srate, 'float32', 'myuid2424')
    # append some meta-data
    # https://github.com/sccn/xdf/wiki/EEG-Meta-Data
    info.desc().append_child_value("manufacturer", "LSLExampleAmp")
    chns = info.desc().append_child("channels")
    for chan_ix, label in enumerate(ch_names[1]):
        ch = chns.append_child("channel")
        ch.append_child_value("label", label)
        ch.append_child_value("unit", "microvolts")
        ch.append_child_value("type", "EEG")
        ch.append_child_value("scaling_factor", "1")
    outlet = pylsl.StreamOutlet(info, 1, 360)
    return outlet


scale_fac_uVolts_per_count = 1.2/(8388607)
def read_and_save_data_to_csv(file_path, num_samples,outlet): 
    num_packets = 0

    with serial.Serial('COM9', baudrate=115200, timeout=1) as ser:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            start_time = time.time() 
            while num_packets < num_samples:
                data=None
                # while not (ser.readline().startswith(b"A5")):
                #     data = ser.readline()
                #     print(data)
                data = ser.readline().decode()
                if(data!='\r\n' and data!= '' and data!='\n'):
                    # print(data)
                    num_packets += 1
                    # print(data)
                # if(data[0]=="A5"):
                    myInt = float(data)
                    #     myInt.append(float(int((data[2]),16)) * scale_fac_uVolts_per_count *1000000/64)
                    #     myInt.append(float(int((data[3]),16)) * scale_fac_uVolts_per_count *1000000/32)
                    #     myInt.append(float(int((data[4]),16)) * scale_fac_uVolts_per_count *1000000/8)
                    writer.writerow([myInt])
                    outlet.push_chunk([myInt])
                    print(myInt)

                #     myInt.clear()
                    

    end_time = time.time()
    elapsed_time = end_time - start_time

    sfreq = num_packets / elapsed_time
    return int(sfreq)      

if __name__ == '__main__':
    num_samples_to_save = 5000000
    csv_file_path = "sensor_data.csv"  
    outlet = Setup_EEG_LSL()
    sfreq=read_and_save_data_to_csv(csv_file_path, num_samples_to_save,outlet)
    raw_data = np.loadtxt(csv_file_path, delimiter=',')
    print(f"Sampling freq is {sfreq}")
    eeg_data = np.array(raw_data, dtype=np.str_)
    # eeg_data = np.transpose(eeg_data)
    eeg_data = eeg_data.reshape(1, -1)  # Reshape the data to (1, n_samples)
    ch_names = ['sensor_data'] 
    ch_types = ['eeg'] 
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw_Array = mne.io.RawArray(eeg_data, info)
    lp, hp = 2,40
    raw_Array.filter(float(lp), float(hp), fir_design='firwin')
    raw_Array.notch_filter(float(50), method='fft',notch_widths=6.0)
    raw_tmp = raw_Array.copy()
    raw_tmp.plot(block=True, scalings={'eeg': 50}, n_channels=1)
    raw_tmp.plot_psd(area_mode='std', fmin=1., fmax=80.)