import os
import random

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = '42'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    sounds = db.relation('Sound', backref='species')


class Behavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    sounds = db.relation('Sound', backref='behavior')


class Sound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(64), unique=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    behavior_id = db.Column(db.Integer, db.ForeignKey('behavior.id'))


def get_sound() -> Sound:
    """Picks a random species and return as random sound from that species"""
    return random.choice(Sound.query.filter_by(
        species=random.choice(Species.query.all())).all())


@app.route('/')
def index():

    sound = get_sound()
    print(sound.path)

    return render_template('index.html')
