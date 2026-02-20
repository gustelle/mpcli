from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional


@dataclass
class TimeStretchConfig:
    source: Path
    output: Path
    format: Literal["wav", "mp3"]
    target_tempo: Optional[float] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    filename: Optional[str] = None

    def __init__(self, **kwargs):

        if kwargs.get("source") is None:
            raise ValueError("Source file must be provided")

        if kwargs.get("output") is None:
            raise ValueError("Output directory must be provided")

        # force path conversion to Path objects
        self.source = Path(kwargs.get("source"))
        self.output = Path(kwargs.get("output"))
        self.format = kwargs.get("format", "wav")
        self.target_tempo = kwargs.get("target_tempo")
        self.min_rate = kwargs.get("min_rate", 1.0)
        self.max_rate = kwargs.get("max_rate", 1.0)
        self.filename = kwargs.get("filename", None)

        # check format validity
        if self.format not in ["wav", "mp3"]:
            raise ValueError(
                f"Invalid format: {self.format}. Supported formats are wav and mp3."
            )

        if (
            self.target_tempo is None
            and self.min_rate is None
            and self.max_rate is None
        ):
            raise ValueError(
                "Either target_tempo or min_rate/max_rate must be provided"
            )

        if self.target_tempo is not None and (
            self.min_rate is not None or self.max_rate is not None
        ):
            raise ValueError(
                "Only one of target_tempo or min_rate/max_rate can be provided"
            )


@dataclass
class ConvertConfig:
    source: Path
    output: Path
    format: Literal["wav", "mp3"]

    def __init__(self, **kwargs):

        # force path conversion to Path objects
        self.source = Path(kwargs.get("source"))
        self.output = Path(kwargs.get("output"))
        self.format = kwargs.get("format", "wav")

        # check format validity
        if self.format not in ["wav", "mp3"]:
            raise ValueError(
                f"Invalid format: {self.format}. Supported formats are wav and mp3."
            )


@dataclass
class DetectTempoConfig:
    source: Path

    def __init__(self, **kwargs):

        # force path conversion to Path objects
        self.source = Path(kwargs.get("source"))
