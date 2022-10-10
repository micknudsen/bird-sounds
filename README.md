# Bird Sounds

I wrote this small [flask](https://flask.palletsprojects.com/en/2.0.x/) app to help me practice bird sound identification. It is neither advanced nor beautiful, but it gets the job done. I am sharing the code here just in case anybody else would find it useful.

## Environment

It is recommended to run the app in a [conda](https://docs.conda.io/en/latest/) environment. Create one and activate it:

```
$ conda env create -f conda.yaml
$ conda activate bird-sounds
````

## Metadata

Now go ahead and fill out `metadata/selection.json` with information about the species and the sounds you would like to download. Here is an example with just two species:

```
$ cat metadata/selection.json
{
    "Cyanistes caeruleus": {
        "behaviors": ["song", "alarm call"],
        "translations": {
            "danish": "Blåmejse",
            "english": "Eurasian Blue Tit"
        }
    },
    "Parus major": {
        "behaviors": ["song"],
        "translations": {
            "danish": "Musvit",
            "english": "Great Tit"
        }
    }
}
```

To download sounds (already downloaded sounds will not be re-downloaded) and update the database, simply run `python download.py`.

## Running

To run the app, you must first tell flask which app to use. The default vernacular language is Danish. If you want a different language, this is the place to specify it, too.

```
$ export FLASK_APP=app
$ export VERNACULAR_LANGUAGE=english
```

Now the app is lauched using `flask run` and can be accessed in a browser using the address provided in the output:

```
$ flask run
* Serving Flask app 'app.py' (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: off
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

The app plays a random bird sound and offers all possible species in the database as choices. Make a guess by clicking on a species name. The app then shows the correct species and allows you to replay the sound. Click on the species name to get a new sound.
