from flask import *
from public import public 
from admin import admin 
from user import user
from advisors import advisors

app=Flask(__name__)
app.secret_key='secretkey'

app.register_blueprint(public)
app.register_blueprint(admin)
app.register_blueprint(user)
app.register_blueprint(advisors)

app.run(debug=True,port=5078)



