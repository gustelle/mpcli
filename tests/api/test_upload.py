from pathlib import Path

from fastapi.testclient import TestClient

from src.mpcli.api import app


def test_upload_wav(wav_source_path):

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


def test_upload_mp3(mp3_source_path):

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


def test_upload_unsupported_format(invalid_source_path):

    # given
    client = TestClient(app)

    txt_bytes = Path(invalid_source_path).read_bytes()

    # when
    response = client.post("/tempo", files={"file": ("test_file.txt", txt_bytes)})

    # then
    assert response.status_code == 422  # Unprocessable Entity for unsupported format
