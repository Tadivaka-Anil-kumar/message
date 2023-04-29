from flask import Flask,render_template,session,url_for,request,flash,redirect
from flask_session import Session
from otp import genotp
from cmail import sendmail
from flask_mysqldb import MySQL
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
from flask_login import current_user, login_required
app=Flask(__name__)
app.secret_key='*67@hjyjhk'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='cma'
Session(app)
mysql=MySQL(app)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration', methods=['POST','GET'])
def register():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        dob=request.form['dob']
        mobile=request.form['mobile']
        password=request.form['password']
        cpassword=request.form['cpassword']
        gender=request.form['gender']
        
        if True:
            cursor=mysql.connection.cursor()
            cursor.execute('select username from users')
            data=cursor.fetchall()
            cursor.execute('select email from users')
            edata=cursor.fetchall()
            if(username,) in data:
                flash('Username Already registerd')
                return render_template('regform.html')
            if(email,) in edata:
                flash('MailId Already Registered')
                return render_template('regform.html')
            
        
        otp=genotp()
        subject='Thanks for registering to the application'
        body=f'Use this otp to register {otp}'
        sendmail(email,subject,body)
        return render_template('otp.html',otp=otp,username=username,email=email,dob=dob,mobile=mobile,password=password,cpassword=cpassword,gender=gender)
        
    #cursor.execute('insert into users(fullname,username,dob,mobile,password,cpassword,gender)values(%s,%s,%s,%s,%s,%s,%s)',(fullname,username,dob,mobile,password,cpassword,gender))
    #mysql.connection.commit()
    #cursor.close()
    return render_template('regform.html')
@app.route('/otp/<otp>/<username>/<email>/<dob>/<mobile>/<password>/<cpassword>/<gender>',methods=['GET','POST'])
def otp(otp,username,email,dob,mobile,password,cpassword,gender):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            lst=[username,email,dob,mobile,password,cpassword,gender]
            query='insert into users values(%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,username=username,email=email,dob=dob,mobile=mobile,password=password,cpassword=cpassword,gender=gender)

@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from users where email=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid Username or password')
            return render_template('login.html')
        else:
            session['user']=username
            return redirect(url_for('home'))
    return render_template('login.html')




@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('index'))
    else:
        flash('already logged out!')
    return redirect(url_for('login'))

# @app.route('/forget')
# def forget():
#     return "hello"




@app.route('/home')
def home():
     
    return render_template('home.html')


@app.route('/forgetpassword',methods=['GET','POST'])
def forget():
    if request.method=='POST':
        username=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select username from users')
        data=cursor.fetchall()
        if (username,) in data:
            cursor.execute('select email from users where username=%s',[username])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the passwword using- {request.host+url_for("createpassword",token=token(username,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user id'
    return render_template('forgot.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        username=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update users set password=%s where username=%s',[npass,username])
                mysql.connection.commit()
                return 'Password reset Successfull'
            else:
                return 'Password mismatch'
        return render_template('newpassword.html')
    except:
        return 'Link expired try again'
    

@app.route('/addfriends')
def addfriends():
     
     cursor=mysql.connection.cursor()
     cursor.execute('select username from users')
     data=cursor.fetchall()
     return render_template('addfriends.html',data=data)
@app.route('/profiledashboard')
def profiledashboard():
    return render_template('profile.html')

@app.route('/chatpage')
def chatpage():

     return render_template('chatpage.html')
@app.route('/dashboard')
def dashboard():
    if session.get('user'):
    cursor=mysql.connection.cursor()
    cursor.execute('select username from users where email=%s',(current_user.email,))
    username = cursor.fetchone()[0]
    print(username)
    cursor.close()
    mysql.connection.commit()
    return render_template('profile.html', username=username)












          



app.run(debug=True,use_reloader=True)

