# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import os
import re
import tomllib
from pathlib import Path
from pprint import pprint

import audioread
import typer
from audiomentations import TimeStretch
from audiomentations.core.audio_loading_utils import load_sound_file
from colorama import Fore, Style
from colorama import init as colorama_init
from scipy.io import wavfile
from tempocnn.classifier import TempoClassifier
from tempocnn.feature import read_features
from tqdm import tqdm

from mpcli.entities.result import Result

app = typer.Typer()

colorama_init()


def list_input_files(source_path: str) -> list[Path]:

    # read the file's features
    batch = []

    if Path(source_path).is_file():
        batch.append(Path(source_path))
    else:

        for source in Path(source_path).glob("*.*"):

            if source.is_dir() or source.stem.startswith("."):
                print(
                    f"{Fore.YELLOW}Skipping {source} (not a valid audio file){Style.RESET_ALL}"
                )
                continue
            elif not re.match(
                r".*\.(wav|mp3|flac|ogg|m4a)$", source.name, re.IGNORECASE
            ):
                print(
                    f"{Fore.YELLOW}Skipping {source} (unsupported file format){Style.RESET_ALL}"
                )
                continue
            else:
                batch.append(source)

    return batch


def estimate_tempo(
    source: Path, model_name: str = "cnn", log_results: bool = False
) -> Result | None:
    """estimate the tempo of an audio file, and print the result in a human-readable format

    source: the path to the audio file, must be a valid audio file (wav|mp3|flac|ogg|m4a)
    model_name: the name of the model to use for tempo estimation, default is "cnn"
    log_results: whether to print the results in a human-readable format, default is False

    """

    model_name = "cnn"

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

    try:

        features = read_features(source, zero_pad=True)

        # estimate the global tempo
        tempo = classifier.estimate_tempo(features, interpolate=True)
        if log_results:
            pprint(
                {
                    "file": source.name,
                    "estimated_tempo": tempo,
                },
                indent=4,
            )

        return Result(file=source.name, tempo=tempo)

    except audioread.exceptions.NoBackendError as e:
        print(f"{Fore.RED}Error processing {source}: {e}{Style.RESET_ALL}")


@app.command()
def tempo():
    """estimate the tempo of an audio fileor a batch of audio files in a directory, and print the results in a human-readable format"""

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        source_path = data["tempo"]["source"]

    batch = list_input_files(source_path)

    for source in batch:
        estimate_tempo(source, log_results=True)


@app.command()
def timestretch():

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        source_path = data["timestretch"]["source"]

    target_tempo: float = float(data["timestretch"]["target_tempo"])

    batch = list_input_files(source_path)

    for source in batch:

        # estimate the global tempo
        result = estimate_tempo(source)

        # compute the time stretch factor
        factor = target_tempo / result.tempo

        # apply time stretch
        transforms = [
            {
                "instance": TimeStretch(
                    # min_rate=0.86, max_rate=0.86, method="signalsmith_stretch", p=1.0
                    min_rate=factor,
                    max_rate=factor,
                    method="signalsmith_stretch",
                    p=1,  # probability of applying the transformation
                    leave_length_unchanged=False,  # keep the output length the same as input
                ),
                "num_runs": 1,
                "name": "TimeStretchSignalsmithStretch",
            },
        ]

        samples, sample_rate = load_sound_file(source, sample_rate=None, mono=False)
        if len(samples.shape) == 2 and samples.shape[0] > samples.shape[1]:
            samples = samples.transpose()

        output_dir = data["timestretch"]["output"]
        output_dir = Path(output_dir) / "timestretch" / str(target_tempo)
        output_dir.mkdir(parents=True, exist_ok=True)

        for transform in tqdm(transforms):
            augmenter = transform["instance"]

            output_file_path = os.path.join(
                output_dir,
                f"{source.stem}_{target_tempo}.wav",
            )

            if Path(output_file_path).exists():
                print(
                    f"{Fore.YELLOW}Output file '{output_file_path}' already exists, overriding...{Style.RESET_ALL}"
                )
                Path(output_file_path).unlink()

            augmented_samples = augmenter(samples=samples, sample_rate=sample_rate)

            if len(augmented_samples.shape) == 2:
                augmented_samples = augmented_samples.transpose()

            wavfile.write(output_file_path, rate=sample_rate, data=augmented_samples)

        print(
            f"{Fore.GREEN}Time-stretched '{source.name}' to {target_tempo} BPM and saved to '{output_file_path}'{Style.RESET_ALL}"
        )


if __name__ == "__main__":
    app()
