# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import textwrap
import tomllib
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from mpcli.entities.config import (
    ConfigError,
    ConvertConfig,
    DetectTempoConfig,
    TimeStretchConfig,
)
from mpcli.use_cases.convert import execute_format_conversion
from mpcli.use_cases.tempo import execute_tempo_estimation
from mpcli.use_cases.timestretch import execute_timestretch

app = typer.Typer()


@app.command()
def detect_tempo():
    """estimate the tempo of an audio fileor a batch of audio files in a directory, and print the results in a human-readable format"""

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        config: DetectTempoConfig = DetectTempoConfig(**data["detect_tempo"])

    table = Table(title="Tempo Detection Results")

    table.add_column("Source", justify="right", style="cyan", no_wrap=True)
    table.add_column("Tempo", style="magenta")

    for result in execute_tempo_estimation(config):
        if result is not None:
            table.add_row(
                f"{Path(result.source_path).name}",
                f"{result.tempo} BPM",
            )

    console = Console()
    console.print(table)


@app.command()
def timestretch():

    try:

        with open("config.toml", "rb") as f:
            data = tomllib.load(f)

            if "timestretch" not in data:
                raise ConfigError("Missing 'timestretch' section in config.toml")

            table = Table(title="Time Stretching Results")

            table.add_column("Source", justify="right", style="cyan", no_wrap=True)
            table.add_column("Target", style="magenta")
            table.add_column("BPM", justify="right", style="green")

            # if config provided as an array, take the first element
            if isinstance(data["timestretch"], list):
                for item in data["timestretch"]:
                    config = TimeStretchConfig(**item)
                    for result in execute_timestretch(config):
                        if result is not None:
                            table.add_row(
                                f"{Path(result.source_path).name}",
                                f"{Path(result.target_path).name}",
                                str(result.target_tempo),
                            )

            else:
                config: TimeStretchConfig = TimeStretchConfig(**data["timestretch"])
                for result in execute_timestretch(config):
                    if result is not None:
                        table.add_row(
                            f"{Path(result.source_path).name}",
                            f"{Path(result.target_path).name}",
                            str(result.target_tempo),
                        )

            console = Console()
            console.print(table)

    except ConfigError as e:
        print(f"Configuration error: {e}")


@app.command()
def convert():

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        config: ConvertConfig = ConvertConfig(**data["convert"])

    table = Table(title="Format Conversion Results")

    table.add_column("Source", justify="right", style="cyan", no_wrap=True)
    table.add_column("Target", style="magenta")

    for result in execute_format_conversion(config):
        if result is not None:
            table.add_row(
                textwrap.shorten(f"{result.source_path}", width=30),
                textwrap.shorten(f"{result.target_path}", width=30),
            )

    console = Console()
    console.print(table)


if __name__ == "__main__":
    app()
