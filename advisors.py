import uuid
from flask import *
from database import *
advisors=Blueprint('advisors',__name__)

@advisors.route("/adv")
def adv():
    return render_template("advisor.html")

@advisors.route("/advisor_manage_fee",methods=['POST','GET'])
def advisor_manage_fee():
    if 'submit' in request.form:
        a=request.form['Amount']
        print(a)
        qry1="insert into fee values(null,'%s','%s')"%(session['advisor'],a)
        insert(qry1)

    return render_template("advisor_manage_fee.html")

@advisors.route("/advisors_notification",methods=['POST','GET'])
def advisors_notification():
    if 'submit' in request.form:
        a=request.form['notification']
        
        qry1="insert into notification values(null,'%s','%s',curdate())"%(session['log'],a)
        insert(qry1)

    return render_template("advisors_notification.html")

@advisors.route("/advisors_view_feedback",methods=['POST','GET'])
def advisors_view_feedback():
    data={}
    qry="select * from feedback"
    res=select(qry)
    data['view']=res

    return render_template("advisors_view_feedback.html",data=data)

@advisors.route("/advisors_send_ratings_reviews",methods=['POST','GET'])
def advisors_send_ratings_reviews():
    data={}
    qry="select * from rating"
    res=select(qry)
    data['view']=res

    if 'submit' in request.form:
        a=request.form['rating']
        b=request.form['review']
        
        qry1="insert into rating values(null,'%s','%s','%s',curdate())"%(session['log'],a,b)
        insert(qry1)
    return render_template("advisors_send_ratings_reviews.html",data=data)

@advisors.route("/advisors_send_complaint_view_reply",methods=['POST','GET'])
def advisors_send_complaint_view_reply():
    data={}
    qry="select * from complaint"
    res=select(qry)
    data['view']=res

    if 'submit' in request.form:
        a=request.form['title']
        b=request.form['description']
        
        qry1="insert into complaint values(null,'%s','%s','%s','pending',curdate())"%(session['log'],a,b)
        insert(qry1)
        return """<script>alert("complaint send successfully");window.location="/'advisors_send_complaint_view_reply'</script>"""

    return render_template("advisors_send_complaint_view_reply.html",data=data)

@advisors.route("/advisors_investment_recommendations",methods=['POST','GET'])
def advisors_investment_recommendations():
    data={}
    qry="select * from investment_recommendations"
    res=select(qry)
    data['view']=res

    if 'submit' in request.form:
        a=request.files['video']

        path='static/inv_videos/'+str(uuid.uuid4())+a.filename
        a.save(path)

        b=request.form['title']
        c=request.form['description']
        
        qry1="insert into investment_recommendations values(null,'%s','%s','%s','%s',curdate())"%(session['advisor'],path,b,c)
        insert(qry1)
        return """<script>alert("investment recommendations send successfully");window.location="/advisors_investment_recommendations"</script>"""


    return render_template("advisors_investment_recommendations.html",res=data)



import cryptocompare
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from flask import Flask, request, render_template



# Fetch historical Bitcoin data
def fetch_stock_data():
    data = cryptocompare.get_historical_price_day(
        'BTC', 
        toTs=int(datetime.now().timestamp()), 
        limit=1095  # Last 3 years of data
    )
    
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'], unit='s', errors='coerce')
    df = df[['time', 'close']]
    
    df.to_csv('stock_data.csv', index=False)
    return df

# Preprocess data for training
def preprocess_data():
    df = pd.read_csv('stock_data.csv')
    
    # Extract and normalize prices
    prices = df['close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    prices_scaled = scaler.fit_transform(prices)
    
    # Create time-series data for LSTM
    N = 60  # Number of past days for prediction
    X, y = [], []
    for i in range(N, len(prices_scaled)):
        X.append(prices_scaled[i-N:i, 0])
        y.append(prices_scaled[i, 0])
    
    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)  # Reshape for LSTM input
    return X, y, scaler

# Build and train the LSTM model
def build_model(X_train, y_train):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))  # Single output
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=1)
    return model

# Forecast Bitcoin price for a future date
def forecast(model, scaler, X_full):
    # Use the last 60 days of prices for prediction
    last_60_days = X_full[-60:].reshape(1, 60, 1)
    
    # Predict scaled price
    predicted_price_scaled = model.predict(last_60_days)
    
    # Convert back to original scale
    predicted_price = scaler.inverse_transform(predicted_price_scaled)
    
    return predicted_price[0][0]

# Route for displaying and processing the Bitcoin prediction form
@advisors.route('/advisor_view_stock_price', methods=['POST', 'GET'])
def advisor_view_stock_price():
    if request.method == 'POST':
        year = request.form['year']
        month = request.form['month']
        date = request.form['date']
        
        # Fetch historical Bitcoin data
        df = fetch_stock_data()
        
        # Preprocess data and build model
        X, y, scaler = preprocess_data()
        model = build_model(X, y)
        
        try:
            # Make a prediction for the last 60 days
            predicted_price = forecast(model, scaler, df['close'].values.reshape(-1, 1))
            predicted_price = float(predicted_price)
            
            # Return a JSON response with the predicted price
            return jsonify({
                'status': 'success',
                'price': predicted_price
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            })
    
    return render_template("advisor_view_stock_price.html")


@advisors.route('/advisor_chat',methods=['POST','GET'])
def advisor_chat():
    data={}
    name=''
    if 'action' in request.args:
        action=request.args['action']
        session['id']=request.args['id']
        name=request.args['name']

    else:
        action=None
    
    f="SELECT * FROM chat WHERE sender_id='%s' AND receiver_id='%s' UNION SELECT * FROM chat WHERE sender_id='%s' AND receiver_id='%s' ORDER BY date , time"%(session['id'],session['log'],session['log'],session['id'])
    rg=select(f)
    print(rg)
    data['rg']=rg

    if 'submit' in request.form:
        chat=request.form['chat']
        print(chat,"000000000000000000000000000000000000000000000000")
        a="insert into chat values(null,'%s','%s','%s','user','advisor',curdate(),curtime())"%(session['log'],session['id'],chat)
        insert(a)
        return redirect(url_for('advisors.advisor_chat'))
    return render_template("advisors_chat_users.html",data=data,name=name)

@advisors.route('/advisor_paid_users')
def advisor_paid_users():
    data={}
    qry="select * from payment inner join user using(user_id) where advisor_id='%s' and status='paid'"%(session['advisor'])
    res=select(qry)
    data['view'] = res
    return render_template("advisor_view_paid_users.html",data=data)

