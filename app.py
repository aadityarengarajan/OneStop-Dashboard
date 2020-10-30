
#/-  importing required modules

from flask import *
import csv
import datetime,os
import uuid
import requests
from flask_session import Session
import app_config
from flask_mail import Mail, Message



#/-  function to convert csv to a dictionary for extracting large amounts of data from csv comfortably

def csvtodict(csvfile):
    a_csv_file = open(csvfile, "r")
    dict_reader = csv.DictReader(a_csv_file)

    mainlist=[]
    for i in list(dict_reader):
        mainlist.append(dict(i))
    return mainlist

#/-  function to create a greeting string for the user based on current time

def greet():
    now = datetime.datetime.now()
    hour=int(now.hour)
    return (
        "Good Morning 🌅, " if 0 <= hour <= 12
        else
        "Good Afternoon 🌞," if 12 <= hour <=13
        else
        "Good Evening 🌇, "
    )

#/-  creating the flask app, and configuring it

app = Flask(__name__)
app.config['CLIENT_SECRET'] = str(uuid.uuid1())
app.config['SESSION_TYPE'] = 'filesystem'


#/-  creating a flask session for storing session variables (see https://flask-session.readthedocs.io/en/latest/)

Session(app)


#/-  creating a flask mail app (see https://pythonhosted.org/Flask-Mail/)
mail = Mail(app = app)

app.config['MAIL_SERVER']='smtp.mail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'onestop@solution4u.com'
app.config['MAIL_PASSWORD'] = 'sjar1234'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


#/-  custom flask decorator/wrap for not allowing cache

from flask import make_response
from functools import wraps, update_wrapper

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)



#/-  custom definition to send an email using Flask-Mail

def send_email(to,subj,content):
    Message(subj, to, content)

@app.route("/")
def homeredirection():
    from flask import g, session
    if not session.get("user"):
        session['loggedin']=False
        return redirect(url_for("login"))
    if session.get('loggedin')==False:
        return redirect(url_for("login"))
    else:
        return redirect(url_for("dashboard"))



@app.route("/login")
@nocache
def login():
    from flask import g, session
    return render_template("login.html")


@app.route('/signup', methods = ['POST','GET'])
@nocache
def signup(): #/- GET request is expected to be sent in by normal visits, POST requests by our forms for the signup process
    from flask import g, session
    if request.method == 'GET':
        return render_template("signup.html")
    if request.method == 'POST':

        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        bm = request.form['Birthday_Month']
        by = request.form['Birthday_Year']
        bd = request.form['Birthday_Day']
        DOB = bd +'/'+ bm +'/'+ by
        Class = request.form['Class']
        email = request.form['user_email']
        mobile = request.form['user_mobile_number']
        gender = request.form['user_gender']
        courses = request.form['Course']

        session["name"]=name
        session["username"]=username
        session["password"]=password
        session["DOB"]= DOB
        session['Email_Id']=email
        session['Mobile_Number']= mobile
        session['Class']= Class
        session['Gender']=gender
        session['Course']=courses


        with open('details.csv','a') as details:
            data=csv.writer(details)
            data.writerow([session.get('name'),session.get('username'),session.get('password'),session.get('DOB'),session.get('Class'), session.get('Gender'), session.get('Email_Id'), session.get('Mobile_Number'), 'student', session.get('Course')])
        return redirect(url_for('login'))

@app.route("/logout")
def logout():
    from flask import g, session

    session.clear() #/- clears all stored session variables
    return redirect(url_for('login'))

@app.route('/dashboard', methods = ['POST','GET'])
def dashboard():
    from flask import g, session
    if not session.get('name'): #/- checking if user is logged in
        session['username']=request.form['name']
        session['password']=request.form['pswd']
    with open('details.csv','r') as details:
        data=csv.reader(details)
        c=0
        for rec in data:
            if len(rec)<=10:
                pass
            if c==0:
                c+=1
                pass
            else:
                c+=1
                if (rec[1].upper()==session.get('username').upper() and rec[2]==session.get('password')):
                    session['name']=(rec[0]).capitalize()
                    session['greetings']=str(greet()+' '+str(session.get('name'))+'!')
                    session['studentdetails']=(
                    { 'name':rec[0],
                    'BOD': rec[3],
                    'class':f'{rec[4]}',
                    'Gender':rec[5],
                    'email':rec[6],
                    'phone':rec[7],
                    'position':rec[8],
                    'stream':rec[9]
                    })
                    session['studclass']=rec[4]
                    boardpapers=csvtodict('pastboardpaper.csv')
                    schoolpapers=csvtodict('schoolpapers.csv')
                    subjpapers=csvtodict('allsubject.csv')
                    session['boardpapers']=boardpapers
                    session['schoolpapers']=schoolpapers
                    session['subjpapers']=subjpapers


                    if session.get('studentdetails')['stream'].upper()=='PCMC':
                        session['subject']=['Chemistry','Computer','English','Mathematics','Physics']

                    elif session.get('studentdetails')['stream'].upper()=='PCMB':
                        session['subject']=['Biology','Chemistry','English','Mathematics','Physics']

                    elif session.get('studentdetails')['stream'].upper()=='PCPB':
                        session['subject']=['Biology','Chemistry','English','Psychology','Physics']

                    elif session.get('studentdetails')['stream'].upper()=='PCEM':
                        session['subject']=['Chemistry','Economics','English','Mathematics','Physics']

                    elif session.get('studentdetails')['stream'].upper()=='PCMB':
                        session['subject']=['Biology','Chemistry','English','Mathematics','Physics']

                    elif session.get('studentdetails')['stream'].upper()=='PCWB':
                        session['subject']=['Biology','Chemistry','English','Web Application','Physics']

                    elif session.get('studentdetails')['stream'].upper()=='CM':
                        session['subject']=['Accounts','Business','Economics','English','Mathematics']

                    elif session.get('studentdetails')['stream'].upper()=='CP':
                        session['subject']=['Accounts','Business','Economics','English','Psychology']

                    elif session.get('studentdetails')['stream'].upper()=='CW':
                        session['subject']=['Accounts','Business','Economics','English','Web Application']

                    elif session.get('studentdetails')['stream'].upper()=='HM':
                        session['subject']=['Economics','English','Mathematics','Political Science','Psychology']

                    elif  session.get('studentdetails')['stream'].upper()=='HW':
                        session['subject']=['Economics','English','Political Science','Psychology','Web Application']

                    else:
                        return 'e'
                    session['loggedin']=True
                    return redirect(url_for("inbox"))
        else:
            return 'wrong password or username, try again.'

@app.route('/circular/compose')
def composemail():
    return render_template("composemail.html")

#/-  new folder with unique code is created with individual content

@app.route('/circular/post', methods = ['POST'])
def sendmail():
    from flask import g, session

    content=request.form['content']
    isfiles=False
    try:
        file=request.files['file']
        isfiles=True
    except:
        pass
    circularname=str('CIRCULAR '+str((datetime.datetime.now().strftime('%j-%d%m%Y-%H%M%S'))))
    here = os.getcwd()
    os.chdir('circulars')
    os.mkdir(circularname)
    os.chdir(here)
    with open(('circulars/'+str(circularname)+'/'+str(circularname)+'.txt'),'w') as f:
        f.write(content)
    return redirect(url_for('dashboard'))

#/-  circular folder is ziped and returned

@app.route('/circular/<circular>/attachment')
def circularattachment(circular):
    import shutil
    shutil.make_archive(str(circular+'.zip'), 'zip', str('circulars/'+circularname))
    return send_file(str(circular+'.zip'))

#/-  makes a list of circulars and passes to jinja

@app.route('/circular')
def showcirculars():
    from flask import g, session
    circulars=[]
    for i in os.listdir('circulars'):
        print('\n'*100,i,'\n'*100)
        c=-1
        for j in os.listdir(f'circulars/{i}'):
            if j.endswith('.txt'):
                circularname=j.replace('.txt','')
                content=(open(f'circulars/{i}/{j}').read())
            c+=1
        circulars.append({'name':circularname,'content':content,'attachments':c})
    return render_template('circulars.html',circulars=circulars,studentdetails=session.get('studentdetails'))

@app.route('/forum')
def postquestion():
    from flask import g, session
    return render_template("/composequestion.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

#/-  makes new csv file per question
#/-  genderated unique code and redirects to the posted question

@app.route('/forum/question', methods = ['POST'])
def createquestion():
    from flask import g, session
    question=request.form['content']
    subject=request.form['subject']
    tags=request.form['tags']
    det=session.get('studentdetails')
    author=det['name']
    date=datetime.datetime.now().strftime('%d/%m/%Y')
    author_pos=det['position']
    author_class=det['class']

    questiondetails=f'''QUESTION,AUTHOR,DATE POSTED,AUTHOR POSITION (STUDENT/TEACHER), SUBJECT,AUTHOR CLASS,TAGS
{question},{author},{date},{author_pos},{subject},{author_class},{tags}
REPLY,AUTHOR,DATE REPLIED,AUTHOR POSITION, AUTHOR CLASS'''

    qncode=str((datetime.datetime.now().strftime('%j%d%m%Y%H%M%S')))
    with open(('questions/'+f'{qncode}.csv'),'w') as f:
        f.write(questiondetails)
    to=det['email']
    send_email(to,question,f'Your question has succesfuly been posted to OneStop! View your question at http://onestop.pythonanywhere.com/question/{qncode}')
    return redirect(url_for('question',qncode=qncode))

#/-  adds unique answer with details to question's csv

@app.route('/forum/answer/<qncode>', methods = ['POST'])
def createanswer(qncode):
    def parse_foundqn(qncode):
        with open(f'./questions/{qncode}.csv') as f:
            contents=f.readlines()
            question={
            'question':contents[1].split(',')[0],
            'author':contents[1].split(',')[1],
            'date':contents[1].split(',')[2],
            'author_pos':contents[1].split(',')[3],
            'subject':contents[1].split(',')[4],
            'author_class':contents[1].split(',')[5],
            'tags':contents[1].split(',')[6].replace('/',', '),
            }
            c=0
            answers=[]
            for x in contents:
                c+=1
                i=x.split(',')
                if c>3:
                    answers.append({
                        'answer':i[0],
                        'author':i[1],
                        'date':i[2],
                        'author_pos':i[3],
                        'author_class':i[4]
                        })
        return([question,answers])
    from flask import g, session
    answer=request.form['content']
    det=session.get('studentdetails')
    author=det['name']
    date=datetime.datetime.now().strftime('%d/%m/%Y')
    author_pos=det['position']
    author_class=det['class']

    answerdetails=f'\n{answer},{author},{date},{author_pos},{author_class}'

    with open(('questions/'+f'{qncode}.csv'),'a') as f:
        f.write(answerdetails)
    to=det['email']
    send_email(to,question,f'Your answer has succesfuly been posted to OneStop! View your answer at http://onestop.pythonanywhere.com/question/{qncode}')
    to_name=parse_foundqn(qncode)[0]['author']
    with open('details.csv') as f:
        for i in f.readlines():
            if i.split(',')[0]==to_name:
                to=i[7]
                break
    send_email(to,question,f'Your question has gotten an answer at OneStop! View it at at http://onestop.pythonanywhere.com/question/{qncode}')
    return redirect(url_for('question',qncode=qncode))

@app.route('/inbox')
def inbox():
    from flask import g, session

    return render_template("inbox.html",greeting=session.get('greetings'),studentdetails=session.get('studentdetails'), subject=session.get('subject'))

@app.route('/myaccount')
def myaccount():
    from flask import g, session

    return render_template("myaccount.html",studentdetail=session.get('studentdetails'))


@app.route('/pastboardpapers')
def pastboardpapers():
    from flask import g, session


    return render_template("pastboardpapers.html",subject=session.get('subject'),boardpapers=session.get('boardpapers'),studclass=session.get('studclass'))


@app.route('/pastschoolpapers')
def pastschoolpapers():
    from flask import g, session

    return render_template("pastschoolpapers.html",studclass=session.get('studclass'),schoolpapers=session.get('schoolpapers'), subject=session.get('subject'))

@app.route('/Accounts')
def accounts():
    from flask import g, session
    return render_template("/subjects/accounts.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Biology')
def biology():
    from flask import g, session
    return render_template("/subjects/biology.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Business')
def business():
     from flask import g, session

     return render_template("/subjects/business.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Chemistry')
def chemistry():
     from flask import g, session

     return render_template("/subjects/chemistry.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Computer')
def computer():
     from flask import g, session

     return render_template("/subjects/computer.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Economics')
def economics():
     from flask import g, session

     return render_template("/subjects/Economics.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/English')
def english():
    from flask import g, session

    return render_template("/subjects/english.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Mathematics')
def math():
     from flask import g, session

     return render_template("/subjects/math.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Physics')
def physics():
      from flask import g, session

      return render_template("/subjects/physics.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Political Science')
def politicalscience():
    from flask import g, session

    return render_template("/subjects/politicalscience.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Psychology')
def psychology():
    from flask import g, session

    return render_template("/subjects/psychology.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

@app.route('/Web Application')
def webapp():
    from flask import g, session

    return render_template("/subjects/webapp.html",boardpapers=session.get('subjpapers'), subject=session.get('subject'))

#/-  parses the question csv and passes to jinja for viewing

@app.route("/question/<qncode>")
def question(qncode):
    from flask import g,session
    from os import listdir

    def parse_foundqn(qncode):
        with open(f'./questions/{qncode}.csv') as f:
            contents=f.readlines()
            question={
            'question':contents[1].split(',')[0],
            'author':contents[1].split(',')[1],
            'date':contents[1].split(',')[2],
            'author_pos':contents[1].split(',')[3],
            'subject':contents[1].split(',')[4],
            'author_class':contents[1].split(',')[5],
            'tags':contents[1].split(',')[6].replace('/',', '),
            }
            c=0
            answers=[]
            for x in contents:
                c+=1
                i=x.split(',')
                if c>3:
                    answers.append({
                        'answer':i[0],
                        'author':i[1],
                        'date':i[2],
                        'author_pos':i[3],
                        'author_class':i[4]
                        })
        return([question,answers])

    if f'{qncode}.csv' in listdir('./questions'):
        return render_template('question.html',question=parse_foundqn(qncode)[0],answers=parse_foundqn(qncode)[1],name=str(session.get('studentdetails')['name']),qncode=str(qncode))
    return str(qncode)

#/-  dynamically returns search queries to javascript in forum search

@app.route('/forum/dynamicsearch')
def dynamicsearch():
    import os
    def matchlevel(str1, str2) :  
        str1=str1.upper()
        str2=str2.upper()
        c = 0; j = 0;  
        for i in range(len(str1)) : 
            if str1[i] in str2 :  
                c += 1;  
            j += 1;  
        return c
    def parse_foundqn(qncode):
        with open(f'./questions/{qncode}csv') as f:
            contents=f.readlines()
            question={
            'question':contents[1].split(',')[0],
            'author':contents[1].split(',')[1],
            'date':contents[1].split(',')[2],
            'author_pos':contents[1].split(',')[3],
            'subject':contents[1].split(',')[4],
            'author_class':contents[1].split(',')[5],
            'tags':contents[1].split(',')[6].replace('/',', '),
            }
            c=0
            answers=[]
            for x in contents:
                c+=1
                i=x.split(',')
                if c>3:
                    answers.append({
                        'answer':i[0],
                        'author':i[1],
                        'date':i[2],
                        'author_pos':i[3],
                        'author_class':i[4]
                        })
        return([question,answers])

    query=request.args.get('jsdata')
    questions=[]
    matching_questions=[]
    for i in os.listdir('./questions'):
        qncode=i.replace('.csv','')
        questions.append({'question':parse_foundqn(i.replace('csv',''))[0]['question'],'tags':parse_foundqn(i.replace('csv',''))[0]['tags'],'parse':parse_foundqn(i.replace('csv','')),'qncode':qncode})
    for i in questions:
        percentage_match=(matchlevel(query,i['question'])/len(query))*100
        tags_match=(matchlevel(query,i['tags'])/len(query))*100
        total_match=0.25*tags_match+0.75*percentage_match
        if total_match>=65:
            matching_questions.append(i)
    return render_template('dynamicsearch.html',results=matching_questions)

@app.route('/forum/search')
def forumsearch():
    from flask import g,session
    return render_template('forumsearch.html',name=str(session.get('studentdetails')['name']))



if __name__ == '__main__':
    app.run(debug=False)
