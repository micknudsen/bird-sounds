import os
import pathlib

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

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


db.create_all()

for path in pathlib.Path('static/sounds').rglob('*.mp3'):

    species_name = path.parts[2].replace('_', ' ').capitalize()
    behavior_name = path.parts[3].replace('_', ' ').capitalize()

    species = Species.query.filter_by(name=species_name).first()
    if not species:
        species = Species(name=species_name)
        db.session.add(species)

    behavior = Behavior.query.filter_by(name=behavior_name).first()
    if not behavior:
        behavior = Behavior(name=behavior_name)
        db.session.add(behavior)

    sound = Sound.query.filter_by(path=str(path)).first()
    if not sound:
        sound = Sound(path=str(path), species=species, behavior=behavior)
        db.session.add(sound)

db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')
