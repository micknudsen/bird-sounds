import json
import pathlib

from collections import defaultdict

from flask import Flask


app = Flask(__name__)


with open('metadata/translation.json', 'r') as f:
    translation = {key.replace(' ', '_').lower(): value
                   for key, value in json.load(f).items()}

sounds = defaultdict(list)
for path in pathlib.Path('static/sounds').rglob('*.mp3'):
    sounds[path.parts[2]].append(str(path).removeprefix('static/'))


@app.route('/')
def index():
    return '<html><p><h1>Hello, World!</h1></p></html>'
