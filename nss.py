from flask import Flask, render_template, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField, IntegerField, RadioField, SelectField
from wtforms.validators import DataRequired, InputRequired
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
import os



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
    start = db.Column(db.DateTime, unique=False)
    end = db.Column(db.DateTime, unique=False)
    eventName = db.Column(db.String, unique=True)
    showNumber = db.Column(db.Integer, unique=True)
    accountManager = db.Column(db.String, unique=False)
    location = db.Column(db.String, unique=False)

    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))

    def __repr__(self):
        return '<Shift %r %r>' % self.showNumber, self.eventName
    
class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    worker = db.Column(db.String, unique=True)
    rate = db.Column(db.Float, unique=False)
    

    shifts = db.relationship('Shift', backref='worker')

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
        return '<Worker %r $r>' % self.worker, self.rate



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/timesheet', methods=['GET', 'POST'])
def timesheet():
    shift = ShiftForm()
    if shift.validate_on_submit():
        worker = Worker.query.filter_by(worker=shift.worker.data)
        session['start'] = shift.start.data
        session['end'] = shift.end.data
        session['eventName'] = shift.eventName.data
        session['showNumber'] = shift.showNumber.data
        session['accountManager'] = shift.accountManager.data
        session['location'] = shift.location.data
        return redirect(url_for('timesheet'))
    return render_template('timesheet.html', shift=shift)

@app.errorhandler(404) 
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Shift=Shift, Worker=Worker)