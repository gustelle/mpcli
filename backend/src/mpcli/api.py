
from typing import Annotated, Literal

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import PlainTextResponse
from loguru import logger
from pydantic import BaseModel, ValidationError, Field

from src.mpcli.entities.source import AudioSource
from src.mpcli.use_cases.convert import execute_format_conversion
from src.mpcli.use_cases.normalization import execute_normalization
from src.mpcli.use_cases.tempo import execute_tempo_estimation
from src.mpcli.use_cases.timestretch import execute_timestretch

app = FastAPI()

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    message = "Validation errors:"
    for error in exc.errors():
        message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(message, status_code=400)


class TempoResponse(BaseModel):

    source_name: str = Field(..., description="The name of the source audio file")
    source_format: str = Field(..., description="The format of the source audio file")
    tempo: float = Field(..., description="The estimated tempo of the audio file in BPM")


class AudioResponse(BaseModel):
    name: str = Field(..., description="The name of the audio file")
    format: Literal["wav", "mp3"]
    content: bytes = Field(..., description="The binary content of the audio file")
    sample_rate: int = Field(..., description="The sample rate of the audio file in Hz")


@app.post("/convert")
def convert(file: Annotated[UploadFile, File(
    description="The audio file to be converted. Supported formats are WAV and MP3.")], 
            target_format: Annotated[str, Form(
                examples=[{"value": "wav", "description": "Convert to WAV format"}, {"value": "mp3", "description": "Convert to MP3 format"}])],
            sample_rate: Annotated[int, Form()] = 44100):

    file_content = file.file.read()

    try:
        audio_source = AudioSource(
            name=file.filename,
            audio_format=file.filename.split(".")[-1],
            audio_bytes=file_content,
            sample_rate=sample_rate,  # Use the provided sample rate
        )

        # Here you would implement the actual conversion logic
        result = execute_format_conversion(audio_source, target_format)
        
        logger.info(
            f"Converted '{audio_source.name}' from {audio_source.audio_format} to {target_format}, resulting in {len(result.converted_audio.audio_bytes)} bytes"
        )

        # generate a response with the converted audio content
        return Response(
            result.converted_audio.audio_bytes, media_type="application/octet-stream"
        )

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/normalize")
def normalize(
    file: Annotated[UploadFile, File(
        description="The audio file to be normalized. Supported formats are WAV and MP3.")], lufs: Annotated[float, Form(
            description="The target loudness in LUFS. Defaults to -14.0 LUFS", ge=-20.0, le=0.0)]= -14.0
):

    file_content = file.file.read()

    try:
        audio_source = AudioSource(
            name=file.filename,
            audio_format=file.filename.split(".")[-1],
            audio_bytes=file_content,
            sample_rate=44100,  # Assuming a default sample rate, adjust as needed
        )

        result = execute_normalization(audio_source, lufs)
        return Response(
            result.converted_audio.audio_bytes,
            media_type="application/octet-stream",
        )

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/timestretch")
def timestretch(
    file: Annotated[UploadFile, File(
        description="The audio file to be timestretched. Supported formats are WAV and MP3.")],
    target_tempo: Annotated[float, Form(
        description="""
        The target tempo for the audio file. 
        At least one of target_tempo or min_rate and max_rate must be provided.
        - when min_rate and max_rate are not provided, the time stretch factor is computed as the ratio of the target tempo to the original tempo.
        - when min_rate and max_rate are provided, the target tempo passed here is ignored and the time stretch factor is a range of values between the min_rate and max_rate.
        """,)] = None,
    min_rate: Annotated[float, Form(
        description="""
            The minimum rate for timestretching.
            Defaults to 1.0, which means no change in tempo.
            At least one of target_tempo or min_rate and max_rate must be provided.
             Values less than 1.0 will slow down the audio, while values greater than 1.0 will speed it up.
            - when target_tempo is provided and min_rate and max_rate are not provided, the time stretch factor is computed as the ratio of the target tempo to the original tempo.
            - when target_tempo is provided and min_rate and max_rate are provided, the target tempo passed here is ignored and the time stretch factor is a range of values between the min_rate and
            """,)] = 1.0,
    max_rate: Annotated[float, Form(
        description="""
            The maximum rate for timestretching.
            Defaults to 1.0, which means no change in tempo.
            At least one of target_tempo or min_rate and max_rate must be provided.
             Values less than 1.0 will slow down the audio, while values greater than 1.0 will speed it up.
            - when target_tempo is provided and min_rate and max_rate are not provided, the time stretch factor is computed as the ratio of the target tempo to the original tempo.
            - when target_tempo is provided and min_rate and max_rate are provided, the target tempo passed here is ignored and the time stretch factor is a range of values between the min_rate and max_rate.
            """,)] = 1.0,
    
):
    logger.info(
        f"Received timestretch request for file '{file.filename}' with target_tempo={target_tempo}, min_rate={min_rate}, max_rate={max_rate}"
    )

    file_content = file.file.read()

    try:
        audio_source = AudioSource(
            name=file.filename,
            audio_format=file.filename.split(".")[-1],
            audio_bytes=file_content,
            sample_rate=44100,  # Assuming a default sample rate, adjust as needed
        )

        result = execute_timestretch(audio_source, target_tempo, min_rate, max_rate)
        return Response(
            result.converted_audio.audio_bytes,
            media_type="application/octet-stream",
        )

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tempo")
def tempo(file: UploadFile = File(...)) -> TempoResponse:
    """Estimate the tempo of an audio file.

    Args:
        file (UploadFile, optional): The audio file for which to estimate the tempo. Defaults to File(...).

    Returns:
        TempoResponse: The estimated tempo of the audio file.
    """

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
