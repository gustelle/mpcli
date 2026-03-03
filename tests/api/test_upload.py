import tempfile
from pathlib import Path

import librosa
from fastapi.testclient import TestClient

from src.mpcli.api import app


def test_tempo_wav(wav_source_path):

    # given
    client = TestClient(app)

    wav_bytes = Path(wav_source_path).read_bytes()

    # when
    response = client.post("/tempo", files={"file": ("test_audio.wav", wav_bytes)})

    # then
    assert response.status_code == 200
    assert response.json()["source_name"] == "test_audio.wav"
    assert response.json()["source_format"] == "wav"
    assert isinstance(response.json()["tempo"], float) and response.json()["tempo"] > 0


def test_tempo_mp3(mp3_source_path):

    # given
    client = TestClient(app)

    mp3_bytes = Path(mp3_source_path).read_bytes()

    # when
    response = client.post("/tempo", files={"file": ("test_audio.mp3", mp3_bytes)})

    # then
    assert response.status_code == 200
    assert response.json()["source_name"] == "test_audio.mp3"
    assert response.json()["source_format"] == "mp3"
    assert isinstance(response.json()["tempo"], float) and response.json()["tempo"] > 0


def test_tempo_unsupported_format(invalid_source_path):

    # given
    client = TestClient(app)

    txt_bytes = Path(invalid_source_path).read_bytes()

    # when
    response = client.post("/tempo", files={"file": ("test_file.txt", txt_bytes)})

    # then
    assert response.status_code == 422  # Unprocessable Entity for unsupported format


def test_convert_unsupported_format(invalid_source_path):

    # given
    client = TestClient(app)

    txt_bytes = Path(invalid_source_path).read_bytes()

    # when
    response = client.post(
        "/convert",
        files={"file": ("test_file.txt", txt_bytes)},
        data={"target_format": "wav"},
    )

    # then
    assert response.status_code == 422  # Unprocessable Entity for unsupported format


def test_convert_wav_to_mp3(wav_source_path):

    # given
    client = TestClient(app)

    initial_duration = librosa.get_duration(filename=wav_source_path)

    wav_bytes = Path(wav_source_path).read_bytes()

    # when
    response = client.post(
        "/convert",
        files={"file": ("test_audio.wav", wav_bytes)},
        data={"target_format": "mp3"},
    )

    # then
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert len(response.content) > 0

    # check the content is a valid mp3 file
    # try to read it
    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp_file:
        tmp_file.write(response.content)
        tmp_file.flush()
        duration = librosa.get_duration(path=tmp_file.name)
        assert (
            duration == initial_duration
        )  # Check that the duration of the converted file matches the original


def test_convert_mp3_to_wav(mp3_source_path):

    # given
    client = TestClient(app)

    mp3_bytes = Path(mp3_source_path).read_bytes()

    initial_duration = librosa.get_duration(filename=mp3_source_path)

    # when
    response = client.post(
        "/convert",
        files={"file": ("test_audio.mp3", mp3_bytes)},
        data={"target_format": "wav"},
    )

    # then
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert len(response.content) > 0

    # check the content is a valid wav file
    # try to read it
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_file:
        tmp_file.write(response.content)
        tmp_file.flush()
        duration = librosa.get_duration(path=tmp_file.name)
        assert (
            duration == initial_duration
        )  # Check that the duration of the converted file matches the original


def test_convert_invalid_target_format(wav_source_path):

    # given
    client = TestClient(app)

    wav_bytes = Path(wav_source_path).read_bytes()

    # when
    response = client.post(
        "/convert",
        files={"file": ("test_audio.wav", wav_bytes)},
        data={"target_format": "flac"},  # Unsupported format
    )

    # then
    assert (
        response.status_code == 422
    )  # Unprocessable Entity for unsupported target format


def test_normalize_invalid_lufs(wav_source_path):

    # given
    client = TestClient(app)

    wav_bytes = Path(wav_source_path).read_bytes()

    # when
    response = client.post(
        "/normalize",
        files={"file": ("test_audio.wav", wav_bytes)},
        data={"lufs": "invalid"},  # Invalid LUFS value
    )

    # then
    assert response.status_code == 422  # Unprocessable Entity for invalid LUFS value


def test_normalize_valid_lufs(wav_source_path):

    # given
    client = TestClient(app)

    wav_bytes = Path(wav_source_path).read_bytes()

    # when
    response = client.post(
        "/normalize",
        files={"file": ("test_audio.wav", wav_bytes)},
        data={"lufs": -14.0},  # Valid LUFS value
    )

    # then
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert len(response.content) > 0


def test_timestretch_invalid_tempo(wav_source_path):

    # given
    client = TestClient(app)

    wav_bytes = Path(wav_source_path).read_bytes()

    # when
    response = client.post(
        "/timestretch",
        files={"file": ("test_audio.wav", wav_bytes)},
        data={"target_tempo": "invalid"},  # Invalid tempo value
    )

    # then
    assert response.status_code == 422  # Unprocessable Entity for invalid tempo value


def test_timestretch_valid_tempo(wav_source_path):

    # given
    client = TestClient(app)

    wav_bytes = Path(wav_source_path).read_bytes()

    # when
    response = client.post(
        "/timestretch",
        files={"file": ("test_audio.wav", wav_bytes)},
        data={"target_tempo": 120.0},  # Valid tempo value
    )

    # then
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert len(response.content) > 0
