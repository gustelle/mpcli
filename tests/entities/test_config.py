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
