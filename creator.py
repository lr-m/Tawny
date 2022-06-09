from keras.backend import dropout
import numpy as np
import os
from keras.callbacks import ModelCheckpoint
from keras.models import Sequential
from keras.layers.core import Dense,Dropout
from tensorflow.keras.optimizers import SGD,Adam
import scipy.io as sci
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

def createModel(input_dimensions, output_dimensions):
    model_im = Sequential()
    model_im.add(Dense(128, activation='sigmoid', input_dim=input_dimensions))
    model_im.add(Dropout(0.25))
    # model_im.add(Dense(64, activation= 'LeakyReLU'))
    model_im.add(Dense(32, activation='LeakyReLU'))
    model_im.add(Dense(output_dimensions, activation='softmax'))
    
    optimizer = Adam()
    model_im.compile(loss='categorical_crossentropy', optimizer=optimizer , metrics=['accuracy'])
    print(model_im.summary())
    return model_im

def createAndTrainModel():
    X, y = loadData()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=1)

    model_im = createModel(len(X_train[0]), len(y_train[0]))

    checkpoint_path = "../model_checkpoints/cp.ckpt"
    cp_callback = ModelCheckpoint(filepath=checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=1)

    history_im = model_im.fit(np.array(X_train), y_train, epochs=25, batch_size=32, callbacks=[cp_callback])
    score = model_im.evaluate(np.array(X_test), y_test, batch_size=32)
    print ('Test Accuracy: ', score[1])

def loadModelAndPredict(samples):
    model = createModel(8820,3)
    model.load_weights('model_checkpoints/cp.ckpt')

    fft_samples = []

    for val in samples:
        fft_samples.append(np.fft.fft(val))

    for val in model.predict(np.array(fft_samples)):
        print(chr(97 + np.argmax(val)), end='')
    print('')

def loadData():
    X = []
    y = []

    # Navigate to samples directory
    os.chdir('samples')
    for x in os.walk('./'):
        if (x[0] != './'):
            os.chdir(x[0])
            print(os.getcwd())
            
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in files:
                data = np.array(sci.wavfile.read(f)[1], copy=True)
                X.append(np.abs(np.fft.fft(data)))
                y.append(ord(os.getcwd()[-1]))

            os.chdir(os.getcwd() + '/..')

    min = 9999
    for element in y:
        if (element < min):
            min = element

    new_y = []

    for element in y:
        new_y.append(element - min)

    final_y = to_categorical(new_y)

    return X, final_y