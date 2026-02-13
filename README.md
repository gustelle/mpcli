# Music Production Client

This tool provides the followins services:
1. it enables to estimate the tempo of a set of files located in a directory
1. it enables to convert a set of files located in a directory to a given BPM

Configuration is done in the file `config.toml`

Example of use case:
* estimate the tempo of each file located in the directory
* Take these files and convert them to 80 BPM. To do this it first detect the file source bpm. The output files are stored in a folder which is configurable

# How to run ?

Configure things in the file `config.toml`

* `poetry run timestretch` will timestrech the given files to the target tempo (`target_tempo`)
* `poetry run detect_tempo` will just give the tempos of the files located in the source directory 
