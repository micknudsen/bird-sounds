import os
import random

from dataclasses import dataclass
from enum import Enum
from typing import List

from flask import Flask, render_template, request, redirect, session, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

bootstrap = Bootstrap(app)

app.config["SECRET_KEY"] = "42"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "database.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


vernacular_language = os.getenv("VERNACULAR_LANGUAGE", default="danish")

history_length = os.getenv("HISTORY_LENGTH", default=100)
minimum_number_of_guesses = os.getenv("MINIMUM_NUMBER_OF_GUESSES", default=10)
minimum_fraction_correct = os.getenv("MINIMUM_FRACTION_CORRECT", default=0.9)


db = SQLAlchemy(app)


class Performance(Enum):
    ACCEPTED = "success"
    FAILED_TOO_FEW_GUESSES = "warning"
    FAILED_TOO_MANY_WRONG_GUESSES = "danger"


class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    sounds = db.relation("Sound", backref="species")
    translations = db.relation("Translation", backref="species")
    guesses = db.relation("Guess", backref="species")

    @property
    def vernacular_name(self) -> str:
        language = Language.query.filter_by(name=vernacular_language).first()
        if translation := Translation.query.filter_by(
            species=self, language=language
        ).first():
            return translation.name
        return self.name

    @property
    def performance(self) -> Performance:
        guesses = [
            guess for guess in Guess.query.all() if guess.correct_species == self
        ][-history_length:]
        if len(guesses) < minimum_number_of_guesses:
            return Performance.FAILED_TOO_FEW_GUESSES
        fraction_correct = sum(1 for guess in guesses if guess.is_correct()) / len(
            guesses
        )
        if fraction_correct >= minimum_fraction_correct:
            return Performance.ACCEPTED
        return Performance.FAILED_TOO_MANY_WRONG_GUESSES


class Behavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    sounds = db.relation("Sound", backref="behavior")


class Sound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(64), unique=True)
    web_link = db.Column(db.String(128), unique=True)
    species_id = db.Column(db.Integer, db.ForeignKey("species.id"))
    behavior_id = db.Column(db.Integer, db.ForeignKey("behavior.id"))
    guesses = db.relation("Guess", backref="sound")


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    translations = db.relation("Translation", backref="language")


class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    species_id = db.Column(db.Integer, db.ForeignKey("species.id"))
    language_id = db.Column(db.Integer, db.ForeignKey("language.id"))


class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sound_id = db.Column(db.Integer, db.ForeignKey("sound.id"))
    species_id = db.Column(db.Integer, db.ForeignKey("species.id"))

    @property
    def correct_species(self) -> Species:
        return self.sound.species

    def is_correct(self) -> bool:
        return self.correct_species == self.species


@dataclass
class Quiz:
    sound: Sound
    choices: List[Species]

    def __post_init__(self) -> None:
        if self.sound.species not in self.choices:
            raise Exception("Impossible Quiz!")


def new_quiz() -> Quiz:
    # Pick a random species as the correct species
    # and pick a random sound from that species.
    all_species = Species.query.all()
    weights = []
    for species in all_species:
        if species.performance == Performance.ACCEPTED:
            weights.append(1)
        else:
            weights.append(len(all_species))
    correct_species = random.choices(all_species, weights=weights, k=1)[0]
    sound = random.choice(Sound.query.filter_by(species=correct_species).all())

    choices = sorted(Species.query.all(), key=lambda species: species.vernacular_name)

    return Quiz(sound=sound, choices=choices)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["species_id_guessed"] = session["species_ids_choices"][
            int(request.form.get("choice_index"))
        ]

        guess = Guess(
            sound=Sound.query.get(session["sound_id"]),
            species=Species.query.get(session["species_id_guessed"]),
        )
        db.session.add(guess)
        db.session.commit()

        return redirect(url_for("answer"))

    quiz = new_quiz()

    session["sound_id"] = quiz.sound.id
    session["species_id_correct"] = quiz.sound.species.id
    session["species_ids_choices"] = [species.id for species in quiz.choices]

    return render_template("index.html", quiz=quiz)


@app.route("/answer", methods=["GET", "POST"])
def answer():
    sound = Sound.query.get(session["sound_id"])
    correct_species = Species.query.get(session["species_id_correct"])
    guessed_species = Species.query.get(session["species_id_guessed"])

    return render_template(
        "answer.html",
        sound=sound,
        correct_species=correct_species,
        guessed_species=guessed_species,
    )
