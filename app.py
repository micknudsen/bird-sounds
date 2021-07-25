import os
import random

from dataclasses import dataclass
from typing import List

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


@dataclass
class Quiz:

    sound: Sound
    choices: List[Species]

    def __post_init__(self) -> None:
        if self.sound.species not in self.choices:
            raise Exception('Impossible Quiz!')


def new_quiz() -> Quiz:

    # Pick a random species as the correct species
    # and pick a random sound from that species.
    correct_species = random.choice(Species.query.all())
    sound = random.choice(Sound.query.filter_by(species=correct_species).all())

    # Now pick three other species to act a candidates.
    other_candidate_species = random.sample(
        [species for species in Species.query.all()
         if not species == correct_species],
        k=3)

    choices = [correct_species] + other_candidate_species
    random.shuffle(choices)

    return Quiz(sound=sound, choices=choices)


@app.route('/')
def index():
    return render_template('index.html')
