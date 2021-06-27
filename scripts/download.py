import pandas as pd


meatadata = pd.read_csv('xeno-canto/verbatim.txt', sep='\t', low_memory=False)
meatadata = meatadata[['gbifID', 'behavior', 'scientificName', 'vernacularName']].set_index('gbifID')

multimedia = pd.read_csv('xeno-canto/multimedia.txt', sep='\t', low_memory=False)
multimedia = multimedia[multimedia['type'] == 'Sound'][['gbifID', 'identifier']].set_index('gbifID')

data = meatadata.join(multimedia)
