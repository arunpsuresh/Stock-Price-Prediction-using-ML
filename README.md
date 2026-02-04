A Flask-based web application that combines LSTM deep learning stock prediction with a financial advisory platform.
The system allows users to view predicted stock/crypto prices, consult advisors, make payments, and interact through chat and feedback, while admins manage the platform.

ADMIN

Manage advisors

Send notifications

View complaints

View ratings & reviews

ADVISOR

Set consultation fees

Send investment recommendations (video upload)

Chat with users

View feedback

Provide ratings & reviews

Stock price prediction access

USER

Register/login

View advisors

Send consultation requests

Make payments

Chat with advisors

Send feedback & complaints

View stock predictions

BACKEND

Python

Flask

MySQL

Machine Learning

TensorFlow / Keras

LSTM Neural Networks

Scikit-learn (MinMaxScaler)

FRONTEND

HTML

CSS

Jinja2 Templates

APIs & LIBRARIES

CryptoCompare API

Pandas

NumPy


1️⃣ Clone Repository
git clone https://github.com/yourusername/stock-prediction.git
cd stock-prediction

2️⃣ Install Dependencies
pip install flask mysql-connector-python pandas numpy scikit-learn tensorflow cryptocompare

3️⃣ Setup Database

Create MySQL database:

stockprediction


Update credentials in database.py:

user="root"
password=""
database="stockprediction"

4️⃣ Run Application
python main.py


Open browser:

http://127.0.0.1:5078
