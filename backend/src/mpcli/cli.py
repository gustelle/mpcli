
from pathlib import Path

import jinja2
import typer
from loguru import logger
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from src.mpcli.cli_entities import (
    CLIConfigError,
    CLIConvertConfig,
    CLINormalizeConfig,
    CLITempoEstimationConfig,
    CLITimeStretchConfig,
)
from src.mpcli.repository.audio_file import iter_sources, save_audio_file
from src.mpcli.repository.toml_config import read_configurations
from src.mpcli.use_cases.convert import execute_format_conversion
from src.mpcli.use_cases.normalization import execute_normalization
from src.mpcli.use_cases.tempo import execute_tempo_estimation
from src.mpcli.use_cases.timestretch import execute_timestretch

app = typer.Typer()


def _timestretched_filename(config: CLITimeStretchConfig, tempo: float) -> str:

    environment = jinja2.Environment()

    tempo_min = round(tempo * config.min_rate, 2)
    tempo_max = round(tempo * config.max_rate, 2)

    if config.filename is not None:
        filename_template = config.filename
    elif tempo_min == tempo_max:
        filename_template = "{{ source.stem }}_{{ tempo_min }}_BPM"
    else:
        filename_template = "{{ source.stem }}_{{ tempo_min }}-{{ tempo_max }}_BPM"

    template = environment.from_string(filename_template)

    return template.render(
        **config.model_dump(), tempo_min=tempo_min, tempo_max=tempo_max
    )


@app.command()
def detect_tempo():
    """estimate the tempo of an audio file"""

    table = Table(title="Tempo Detection Results")

    table.add_column("Source", justify="right", style="cyan", no_wrap=True)
    table.add_column("Tempo", style="magenta")

    configs = read_configurations(
        "config.toml", "detect_tempo", CLITempoEstimationConfig
    )

    for config in configs:

        for audio in iter_sources(config.source):
            try:
                result = execute_tempo_estimation(audio)
                if result is not None:
                    table.add_row(
                        result.audio_source.name,
                        f"{result.tempo} BPM",
                    )
            except ValidationError as e:
                logger.error(
                    f"Ignore {audio.name if audio.name else 'Unknown'} check `config.toml` file and ensure it is correctly formatted."
                )
            except Exception as e:
                logger.error(f"Error during tempo estimation: {e}")

    console = Console()
    console.print(table)


@app.command()
def timestretch():

    try:

        table = Table(title="Time Stretching Results")

        table.add_column("Source", justify="right", style="cyan", no_wrap=True)
        table.add_column("Target", style="magenta")
        table.add_column("BPM", justify="right", style="green")

        # if config provided as an array, take the first element
        configs = read_configurations(
            "config.toml", "timestretch", CLITimeStretchConfig
        )

        for c in configs:

            for source in iter_sources(c.source):

                result = execute_timestretch(
                    source=source,
                    target_tempo=c.target_tempo,
                    min_rate=c.min_rate,
                    max_rate=c.max_rate,
                )

                if result is not None:
                    # dump to a file according to the provided filename template, for debugging purposes
                    filename = _timestretched_filename(c, result.original_tempo)
                    sound_file = save_audio_file(
                        output_dir=Path(c.output),
                        filename=filename,
                        data=result.converted_audio.to_array(),
                        sample_rate=result.converted_audio.sample_rate,
                        format=result.converted_audio.audio_format,
                    )
                    table.add_row(
                        str(c.source),
                        sound_file.name,
                        str(result.target_tempo),
                    )

        console = Console()
        console.print(table)

    except CLIConfigError as e:
        print(f"Configuration error: {e}")


@app.command()
def convert():

    table = Table(title="Format Conversion Results")

    table.add_column("Source name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Source format", justify="right", style="cyan", no_wrap=True)
    table.add_column("Target name", style="magenta", no_wrap=True)
    table.add_column("Target format", style="magenta")

    configs = read_configurations("config.toml", "convert", CLIConvertConfig)

    for c in configs:

        for source in iter_sources(c.source):

            result = execute_format_conversion(source, target_format=c.target_format)

            if result is not None:
                
                
                # get numpy array from the converted audio source
                converted_array = result.converted_audio.to_array()

                # dump to a file according to the provided filename template, for debugging purposes
                save_audio_file(
                    output_dir=c.output,
                    filename=result.converted_audio.name,
                    data=converted_array,
                    sample_rate=result.converted_audio.sample_rate,
                    format=result.converted_audio.audio_format,
                )
                table.add_row(
                    result.audio_source.name,
                    result.audio_source.audio_format,
                    result.converted_audio.name,
                    result.converted_audio.audio_format,
                )

    console = Console()
    console.print(table)


@app.command()
def normalize():

    configs = read_configurations("config.toml", "normalize", CLINormalizeConfig)

    table = Table(title="Normalization Results")

    table.add_column("Source name", justify="right", style="cyan", no_wrap=True)
    table.add_column("LUFS", style="magenta")
    table.add_column("Target name", style="green", no_wrap=True)

    for c in configs:
        for source in iter_sources(c.source):
            result = execute_normalization(source, lufs=c.lufs)
            if result is not None:
                
                save_audio_file(
                    output_dir=c.output,
                    filename=result.converted_audio.name,
                    data=result.converted_audio.to_array(),
                    sample_rate=result.converted_audio.sample_rate,
                    format=result.converted_audio.audio_format,
                )
                table.add_row(
                    result.audio_source.name,
                    str(result.lufs),
                    result.converted_audio.name,
                )

    console = Console()
    console.print(table)


if __name__ == "__main__":
    app()
