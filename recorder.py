import sounddevice as sd
from scipy.io.wavfile import write
import msvcrt
import numpy as np
import matplotlib.pyplot as plt
import math

fs = 44100  # Sample rate

def record(key):
    print("Press the key you want to extract")
    while True:
        if msvcrt.kbhit():
            key_stroke = msvcrt.getch()
            print('You will be recording the', str(key_stroke)[2], 'key...')   # will print which key is pressed
            break

    recording = sd.rec(int(5 * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    splitted = split_audio(recording, 44100, 0.2, 0.0075, 0.05, 0.0005)

    i = 0
    for sample in splitted:
        write('key' + str(i) + '.wav', fs, np.array(sample))
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

                print("Keypress detected at index:", start_index)

                for j in range(start_index, end_index):
                    sample.append(audio_data[j])
                
                samples.append(sample)

                i = math.ceil(end_index / split)

        i+=1

    print("Samples detected:", len(samples))
    
    return samples

def plot_audio(audio_data):
    plt.plot(range(0, audio_data.size), audio_data)
    plt.show()

def plot_extracted_samples(samples):
    for j in range(len(samples)):
        plt.plot(range(len(samples[j])), samples[j])
        plt.show()
    