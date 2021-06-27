import json
import pathlib
import random

from collections import defaultdict

from flask import Flask, render_template


app = Flask(__name__)


with open('metadata/translation.json', 'r') as f:
    translation = {key.replace(' ', '_').lower(): value
                   for key, value in json.load(f).items()}

sounds = defaultdict(list)
for path in pathlib.Path('static/sounds').rglob('*.mp3'):
    sounds[path.parts[2]].append(str(path).removeprefix('static/'))


@app.route('/')
def index():
    return render_template('index.html')
