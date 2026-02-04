from flask import *
from database import *
public=Blueprint('public',__name__)

@public.route("/")
def home():
    return render_template("home.html")

@public.route("/login",methods=['POST','GET'])
def login():
    if 'login' in request.form:
        a=request.form['u']
        b=request.form['p']
        print(a,b)

        z="select * from login where username='%s' and password='%s'"%(a,b)
        e=select(z)
        print(e)

        if e:
            session['log']=e[0]['login_id']
            if e[0]['usertype']=='admin':
                return redirect(url_for('admin.adm'))
            elif e:
                if e[0]['usertype']=='user':
                    q="select * from user where login_id='%s'"%(session['log'])
                    r=select(q)
                    if r:
                        session['user']=r[0]['User_id']
                    return redirect(url_for('user.use'))
                if e[0]['usertype']=='advisors':
                    q="select * from advisors where login_id='%s'"%(session['log'])
                    r=select(q)
                    if r:
                        session['advisor']=r[0]['advisor_id']
                    return redirect(url_for('advisors.adv'))
            elif e:

                if e[0]['usertype']=='user':
                    q="select * from user where login_id='%s'"%(session['log'])
                    r=select(q)
                    if r:
                        session['user']=r[0]['User_id']
                    return redirect(url_for('user.use'))
    return render_template("login.html")

@public.route("/register",methods=['POST','GET'])
def register():
    if 'submit' in request.form:
        print("/////////////////////////")
        a=request.form['uname']
        b=request.form['password']
        c=request.form['name']
        d=request.form['place']
        e=request.form['phone']
        f=request.form['email']
        g=request.form['Work_exp']
        h=request.form['proff_certificate']
        print(c,d,e,f,g,h)
        qry="insert into login values(null,'%s','%s','pending')"%(a,b)
        res=insert(qry)

        qry1="insert into advisors values(null,'%s','%s','%s','%s','%s','%s','%s')"%(res,c,d,e,f,g,h)
        insert(qry1)
        return "<script>alert('Registered successfully');window.location='/register'</script>"

    return render_template("advisor_register.html")

@public.route("/user_register",methods=['POST','GET'])
def user_register():
    if 'submit' in request.form:
        a=request.form['uname']
        b=request.form['password']
        c=request.form['name']
        d=request.form['phone']
        e=request.form['gender']
        f=request.form['email']
        g=request.form['place']
    
        print(a,b,c,d,e,f,g)

        qry="insert into login values(null,'%s','%s','user')"%(a,b)
        res=insert(qry)

        qry1="insert into user values(null,'%s','%s','%s','%s','%s','%s')"%(res,c,d,e,f,g)
        insert(qry1)
        return "<script>alert('Registered successfully');window.location='/user_register'</script>"

    return render_template("user_register.html")

