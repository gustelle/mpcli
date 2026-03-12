# Music Production Client

This tool provides the followins services:
1. estimate the tempo of a set of files located in a directory
2. timestretch a set of files located in a directory to a given BPM
3. convert from an audio format to another 
4. normalize an audio file to a given LUFS 

Example of use case:
* estimate the tempo of each file located in the directory
* Take these files and convert them to 80 BPM. To do this it first detect the file source bpm. The output files are stored in a folder which is configurable

## How to run the API

this is required if you want to use the frontend

```sh
fastapi dev src/mpcli/api.py
```

Then go to the frontend and start Node

## How to run with the CLI

The CLI provides a simple way yet not quite user friendly. 
You don't need to run the frontend to run the CLI, but the drawback is that you have to configure things in the file `config.toml`

* `poetry run timestretch` will timestrech the given files to the target tempo (`target_tempo`)
* `poetry run detect_tempo` will just give the tempos of the files located in the source directory 
* `poetry run convert` 
* `poetry run normalize` 
