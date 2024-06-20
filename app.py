from flask import Flask, render_template, session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField, IntegerField, FloatField, SelectField, FileField
from wtforms.validators import DataRequired, InputRequired
from flask_wtf.file import FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'scrypt:32768:8:1$CH7bJscsRxJzQ8jm$81aa6a6cb92092fb303cf1147ebe5cd4e8eb67523c52527a6e8b88d231e3d7fb7c7e81f9dd2dae78855d8e5f027921c4d73cfe0661340cd995aebb6f0324d338'
bootstrap = Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

UPLOAD_FOLDER = 'uploads/receipts'
ALLOWED_EXTENSIONS = {'pdf', 'jpeg', 'jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

accountManagersList = ['Rob Sandolowich', 'Joel Dubin', 'Corbin Elliott', 'Fox Procenko', 'Dave Lickers']

class ShiftForm(FlaskForm):
    worker = StringField('Worker Name: ', validators=[InputRequired(), DataRequired()])
    start = StringField('Shift Start: ', id='startpick', validators=[InputRequired(), DataRequired()])
    end = StringField('Shift End: ', id='endpick', validators=[InputRequired(), DataRequired()])
    showNumber = IntegerField('Event Number: ', validators=[InputRequired(), DataRequired()])
    submit = SubmitField('Submit')

class ExpenseForm(FlaskForm):
    worker = StringField('Worker Name: ', validators=[InputRequired(), DataRequired()])
    receiptNumber = IntegerField('Receipt Number: ', validators=[InputRequired(), DataRequired()])
    date = StringField('Date: ', id='expdatepick', validators=[InputRequired(), DataRequired()])
    showNumber = IntegerField('Event Number: ', validators=[InputRequired(), DataRequired()])
    details = StringField('Expense Details: ', validators=[InputRequired(), DataRequired()])
    net = FloatField("Subtotal: ", validators=[InputRequired(), DataRequired()])
    hst = FloatField("HST: ", validators=[InputRequired(), DataRequired()])
    receipt = FileField('Receipt', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDFs only!')])

    submit = SubmitField('Submit')

class EventForm(FlaskForm):
    showName = StringField('Show Name: ', validators=[InputRequired(), DataRequired()])
    showNumber = IntegerField('Show Number: ', validators=[InputRequired(), DataRequired()])
    accountManager = SelectField('Account Manager: ', choices=[], validators=[InputRequired(), DataRequired()])
    location = StringField('Location: ', validators=[InputRequired(), DataRequired()])
    submit = SubmitField('Submit')

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    showName = db.Column(db.String, unique=False)
    showNumber = db.Column(db.Integer, unique=True, nullable=False)
    accountManager = db.Column(db.String, unique=False)
    location = db.Column(db.String, unique=False)

    def __repr__(self):
        return '<Event {0} {1} {2}>'.format(self.showName, self.showNumber, self.accountManager)

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    worker = db.Column(db.String, unique=False)
    receiptNumber = db.Column(db.Integer, unique=False)
    date = db.Column(db.DateTime, unique=False)
    accountManager = db.Column(db.String, unique=False)
    showName = db.Column(db.String, unique=False)
    showNumber = db.Column(db.Integer, unique=False)
    details = db.Column(db.String, unique=False)
    net = db.Column(db.Float, unique=False)
    hst = db.Column(db.Float, unique=False)
    total = db.Column(db.Float, unique=False)
    receipt = db.Column(db.String(255), nullable=True) 

    def create(self):
        expense = Expense()
        expense.date = datetime.strptime(session['date'], '%m/%d/%Y %I:%M %p')
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

    def create(self):
        shift = Shift()
        shift.start = datetime.strptime(session['start'], '%m/%d/%Y %I:%M %p')
        shift.end = datetime.strptime(session['end'], '%m/%d/%Y %I:%M %p')
        shift.showName = session['showName']
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

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    form = EventForm()
    form.accountManager.choices = [(manager, manager) for manager in accountManagersList]

    if form.validate_on_submit():
        event = Event(
            showName=form.showName.data,
            showNumber=form.showNumber.data,
            accountManager=form.accountManager.data,
            location=form.location.data
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_event.html', form=form)

@app.route('/timesheet', methods=['GET', 'POST'])
def timesheet():
    report = createTimeReportCH()
    shift = ShiftForm()
    if shift.validate_on_submit():
        showNumber = shift.showNumber.data
        event = Event.query.filter_by(showNumber=showNumber).first()
        if event:
            session['start'] = shift.start.data
            session['end'] = shift.end.data
            session['showName'] = event.showName
            session['showNumber'] = showNumber
            session['accountManager'] = event.accountManager
            session['location'] = event.location

            shift_model = Shift()
            shift_model.create()

            return redirect(url_for('timesheet'))
        else:
            flash('Invalid Event Number', 'danger')
    return render_template('timesheet.html', shift=shift, report=report)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    report = createExpenseReportCH()
    expense_form = ExpenseForm()
    
    if expense_form.validate_on_submit():
        show_number = expense_form.showNumber.data
        event = Event.query.filter_by(showNumber=show_number).first()
        
        if event:
            # Handle file upload
            receipt_file = expense_form.receipt_file.data
            if receipt_file and allowed_file(receipt_file.filename):
                filename = secure_filename(receipt_file.filename)
                receipt_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Create a new Expense object and populate its attributes
                new_expense = Expense(
                    receipt_number=expense_form.receiptNumber.data,
                    date=expense_form.date.data,
                    worker=expense_form.worker.data,
                    account_manager=event.accountManager,
                    show_name=event.showName,
                    show_number=show_number,
                    details=expense_form.details.data,
                    net=expense_form.net.data,
                    hst=expense_form.hst.data,
                    receipt_filename=filename  # Assuming receipt_filename is a field in your Expense model
                )
                
                new_expense.create()  # Assuming 'create' method adds and commits the new expense to the database
                
                flash('Expense added successfully', 'success')
                return redirect(url_for('expenses'))
            else:
                flash('Invalid file format for receipt (PDF or JPEG required)', 'danger')
        else:
            flash('Invalid Event Number', 'danger')
    
    return render_template('expenses.html', expense=expense_form, report=report)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Shift=Shift, Worker=Worker, Event=Event)

@app.route('/refreshTimesheetDisplay')
def refresh_Timesheet_Display():
    createTimeReportCH()

@app.route('/refreshExpenseDisplay')
def refresh_Expense_Display():
    createExpenseReportCH()

###### Reports ######

def createTimeReportCH():
    shifts = Shift.query.all()
    date = []
    show = []
    location = []
    times = []
    hours = []

    for shift in shifts:
        date.append(shift.start.date())
        show.append('{0}/{1}/{2}'.format(shift.showName, shift.showNumber, shift.accountManager))
        location.append(shift.location)
        times.append('{0}/{1}'.format(shift.start.time(), shift.end.time()))
        hours.append(float((shift.end - shift.start).total_seconds() / 3600))

    timesheet = pd.DataFrame()
    timesheet['Date'] = date
    timesheet['Show'] = show
    timesheet['Location'] = location
    timesheet['Times'] = times
    timesheet['Hours'] = hours

    timesheet['Date'] = pd.to_datetime(timesheet['Date'], format='%m/%d/%Y')

    timesheet = timesheet.sort_values('Date')

    pd.set_option('display.max_colwidth', None)

    reportHTML = timesheet.to_html(index=False, justify='left')
    reportHTML = reportHTML.replace('border="1" class="dataframe"', 'class="table table-striped table-hover"')

    return reportHTML

def createExpenseReportCH():
    expenses = Expense.query.all()
    date = []
    show = []
    location = []
    worker = []
    details = []
    total = []

    for expense in expenses:
        date.append(expense.date.date())
        show.append('{0}/{1}/{2}'.format(expense.showName, expense.showNumber, expense.accountManager))
        location.append(expense.location)
        worker.append(expense.worker)
        details.append(expense.details)
        total.append(expense.total)

    expensereport = pd.DataFrame()
    expensereport['Date'] = date
    expensereport['Show'] = show
    expensereport['Location'] = location
    expensereport['Worker'] = worker
    expensereport['Details'] = details
    expensereport['Total'] = total

    expensereport['Date'] = pd.to_datetime(expensereport['Date'], format='%m/%d/%Y')

    expensereport = expensereport.sort_values(by='Date')

    pd.set_option('display.max_colwidth', None)

    reportHTML = expensereport.to_html(index=False, justify='left')
    reportHTML = reportHTML.replace('border="1" class="dataframe"', 'class="table table-striped table-hover"')

    return reportHTML

if __name__ == '__main__':
    app.run(debug=True)
