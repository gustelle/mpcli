from dataclasses import dataclass


@dataclass
class TempoResult:
    source_path: str
    tempo: float

    def __init__(self, **kwargs):
        self.source_path = kwargs.get("source_path")
        self.tempo = kwargs.get("tempo")


@dataclass
class TimeStretchResult:
    source_path: str
    original_tempo: float
    target_tempo: float
    target_path: str

    def __init__(self, **kwargs):
        self.source_path = kwargs.get("source_path")
        self.original_tempo = kwargs.get("original_tempo")
        self.target_tempo = kwargs.get("target_tempo")
        self.target_path = kwargs.get("target_path")


@dataclass
class ConvertResult:
    source_path: str
    target_path: str

    def __init__(self, **kwargs):
        self.source_path = kwargs.get("source_path")
        self.target_path = kwargs.get("target_path")


@dataclass
class NormalizeResult:
    source_path: str
    target_path: str
    lufs: float

    def __init__(self, **kwargs):
        self.source_path = kwargs.get("source_path")
        self.target_path = kwargs.get("target_path")
        self.lufs = kwargs.get("lufs")
