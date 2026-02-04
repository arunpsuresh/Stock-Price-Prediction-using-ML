import cryptocompare
import pandas as pd
import numpy as np
from datetime import datetime

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Set the current Bitcoin rate manually (e.g., 96,000 USD)
CURRENT_BITCOIN_RATE = 983872

# Fetch historical data for Bitcoin (daily data for the past 3 years)
def fetch_bitcoin_data():
    data = cryptocompare.get_historical_price_day(
        'BTC', 
        toTs=datetime.now(), 
        limit=1095  # Increase to 3 years of data
    )
    
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'], unit='s', errors='coerce')
    df = df[['time', 'close']]
    
    df.to_csv('bitcoin_data.csv', index=False)
    return df

# Preprocess the data (feature scaling, time series preparation)
def preprocess_data():
    df = pd.read_csv('bitcoin_data.csv')
    
    # Use 'close' prices as target
    prices = df['close'].values.reshape(-1, 1)
    
    # Normalize the data using MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    prices_scaled = scaler.fit_transform(prices)
    
    # Create a dataset with the previous N days of prices
    N = 60  # Use 60 previous days to predict the next day
    X = []
    y = []
    
    for i in range(N, len(prices_scaled)):
        X.append(prices_scaled[i-N:i, 0])  # Last 60 days
        y.append(prices_scaled[i, 0])  # Next day's closing price
    
    X, y = np.array(X), np.array(y)
    
    # Reshape X to be in 3D format as expected by LSTM [samples, time steps, features]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    
    return X, y, scaler

# Build and train LSTM model
def build_model(X_train, y_train):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))  # Dropout to prevent overfitting
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))  # Output layer for price prediction
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=5, batch_size=32)
    
    return model

# Forecast Bitcoin price for a given date
def forecast(model, future_date, scaler, X_full):
    future_date = pd.to_datetime(future_date)
    
    # Take the last 60 days from the historical data
    last_60_days = X_full[-60:]
    
    # Reshape and scale the data for prediction
    last_60_days = last_60_days.reshape(1, -1, 1)
    
    # Predict the price using LSTM
    predicted_price_scaled = model.predict(last_60_days)
    
    # Rescale the predicted price back to the original scale
    predicted_price = scaler.inverse_transform(predicted_price_scaled)
    
    print(f"Predicted Bitcoin price on {future_date.date()}: ${predicted_price[0][0]:.2f}")

# Main execution
df = fetch_bitcoin_data()
X, y, scaler = preprocess_data()
model = build_model(X, y)

# Forecast the Bitcoin price for a specific future date
future_date = input("Enter a date to forecast Bitcoin price (YYYY-MM-DD): ")
forecast(model, future_date, scaler, df['close'].values)
