import recorder
import creator
import matplotlib.pyplot as plt
import sys
import os

training_data = []

def main():
    # recorder.load_background_noises()

    # os.mkdir('samples')
    # os.chdir('samples')

    # for letter in ['a', 'b', 'c']:
    #     training_data.append(recorder.record(letter, 30))

    #recorder.record_background_noise()

    #recorder.record_test()

    # creator.createAndTrainModel()

    # os.chdir('..')

    creator.loadModelAndPredict(recorder.get_test_samples())

if __name__ == "__main__":
    main()