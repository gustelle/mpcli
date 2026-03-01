from typing import Optional

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from mpcli.cli_entities import AudioSource, FileAudioSource
from mpcli.use_cases.tempo import execute_tempo_estimation

app = FastAPI()


class TempoResponse(BaseModel):

    source_name: str
    source_format: str
    tempo: float


@app.post("/convert")
def convert(source: AudioSource):
    return {"message": "Hello World"}


@app.post("/normalize")
def normalize(source: AudioSource):
    return {"message": "Hello World"}


@app.post("/timestretch")
def timestretch(source: AudioSource, target_tempo: float):
    return {"message": "Hello World"}


@app.post("/tempo")
def tempo(file: UploadFile = File(...)) -> TempoResponse:
    config: FileAudioSource = FileAudioSource(source=file.file)
    for result in execute_tempo_estimation(config):
        if result is not None:
            return TempoResponse(
                source_name=file.filename, source_format=file.content_type, tempo=120.0
            )
    raise ValueError("Tempo estimation failed")
