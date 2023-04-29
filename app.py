from flask import Flask,flash,redirect,render_template,url_for,request,jsonify,session,send_file
from flask_mysqldb import MySQL
#from flaskext.mysql import MySQL
from io import BytesIO
from otp import genotp
from cmail import sendmail
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
app=Flask(__name__)
app.secret_key='*67@hjyjhk'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
#app.config['MYSQL_DATABASE_HOST'] ='localhost'
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD']='admin'
app.config['MYSQL_PASSWORD']='admin'
#app.config['MYSQL_DATABASE_DB']='CMA'
app.config['MYSQL_DB']='CMA'
app.config["SESSION_TYPE"] = "filesystem"
mysql=MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home/<id>')
def chat(id):
    cursor=mysql.connection.cursor()
    #cursor=mysql.get_db().cursor()
    cursor.execute('SELECT following from friends where followers=%s',[id])
    data=cursor.fetchall()
    return render_template('chat.html',id=id,data=data)


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=="POST":
        id=request.form['Username']
        First_Name=request.form['First_Name']
        Last_Name=request.form['Last_Name']
        Bio=request.form['Bio'] #Bio Column
        Email=request.form['Email']
        Password=request.form['Password']
        #cursor=mysql.get_db().cursor()
        cursor=mysql.connection.cursor()
        cursor.execute("select id from users")
        data=cursor.fetchall()
        cursor.execute("select Email from users")
        edata=cursor.fetchall()
        if (id,) in data:
            flash("id already exist")
            return redirect(url_for('home'))
        if(Email,) in edata:
            flash("Email Alreday Exists")
            return redirect(url_for('home'))
        otp=genotp()
        subject='Thanks for registering to the application'
        body=f'Use this otp to register {otp}'
        sendmail(Email,subject,body)
        return render_template('otp.html',otp=otp,id=id,First_Name=First_Name,Last_Name=Last_Name,Email=Email,Password=Password,Bio=Bio)
        # cursor.execute('insert into users(id,Frist_Name,Last_Name,Email,Password) values(%s,%s,%s,%s,%s)',[id,First_Name,Last_Name,Email,Password])
        # #mysql.get_db().commit()
        # mysql.connection.commit()
        # cursor.close()
        # flash('details registered') 
        # return redirect(url_for('home'))
    return render_template('Signup.html')
@app.route('/otp/<otp>/<id>/<First_Name>/<Last_Name>/<Email>/<Password>/<Bio>',methods=['GET','POST'])
def otp(otp,id,First_Name,Last_Name,Email,Password,Bio):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            # lst=[id,First_Name,Last_Name,Email,Password]
            # query='insert into users values(%s,%s,%s,%s,%s)'
            cursor.execute('insert into users(id,First_Name,Last_Name,Email,Password,Bio) values(%s,%s,%s,%s,%s,%s)',(id,First_Name,Last_Name,Email,Password,Bio))
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,id=id,First_Name=First_Name,Last_Name=Last_Name,Email=Email,Password=Password,Bio=Bio)



@app.route('/login', methods =['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('chat',id=session['user']))
    if request.method=="POST":
        user=request.form['Username']
        password=request.form['Password']
        cursor=mysql.connection.cursor()
        #cursor=mysql.get_db().cursor()
        cursor.execute('select id from users')
        users=cursor.fetchall()            
        cursor.execute('select password from users where id=%s',[user])
        data=cursor.fetchone()
        #mysql.get_db().commit()
        mysql.connection.commit()
        cursor.close()
        if (user,) in users:
            if password==data[0]:
                session["user"]=user
                return redirect(url_for('chat',id=user))
            else:
                flash('Invalid Password')
                return render_template('login.html')
        else:
            flash('Invalid id')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session['user']=None
    return redirect(url_for('home'))


@app.route('/addcontact',methods=['GET','POST'])
def addcontact():
    #cursor=mysql.get_db().cursor()
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT id  from users where id!=%s',[session.get('user')])
    data=cursor.fetchall()
    cursor.execute('select following from friends where followers=%s',[session.get('user')])
    new_data=cursor.fetchall()
    data=tuple([i for i in data if i  not in new_data])
    print(data)
    if request.method=="POST":
        Enter_Username=request.form['option']
        #cursor=mysql.get_db().cursor()
        cursor=mysql.connection.cursor()
        cursor.execute('insert into friends values(%s,%s)',[session.get('user'),Enter_Username])
        #mysql.get_db().commit()
        mysql.connection.commit()
        return redirect(url_for('chat',id=session.get('user')))
    return render_template('Addcontact.html',data=data)


@app.route('/profile',methods=["GET","POST"])
def profilepage():
    # if request.method=="POST":
    #     name=request.form['Name']
    #     about=request.form['About']
    #     #cursor=mysql.get_db().cursor()
    #     cursor=mysql.connection.cursor()
    #     #cursor.execute('select name,about from profile')
    #     cursor.execute('insert into profile(name,about) values(%s,%s)',[name,about])
    #     cursor.connection.commit()
    #     data=cursor.fetchall()
    #     print(data)
    #     cursor.execute('select name,bio from users')
    #     cursor.connection.commit()
    #     cursor.close()
        
    #     return redirect(url_for('chat',id=session['user'],data=data))
     
    cursor=mysql.connection.cursor()
    cursor.execute('select First_Name,Last_Name,Email,Bio from users where id=%s',[session.get('user')])
    data=cursor.fetchone()
    print(data)
    cursor.connection.commit()
    cursor.close()

    
    return render_template('Profile.html',data=data)


@app.route('/settings')
def settings():
    return render_template('setting.html')


@app.route('/back')
def back():
    return redirect(url_for('login'))


@app.route('/message/<id>',methods=['GET','POST'])
def message(id):
    if session.get('user'):
        #cursor=mysql.get_db().cursor()
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT message,date_format(created_at,'%%h:%%i %%p') as date from messenger where followers=%s and following=%s order by date",(session.get('user'),id))
        sender=cursor.fetchall()
        cursor.execute("SELECT message,date_format(created_at,'%%h:%%i %%p') as date from messenger where followers=%s and following=%s order by date",(id,session.get('user')))
        reciever=cursor.fetchall()
        cursor.execute('select filename from files where follower=%s and following=%s',(session.get('user'),id))
        sender_files=cursor.fetchall()
        cursor.execute('select filename from files where follower=%s and following=%s',(id,session.get('user')))
        reciever_files=cursor.fetchall()
        cursor.close()
        if request.method=='POST':
            if 'file' in request.files:
                file=request.files['file']
                filename=file.filename
                #cursor=mysql.get_db().cursor()
                cursor=mysql.connection.cursor()
                cursor.execute('INSERT INTO files (follower,following,filename,file) values(%s,%s,%s,%s)',(session.get('user'),id,filename,file.read()))
                #mysql.get_db().commit()
                mysql.connection.commit()
                cursor.execute('select filename from files where follower=%s and following=%s',(session.get('user'),id))
                sender_files=cursor.fetchall()
                cursor.execute('select filename from files where follower=%s and following=%s',(id,session.get('user')))
                reciever_files=cursor.fetchall()
                return render_template('Messenger.html',id=id,sender=sender,reciever=reciever,sender_files=sender_files,reciever_files=reciever_files)
            message=request.form['Message']
            # cursor=mysql.get_db().cursor()
            cursor=mysql.connection.cursor()
            cursor.execute('INSERT INTO messenger(followers,following,message) values(%s,%s,%s)',(session['user'],id,message))
            #mysql.get_db().commit()
            mysql.connection.commit()
            cursor.execute("SELECT message,date_format(created_at,'%%h:%%i %%p') as date from messenger where followers=%s and following=%s order by date",(session.get('user'),id))
            sender=cursor.fetchall()
            cursor.execute("SELECT message,date_format(created_at,'%%h:%%i %%p') as date from messenger where followers=%s and following=%s order by date",(id,session.get('user')))
            reciever=cursor.fetchall()
        return render_template('Messenger.html',id=id,sender=sender,reciever=reciever,sender_files=sender_files,reciever_files=reciever_files)
    return redirect(url_for('login'))

@app.route('/download/<filename>')
def download(filename):
    #cursor=mysql.get_db().cursor()
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT file from files where filename=%s',[filename])
    data=cursor.fetchone()[0]
    return send_file(BytesIO(data),download_name=filename,as_attachment=True)
@app.route('/forgetpassword',methods=['GET','POST'])
def forget():
    if request.method=='POST':
        id=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select id from users')
        data=cursor.fetchall()
        if (id,) in data:
            cursor.execute('select email from users where id=%s',[id])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the passwword using- {request.host+url_for("createpassword",token=token(id,120))}'
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
        id=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update users set password=%s where id=%s',[npass,id])
                mysql.connection.commit()
                flash('Password reset Successfull')
                return redirect(url_for('login'))
            else:
                return 'Password mismatch'
        return render_template('newpassword.html')
    except:
        return 'Link expired try again'
    





app.run(use_reloader=True,debug=True)


