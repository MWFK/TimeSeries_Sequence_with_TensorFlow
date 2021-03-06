# -*- coding: utf-8 -*-
"""Solution.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qRJGD6-_3affmm0tPiYLHyuTXbB0UQ3J
"""

from turtle import shape
import urllib
import zipfile
import pandas as pd
import tensorflow as tf
import numpy as np

def normalize_series(data, min, max):
    data = data - min
    data = data / max
    return data

def windowed_dataset(series, batch_size, n_past=24, n_future=24, shift=1):
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(size=n_past + n_future, shift=shift, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(n_past + n_future))
    ds = ds.map(lambda w: (w[:n_past], w[n_past:]))
    #return ds.batch(batch_size).prefetch(1)
    return ds.batch(batch_size, drop_remainder=True).prefetch(1)

df = pd.read_csv('household_power_consumption.csv', sep=',',
                     infer_datetime_format=True, index_col='datetime', header=0)

N_FEATURES = len(df.columns)  # DO NOT CHANGE THIS

data = df.values
data = normalize_series(data, data.min(axis=0), data.max(axis=0))

SPLIT_TIME = int(len(data) * 0.5)  # DO NOT CHANGE THIS
x_train = data[:SPLIT_TIME]
x_valid = data[SPLIT_TIME:]

tf.keras.backend.clear_session()
tf.random.set_seed(42)

BATCH_SIZE = 32  # ADVISED NOT TO CHANGE THIS
N_PAST = 24  # DO NOT CHANGE THIS
N_FUTURE = 24  # DO NOT CHANGE THIS
SHIFT = 1  # DO NOT CHANGE THIS

train_set = windowed_dataset(series=x_train, batch_size=BATCH_SIZE,
                                 n_past=N_PAST, n_future=N_FUTURE,
                                 shift=SHIFT)


valid_set = windowed_dataset(series=x_valid, batch_size=BATCH_SIZE,
                                 n_past=N_PAST, n_future=N_FUTURE,
                                 shift=SHIFT)

model = tf.keras.models.Sequential([

        # ADD YOUR LAYERS HERE.

        # If you don't follow the instructions in the following comments,
        # tests will fail to grade your code:
        # The input layer of your model must have an input shape of:
        # (BATCH_SIZE, N_PAST = 24, N_FEATURES = 7)
        # The model must have an output shape of:
        # (BATCH_SIZE, N_FUTURE = 24, N_FEATURES = 7).
        # Make sure that there are N_FEATURES = 7 neurons in the final dense
        # layer since the model predicts 7 features.

        # HINT: Bidirectional LSTMs may help boost your score. This is only a
        # suggestion.

        # WARNING: If you are using the GRU layer, it is advised not to use the
        # recurrent_dropout argument (you can alternatively set it to 0),
        # since it has not been implemented in the cuDNN kernel and may
        # result in much longer training times.

    tf.keras.layers.InputLayer(input_shape=(N_PAST, N_FEATURES), batch_size = BATCH_SIZE, name='Input'),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(N_FEATURES, activation='relu', return_sequences=True)),
    tf.keras.layers.Dense(N_FEATURES)
])

optimizer = tf.keras.optimizers.Adam()

model.summary()

model.compile(
        optimizer=optimizer,
        loss='mae'
    )

model.fit(
        train_set,
        epochs = 10,
        validation_data = valid_set,
)