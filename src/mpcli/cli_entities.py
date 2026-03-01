from pathlib import Path
from typing import Literal, Optional, Self

from pydantic import Field, model_validator

from src.mpcli.entities.source import FileAudioSource


class CLIConfigError(ValueError):
    pass


class CLINormalizeConfig(FileAudioSource):
    output: Path
    lufs: float = Field(default=-14.0, le=0.0)


class CLITimeStretchConfig(FileAudioSource):
    """Controls are done here, among others:
    - if min_rate is provided but not max_rate, max_rate is set to 1.0 (no time stretch)
    - if max_rate is provided but not min_rate, min_rate is set to 1.0 (no time stretch)

    """

    output: Path  # directory where the time stretched audio file will be saved
    target_tempo: Optional[float] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    filename: Optional[str] = None

    @model_validator(mode="after")
    def validate_config(self) -> Self:

        if (
            self.target_tempo is None
            and self.min_rate is None
            and self.max_rate is None
        ):
            raise CLIConfigError(
                "Either target_tempo or min_rate/max_rate must be provided"
            )

        if self.target_tempo is not None and (
            self.min_rate is not None or self.max_rate is not None
        ):
            raise CLIConfigError(
                "Only one of target_tempo or min_rate/max_rate can be provided"
            )

        if (
            self.min_rate is not None
            and self.max_rate is not None
            and self.min_rate > self.max_rate
        ):
            raise CLIConfigError("min_rate cannot be greater than max_rate")

        # set max_rate to 1.0 if min_rate is provided but not max_rate
        if self.min_rate is not None and self.max_rate is None:
            self.max_rate = 1.0

        # set min_rate to 1.0 if max_rate is provided but not min_rate
        if self.max_rate is not None and self.min_rate is None:
            self.min_rate = 1.0

        return self


class CLIConvertConfig(FileAudioSource):

    output: Path
    target_format: Literal["wav", "mp3"] = Field(default="wav")
