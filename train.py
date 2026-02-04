# 2027-09-15: 54425.453125
# 2027-09-18: 58223.5234375
# 2027-09-11: 45864.1953125
# 2029-09-18: 587.685791015625
# 2029-07-18: 71597.8203125



#new code 


import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os

def train_model(file_path, model_name, scaler_name):
    # Load the dataset
    data = pd.read_csv(file_path)

    # Select the relevant columns
    data['Open time'] = pd.to_datetime(data['Open time'])
    data.set_index('Open time', inplace=True)
    prices = data['Close']

    # Normalize the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    prices_scaled = scaler.fit_transform(prices.values.reshape(-1, 1))

    # Prepare the data for LSTM
    sequence_length = 60  # Using the past 60 intervals to predict the next one
    X, y = [], []

    for i in range(sequence_length, len(prices_scaled)):
        X.append(prices_scaled[i-sequence_length:i, 0])
        y.append(prices_scaled[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    # Split into training and test sets
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Build the LSTM model
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
        LSTM(units=50, return_sequences=False),
        Dense(units=25),
        Dense(units=1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(X_train, y_train, batch_size=32, epochs=50)

    # Save the model and scaler
    model.save(model_name)
    joblib.dump(scaler, scaler_name)

    print(f"Model trained and saved as {model_name}!")
    return model, scaler

# Train models for 1-hour, 4-hour, and 15-minute intervals
file_configs = [
    {'file': 'D:\RissProjects\Christ(BCA)\BitVantage\web\dataset\btc_1h_data_2018_to_2024-09-06.csv', 'model': 'model_1hr.h5', 'scaler': 'scaler_1hr.save'},
    {'file': 'D:\RissProjects\Christ(BCA)\BitVantage\web\dataset\btc_4h_data_2018_to_2024-09-06.csv', 'model': 'model_4hr.h5', 'scaler': 'scaler_4hr.save'},
    {'file': 'D:\RissProjects\Christ(BCA)\BitVantage\web\dataset\btc_15m_data_2018_to_2024-09-09.csv', 'model': 'model_15min.h5', 'scaler': 'scaler_15min.save'},
    {'file': 'D:\RissProjects\Christ(BCA)\BitVantage\web\dataset\btc_1d_data_2018_to_2024-09-06.csv', 'model': 'model_1d.h5', 'scaler': 'scaler_1d.save'}

]

for config in file_configs:
    train_model(config['file'], config['model'], config['scaler'])
