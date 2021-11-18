# Tawny_Framework
This project aims to be the hub of acoustic keylogging. There will be a database of audio samples taken from various laptops that can be utilised, alongside a machine learning model, to accurately guess keypresses that have been typed on intercepted machines.

# Use Case
The use case of this project will be to see what keys have been pressed by somebody on a computer based on the audio signatures of captured data, and knowledge of the computer of whose keys were pressed.

The program will exploit the fact that all laptops of the same brand utilise very similar microphone modules, and keyboards that will sound near identical. During model training, various samples of background noise will be added to create a robust model.

To utilise, download the program, select the model for the laptop being attacked, pass the audio signatures into the program, and let the program do its magic to extract the keys.
