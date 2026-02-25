from typing import Generator

from mpcli.entities.config import ConvertConfig
from mpcli.entities.result import ConvertResult
from mpcli.repository.audio_file import iter_sources, load_audio_file, save_audio_file


def execute_format_conversion(
    config: ConvertConfig,
) -> Generator[ConvertResult | None, None, None]:

    for source in iter_sources(config.source):

        audio_data, sr = load_audio_file(source)

        yield save_audio_file(
            output_dir=config.output,
            filename=source.stem,
            samples=audio_data,
            sample_rate=sr,
            format=config.format,
        )
