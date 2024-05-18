from flask import Flask, render_template, session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField, IntegerField, RadioField, SelectField
from wtforms.validators import DataRequired, InputRequired
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
import os
import datetime 
import pandas as pd



basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'scrypt:32768:8:1$CH7bJscsRxJzQ8jm$81aa6a6cb92092fb303cf1147ebe5cd4e8eb67523c52527a6e8b88d231e3d7fb7c7e81f9dd2dae78855d8e5f027921c4d73cfe0661340cd995aebb6f0324d338'
bootstrap = Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

accountManagersList = ['Rob Sandolowich', 'Joel Dubin', 'Corbin Elliott', 'Fox Procenko', 'Dave Lickers']

class ShiftForm(FlaskForm):
    # Date, Event Name, #, Account Manager, Location, Time In, Time Out, Number of Hours
    worker = StringField('Worker Name: ', validators=([InputRequired(), DataRequired()]))
    start = StringField('Shift Start: ', id='startpick', validators=([InputRequired(), DataRequired()]))
    end = StringField('Shift End: ', id='endpick', validators=([InputRequired(), DataRequired()]))
    eventName = StringField('Event Name: ', validators=([InputRequired(), DataRequired()]))
    showNumber = IntegerField('Show Number: ', validators=([InputRequired(), DataRequired()]))
    accountManager = SelectField('Account Manager: ', validators=([InputRequired(), DataRequired()]), choices=accountManagersList)
    location = StringField('Location: ', validators=([InputRequired(), DataRequired()]))

    submit = SubmitField('Submit')

class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    worker = db.Column(db.String, unique=False)
    start = db.Column(db.DateTime, unique=False)
    end = db.Column(db.DateTime, unique=False)
    eventName = db.Column(db.String, unique=False)
    showNumber = db.Column(db.Integer, unique=False)
    accountManager = db.Column(db.String, unique=False)
    location = db.Column(db.String, unique=False)

    # worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))

    def create(self):
        
        shift = Shift()
        shift.start = datetime.datetime.strptime(session['start'], '%m/%d/%Y %I:%M %p')
        shift.end = datetime.datetime.strptime(session['end'], '%m/%d/%Y %I:%M %p')    

        shift.eventName= session['eventName']
        shift.showNumber = session['showNumber']
        shift.accountManager = session['accountManager']
        shift.location = session['location']

        db.session.add(shift)
        db.session.commit()
    
    def retrieve(self, id):
        return Shift.query.filter_by(id=id)
    
    def delete(self, id):
        shift = Shift.query.filter_by(id=id)
        db.session.delete(shift)
        db.session.commit()



    def __repr__(self):
        return '<Shift {0} {1} {2}>'.format(self.showNumber, self.eventName, self.worker)
    
class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    worker = db.Column(db.String, unique=True)
    rate = db.Column(db.Float, unique=False)
    

    # shifts = db.relationship('Shift', backref='worker')

    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Worker {0}, {1}'.format(self.worker, self.rate)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/timesheet', methods=['GET', 'POST'])
def timesheet():
    report = createTimeReportCH()
    shift = ShiftForm()
    if shift.validate_on_submit():
        worker = Worker.query.filter_by(worker=shift.worker.data)
        session['start'] = shift.start.data
        session['end'] = shift.end.data
        session['eventName'] = shift.eventName.data
        session['showNumber'] = shift.showNumber.data
        session['accountManager'] = shift.accountManager.data
        session['location'] = shift.location.data

        shift = Shift()
        shift.create()

        return redirect(url_for('timesheet'))
    return render_template('timesheet.html', shift=shift, report=report)

@app.errorhandler(404) 
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Shift=Shift, Worker=Worker)

@app.route('/refreshDisplay')
def refresh_Display():
    # display = request.args.get('data')
    # print(display)

    createTimeReportCH()

###### Reports ######

#function will create an excel file in the format Cheryl wants for timesheets
def createTimeReportCH():
    shifts = Shift.query.all()
    print(shifts)

    date =[]
    event =[]
    location =[]
    times =[]
    hours =[]

# Date	Event Name/#/Account Mgr	Location	Time In/Out	# of Hours
    for shift in shifts:
        date.append(shift.start.date())
        event.append('{0}/{1}/{2}'.format(shift.eventName, shift.showNumber, shift.accountManager))
        location.append(shift.location)
        times.append('{0}/{1}'.format(shift.start.time(), shift.end.time()))
        hours.append(float((shift.end - shift.start).total_seconds()/3600))

    df = pd.DataFrame({"date":date, "event":event, "location":location, "times":times, "hours":hours})

    return df.to_html(index=False, header=False)
