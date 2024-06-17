from flask import Flask, render_template, session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField, IntegerField, RadioField, SelectField, FloatField
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
    showName = StringField('Show Name: ', validators=([InputRequired(), DataRequired()]))
    showNumber = IntegerField('Show Number: ', validators=([InputRequired(), DataRequired()]))
    accountManager = SelectField('Account Manager: ', validators=([InputRequired(), DataRequired()]), choices=accountManagersList)
    location = StringField('Location: ', validators=([InputRequired(), DataRequired()]))

    submit = SubmitField('Submit')

class ExpenseForm(FlaskForm):
    worker = StringField('Worker Name: ', validators=([InputRequired(), DataRequired()]))
    receiptNumber = IntegerField('Receipt Number: ', validators=([InputRequired(), DataRequired()]))
    date = StringField('Date: ', id='expdatepick', validators=([InputRequired(), DataRequired()]))
    accountManager = SelectField('Account Manager: ', validators=([InputRequired(), DataRequired()]), choices=accountManagersList)
    showName = StringField('Show Name: ', validators=([InputRequired(), DataRequired()]))
    showNumber = IntegerField('Show Number: ', validators=([InputRequired(), DataRequired()]))
    details = StringField('Expense Details: ', validators=([InputRequired(), DataRequired()]))
    net = FloatField("Subtotal: ", validators=([InputRequired(), DataRequired()]))
    hst = FloatField("HST: ", validators=([InputRequired(), DataRequired()]))

    submit = SubmitField('Submit')


class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    worker = db.Column(db.String, unique = False)
    receiptNumber = db.Column(db.Integer, unique=False)
    date = db.Column(db.DateTime, unique=False)
    accountManager = db.Column(db.String, unique=False)
    showName = db.Column(db.String, unique=False)
    showNumber = db.Column(db.Integer, unique=False)
    details = db.Column(db.String, unique=False)
    net = db.Column(db.Float, unique=False)
    hst = db.Column(db.Float, unique=False)
    total = db.Column(db.Float, unique=False)

    def create(self):
        expense = Expense()
        expense.date = datetime.datetime.strptime(session['date'], '%m/%d/%Y %I:%M %p')
        expense.worker = session['worker']
        expense.receiptNumber = session['receiptNumber']
        expense.accountManager = session['accountManager']
        expense.showName = session['showName']
        expense.showNumber = session['showNumber']
        expense.details = session['details']
        expense.net = session['net']
        expense.hst = session['hst']
        expense.total = float(session['net']) + float(session['hst'])

        db.session.add(expense)
        db.session.commit()

    def __repr__(self):
        return '<Expense {0} {1} {2}>'.format(self.showNumber, self.showName, self.worker)

class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    worker = db.Column(db.String, unique=False)
    start = db.Column(db.DateTime, unique=False)
    end = db.Column(db.DateTime, unique=False)
    showName = db.Column(db.String, unique=False)
    showNumber = db.Column(db.Integer, unique=False)
    accountManager = db.Column(db.String, unique=False)
    location = db.Column(db.String, unique=False)

    # worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))

    def create(self):
        
        shift = Shift()
        shift.start = datetime.datetime.strptime(session['start'], '%m/%d/%Y %I:%M %p')
        shift.end = datetime.datetime.strptime(session['end'], '%m/%d/%Y %I:%M %p')    

        shift.showName= session['showName']
        shift.showNumber = session['showNumber']
        shift.accountManager = session['accountManager']
        shift.location = session['location']

        db.session.add(shift)
        db.session.commit()
    
    def retrieve(self, id):
        return Shift.query.filter_by(id=id)
  

    def __repr__(self):
        return '<Shift {0} {1} {2}>'.format(self.showNumber, self.showName, self.id)
    
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
        session['showName'] = shift.showName.data
        session['showNumber'] = shift.showNumber.data
        session['accountManager'] = shift.accountManager.data
        session['location'] = shift.location.data

        shift = Shift()
        shift.create()

        return redirect(url_for('timesheet'))
    return render_template('timesheet.html', shift=shift, report=report)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    report = createExpenseReportCH()
    expense = ExpenseForm()
    if expense.validate_on_submit():
        session['receiptNumber'] = expense.receiptNumber.data
        session['date'] = expense.date.data
        session['worker'] = expense.worker.data
        session['accountManager'] = expense.accountManager.data
        session['showName'] = expense.showName.data
        session['showNumber'] = expense.showNumber.data
        session['details'] = expense.details.data
        session['net'] = expense.net.data
        session['hst'] = expense.hst.data

        expense = Expense()
        expense.create()
        return redirect(url_for('expenses'))
    return render_template('expenses.html', expense=expense, report=report)


@app.errorhandler(404) 
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Shift=Shift, Worker=Worker)

@app.route('/refreshTimesheetDisplay')
def refresh_Timesheet_Display():
    # display = request.args.get('data')
    # print(display)

    createTimeReportCH()

@app.route('/refreshExpenseDisplay')
def refresh_Expense_Display():
    # display = request.args.get('data')
    # print(display)

    createExpenseReportCH()

###### Reports ######

#function will create an excel file in the format Cheryl wants for timesheets
def createTimeReportCH():
    shifts = Shift.query.all()
    print(shifts)

    date =[]
    show =[]
    location =[]
    times =[]
    hours =[]

# Date	Event Name/#/Account Mgr	Location	Time In/Out	# of Hours
    for shift in shifts:
        date.append(shift.start.date())
        show.append('{0}/{1}/{2}'.format(shift.showName, shift.showNumber, shift.accountManager))
        location.append(shift.location)
        times.append('{0}/{1}'.format(shift.start.time(), shift.end.time()))
        hours.append(float((shift.end - shift.start).total_seconds()/3600))

    df = pd.DataFrame({"date":date, "show":show, "location":location, "times":times, "hours":hours})

    return df.to_html(index=False, header=False)

def createExpenseReportCH():
    expenses = Expense.query.all()
    # print(expenses)
    receiptNumber = []
    datePurchased= []
    middle = []
    net = []
    hst = []
    total = [] 

    for expense in expenses:
        receiptNumber.append(expense.receiptNumber)
        datePurchased.append(expense.date.strftime("%m/%d/%Y"))
        middle.append('{0}, {1}/{2}, {3}'.format(expense.accountManager, expense.showName, expense.showNumber, expense.details))
        net.append(expense.net)
        hst.append(expense.hst)
        total.append(expense.total)

    
    
    df = pd.DataFrame({"receipt number": receiptNumber, "date purchased": datePurchased,  "middle": middle, "net": net, "hst": hst, "total": total})

    return df.to_html(index=False, header=False)
        
        


