from pathlib import Path

import pytest
from pydantic import ValidationError

from src.mpcli.cli_entities import CLIConfigError, CLITimeStretchConfig


@pytest.mark.parametrize(
    "format",
    [
        "flac",
        "ogg",
        "m4a",
        "aac",
        "opus",
        "wma",
        "alac",
        "aiff",
        "pcm",
        "aifc",
        "aif",
        "aiffc",
        "aif",
        "aiff",
    ],
)
def test_TimeStretchConfig_format_validation(format, wav_source_path):
    with pytest.raises(ValidationError, match="Input should be 'wav' or 'mp3'"):
        CLITimeStretchConfig(
            **{
                "source": wav_source_path,
                "output": "/tmp/output/",
                "audio_format": format,
                "min_rate": 0.8,
                "max_rate": 1.2,
            }
        )


def test_TimeStretchConfig_rate_validation(wav_source_path):
    with pytest.raises(
        ValidationError, match="min_rate cannot be greater than max_rate"
    ):
        CLITimeStretchConfig(
            **{
                "source": wav_source_path,
                "output": "/tmp/output/",
                "audio_format": "wav",
                "min_rate": 1.2,
                "max_rate": 0.8,
            }
        )


def test_TimeStretchConfig_rate_defaults(wav_source_path):
    config = CLITimeStretchConfig(
        **{
            "source": wav_source_path,
            "output": "/tmp/output/",
            "audio_format": "wav",
            "min_rate": 0.8,
        }
    )

    assert config.min_rate == 0.8
    assert config.max_rate == 1.0

    config = CLITimeStretchConfig(
        **{
            "source": wav_source_path,
            "output": "/tmp/output/",
            "audio_format": "wav",
            "max_rate": 1.2,
        }
    )

    assert config.min_rate == 1.0
    assert config.max_rate == 1.2


def test_TimeStretchConfig_default_format(wav_source_path):
    config = CLITimeStretchConfig(
        **{
            "source": wav_source_path,
            "output": "/tmp/output/",
            "min_rate": 0.8,
            "max_rate": 1.2,
        }
    )

    assert config.audio_format == "wav"


def test_TimeStretchConfig_path_conversion(wav_source_path):
    config = CLITimeStretchConfig(
        **{
            "source": wav_source_path,
            "output": "/tmp/output/",
            "audio_format": "wav",
            "min_rate": 0.8,
            "max_rate": 1.2,
        }
    )

    assert isinstance(config.source, Path)
    assert isinstance(config.output, Path)


def test_TimeStretchConfig_source_is_mandatory():
    with pytest.raises(ValidationError, match="Field required"):
        CLITimeStretchConfig(
            **{
                "output": "/tmp/output/",
                "audio_format": "wav",
                "min_rate": 0.8,
                "max_rate": 1.2,
            }
        )


def test_TimeStretchConfig_output_is_mandatory(wav_source_path):
    with pytest.raises(ValidationError, match="Field required"):
        CLITimeStretchConfig(
            **{
                "source": wav_source_path,
                "audio_format": "wav",
                "min_rate": 0.8,
                "max_rate": 1.2,
            }
        )


def test_TimeStretchConfig_target_tempo_and_rate_mutual_exclusivity(wav_source_path):
    with pytest.raises(
        ValidationError,
        match="Only one of target_tempo or min_rate/max_rate can be provided",
    ):
        CLITimeStretchConfig(
            **{
                "source": wav_source_path,
                "output": "/tmp/output/",
                "audio_format": "wav",
                "target_tempo": 120.0,
                "min_rate": 0.8,
                "max_rate": 1.2,
            }
        )


def test_TimeStretchConfig_target_tempo_or_rate_requirement(wav_source_path):
    with pytest.raises(
        ValidationError,
        match="Either target_tempo or min_rate/max_rate must be provided",
    ):
        CLITimeStretchConfig(
            **{
                "source": wav_source_path,
                "output": "/tmp/output/",
                "audio_format": "wav",
            }
        )
