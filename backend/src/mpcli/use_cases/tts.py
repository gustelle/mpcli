from pathlib import Path

from src.mpcli.entities.result import TextToSpeechResult
from src.mpcli.repository.tts import synthesize_speech


def execute_text_to_speech(
    text: str,
    ref_audio: Path,
) -> TextToSpeechResult | None:
    """Generate speech from text using the voice of the reference audio.

    Args:
        text (str): The text to synthesize.
        ref_audio (Path): Path to the reference audio whose voice is cloned.

    Returns:
        TextToSpeechResult: The generated speech result.
    """

    generated_audio = synthesize_speech(
        text=text,
        ref_audio=ref_audio,
        name=f"{ref_audio.stem}-gen",
    )

    return TextToSpeechResult(
        text=text,
        ref_audio=str(ref_audio),
        generated_audio=generated_audio,
    )
