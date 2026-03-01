# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import dataclasses
import tomllib
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
    CLITimeStretchConfig,
    FileAudioSource,
)
from src.mpcli.entities.source import AudioSource
from src.mpcli.repository.audio_file import save_audio_file
from src.mpcli.use_cases.convert import execute_format_conversion
from src.mpcli.use_cases.normalization import execute_normalization
from src.mpcli.use_cases.tempo import execute_tempo_estimation
from src.mpcli.use_cases.timestretch import execute_timestretch

app = typer.Typer()


def _compute_filename(config: CLITimeStretchConfig, tempo: float) -> str:

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
        **dataclasses.asdict(config), tempo_min=tempo_min, tempo_max=tempo_max
    )


@app.command()
def detect_tempo():
    """estimate the tempo of an audio file"""

    table = Table(title="Tempo Detection Results")

    table.add_column("Source", justify="right", style="cyan", no_wrap=True)
    table.add_column("Tempo", style="magenta")

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)

        configs = []
        if isinstance(data["detect_tempo"], list):
            configs = data["detect_tempo"]
        else:
            configs = [data["detect_tempo"]]

        for config in configs:

            files = []
            if Path(config["source"]).is_dir():
                files = list(Path(config["source"]).glob("**/*.*"))
            else:
                files = [Path(config["source"])]
            for file in files:
                try:
                    config: FileAudioSource = FileAudioSource(source=file)
                    result = execute_tempo_estimation(config)
                    if result is not None:
                        table.add_row(
                            (
                                result.audio_source.name
                                if result.audio_source.name
                                else "Unknown"
                            ),
                            f"{result.tempo} BPM",
                        )
                except ValidationError as e:
                    logger.error(
                        f"Ignore {file} check `config.toml` file and ensure it is correctly formatted."
                    )
                except Exception as e:
                    logger.error(f"Error during tempo estimation: {e}")

    console = Console()
    console.print(table)


@app.command()
def timestretch():

    try:

        with open("config.toml", "rb") as f:
            data = tomllib.load(f)

            if "timestretch" not in data:
                raise CLIConfigError("Missing 'timestretch' section in config.toml")

            table = Table(title="Time Stretching Results")

            table.add_column("Source", justify="right", style="cyan", no_wrap=True)
            table.add_column("Target", style="magenta")
            table.add_column("BPM", justify="right", style="green")

            # if config provided as an array, take the first element
            if isinstance(data["timestretch"], list):
                configs = data["timestretch"]
            else:
                configs = [data["timestretch"]]

            for item in configs:
                config = CLITimeStretchConfig(**item)
                result = execute_timestretch(
                    source=AudioSource(
                        source=config.source,
                        audio_bytes=config.audio_bytes,
                        audio_format=config.audio_format,
                        sample_rate=config.sample_rate,
                    ),
                    target_tempo=config.target_tempo,
                    min_rate=config.min_rate,
                    max_rate=config.max_rate,
                )

                # dump to a file according to the provided filename template, for debugging purposes
                filename = _compute_filename(config, result.original_tempo)
                sound_file = save_audio_file(
                    output_dir=Path(config.output),
                    filename=filename,
                    data=result.converted_audio.audio_bytes,
                    sample_rate=result.converted_audio.sample_rate,
                    format=result.converted_audio.audio_format,
                )

                if result is not None:
                    table.add_row(
                        str(config.source),
                        str(sound_file),
                        str(result.target_tempo),
                    )

            console = Console()
            console.print(table)

    except CLIConfigError as e:
        print(f"Configuration error: {e}")


@app.command()
def convert():

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        config: CLIConvertConfig = CLIConvertConfig(**data["convert"])

    table = Table(title="Format Conversion Results")

    table.add_column("Source name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Source format", justify="right", style="cyan", no_wrap=True)
    table.add_column("Target name", style="magenta", no_wrap=True)
    table.add_column("Target format", style="magenta")

    result = execute_format_conversion(config, target_format=config.target_format)
    if result is not None:
        table.add_row(
            result.audio_source.name if result.audio_source.name else "Unknown",
            result.audio_source.audio_format,
            result.converted_audio.name if result.converted_audio.name else "Unknown",
            result.converted_audio.audio_format,
        )

    console = Console()
    console.print(table)


@app.command()
def normalize():

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        config: CLINormalizeConfig = CLINormalizeConfig(**data["normalize"])

    table = Table(title="Normalization Results")

    table.add_column("Source name", justify="right", style="cyan", no_wrap=True)
    table.add_column("LUFS", style="magenta")

    result = execute_normalization(config, lufs=config.lufs)
    if result is not None:
        table.add_row(
            result.audio_source.name if result.audio_source.name else "Unknown",
            str(result.lufs),
        )

    console = Console()
    console.print(table)


if __name__ == "__main__":
    app()
