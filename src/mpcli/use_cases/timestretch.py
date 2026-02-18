from pathlib import Path
from typing import Generator

from audiomentations import TimeStretch
from audiomentations.core.audio_loading_utils import load_sound_file
from scipy.io import wavfile

from mpcli.entities.config import ConvertConfig, DetectTempoConfig, TimeStretchConfig
from mpcli.entities.result import TimeStretchResult
from mpcli.repository.files import iter_sources
from mpcli.use_cases.convert import execute_format_conversion
from mpcli.use_cases.tempo import execute_tempo_estimation


def execute_timestretch(
    config: TimeStretchConfig,
) -> Generator[TimeStretchResult | None, None, None]:

    for source in iter_sources(config.source):

        # estimate the global tempo
        tempo_config = DetectTempoConfig(source=source)
        result = next(execute_tempo_estimation(tempo_config))

        # compute the time stretch factor
        if config.ratio is not None:
            factor = config.ratio
            target_tempo = round(result.tempo * factor, 2)
        else:
            target_tempo = config.target_tempo
            factor = target_tempo / result.tempo

        samples, sample_rate = load_sound_file(source, sample_rate=None, mono=False)

        if len(samples.shape) == 2 and samples.shape[0] > samples.shape[1]:
            samples = samples.transpose()

        output_dir = config.output
        output_format = config.format

        if config.create_target_dir:
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

        wav_output_path = output_dir / f"{source.stem}_{target_tempo}.wav"

        if wav_output_path.exists():
            wav_output_path.unlink()

        augmented_samples = augmenter(samples=samples, sample_rate=sample_rate)

        if len(augmented_samples.shape) == 2:
            augmented_samples = augmented_samples.transpose()

        # always export as wav, even if the output format is mp3,
        wavfile.write(wav_output_path, rate=sample_rate, data=augmented_samples)

        match output_format:
            case "mp3":
                conversion_config = ConvertConfig(
                    source=wav_output_path,
                    output=output_dir,
                    format=output_format,
                )
                next(execute_format_conversion(conversion_config))

                # remove the wav file
                wav_output_path.unlink()

        yield TimeStretchResult(
            source_path=str(source),
            original_tempo=result.tempo,
            target_tempo=target_tempo,
            target_path=str(
                output_dir / f"{source.stem}_{target_tempo}.{output_format}"
            ),
        )
