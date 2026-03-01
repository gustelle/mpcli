from typing import Literal

from src.mpcli.entities.result import ConvertResult
from src.mpcli.entities.source import AudioSource
from src.mpcli.repository.audio_convert import convert


def execute_format_conversion(
    config: AudioSource, target_format: Literal["wav", "mp3"]
) -> ConvertResult | None:

    result = convert(config, target_format=target_format)

    return result
