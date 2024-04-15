from flask import *
from pymongo import MongoClient

import random
from datetime import datetime
from pymongo import MongoClient
app=Flask(__name__,static_url_path='/static')
client=MongoClient('mongodb://localhost:27017/')
db=client['airlines']
app.secret_key="afsgsgsjoj"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home')
def home1():
    return render_template('home.html')

@app.route('/login')
def login():
    if 'user' not in session:
         return render_template('login.html')
    else:
        return redirect('/logout')

@app.route('/dlogin',methods=['POST'])
def dlogin():
    username=request.form['username']
    password=request.form['password']
    if (username=="admin" and password=="admin"):
        session['user']="admin"
        session['userid']=1
        return render_template('admin.html',name=username)
    else:
        result=db.accounts.find_one({"first":username,"password":password})
        if(result):
            session['user']=result["first"]
            session["userid"]=result["userid"]
            return render_template('home.html')
        else:
            return "you have entered wrong credentials,try again"

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user',None)
        session.pop('userid',None)
        return render_template('logout.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dregister',methods=['POST'])
def dregister():
    firstname=request.form['username']
    lastname=request.form['last']
    mail=request.form['email']
    mob=request.form['mobile']
    password=request.form['password']
    userid=firstname+str(random.randint(1,1000))
    db.accounts.insert_one({"first":firstname,"last":lastname,"email":mail,"mobile":mob,"password":password,"userid":userid})
    return render_template('dregister.html',first=firstname)

@app.route('/add',methods=['POST'])
def add():
    flight_id=request.form['flight_id']
    name=request.form['name']
    fromp=request.form['from']
    top=request.form['to']
    departure_date=request.form['departure_date']
    arrival_date=request.form['arrival_date']
    first_class=int(request.form['seats'])//3
    business=first_class
    economy=first_class+int(request.form['seats'])%3
    departure=request.form['departure']+":00"
    arrival=request.form['arrival']+":00"
    economy_p=request.form['economy']
    business_p=request.form['business']
    first_class_p=request.form['first_class']
    if(db.flights.insert_one({"flight_id":flight_id,"flight_name":name,"from_place":fromp,"to_place":top,"departure_date":departure_date,"arrival_date":arrival_date,"economy":economy,"business":business,"first_class":first_class,"departure":departure,"arrival":arrival, "economy_p":economy_p,"business_p":business_p,"first_class_p":first_class_p })):
        return render_template('afteradd.html')

@app.route('/book',methods=['POST'])
def book():
    from_place=request.form['from']
    to_place=request.form['to']
    date=request.form['date']
    ses=""
    if 'user' in session:
        ses=session['user']
    if(date==""):
        data=db.flights.find({"from_place":from_place,"to_place":to_place})
        return render_template('book.html',ses=ses,res=data)
    else:
        data=db.flights.find({"from_place":from_place,"to_place":to_place,"departure_date":date})
        return render_template('book.html',ses=ses,res=data)

@app.route('/confirm',methods=['POST'])
def confirm():
    ses=""
    if 'user' in session:
        ses=session['user']
    flight_id=request.form["flight_id"]
    data=db.flights.find_one({"flight_id":flight_id})
    return render_template('confirm.html',row=data,ses=ses)

@app.route('/confirmed',methods=['POST'])
def confirmed():
    pnr=random.randint(10**5,10**12)
    flight_name=request.form['flight_name']
    flight_id=request.form['flight_id']
    fromp=request.form['from']
    top=request.form['to']
    classes=request.form['classes']
    fare=int(request.form['fare'])
    depdate=request.form['depdate']
    arrdate=request.form['arrdate']
    dep=request.form['dep']
    arr=request.form['arr']
    numberof=int(request.form['numberof'])
    fare=fare*numberof
    e=int(request.form['economy'])
    b=int(request.form['business'])
    f=int(request.form['first_class'])
    userid=session['userid']
    data1=db.bookings.insert_one({"pnr":pnr,"userid":userid,"flight_id":flight_id,"flight_name":flight_name,"from_place":fromp,"to_place":top,"classes":classes,"fare":fare,"seats_booked":numberof,"departure_date":depdate,"arrival_date":arrdate,"departure":dep,"arrival":arr})
    if(data1):
        data2=db.flights.update_one({"flight_id":flight_id},{"$set":{"economy":e,"business":b,"first_class":f}})
        if(data2):
            return render_template('confirmed.html',pnr=pnr)

@app.route('/profile')
def profile():
    if 'user' not in session:
        return render_template('profileout.html')
    else:
        ses=session['userid']
        data1=db.accounts.find({"userid":ses})
        today=datetime.now().strftime('%Y-%m-%d')
        if(data1):
            data2=db.bookings.find({"userid":ses})
            data2=sorted(data2,key=lambda x: datetime.strptime(x['departure_date'],'%Y-%m-%d'))
            return render_template('profile.html',data1=data1,data2=data2,today=today)
        
@app.route('/cancel',methods=['POST'])
def cancel():
    es,bs,fs=0,0,0
    pnr=int(request.form['pnr'])
    flight_id=request.form['flight_id']
    data1=db.bookings.find_one({"pnr":pnr})
    if(data1):
        if(data1['classes']=='Economy'):
             es=data1['seats_booked']
        elif(data1['classes']=='Business'):
             bs=data1['seats_booked']
        else:
             fs=data1['seats_booked']
    data2=db.flights.update_one({"flight_id":flight_id},{"$inc":{"economy":es,"business":bs,"first_class":fs}})
    if(data2):
        data3=db.bookings.delete_one({"pnr":pnr})
        if(data3):
            return redirect('/profile')

@app.route('/contact')
def contct():
    return render_template('contact.html')

@app.route('/dcontact',methods=['POST'])
def dcontact():
    name=request.form['name']
    desc=request.form['description']
    return render_template('dcontact.html',name=name,desc=desc)

@app.route('/about')
def about():
    return render_template('about.html')
if __name__=='__main__':
    app.run(debug=True)