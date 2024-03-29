import recorder
import matplotlib.pyplot as plt
from scipy.io import wavfile
import sys
import os
import tkinter as tk
import librosa
import librosa.display
import numpy as np
import scipy.spatial.distance as dist
import fnmatch
import time
import threading
import tkinter.font as font
from tkinter import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)

def record_samples():
    t = threading.Thread(target=record_all_keys, args=())
    t.start()

def record_all_keys():
    if "samples" not in os.getcwd():
        if (not os.path.exists(os.getcwd() + '\samples')):
            os.mkdir('samples')
        
        os.chdir('samples')

    key_entry.config(state='disabled')
    for char in record_key.get():
        recorder.record(char, int(sample_duration.get()), output) # Records key presses for 15 seconds
    key_entry.config(state='normal')

    os.chdir('..')

def record_test_thread():
    t = threading.Thread(target=record_test_fun, args=())
    t.start()

def record_test_fun():
    dir = 'test_samples'

    if (not os.path.exists(os.getcwd() + '\\test_samples')):
        os.mkdir('test_samples')

    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

    key_entry.config(state='disabled')
    recorder.record_test(output, test_duration)
    key_entry.config(state='normal')

    t = threading.Thread(target=mfcc, args=())
    t.start()

def dp(dist_mat):
    """
    Find minimum-cost path through matrix `dist_mat` using dynamic programming.

    The cost of a path is defined as the sum of the matrix entries on that
    path. See the following for details of the algorithm:

    - http://en.wikipedia.org/wiki/Dynamic_time_warping
    - https://www.ee.columbia.edu/~dpwe/resources/matlab/dtw/dp.m

    The notation in the first reference was followed, while Dan Ellis's code
    (second reference) was used to check for correctness. Returns a list of
    path indices and the cost matrix.
    """

    N, M = dist_mat.shape
    
    # Initialize the cost matrix
    cost_mat = np.zeros((N + 1, M + 1))
    for i in range(1, N + 1):
        cost_mat[i, 0] = np.inf
    for i in range(1, M + 1):
        cost_mat[0, i] = np.inf

    # Fill the cost matrix while keeping traceback information
    traceback_mat = np.zeros((N, M))
    for i in range(N):
        for j in range(M):
            penalty = [
                cost_mat[i, j],      # match (0)
                cost_mat[i, j + 1],  # insertion (1)
                cost_mat[i + 1, j]]  # deletion (2)
            i_penalty = np.argmin(penalty)
            cost_mat[i + 1, j + 1] = dist_mat[i, j] + penalty[i_penalty]
            traceback_mat[i, j] = i_penalty

    # Traceback from bottom right
    i = N - 1
    j = M - 1
    path = [(i, j)]
    while i > 0 or j > 0:
        tb_type = traceback_mat[i, j]
        if tb_type == 0:
            # Match
            i = i - 1
            j = j - 1
        elif tb_type == 1:
            # Insertion
            i = i - 1
        elif tb_type == 2:
            # Deletion
            j = j - 1
        path.append((i, j))

    # Strip infinity edges from cost_mat before returning
    cost_mat = cost_mat[1:, 1:]
    return (path[::-1], cost_mat)

def mfcc():
    avgs = []
    closest = []

    test_result.set("Result:\n")

    for j in range(len(fnmatch.filter(os.listdir("test_samples"), '*.wav'))):
        file_A = "test_samples/" + str(j) + ".wav"
        f_s_A, x_A = wavfile.read(file_A)

        n_fft_A = int(0.025*f_s_A)
        hop_length_A = int(0.01*f_s_A)
        mel_spec_x_A = librosa.feature.melspectrogram(y=x_A/1.0, sr=f_s_A, n_mels = 40, n_fft=n_fft_A, hop_length=hop_length_A)
        log_mel_spec_x_A = np.log(mel_spec_x_A)

        # the figure that will contain the plot
        plot1.imshow(log_mel_spec_x_A, origin='lower', interpolation='nearest')
        canvas.draw()
        
        tot = 0

        for let in os.listdir('samples'):
            for i in range(len(fnmatch.filter(os.listdir("samples/" + let), '*.wav'))):
                file_B = "samples/" + let + "/" + str(i) + ".wav"
                f_s_B, x_B = wavfile.read(file_B)

                n_fft_B = int(0.025*f_s_B)
                hop_length_B = int(0.01*f_s_B)
                mel_spec_x_B = librosa.feature.melspectrogram(y=x_B/1.0, sr=f_s_B, n_mels = 40, n_fft=n_fft_B, hop_length=hop_length_B)
                log_mel_spec_x_B = np.log(mel_spec_x_B)

                x_seq = log_mel_spec_x_B.T
                y_seq = log_mel_spec_x_A.T

                dist_mat = dist.cdist(x_seq, y_seq, "cosine")

                path, cost_mat = dp(dist_mat)
                tot+=cost_mat[-1, -1]

                if (len(closest) < 10):
                    closest.append([let, cost_mat[-1, -1]])
                elif (cost_mat[-1, -1] < min(closest)[1]):
                    closest[closest.index(min(closest))] = [let, cost_mat[-1, -1]]

            avg = tot/15
            avgs.append([let, avg])
            tot = 0

        letters = []
        for elem in closest:
            letters.append(elem[0])

        test_result.set(test_result.get() + get_mode(letters))

        for key in keys:
            keyboard_keys[key].config(bg='#bf9101')
        
        time.sleep(0.05)

        for letter in letters:
            keyboard_keys[letter].config(bg='green')

        time.sleep(0.5)

        avgs = []
        closest = []

    for key in keys:
        keyboard_keys[key].config(bg='#bf9101')

def get_mode(query_list):
    top_letter = ''
    max_count = 0
    for unique in list(dict.fromkeys(query_list)):
        count = 0
        for letter in query_list:
            if unique == letter:
                count+=1
        
        if count > max_count:
            top_letter = unique
            max_count = count

    return top_letter

    

root=tk.Tk()

plt.set_cmap('inferno')

test_duration = tk.StringVar(root)
test_duration.set("10")

sample_duration = tk.StringVar(root)
sample_duration.set("10")

myFont = font.Font(size=20)

output = tk.StringVar()
test_result = tk.StringVar()
record_key = tk.StringVar()

root.title('Tawny')
root.geometry("1280x720")
root.configure(bg='#0a0724')

# Left frame
left = tk.Frame(root, bg='#0a0724')
left.grid(column=0, row=0)

right = tk.Frame(root, bg='#0a0724')
right.grid(column=1, row=0)

# Logo
canvas = tk.Canvas(left, width = 400, height = 287, bg='#0a0724', highlightthickness = 0)      
canvas.pack(side=tk.TOP, fill='both', padx='100', pady=20)      
img = tk.PhotoImage(file="logo.png")      
canvas.create_image(0, 0, anchor=tk.NW, image=img) 

# Key entry
key_frame = tk.Frame(left, bg='#0a0724')

key_label = tk.Label(key_frame,text='Sample Key(s):', bg='#0a0724', fg='white')
key_label.grid(column=0, row=0, pady=20)

key_entry = tk.Entry(key_frame, textvariable = record_key, width=40)
key_entry.grid(column=1, row=0, padx=25, columnspan=2)

key_label = tk.Label(key_frame,text='Duration (seconds):', bg='#0a0724', fg='white')
key_label.grid(column=0, row=1)

duration_options = tk.OptionMenu(key_frame, sample_duration, "5", "10", "15", "30", "60")
duration_options.config(highlightthickness=0)
duration_options.grid(column=1, row=1)

# Record button
record_button = tk.Button(key_frame, text ="Record Keys", command = record_samples)
record_button.grid(column=2, row=1)

key_frame.pack(side=tk.TOP, pady=25)

output.set("Welcome to TAWNY...")
output_label = tk.Label(left, textvariable=output, fg='white', bg='#7e6100', width=50, height=15)
output_label.pack(side=tk.TOP)

# Record button

# Key entry
test_frame = tk.Frame(right, bg='#0a0724')

test_label = tk.Label(test_frame,text='Duration (seconds):', bg='#0a0724', fg='white')
test_label.grid(column=0, row=0)

test_duration_options = tk.OptionMenu(test_frame, test_duration, "5", "10", "15", "30", "60")
test_duration_options.config(highlightthickness=0)
test_duration_options.grid(column=1, row=0, padx=70)

# Record button
record_test = tk.Button(test_frame, text ="Record Test", command = record_test_thread)
record_test.grid(column=2, row=0)

test_frame.pack(side=tk.TOP, pady=25)


# keyboard
keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']

keyboard_frame = tk.Frame(right, bg='#0a0724')

keyboard_keys = {}
row = 0
col = 0

for key in keys:
    keyboard_keys[key] = tk.Button(keyboard_frame, text=key, width=2, height=1, 
        highlightthickness=0, bg='#bf9101', font=myFont, fg='white')
    # keyboard_keys[key]['font'] = myFont
    keyboard_keys[key].grid(row = row, column = col, columnspan=2, padx=2, pady=2)
    col += 2

    if (row == 0 and col == 20):
        row = 1
        col = 0
    elif (row == 1 and col == 20):
        row = 2
        col = 1
    elif (row == 2 and col == 19):
        row = 3
        col = 3

keyboard_frame.pack(side=tk.TOP)

# the figure that will contain the plot
fig = Figure(figsize = (5, 3),
                dpi = 100)
fig.patch.set_facecolor('#0a0724')

# list of squares
y = [i**2 for i in range(101)]

# adding the subplot
plot1 = fig.add_subplot(111)
plot1.set_facecolor('#0a0724')
plot1.yaxis.label.set_color('white') 
plot1.tick_params(axis="y", colors="white")
plot1.tick_params(axis="x", colors="white")

plot1.spines['bottom'].set_color('white')
plot1.spines['top'].set_color('white')
plot1.spines['left'].set_color('white')
plot1.spines['right'].set_color('white')

plot1.set_ylabel("Feature Dimensions")

# creating the Tkinter canvas
# containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig,
                            master = right) 

# placing the canvas on the Tkinter window
canvas.get_tk_widget().pack()

test_output_label = tk.Label(right, textvariable=test_result, fg='white', bg='#7e6100', width=50, height=5)
test_output_label.pack(side=tk.TOP, pady=10)
test_result.set("Result:\n")

root.mainloop()