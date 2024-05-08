from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'scrypt:32768:8:1$CH7bJscsRxJzQ8jm$81aa6a6cb92092fb303cf1147ebe5cd4e8eb67523c52527a6e8b88d231e3d7fb7c7e81f9dd2dae78855d8e5f027921c4d73cfe0661340cd995aebb6f0324d338'
bootstrap = Bootstrap(app)

class ShiftForm(FlaskForm):
    # Date, Event Name, #, Account Manager, Location, Time In, Time Out, Number of Hours
    start = DateTimeField('Shift Start: ', validators=[DataRequired()])
    end = DateTimeField('Shift End: ', validators=[DataRequired()])

    submit = SubmitField('Submit')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/timesheet', methods=['GET', 'POST'])
def timesheet():
    form = ShiftForm()
    if form.validate_on_submit():
        session['start'] = form.start.data
        session['end'] = form.end.data
        form.end.data = None
    return render_template('timesheet.html', form=form, start=session.get('start'), end=session.get('end'))

@app.errorhandler(404) 
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500