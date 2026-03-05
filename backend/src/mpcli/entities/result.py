from pydantic import BaseModel

from src.mpcli.entities.source import AudioSource


class TempoResult(BaseModel):
    tempo: float
    audio_source: AudioSource


class TimeStretchResult(BaseModel):
    audio_source: AudioSource
    converted_audio: AudioSource
    original_tempo: float
    target_tempo: float


class ConvertResult(BaseModel):
    audio_source: AudioSource
    converted_audio: AudioSource


class NormalizeResult(BaseModel):
    audio_source: AudioSource
    converted_audio: AudioSource
    lufs: float
