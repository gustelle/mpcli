from src.mpcli.entities.source import AudioSource
from src.mpcli.repository.audio_file import load_audio_file
from src.mpcli.use_cases.timestretch import execute_timestretch


def test_execute_timestretch(mp3_source_path):

    # given
    data, sample_rate = load_audio_file(mp3_source_path)

    audio_source = AudioSource.from_array(
        data=data, audio_format="mp3", sample_rate=sample_rate
    )

    # when
    result = execute_timestretch(
        source=audio_source,
        target_tempo=120.0,  # Example target tempo
        min_rate=1.1,
        max_rate=1.2,
    )

    # then
    assert result is not None
