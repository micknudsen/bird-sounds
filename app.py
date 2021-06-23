from flask import Flask


app = Flask(__name__)


@app.route('/')
def index():
    return '<html><p><h1>Hello, World!</h1></p></html>'
