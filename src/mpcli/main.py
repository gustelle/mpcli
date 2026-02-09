# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import os
import re
import tomllib
from pathlib import Path
from pprint import pprint
from typing import Annotated

import audioread
import typer
from audiomentations import TimeStretch
from audiomentations.core.audio_loading_utils import load_sound_file
from audiomentations.core.transforms_interface import (
    MultichannelAudioNotSupportedException,
)
from colorama import Fore, Style
from colorama import init as colorama_init
from scipy.io import wavfile
from tempocnn.classifier import TempoClassifier
from tempocnn.feature import read_features
from tqdm import tqdm

from mpcli.entities.result import Result

app = typer.Typer()

colorama_init()


@app.command()
def tempo():

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        source_path = data["tempo"]["source"]

    tempi: list[Result] = []

    model_name = "cnn"

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

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

    for source in batch:
        try:

            features = read_features(source)

            # estimate the global tempo
            tempo = classifier.estimate_tempo(features, interpolate=False)
            tempi.append(Result(file=source.name, tempo=tempo))

        except audioread.exceptions.NoBackendError as e:
            print(f"{Fore.RED}Error processing {source}: {e}{Style.RESET_ALL}")

    print(f"{Fore.GREEN}Estimated tempi:{Style.RESET_ALL}")
    pprint(tempi, indent=2)


@app.command()
def timestretch():

    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
        source_path = data["timestretch"]["source"]

    target_tempo: float = float(data["timestretch"]["target_tempo"])

    model_name = "cnn"

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

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

    print(
        f"{Fore.GREEN}Processing {len(batch)} files for time-stretching...{Style.RESET_ALL}"
    )

    for source in batch:

        try:
            features = read_features(source)

            # estimate the global tempo
            tempo = classifier.estimate_tempo(features, interpolate=False)

            # compute the time stretch factor
            factor = target_tempo / tempo

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

                wavfile.write(
                    output_file_path, rate=sample_rate, data=augmented_samples
                )

        except audioread.exceptions.NoBackendError as e:
            print(f"{Fore.RED}Error processing {source}: {e}{Style.RESET_ALL}")
        except MultichannelAudioNotSupportedException as e:
            print(f"{Fore.RED}{e}{Style.RESET_ALL}")

        print(
            f"{Fore.GREEN}Time-stretched '{source.name}' to {target_tempo} BPM and saved to '{output_file_path}'{Style.RESET_ALL}"
        )


if __name__ == "__main__":
    app()
