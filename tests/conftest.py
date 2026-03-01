from pathlib import Path

import pytest


@pytest.fixture
def wav_source_path():
    p = Path(__file__).parent / "assets" / "valid_audio.wav"
    return p


@pytest.fixture
def long_wav_source_path():
    p = Path(__file__).parent / "assets" / "Beethoven_Sonata.wav"
    return p


@pytest.fixture
def mp3_source_path():
    p = Path(__file__).parent / "assets" / "valid_audio.mp3"
    return p


@pytest.fixture
def invalid_source_path():
    p = Path(__file__).parent / "assets" / "invalid_audio.txt"
    return p
