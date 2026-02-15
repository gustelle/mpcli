# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import os
import re
import tomllib
from pathlib import Path
from pprint import pprint
from typing import Annotated, Literal

import audioread
import typer
from audiomentations import TimeStretch
from audiomentations.core.audio_loading_utils import load_sound_file
from colorama import Fore, Style
from colorama import init as colorama_init
from pydub import AudioSegment
from scipy.io import wavfile
from tempocnn.classifier import TempoClassifier
from tempocnn.feature import read_features

from mpcli.entities.result import Result

app = typer.Typer()

colorama_init()


def list_input_files(
    source_path: str | Path,
    format: Literal["*", "wav", "mp3", "flac", "ogg", "m4a"] = "*",
) -> list[Path]:

    # read the file's features
    batch = []

    if Path(source_path).is_file():
        batch.append(Path(source_path))
    else:

        for source in Path(source_path).glob("*.*"):

            if format == "*":
                format_pattern = r".*\.(wav|mp3|flac|ogg|m4a)$"
            else:
                format_pattern = rf".*\.{format}$"

            if source.is_dir() or source.stem.startswith("."):
                print(
                    f"{Fore.YELLOW}Skipping {source} (not a valid audio file){Style.RESET_ALL}"
                )
                continue
            elif not re.match(format_pattern, source.name, re.IGNORECASE):
                print(
                    f"{Fore.YELLOW}Skipping {source} (unsupported file format){Style.RESET_ALL}"
                )
                continue
            else:
                batch.append(source)

    return batch


def _estimate_tempo(source: Path, model_name: str = "cnn") -> Result | None:
    """estimate the tempo of an audio file, and print the result in a human-readable format

    source: the path to the audio file, must be a valid audio file (wav|mp3|flac|ogg|m4a)
    model_name: the name of the model to use for tempo estimation, default is "cnn"

    """

    model_name = "cnn"

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

    try:

        features = read_features(source, zero_pad=True)

        # estimate the global tempo
        tempo = classifier.estimate_tempo(features, interpolate=True)

        return Result(file=source.name, tempo=tempo)

    except audioread.exceptions.NoBackendError as e:
        print(f"{Fore.RED}Error processing {source}: {e}{Style.RESET_ALL}")


@app.command()
def detect_tempo():
    """estimate the tempo of an audio fileor a batch of audio files in a directory, and print the results in a human-readable format"""

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        source_path = data["detect_tempo"]["source"]
    batch = list_input_files(source_path)

    for source in batch:
        r: Result = _estimate_tempo(source, log_results=True)

        pprint(
            {
                "file": source.name,
                "estimated_tempo": r.tempo if r is not None else None,
            },
            indent=4,
        )


@app.command()
def timestretch(
    apply_ratio: Annotated[
        float | None,
        typer.Option(
            help="force a ratio instead of a target tempo. Leave it empty to compute the ratio from the target tempo and the estimated tempo of the source file."
        ),
    ] = None,
):

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        source_path = data["timestretch"]["source"]

    batch = list_input_files(source_path)

    output_format: str = data["timestretch"]["output_format"].lower()

    for source in batch:

        # estimate the global tempo
        result = _estimate_tempo(source)

        # compute the time stretch factor
        if apply_ratio is not None:
            factor = apply_ratio
            target_tempo = round(result.tempo * factor, 2)
        else:
            target_tempo = float(data["timestretch"]["target_tempo"])
            factor = target_tempo / result.tempo

        samples, sample_rate = load_sound_file(source, sample_rate=None, mono=False)

        print(
            f"{Fore.BLUE}Processing '{source.name}': estimated tempo = {result.tempo} BPM, target tempo = {target_tempo} BPM, time stretch factor = {factor:.4f}, sample rate = {sample_rate} Hz{Style.RESET_ALL}"
        )

        if len(samples.shape) == 2 and samples.shape[0] > samples.shape[1]:
            samples = samples.transpose()

        output_dir = data["timestretch"]["output"]

        output_dir = Path(output_dir) / "timestretch" / str(target_tempo)
        output_dir.mkdir(parents=True, exist_ok=True)

        # see https://iver56.github.io/audiomentations/waveform_transforms/time_stretch/
        augmenter = TimeStretch(
            min_rate=factor,
            max_rate=factor,
            method="signalsmith_stretch",
            p=1,  # probability of applying the transformation
            leave_length_unchanged=False,  # keep the output length the same as input
        )

        wav_output_path = os.path.join(
            output_dir,
            f"{source.stem}_{target_tempo}.wav",
        )

        if Path(wav_output_path).exists():
            print(
                f"{Fore.YELLOW}Output file '{wav_output_path}' already exists, overriding...{Style.RESET_ALL}"
            )
            Path(wav_output_path).unlink()

        augmented_samples = augmenter(samples=samples, sample_rate=sample_rate)

        if len(augmented_samples.shape) == 2:
            augmented_samples = augmented_samples.transpose()

        # alwzays export as wav, even if the output format is mp3,
        wavfile.write(wav_output_path, rate=sample_rate, data=augmented_samples)

        match output_format:
            case "mp3":
                _process_conversion(wav_output_path, output_format, output_dir)

                # remove the wav file
                Path(wav_output_path).unlink()

                print(
                    f"{Fore.GREEN}Time-stretched '{source.name}' to {target_tempo} BPM and saved to '{output_dir}'{Style.RESET_ALL}"
                )
            case "wav":
                print(
                    f"{Fore.GREEN}Time-stretched '{source.name}' to {target_tempo} BPM and saved to '{wav_output_path}'{Style.RESET_ALL}"
                )


@app.command()
def convert():
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        source_path = Path(data["convert"]["source"])

    output_format: str = data["convert"]["output_format"].lower()
    output_dir: Path = Path(data["convert"]["output"])

    _process_conversion(source_path, output_format, output_dir)


def _process_conversion(source_path: Path, output_format: str, output_dir: Path):

    batch = list_input_files(source_path)

    print(
        f"{Fore.BLUE}Converting {len(batch)} files from '{source_path}' to {output_format.upper()} and saving to '{output_dir}'{Style.RESET_ALL}"
    )

    for source in batch:

        audio = AudioSegment.from_file(source)

        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = os.path.join(
            output_dir,
            f"{source.stem}.{output_format}",
        )

        if Path(output_path).exists():
            print(
                f"{Fore.YELLOW}Output file '{output_path}' already exists, overriding...{Style.RESET_ALL}"
            )
            Path(output_path).unlink()

        audio.export(output_path, format=output_format)

        print(
            f"{Fore.GREEN}Converted '{source.name}' to {output_format.upper()} and saved to '{output_dir}'{Style.RESET_ALL}"
        )


if __name__ == "__main__":
    app()
