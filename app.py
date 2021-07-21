import os
import random

from dataclasses import dataclass
from typing import List

from flask import Flask, render_template, redirect, request, session, url_for
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
    guesses = db.relation('Guess', backref='species')


class Behavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    sounds = db.relation('Sound', backref='behavior')


class Sound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(64), unique=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    behavior_id = db.Column(db.Integer, db.ForeignKey('behavior.id'))
    guesses = db.relation('Guess', backref='sound')


class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sound_id = db.Column(db.Integer, db.ForeignKey('sound.id'))
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))


def get_sound() -> Sound:

    candidate_species = Species.query.all()

    wrong_counts = []
    for species in candidate_species:
        wrong_counts.append(sum(1 for guess in Guess.query.filter_by(species=species)
                                if not guess.species == guess.sound.species))

    weights = [1 + count for count in wrong_counts]
    selected_species = random.choices(candidate_species, weights=weights, k=1)[0]

    return random.sample(Sound.query.filter_by(species=selected_species).all(), k=1)[0]


def get_choices(sound: Sound) -> List[Species]:

    alternatives = [alternative for alternative in Species.query.all() if not alternative == sound.species]

    wrong_counts = []
    for alternative in alternatives:
        wrong_counts.append(sum(1 for guess in Guess.query.filter_by(species=sound.species)
                                if guess.sound.species == alternative))

    weigths = [1 + count for count in wrong_counts]
    choices = [sound.species] + random.choices(alternatives, weights=weigths, k=3)

    random.shuffle(choices)

    return choices


@dataclass
class Quiz:

    sound: Sound
    choices: List[Species]

    def __post_init__(self) -> None:
        if self.sound.species not in self.choices:
            raise Exception('Impossible Quiz!')


def make_quiz() -> Quiz:

    sound = get_sound()
    choices = get_choices(sound=sound)

    return Quiz(sound=sound, choices=choices)


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        session['choice_form_index'] = request.form.get('choice')
        return redirect(url_for('answer'))

    quiz = make_quiz()

    session['correct_species_id'] = quiz.sound.species.id
    session['choice_species_ids'] = [species.id for species in quiz.choices]

    return render_template('index.html', quiz=quiz)


@app.route('/answer')
def answer():

    correct = Species.query.get(session['correct_species_id'])

    return render_template('answer.html', correct=correct)
