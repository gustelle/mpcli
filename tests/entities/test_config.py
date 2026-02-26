from pathlib import Path

import pytest

from src.mpcli.entities.config import ConfigError, TimeStretchConfig


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
def test_TimeStretchConfig_format_validation(format):
    with pytest.raises(ConfigError, match="Invalid format"):
        TimeStretchConfig(
            **{
                "source": "input.wav",
                "output": "output/",
                "format": format,
                "min_rate": 0.8,
                "max_rate": 1.2,
            }
        )


def test_TimeStretchConfig_rate_validation():
    with pytest.raises(ConfigError, match="min_rate cannot be greater than max_rate"):
        TimeStretchConfig(
            **{
                "source": "input.wav",
                "output": "output/",
                "format": "wav",
                "min_rate": 1.2,
                "max_rate": 0.8,
            }
        )


def test_TimeStretchConfig_rate_defaults():
    config = TimeStretchConfig(
        **{
            "source": "input.wav",
            "output": "output/",
            "format": "wav",
            "min_rate": 0.8,
        }
    )

    assert config.min_rate == 0.8
    assert config.max_rate == 1.0

    config = TimeStretchConfig(
        **{
            "source": "input.wav",
            "output": "output/",
            "format": "wav",
            "max_rate": 1.2,
        }
    )

    assert config.min_rate == 1.0
    assert config.max_rate == 1.2


def test_TimeStretchConfig_default_format():
    config = TimeStretchConfig(
        **{
            "source": "input.wav",
            "output": "output/",
            "min_rate": 0.8,
            "max_rate": 1.2,
        }
    )

    assert config.format == "wav"


def test_TimeStretchConfig_path_conversion():
    config = TimeStretchConfig(
        **{
            "source": "input.wav",
            "output": "output/",
            "format": "wav",
            "min_rate": 0.8,
            "max_rate": 1.2,
        }
    )

    assert isinstance(config.source, Path)
    assert isinstance(config.output, Path)


def test_TimeStretchConfig_source_is_mandatory():
    with pytest.raises(ConfigError, match="Source file must be provided"):
        TimeStretchConfig(
            **{
                "output": "output/",
                "format": "wav",
                "min_rate": 0.8,
                "max_rate": 1.2,
            }
        )


def test_TimeStretchConfig_output_is_mandatory():
    with pytest.raises(ConfigError, match="Output directory must be provided"):
        TimeStretchConfig(
            **{
                "source": "input.wav",
                "format": "wav",
                "min_rate": 0.8,
                "max_rate": 1.2,
            }
        )


def test_TimeStretchConfig_target_tempo_and_rate_mutual_exclusivity():
    with pytest.raises(
        ConfigError,
        match="Only one of target_tempo or min_rate/max_rate can be provided",
    ):
        TimeStretchConfig(
            **{
                "source": "input.wav",
                "output": "output/",
                "format": "wav",
                "target_tempo": 120.0,
                "min_rate": 0.8,
                "max_rate": 1.2,
            }
        )


def test_TimeStretchConfig_target_tempo_or_rate_requirement():
    with pytest.raises(
        ConfigError,
        match="Either target_tempo or min_rate/max_rate must be provided",
    ):
        TimeStretchConfig(
            **{
                "source": "input.wav",
                "output": "output/",
                "format": "wav",
            }
        )
