from flask import *
from database import *
user=Blueprint('user',__name__)

@user.route("/use")
def use():
    return render_template("user.html")

@user.route("/complaint",methods=['POST','GET'])
def register():
    if 'register' in request.form:
        h=request.form['cmt']
        print(h)
        qry2="insert into complaint values(null,'%s','%s','pending',curdate())"%(session['user'],h)
        insert(qry2)

    return render_template("complaint.html")

@user.route("/user_notification",methods=['POST','GET'])
def user_notification():
    if 'submit' in request.form:
        a=request.form['notification']
        
        qry1="insert into notification values(null,'%s','%s',curdate())"%(session['log'],a)
        insert(qry1)

    return render_template("user_notification.html")

@user.route("/user_send_complaints_view_reply",methods=['POST','GET'])
def user_send_complaints_view_reply():
    data={}
    qry="select * from complaint"
    res=select(qry)
    data['view']=res

    if 'submit' in request.form:
        a=request.form['title']
        b=request.form['description']
        
        qry1="insert into complaint values(null,'%s','%s','%s','pending',curdate())"%(session['log'],a,b)
        insert(qry1)
        return """<script>alert("complaint send successfully");window.location="/user_send_complaints_view_reply"</script>"""

    return render_template("user_send_complaints_view_reply.html",data=data)

@user.route("/user_send_ratings_reviews",methods=['POST','GET'])
def user_send_ratings_reviews():
    data={}
    qry="select * from rating"
    res=select(qry)
    data['view']=res

    if 'submit' in request.form:
        a=request.form['rating']
        b=request.form['review']
        
        qry1="insert into rating values(null,'%s','%s','%s',curdate())"%(session['log'],a,b)
        insert(qry1)
    return render_template("user_send_ratings_reviews.html",data=data)

@user.route("/user_send_feedback_to_adv",methods=['POST','GET'])
def user_send_feedback_to_adv():

    if 'submit' in request.form:
        a=request.form['feedback']
        
        qry1="insert into feedback values(null,'%s','%s',curdate())"%(session['log'],a)
        insert(qry1)
        return """<script>alert("feedback send successfully");window.location="/user_send_feedback_to_adv"</script>"""

    return render_template("user_send_feedback_to_adv.html")



@user.route("/view_advisors",methods=['POST','GET'])
def view_advisors():
    data={}
    qry="select * from advisors inner join login using(login_id) where usertype='advisors'"
    res=select(qry)
    data['view']=res

    return render_template("view_advisors.html",d=data)



@user.route("/user_request",methods=['POST','GET'])
def user_request():

    advisor_id=request.args['id']

    if 'submit' in request.form:

        a=request.form['title']
        b=request.form['description']
       
        qry1="insert into request values(null,'%s','%s','%s',curdate(),'pending','%s')"%(advisor_id,a,b,session['user'])
        insert(qry1)
        return """<script>alert("consultation request send successfully");window.location="/view_request"</script>"""

    return render_template("user_request.html")


@user.route("/view_request",methods=['POST','GET'])
def view_request():
    data={}
    qry="select * from request innner join advisors using(advisor_id) inner join fee using (advisor_id) where user_id='%s'"%(session['user'])
    res=select(qry)
    data['view']=res

    return render_template("view_request.html",d=data)

@user.route("/user_payment",methods=['POST','GET'])
def user_payment():

    advisor_id=request.args['advisor_id']
    amount=request.args['amt']

    if 'submit' in request.form:
        a=request.form['Amount']


        print(a)
        qry1="insert into payment values(null,'%s','%s','%s','paid',curdate())"%(session['user'],advisor_id,a)
        insert(qry1)
        return """<script>alert("Payment successfully completed");window.location="/view_request"</script>"""

    return render_template("user_payment.html",amt=amount)




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
@user.route('/user_view_stock_price', methods=['POST', 'GET'])
def user_view_stock_price():
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
    
    return render_template("user_view_stock_price.html")


@user.route('/user_chat',methods=['POST','GET'])
def user_chat():
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
        a="insert into chat values(null,'%s','%s','%s','advisor','user',curdate(),curtime())"%(session['log'],session['id'],chat)
        insert(a)
        return redirect(url_for('user.user_chat'))
    return render_template("user_chat.html",data=data,name=name)





   
