import json
import logging
import os
import pathlib
import urllib.request

from collections import defaultdict

from pydub import AudioSegment

from rich.logging import RichHandler
from rich.progress import track

from app import db, Language, Species, Behavior, Sound, Translation


logging.basicConfig(
    format="[%(levelname)s] %(asctime)s %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.INFO,
    handlers=[RichHandler()],
)


def download(species, behavior, xc_numbers):
    simple_species = species.replace(" ", "_").lower()
    simple_behavior = behavior.replace(" ", "_").lower()

    for xc_number, (start, end) in track(
        xc_numbers.items(),
        description=f"{species} ({behavior.capitalize()})",
        transient=True,
    ):
        download_link = f"https://xeno-canto.org/{xc_number}/download"
        local_file = os.path.join(
            "static", "raw", simple_species, simple_behavior, f"{xc_number}.mp3"
        )

        if not os.path.isfile(local_file):
            try:
                os.makedirs(os.path.dirname(local_file), exist_ok=True)
                urllib.request.urlretrieve(download_link, local_file)
            except urllib.error.HTTPError as e:
                logging.warning(
                    f"Unable to download sound XC_{xc_number} for {species} ({behavior}). Reason given: {e}"
                )
                continue

        processed_file = os.path.join(
            "static",
            "sounds",
            simple_species,
            simple_behavior,
            f"{xc_number}_{start}_{end}.mp3",
        )
        if not os.path.isfile(processed_file):
            os.makedirs(os.path.dirname(processed_file), exist_ok=True)
            sound = AudioSegment.from_file(local_file)
            sound[start:end].export(processed_file, format="mp3")


logging.info("Downloading and processing sounds")

dictionary = defaultdict(dict)

with open("metadata/selection.json", "r") as f:
    for species, metadata in json.load(f).items():
        for behavior, xc_numbers in metadata["sounds"].items():
            download(species=species, behavior=behavior, xc_numbers=xc_numbers)
        for language, translation in metadata["translations"].items():
            dictionary[species][language] = translation

logging.info("Updating database")

db.create_all()

for path in track(list(pathlib.Path("static/sounds").rglob("*.mp3")), transient=True):
    xc_number = path.name.removesuffix(".mp3")
    web_link = f"https://xeno-canto.org/{xc_number}"

    species_name = path.parts[2].replace("_", " ").capitalize()
    behavior_name = path.parts[3].replace("_", " ").capitalize()

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
        sound = Sound(
            path=str(path), web_link=web_link, species=species, behavior=behavior
        )
        db.session.add(sound)

for species in Species.query.all():
    for language_, translation_ in dictionary[species.name].items():
        language = Language.query.filter_by(name=language_).first()
        if not language:
            language = Language(name=language_)
            db.session.add(language)
        translation = Translation.query.filter_by(
            language=language, species=species
        ).first()
        if not translation:
            translation = Translation(
                name=translation_, language=language, species=species
            )
            db.session.add(translation)

db.session.commit()
