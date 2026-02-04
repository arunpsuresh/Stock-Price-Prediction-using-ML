# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import Sequential
# from keras.layers import LSTM, Dense
# from datetime import datetime

# # Load the dataset
# df = pd.read_csv(r'D:\RissProjects\Christ(BCA)\BitVantage\web\dataset\btc_1d_data_2018_to_2024-09-06.csv')

# # Select the 'Close' price for forecasting
# df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

# # Fill missing values if any
# df = df.fillna(method='ffill')

# # Use the 'Close' column for training
# data = df[['Close']].values

# # Scaling the data (Normalization)
# scaler = MinMaxScaler(feature_range=(0, 1))
# scaled_data = scaler.fit_transform(data)

# # Define the function to create sequences for LSTM
# def create_sequences(data, seq_length):
#     x = []
#     y = []
#     for i in range(seq_length, len(data)):
#         x.append(data[i-seq_length:i, 0])
#         y.append(data[i, 0])
#     return np.array(x), np.array(y)

# # Set sequence length (how many past data points we use to predict)
# sequence_length = 60

# # Create the training sequences
# x_train, y_train = create_sequences(scaled_data, sequence_length)

# # Reshape data to fit LSTM input shape [samples, time steps, features]
# x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

# # Build the LSTM model
# model = Sequential()

# # Add LSTM layers
# model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
# model.add(LSTM(units=50, return_sequences=False))

# # Add output layer
# model.add(Dense(units=1))

# # Compile the model
# model.compile(optimizer='adam', loss='mean_squared_error')

# # Train the model
# model.fit(x_train, y_train, epochs=10, batch_size=64)

# # Use the last 60 days of data from the training set to start predictions
# last_sequence = scaled_data[-sequence_length:]
# last_sequence = np.reshape(last_sequence, (1, sequence_length, 1))

# # Function to calculate the number of days from today to the input date
# def calculate_days_to_future(target_year, target_month, target_day):
#     current_date = datetime.now()
#     target_date = datetime(target_year, target_month, target_day)
#     delta = target_date - current_date
#     return delta.days

# # Forecast future prices for a given number of days
# def forecast_future_prices(model, last_sequence, days_to_predict, scaler):
#     forecasted_prices = []
#     current_sequence = last_sequence

#     for _ in range(days_to_predict):
#         # Make the prediction
#         prediction = model.predict(current_sequence)
        
#         # Inverse scale the prediction to get the actual price
#         forecasted_price = scaler.inverse_transform(prediction)
#         forecasted_prices.append(forecasted_price[0][0])

#         # Reshape prediction to match the dimensions of current_sequence
#         prediction_reshaped = np.reshape(prediction, (1, 1, 1))

#         # Update the sequence by adding the predicted price and removing the oldest value
#         current_sequence = np.append(current_sequence[:, 1:, :], prediction_reshaped, axis=1)

#     return forecasted_prices


# # User input for the target date (future year, month, and day)
# target_year = int(input("Enter the year (YYYY): "))
# target_month = int(input("Enter the month (MM): "))
# target_day = int(input("Enter the day (DD): "))

# # Calculate how many days to forecast into the future
# days_to_forecast = calculate_days_to_future(target_year, target_month, target_day)

# if days_to_forecast < 0:
#     print("The input date is in the past. Please enter a future date.")
# else:
#     # Predict for the given future date
#     forecasted_prices = forecast_future_prices(model, last_sequence, days_to_forecast, scaler)
#     predicted_price_for_date = forecasted_prices[-1]

#     print(f'Predicted Bitcoin Price for {target_year}-{target_month:02d}-{target_day:02d}: {predicted_price_for_date}')

#     # Plot the forecasted prices
#     plt.plot(range(1, days_to_forecast + 1), forecasted_prices, label='Forecasted Prices')
#     plt.title(f'Bitcoin Price Forecast until {target_year}-{target_month:02d}-{target_day:02d}')
#     plt.xlabel('Days from today')
#     plt.ylabel('Price (USD)')
#     plt.legend()
#     plt.show()







#new code


import numpy as np
from tensorflow.keras.models import load_model
import joblib
import pandas as pd

def forecast_future(file_path, model_name, scaler_name, days_ahead=30, interval_length=60):
    # Load the model and scaler
    model = load_model(model_name)
    scaler = joblib.load(scaler_name)

    # Load the dataset
    data = pd.read_csv(file_path)
    data['Open time'] = pd.to_datetime(data['Open time'])
    data.set_index('Open time', inplace=True)
    prices = data['Close']

    # Normalize and get the last sequence
    prices_scaled = scaler.transform(prices.values.reshape(-1, 1))
    last_sequence = prices_scaled[-interval_length:]  # Last `interval_length` from the dataset

    # Forecast future prices
    predictions = []
    current_sequence = last_sequence

    for _ in range(days_ahead):
        pred = model.predict(current_sequence.reshape(1, interval_length, 1))
        predictions.append(pred[0, 0])
        current_sequence = np.append(current_sequence[1:], pred)

    predictions = np.array(predictions).reshape(-1, 1)
    predictions = scaler.inverse_transform(predictions)

    return predictions

# Predict for 1-hour, 4-hour, and 15-minute intervals
file_configs = [
    {'file': 'bitcoin_1hr.csv', 'model': 'model_1hr.h5', 'scaler': 'scaler_1hr.save'},
    {'file': 'bitcoin_4hr.csv', 'model': 'model_4hr.h5', 'scaler': 'scaler_4hr.save'},
    {'file': 'bitcoin_15min.csv', 'model': 'model_15min.h5', 'scaler': 'scaler_15min.save'}
]

for config in file_configs:
    future_prices = forecast_future(config['file'], config['model'], config['scaler'], days_ahead=30)
    print(f"Forecasted Prices ({config['file']}):")
    print(future_prices)
