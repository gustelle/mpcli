from typing import Optional

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from mpcli.use_cases.tempo import execute_tempo_estimation
from src.mpcli.entities.source import AudioSource

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

    file_content = file.file.read()
    audio_source = AudioSource(
        name=file.filename,
        audio_format=file.filename.split(".")[-1],
        audio_bytes=file_content,
        sample_rate=44100,  # Assuming a default sample rate, adjust as needed
    )

    result = execute_tempo_estimation(audio_source)
    if result is not None:
        return TempoResponse(
            source_name=audio_source.name,
            source_format=audio_source.audio_format,
            tempo=result.tempo,
        )

    raise ValueError("Tempo estimation failed")
