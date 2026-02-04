from flask import *
from database import *
admin=Blueprint('admin',__name__)

@admin.route("/adm")
def adm():
    return render_template("admin.html")

@admin.route("/admin_manage_notification",methods=['POST','GET'])
def admin_manage_notification():
    if 'submit' in request.form:
        a=request.form['Notification']
        
        qry1="insert into notification values(null,'%s','%s',curdate())"%(session['log'],a)
        insert(qry1)

    return render_template("admin_manage_notification.html")

@admin.route("/admin_view_advisors",methods=['POST','GET'])
def admin_view_advisors():
    data={}
    qry="select * from advisors inner join login using(login_id)"
    res=select(qry)
    data['view']=res

    if 'action' in request.args:
        act=request.args['action']
        id=request.args['lid']
        if act == 'accept':
            q="update login set usertype='advisors' where login_id='%s'"%(id)
            update(q)
            return"""<script>alert("Accepted);window.location=/admin_view_advisors</script>"""
        if act == 'reject':
            q="update login set usertype='rejected' where login_id='%s'"%(id)
            update(q)
            return"""<script>alert("Rejected");window.location=/admin_view_advisors</script>"""
    return render_template("admin_view_advisors.html",d=data)

@admin.route("/admin_view_reply_complaint",methods=['POST','GET'])
def admin_view_reply_complaint():
    data={}
    qry="select * from complaint"
    res=select(qry)
    data['view']=res
    return render_template("admin_view_reply_complaint.html",data=data)

@admin.route("/admin_view_ratings_reviews",methods=['POST','GET'])
def admin_view_ratings_reviews():
    data={}
    qry="select * from rating"
    res=select(qry)
    data['view']=res
    return render_template("admin_view_ratings_reviews.html",data=data)
