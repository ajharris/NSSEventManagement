from flask import Flask
from dotenv import load_dotenv

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello World</h1>'