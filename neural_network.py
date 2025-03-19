import os
import random

import numpy as np

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import tensorflow as tf
from keras import Sequential
from keras.layers import Flatten, Dense, Conv2D
from keras.losses import Huber
from keras.optimizers import Adam
from keras.optimizers.schedules import ExponentialDecay
from keras.initializers import HeUniform, Zeros

def initialize_model(self):

    # this was used for the pretrained model
    model = Sequential()
    model.add(Flatten(input_shape=(5, 5, 13)))
    model.add(Dense(128, activation='relu', kernel_initializer=HeUniform()))
    model.add(Dense(96, activation='relu', kernel_initializer=HeUniform()))
    model.add(Dense(64, activation='relu', kernel_initializer=HeUniform()))
    model.add(Dense(32, activation='relu', kernel_initializer=HeUniform()))
    model.add(Dense(1, activation='linear', kernel_initializer=Zeros()))
    lr_schedule = ExponentialDecay(initial_learning_rate=self.lr_schedule_config['init_lr'],
                                   decay_steps=self.lr_schedule_config['decay_steps'],
                                   decay_rate=self.lr_schedule_config['decay_rate'])
    model.compile(optimizer=Adam(learning_rate=lr_schedule), loss=Huber())
    return model