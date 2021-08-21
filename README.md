# Bird Sounds

I wrote this small [flask](https://flask.palletsprojects.com/en/2.0.x/) app to help me practice bird sound identification. It is neither advanced nor beautiful, but it gets the jobs done. Sharing the code here just in case anybody else would find it useful.

## Environment

It is recommended to run the app in a [conda](https://docs.conda.io/en/latest/) environment. Create one and activate it:

```
$ conda env create -f conda.yaml
$ conda activate bird-sounds
````

## Metadata

Sounds can be obtained from the [xeno-canto](https://www.gbif.org/dataset/b1047888-ae52-4179-9dd5-5448ea342a24) dataset. Download the metadata and place it in `metadata/xeno-canto` inside the app folder:

```
$ tree metadata/xeno-canto
metadata/xeno-canto
├── citations.txt
├── dataset
│   └── b1047888-ae52-4179-9dd5-5448ea342a24.xml
├── meta.xml
├── metadata.xml
├── multimedia.txt
├── occurrence.txt
├── rights.txt
└── verbatim.txt
```

Now go ahead and fill out `metadata/selection.json` with information about the species and the behaviors you would like to download. Here is an example with just two species:
