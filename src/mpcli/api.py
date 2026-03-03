from typing import Literal

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from pydantic import BaseModel, ValidationError

from src.mpcli.entities.source import AudioSource
from src.mpcli.use_cases.convert import execute_format_conversion
from src.mpcli.use_cases.tempo import execute_tempo_estimation

app = FastAPI()


class TempoResponse(BaseModel):

    source_name: str
    source_format: str
    tempo: float


class AudioResponse(BaseModel):
    name: str
    format: Literal["wav", "mp3"]
    content: bytes
    sample_rate: int


@app.post("/convert")
def convert(file: UploadFile = File(...), target_format: Literal["wav", "mp3"] = "wav"):

    file_content = file.file.read()

    try:
        audio_source = AudioSource(
            name=file.filename,
            audio_format=file.filename.split(".")[-1],
            audio_bytes=file_content,
            sample_rate=44100,  # Assuming a default sample rate, adjust as needed
        )

        # Here you would implement the actual conversion logic
        result = execute_format_conversion(audio_source, target_format)

        # generate a response with the converted audio content
        return Response(
            result.converted_audio.audio_bytes, media_type="application/octet-stream"
        )

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/normalize")
def normalize(source: AudioSource):
    return {"message": "Hello World"}


@app.post("/timestretch")
def timestretch(source: AudioSource, target_tempo: float):
    return {"message": "Hello World"}


@app.post("/tempo")
def tempo(file: UploadFile = File(...)) -> TempoResponse:

    file_content = file.file.read()

    try:
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

        raise ValueError("No tempo estimation result returned")

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
