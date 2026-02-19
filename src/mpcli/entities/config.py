from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional


@dataclass
class TimeStretchConfig:
    source: Path
    output: Path
    format: Literal["wav", "mp3"]
    target_tempo: Optional[float] = None
    ratio: Optional[float] = None
    create_target_dir: bool = True
    filename: Optional[str] = None

    def __init__(self, **kwargs):

        # force path conversion to Path objects
        self.source = Path(kwargs.get("source"))
        self.output = Path(kwargs.get("output"))
        self.format = kwargs.get("format", "wav")
        self.target_tempo = kwargs.get("target_tempo")
        self.ratio = kwargs.get("ratio")
        self.create_target_dir = kwargs.get("create_target_dir", True)
        self.filename = kwargs.get("filename")

        # check format validity
        if self.format not in ["wav", "mp3"]:
            raise ValueError(
                f"Invalid format: {self.format}. Supported formats are wav and mp3."
            )

        if self.target_tempo is None and self.ratio is None:
            raise ValueError("Either target_tempo or ratio must be provided")

        if self.target_tempo is not None and self.ratio is not None:
            raise ValueError("Only one of target_tempo or ratio can be provided")


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
