from pathlib import Path
from typing import Generator

from pydub import AudioSegment

from mpcli.entities.config import ConvertConfig
from mpcli.entities.result import ConvertResult

from ..repository.files import iter_sources


def execute_format_conversion(
    config: ConvertConfig,
) -> Generator[ConvertResult | None, None, None]:

    for source in iter_sources(config.source):

        print(f"Converting {source} to {config.format} format...")

        audio = AudioSegment.from_file(source)

        output_dir = config.output
        output_format = config.format

        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{source.stem}.{output_format}"

        if output_path.exists():
            output_path.unlink()

        audio.export(output_path, format=output_format)

        yield ConvertResult(
            source_path=str(source),
            target_path=str(output_path),
        )
