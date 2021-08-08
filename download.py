import json
import logging
import os
import pathlib
import urllib.request

from collections import defaultdict

import pandas as pd
from tqdm import tqdm

from app import db, Language, Species, Behavior, Sound, Translation


logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S', level=logging.INFO)

logging.info('Parsing metadata')

meatadata = pd.read_csv('metadata/xeno-canto/verbatim.txt', sep='\t', low_memory=False)
meatadata = meatadata[['gbifID', 'behavior', 'scientificName']].set_index('gbifID')

multimedia = pd.read_csv('metadata/xeno-canto/multimedia.txt', sep='\t', low_memory=False)
multimedia = multimedia[multimedia['type'] == 'Sound'][['gbifID', 'identifier']].set_index('gbifID')

data = meatadata.join(multimedia)


def download(data, species, behavior):

    data_subset = data[(data['scientificName'] == species) & (data['behavior'] == behavior)]

    simple_species = species.replace(' ', '_').lower()
    simple_behavior = behavior.replace(' ', '_').lower()

    for gbif_id, row in tqdm(data_subset.iterrows(), total=len(data_subset), desc=f'{species} ({behavior.capitalize()})'):

        download_link = row['identifier']
        local_file = os.path.join('static', 'sounds', simple_species, simple_behavior, f'{gbif_id}.mp3')

        if not os.path.isfile(local_file):
            try:
                os.makedirs(os.path.dirname(local_file), exist_ok=True)
                urllib.request.urlretrieve(download_link, local_file)
            except urllib.error.HTTPError as e:
                logging.warning(f'Unable to download sound for {species} ({behavior}) with GBIF_ID {gbif_id}. Reason given: {e}')


logging.info('Downloading sounds')

dictionary = defaultdict(dict)

with open('metadata/selection.json', 'r') as f:
    for species, metadata in json.load(f).items():
        for behavior in metadata['behaviors']:
            download(data=data, species=species, behavior=behavior)
        for language, translation in metadata['translations'].items():
            dictionary[species][language] = translation

logging.info('Updating database')

db.create_all()

for path in tqdm(list(pathlib.Path('static/sounds').rglob('*.mp3'))):

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

for species in Species.query.all():
    for language_, translation_ in dictionary[species_name].items():
        language = Language.query.filter_by(name=language_).first()
        if not language:
            language = Language(name=language_)
            db.session.add(language)
            db.session.commit()
        translation = Translation(name=translation_, language=language, species=species)
        db.session.add(translation)

db.session.commit()
