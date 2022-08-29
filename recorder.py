import sounddevice as sd
from scipy.io.wavfile import write
import time
import numpy as np
import matplotlib.pyplot as plt
import math
import os
import scipy.io as sci
from random import randrange
import random

fs = 44100  # Sample rate
press_dur = 0.2

# Record samples for x duration
def record(key, dur):
    print('You will be recording the', key, 'key in 3 seconds')   # will print which key is pressed

    for i in range(3):
        print(3 - i)
        time.sleep(1)


    recording = sd.rec(int(dur * fs), samplerate = fs, channels=1)
    print(dur, "Second recording started...")
    sd.wait()  # Wait until recording is finished
    splitted = split_audio(recording, fs, press_dur, 0.0075, 0.04, 0.0005)

    os.mkdir(key)

    i = 0
    for sample in splitted:
        write('./' + key + '/' + str(i) + '.wav', fs, np.array(sample))
        i+=1

    return splitted

#
# audio_data = captured data in np array form
# rate = capture frequency
# duration = duration of samples
# jump_back = when threshold hit, how much to go back by
# threshold = audio threshold
# split_dur  = duration of the split to speed up processing
#
def split_audio(audio_data, rate, duration, jump_back, threshold, split_dur):
    samples = []

    split = max(1, int(split_dur * rate))

    i = 0
    while i < int(len(audio_data)/split):
        index = split * i
        if (abs(audio_data[index]) > threshold):
            sample = []

            start_index = int(index - (jump_back * rate))
            end_index = int(start_index + (duration * rate))
            
            if (end_index < len(audio_data)):

                #print("Keypress detected at index:", start_index)

                for j in range(start_index, end_index):
                    sample.append(np.array(audio_data[j]))
                
                samples.append(sample)

                i = math.ceil(end_index / split)

        i+=1

    print("Number of samples detected:", len(samples), '\n')
    
    return np.array(samples)

# Plot the audio file on matplotlib
def plot_audio(audio_data):
    plt.plot(range(0, audio_data.size), audio_data)
    plt.show()

# Plot the list of extracted samples
def plot_extracted_samples(samples):
    for j in range(len(samples)):
        plt.plot(range(len(samples[j])), samples[j])
        plt.show()

def record_test():
    print("Recording of test started")
    recording = sd.rec(10 * fs, samplerate = fs, channels=1)
    sd.wait()  # Wait until recording is finished
    # write('./test.wav', fs, recording)
    # print("Test saved")

    splitted = split_audio(recording, fs, press_dur, 0.0075, 0.04, 0.0005)

    os.chdir('test_samples')

    i = 0
    for sample in splitted:
        write('./' + str(i) + '.wav', fs, np.array(sample))
        i+=1

    os.chdir('..')

def get_test_samples():
    recording = np.array(sci.wavfile.read('./test.wav')[1], copy=True)
    splitted = split_audio(recording, fs, press_dur, 0.0075, 0.05, 0.0005)
    return splitted

    
    