import os
import urllib

import pandas as pd
from tqdm import tqdm


meatadata = pd.read_csv('xeno-canto/verbatim.txt', sep='\t', low_memory=False)
meatadata = meatadata[['gbifID', 'behavior', 'scientificName', 'vernacularName']].set_index('gbifID')

multimedia = pd.read_csv('xeno-canto/multimedia.txt', sep='\t', low_memory=False)
multimedia = multimedia[multimedia['type'] == 'Sound'][['gbifID', 'identifier']].set_index('gbifID')

data = meatadata.join(multimedia)


def download(data, species, behavior):

    data_subset = data[(data['scientificName'] == species) & (data['behavior'] == behavior)]

    simple_species = species.replace(' ', '_').lower()
    simple_behavior = behavior.replace(' ', '_').lower()

    for gbif_id, row in tqdm(data_subset.iterrows(), total=len(data_subset), desc=f'{species} ({behavior})'):

        download_link = row['identifier']
        local_file = os.path.join('..', 'static', 'sounds', simple_species, simple_behavior, f'{gbif_id}.mp3')

        if not os.path.isfile(local_file):
            os.makedirs(os.path.dirname(local_file), exist_ok=True)
            urllib.request.urlretrieve(download_link, local_file)
