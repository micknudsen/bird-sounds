import os
import random

from flask import Flask, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

bootstrap = Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Species(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    sounds = db.relation('Sound', backref='species')

    def __repr__(self) -> str:
        return f'<Species {self.name}>'


class Behavior(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    sounds = db.relation('Sound', backref='behavior')

    def __repr__(self) -> str:
        return f'<Behavior {self.name}>'


class Sound(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(64), unique=True)

    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    behavior_id = db.Column(db.Integer, db.ForeignKey('behavior.id'))


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        return redirect(url_for('index'))

    choices = random.sample(Species.query.all(), 4)
    correct = random.choice(choices)

    sound = random.choice(Sound.query.filter_by(species=correct).all())

    return render_template('index.html', sound=sound, choices=choices)
