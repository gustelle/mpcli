from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional


class ConfigError(ValueError):
    pass


@dataclass
class TimeStretchConfig:
    """Controls are done here, among others:
    - if min_rate is provided but not max_rate, max_rate is set to 1.0 (no time stretch)
    - if max_rate is provided but not min_rate, min_rate is set to 1.0 (no time stretch)

    """

    source: Path
    output: Path
    format: Literal["wav", "mp3"]
    target_tempo: Optional[float] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    filename: Optional[str] = None

    def __init__(self, **kwargs):

        if kwargs.get("source") is None:
            raise ConfigError("Source file must be provided")

        if kwargs.get("output") is None:
            raise ConfigError("Output directory must be provided")

        # force path conversion to Path objects
        self.source = Path(kwargs.get("source"))
        self.output = Path(kwargs.get("output"))
        self.format = kwargs.get("format", "wav")
        self.target_tempo = kwargs.get("target_tempo")
        self.min_rate = kwargs.get("min_rate", None)
        self.max_rate = kwargs.get("max_rate", None)
        self.filename = kwargs.get("filename", None)

        # check format validity
        if self.format not in ["wav", "mp3"]:
            raise ConfigError(
                f"Invalid format: {self.format}. Supported formats are wav and mp3."
            )

        if (
            self.target_tempo is None
            and self.min_rate is None
            and self.max_rate is None
        ):
            raise ConfigError(
                "Either target_tempo or min_rate/max_rate must be provided"
            )

        if self.target_tempo is not None and (
            self.min_rate is not None or self.max_rate is not None
        ):
            raise ConfigError(
                "Only one of target_tempo or min_rate/max_rate can be provided"
            )

        if (
            self.min_rate is not None
            and self.max_rate is not None
            and self.min_rate > self.max_rate
        ):
            raise ConfigError("min_rate cannot be greater than max_rate")

        # set max_rate to 1.0 if min_rate is provided but not max_rate
        if self.min_rate is not None and self.max_rate is None:
            self.max_rate = 1.0

        # set min_rate to 1.0 if max_rate is provided but not min_rate
        if self.max_rate is not None and self.min_rate is None:
            self.min_rate = 1.0


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
            raise ConfigError(
                f"Invalid format: {self.format}. Supported formats are wav and mp3."
            )


@dataclass
class DetectTempoConfig:
    source: Path

    def __init__(self, **kwargs):

        # force path conversion to Path objects
        self.source = Path(kwargs.get("source"))
        self.source = Path(kwargs.get("source"))
