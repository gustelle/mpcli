
# Music Production Client

This is a very simple tool to help producing music. It enables:
- time stretching using either a target tempo or stretching ratios
- converting from `'wav` to `mp3`
- normalizing the sound to a given [LUFS](https://fr.wikipedia.org/wiki/LKFS)
- Detect the tempo of an audio file

# How to use ?


## Simple way

The most simple way is to use the REST API and an API client like [Bruno](https://www.usebruno.com/).

You'll find in the folder [bruno-api](/bruno-api/) a ready to use local environment 

```sh
# start the backend
cd backend
fastapi dev src/mpcli/api.py 
```

## The hard way

A more robust but complete way of using the tool is to use the `cli`.

Firstly, proceed as follows:
```sh
# go to the backend
cd backend
```

Configure the [config.toml](/backend/config.toml) 

There are 4 commands:
- detect_tempo 
- timestretch
- convert
- normalize

Each command may be used as a single command or as an array:
```toml
# example using a single config

[normalize]
source = "/my/location/Metallica - One (Drums Only).wav"
output = "/my/location/normalized/"
lufs=-14.0
target_format = "mp3" 

# example using a list of configurations
[[normalize]]
source = "/my/location/Metallica - One (Drums Only).wav"
output = "/my/location/normalized/"
lufs=-14.0
target_format = "mp3" 

[[normalize]]
source = "/my/location/another_file.mp3"
output = "/my/location/normalized/"
lufs=-11.0
target_format = "mp3" 
```

An example / template of config file can be found here [template config file](/backend/config.toml)

to run the command, simply launch it:
```sh
# example to normalize both files
# according the configuration above:
poetry run normalize

# if you want to normalize
poetry run normalize

# to detect tempo
poetry run detect_tempo

# to timestretch
poetry run timestretch
```
